"""Minimal plugin host for vstbridge's real-Wine tests.

Loads a bridged plugin (the yabridge chainloader) the way a DAW does and prints
JSON. Each call runs in its own process, so a crash in the bridge or in Wine
fails one test instead of the test run.

    python3 vstbridge_host.py clap-scan <file.clap>
    python3 vstbridge_host.py clap-process <file.clap> [--frames N] [--blocks N]
    python3 vstbridge_host.py clap-gui <file.clap> --out DIR [--seconds N] [--click X,Y]
    python3 vstbridge_host.py vst3-scan <bundle.vst3 or .so>
    python3 vstbridge_host.py vst3-process <plugin.vst3> [--pitch N] [--wait S] [--frames N]
"""

import ctypes as C
import hashlib
import json
import math
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# --- CLAP (https://github.com/free-audio/clap, include/clap/*.h) --------------------------


class Version(C.Structure):
    _fields_ = [("major", C.c_uint32), ("minor", C.c_uint32), ("revision", C.c_uint32)]


class Descriptor(C.Structure):
    _fields_ = (
        [("clap_version", Version)]
        + [
            (n, C.c_char_p)
            for n in (
                "id",
                "name",
                "vendor",
                "url",
                "manual_url",
                "support_url",
                "version",
                "description",
            )
        ]
        + [("features", C.POINTER(C.c_char_p))]
    )


class Host(C.Structure):
    pass


GET_EXT = C.CFUNCTYPE(C.c_void_p, C.POINTER(Host), C.c_char_p)
HOST_CB = C.CFUNCTYPE(None, C.POINTER(Host))
Host._fields_ = [
    ("clap_version", Version),
    ("host_data", C.c_void_p),
    ("name", C.c_char_p),
    ("vendor", C.c_char_p),
    ("url", C.c_char_p),
    ("version", C.c_char_p),
    ("get_extension", GET_EXT),
    ("request_restart", HOST_CB),
    ("request_process", HOST_CB),
    ("request_callback", HOST_CB),
]


class AudioBuffer(C.Structure):
    _fields_ = [
        ("data32", C.POINTER(C.POINTER(C.c_float))),
        ("data64", C.POINTER(C.POINTER(C.c_double))),
        ("channel_count", C.c_uint32),
        ("latency", C.c_uint32),
        ("constant_mask", C.c_uint64),
    ]


class InputEvents(C.Structure):
    pass


class OutputEvents(C.Structure):
    pass


IN_SIZE = C.CFUNCTYPE(C.c_uint32, C.POINTER(InputEvents))
IN_GET = C.CFUNCTYPE(C.c_void_p, C.POINTER(InputEvents), C.c_uint32)
OUT_PUSH = C.CFUNCTYPE(C.c_bool, C.POINTER(OutputEvents), C.c_void_p)
InputEvents._fields_ = [("ctx", C.c_void_p), ("size", IN_SIZE), ("get", IN_GET)]
OutputEvents._fields_ = [("ctx", C.c_void_p), ("try_push", OUT_PUSH)]


class Process(C.Structure):
    _fields_ = [
        ("steady_time", C.c_int64),
        ("frames_count", C.c_uint32),
        ("transport", C.c_void_p),
        ("audio_inputs", C.POINTER(AudioBuffer)),
        ("audio_outputs", C.POINTER(AudioBuffer)),
        ("audio_inputs_count", C.c_uint32),
        ("audio_outputs_count", C.c_uint32),
        ("in_events", C.POINTER(InputEvents)),
        ("out_events", C.POINTER(OutputEvents)),
    ]


class Plugin(C.Structure):
    pass


P = C.POINTER(Plugin)
Plugin._fields_ = [
    ("desc", C.POINTER(Descriptor)),
    ("plugin_data", C.c_void_p),
    ("init", C.CFUNCTYPE(C.c_bool, P)),
    ("destroy", C.CFUNCTYPE(None, P)),
    ("activate", C.CFUNCTYPE(C.c_bool, P, C.c_double, C.c_uint32, C.c_uint32)),
    ("deactivate", C.CFUNCTYPE(None, P)),
    ("start_processing", C.CFUNCTYPE(C.c_bool, P)),
    ("stop_processing", C.CFUNCTYPE(None, P)),
    ("reset", C.CFUNCTYPE(None, P)),
    ("process", C.CFUNCTYPE(C.c_int32, P, C.POINTER(Process))),
    ("get_extension", C.CFUNCTYPE(C.c_void_p, P, C.c_char_p)),
    ("on_main_thread", C.CFUNCTYPE(None, P)),
]


class Factory(C.Structure):
    pass


F = C.POINTER(Factory)
Factory._fields_ = [
    ("get_plugin_count", C.CFUNCTYPE(C.c_uint32, F)),
    ("get_plugin_descriptor", C.CFUNCTYPE(C.POINTER(Descriptor), F, C.c_uint32)),
    ("create_plugin", C.CFUNCTYPE(P, F, C.POINTER(Host), C.c_char_p)),
]


class Entry(C.Structure):
    _fields_ = [
        ("clap_version", Version),
        ("init", C.CFUNCTYPE(C.c_bool, C.c_char_p)),
        ("deinit", C.CFUNCTYPE(None)),
        ("get_factory", C.CFUNCTYPE(C.c_void_p, C.c_char_p)),
    ]


class PortInfo(C.Structure):
    _fields_ = [
        ("id", C.c_uint32),
        ("name", C.c_char * 256),
        ("flags", C.c_uint32),
        ("channel_count", C.c_uint32),
        ("port_type", C.c_char_p),
        ("in_place_pair", C.c_uint32),
    ]


class AudioPorts(C.Structure):
    _fields_ = [
        ("count", C.CFUNCTYPE(C.c_uint32, P, C.c_bool)),
        ("get", C.CFUNCTYPE(C.c_bool, P, C.c_uint32, C.c_bool, C.POINTER(PortInfo))),
    ]


def text(value):
    return value.decode(errors="replace") if value else None


def clap_open(path):
    lib = C.CDLL(str(path))
    entry = Entry.in_dll(lib, "clap_entry")
    if not entry.init(str(path).encode()):
        raise SystemExit("clap_entry.init failed")
    factory = C.cast(entry.get_factory(b"clap.plugin-factory"), F)
    if not factory:
        raise SystemExit("no clap.plugin-factory")
    return lib, entry, factory


def clap_scan(path):
    _lib, entry, factory = clap_open(path)
    plugins = []
    for i in range(factory.contents.get_plugin_count(factory)):
        d = factory.contents.get_plugin_descriptor(factory, i).contents
        plugins.append(
            {
                "id": text(d.id),
                "name": text(d.name),
                "vendor": text(d.vendor),
                "version": text(d.version),
            }
        )
    entry.deinit()
    return {"plugins": plugins}


def make_host():
    keep = []

    def get_extension(host, ext):
        return None

    def noop(host):
        return None

    callbacks = (GET_EXT(get_extension), HOST_CB(noop), HOST_CB(noop), HOST_CB(noop))
    keep.extend(callbacks)
    host = Host(Version(1, 2, 0), None, b"vstbridge-test-host", b"vstbridge", b"", b"1", *callbacks)
    return host, keep


def ports(plugin, is_input):
    ext = plugin.contents.get_extension(plugin, b"clap.audio-ports")
    if not ext:
        return [2]
    api = C.cast(ext, C.POINTER(AudioPorts)).contents
    counts = []
    for i in range(api.count(plugin, is_input)):
        info = PortInfo()
        if api.get(plugin, i, is_input, C.byref(info)):
            counts.append(info.channel_count)
    return counts


def buffers(channel_counts, frames):
    arrays, keep = (AudioBuffer * max(1, len(channel_counts)))(), []
    for i, channels in enumerate(channel_counts):
        chans = (C.POINTER(C.c_float) * channels)()
        for c in range(channels):
            data = (C.c_float * frames)()
            keep.append(data)
            chans[c] = C.cast(data, C.POINTER(C.c_float))
        keep.append(chans)
        arrays[i].data32 = C.cast(chans, C.POINTER(C.POINTER(C.c_float)))
        arrays[i].channel_count = channels
    return arrays, keep


def clap_process(path, frames=256, blocks=40, rate=48000.0):
    _lib, entry, factory = clap_open(path)
    desc = factory.contents.get_plugin_descriptor(factory, 0).contents
    name = text(desc.name)
    host, _keep = make_host()
    plugin = factory.contents.create_plugin(factory, C.byref(host), desc.id)
    if not plugin or not plugin.contents.init(plugin):
        raise SystemExit("create_plugin or init failed")
    ins, outs = ports(plugin, True), ports(plugin, False)
    if not plugin.contents.activate(plugin, rate, 1, frames):
        raise SystemExit("activate failed")
    if not plugin.contents.start_processing(plugin):
        raise SystemExit("start_processing failed")
    in_bufs, _k1 = buffers(ins, frames)
    out_bufs, _k2 = buffers(outs, frames)
    events_in = InputEvents(None, IN_SIZE(lambda lst: 0), IN_GET(lambda lst, i: None))
    events_out = OutputEvents(None, OUT_PUSH(lambda lst, ev: True))
    proc = Process(
        0,
        frames,
        None,
        in_bufs,
        out_bufs,
        len(ins),
        len(outs),
        C.pointer(events_in),
        C.pointer(events_out),
    )
    peak_in = peak_out = 0.0
    finite = True
    statuses = set()
    for block in range(blocks):
        for b in range(len(ins)):
            for c in range(ins[b]):
                data = in_bufs[b].data32[c]
                for n in range(frames):
                    value = 0.5 * math.sin(2 * math.pi * 440 * (block * frames + n) / rate)
                    data[n] = value
                    peak_in = max(peak_in, abs(value))
        proc.steady_time = block * frames
        statuses.add(plugin.contents.process(plugin, C.byref(proc)))
        for b in range(len(outs)):
            for c in range(outs[b]):
                data = out_bufs[b].data32[c]
                for n in range(frames):
                    value = data[n]
                    finite &= math.isfinite(value)
                    peak_out = max(peak_out, abs(value))
    plugin.contents.stop_processing(plugin)
    plugin.contents.deactivate(plugin)
    plugin.contents.destroy(plugin)
    entry.deinit()
    return {
        "plugin": name,
        "inputs": ins,
        "outputs": outs,
        "statuses": sorted(statuses),
        "peak_in": peak_in,
        "peak_out": peak_out,
        "finite": finite,
        "frames": frames * blocks,
    }


# --- VST3 (pluginterfaces/base/ipluginbase.h) ------------------------------------------------


class FactoryInfo(C.Structure):
    _fields_ = [
        ("vendor", C.c_char * 64),
        ("url", C.c_char * 256),
        ("email", C.c_char * 128),
        ("flags", C.c_int32),
    ]


class ClassInfo(C.Structure):
    _fields_ = [
        ("cid", C.c_char * 16),
        ("cardinality", C.c_int32),
        ("category", C.c_char * 32),
        ("name", C.c_char * 64),
    ]


def vst3_library(path):
    path = Path(path)
    if path.suffix == ".vst3":
        found = sorted((path / "Contents/x86_64-linux").glob("*.so"))
        if not found:
            raise SystemExit(f"no Linux module in {path}")
        path = found[0]
    return path


def vst3_scan(path):
    module = vst3_library(path)
    lib = C.CDLL(str(module))
    handle = C.c_void_p(lib._handle)
    lib.ModuleEntry.restype, lib.ModuleEntry.argtypes = C.c_bool, [C.c_void_p]
    if not lib.ModuleEntry(handle):
        raise SystemExit("ModuleEntry failed")
    lib.GetPluginFactory.restype = C.c_void_p
    factory = lib.GetPluginFactory()
    if not factory:
        raise SystemExit("GetPluginFactory returned null")
    vtable = C.cast(C.cast(factory, C.POINTER(C.c_void_p))[0], C.POINTER(C.c_void_p))
    get_factory_info = C.CFUNCTYPE(C.c_int32, C.c_void_p, C.POINTER(FactoryInfo))(vtable[3])
    count_classes = C.CFUNCTYPE(C.c_int32, C.c_void_p)(vtable[4])
    get_class_info = C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_int32, C.POINTER(ClassInfo))(vtable[5])
    release = C.CFUNCTYPE(C.c_uint32, C.c_void_p)(vtable[2])
    info = FactoryInfo()
    get_factory_info(factory, C.byref(info))
    classes = []
    for i in range(count_classes(factory)):
        ci = ClassInfo()
        if get_class_info(factory, i, C.byref(ci)) == 0:
            classes.append(
                {
                    "name": ci.name.decode(errors="replace"),
                    "category": ci.category.decode(errors="replace"),
                }
            )
    release(factory)
    lib.ModuleExit.restype = C.c_bool
    lib.ModuleExit()
    return {"vendor": info.vendor.decode(errors="replace"), "classes": classes}


# --- CLAP editor (clap/ext/gui.h, timer-support.h, posix-fd-support.h) ---------------------


class Window(C.Structure):
    _fields_ = [("api", C.c_char_p), ("x11", C.c_ulong)]


class PluginGui(C.Structure):
    _fields_ = [
        ("is_api_supported", C.CFUNCTYPE(C.c_bool, P, C.c_char_p, C.c_bool)),
        ("get_preferred_api", C.c_void_p),
        ("create", C.CFUNCTYPE(C.c_bool, P, C.c_char_p, C.c_bool)),
        ("destroy", C.CFUNCTYPE(None, P)),
        ("set_scale", C.CFUNCTYPE(C.c_bool, P, C.c_double)),
        ("get_size", C.CFUNCTYPE(C.c_bool, P, C.POINTER(C.c_uint32), C.POINTER(C.c_uint32))),
        ("can_resize", C.CFUNCTYPE(C.c_bool, P)),
        ("get_resize_hints", C.c_void_p),
        ("adjust_size", C.c_void_p),
        ("set_size", C.CFUNCTYPE(C.c_bool, P, C.c_uint32, C.c_uint32)),
        ("set_parent", C.CFUNCTYPE(C.c_bool, P, C.POINTER(Window))),
        ("set_transient", C.c_void_p),
        ("suggest_title", C.c_void_p),
        ("show", C.CFUNCTYPE(C.c_bool, P)),
        ("hide", C.CFUNCTYPE(C.c_bool, P)),
    ]


H = C.POINTER(Host)
HOST_GUI = [
    ("resize_hints_changed", C.CFUNCTYPE(None, H)),
    ("request_resize", C.CFUNCTYPE(C.c_bool, H, C.c_uint32, C.c_uint32)),
    ("request_show", C.CFUNCTYPE(C.c_bool, H)),
    ("request_hide", C.CFUNCTYPE(C.c_bool, H)),
    ("closed", C.CFUNCTYPE(None, H, C.c_bool)),
]
HOST_TIMER = [
    ("register_timer", C.CFUNCTYPE(C.c_bool, H, C.c_uint32, C.POINTER(C.c_uint32))),
    ("unregister_timer", C.CFUNCTYPE(C.c_bool, H, C.c_uint32)),
]
HOST_FD = [
    ("register_fd", C.CFUNCTYPE(C.c_bool, H, C.c_int, C.c_uint32)),
    ("modify_fd", C.CFUNCTYPE(C.c_bool, H, C.c_int, C.c_uint32)),
    ("unregister_fd", C.CFUNCTYPE(C.c_bool, H, C.c_int)),
]


def struct(fields, **impl):
    cls = type("HostExt", (C.Structure,), {"_fields_": fields})
    return cls(*(ftype(impl[name]) for name, ftype in fields))


class Loop:
    """The host's main thread: timers, file descriptors and request_callback."""

    def __init__(self):
        self.timers, self.fds, self.callback, self.resized = {}, {}, False, None
        self.next_id = 1

        def register_timer(host, period, out):
            out[0] = self.next_id
            self.timers[self.next_id] = [period / 1000, 0.0]
            self.next_id += 1
            return True

        def register_fd(host, fd, flags):
            self.fds[fd] = flags
            return True

        def unregister_fd(host, fd):
            return self.fds.pop(fd, None) is not None

        def request_resize(host, width, height):
            self.resized = (width, height)
            return True

        self.exts = {
            b"clap.gui": struct(
                HOST_GUI,
                resize_hints_changed=lambda h: None,
                request_resize=request_resize,
                request_show=lambda h: True,
                request_hide=lambda h: True,
                closed=lambda h, destroyed: None,
            ),
            b"clap.timer-support": struct(
                HOST_TIMER,
                register_timer=register_timer,
                unregister_timer=lambda h, i: self.timers.pop(i, None) is not None,
            ),
            b"clap.posix-fd-support": struct(
                HOST_FD, register_fd=register_fd, modify_fd=register_fd, unregister_fd=unregister_fd
            ),
        }

    def host(self):
        def get_extension(host, ext):
            found = self.exts.get(ext)
            return C.addressof(found) if found is not None else None

        def request_callback(host):
            self.callback = True

        self.callbacks = (
            GET_EXT(get_extension),
            HOST_CB(lambda h: None),
            HOST_CB(lambda h: None),
            HOST_CB(request_callback),
        )
        return Host(
            Version(1, 2, 0), None, b"vstbridge-test-host", b"vstbridge", b"", b"1", *self.callbacks
        )

    def run(self, plugin, seconds):
        import select
        import time

        timer_ext = plugin.contents.get_extension(plugin, b"clap.timer-support")
        on_timer = (
            C.cast(timer_ext, C.POINTER(C.CFUNCTYPE(None, P, C.c_uint32))) if timer_ext else None
        )
        fd_ext = plugin.contents.get_extension(plugin, b"clap.posix-fd-support")
        on_fd = (
            C.cast(fd_ext, C.POINTER(C.CFUNCTYPE(None, P, C.c_int, C.c_uint32))) if fd_ext else None
        )
        end = time.monotonic() + seconds
        while (now := time.monotonic()) < end:
            if self.callback:
                self.callback = False
                plugin.contents.on_main_thread(plugin)
            due = [t[1] for t in self.timers.values()] or [now + 0.01]
            wait = max(0.0, min(min(due) - now, end - now, 0.01))
            readable = [fd for fd, flags in self.fds.items() if flags & 1]
            ready = select.select(readable, [], [], wait)[0] if readable else time.sleep(wait) or []
            if on_fd:
                for fd in ready:
                    on_fd[0](plugin, fd, 1)
            now = time.monotonic()
            for tid, timer in list(self.timers.items()):
                if on_timer and timer[1] <= now:
                    timer[1] = now + timer[0]
                    on_timer[0](plugin, tid)


def x11():
    lib = C.CDLL("libX11.so.6")
    lib.XOpenDisplay.restype = C.c_void_p
    lib.XOpenDisplay.argtypes = [C.c_char_p]
    lib.XDefaultRootWindow.restype = C.c_ulong
    lib.XDefaultRootWindow.argtypes = [C.c_void_p]
    lib.XCreateSimpleWindow.restype = C.c_ulong
    lib.XCreateSimpleWindow.argtypes = (
        [C.c_void_p, C.c_ulong] + [C.c_int] * 2 + [C.c_uint] * 3 + [C.c_ulong] * 2
    )
    for name in ("XMapWindow", "XResizeWindow", "XFlush", "XStoreName"):
        getattr(lib, name).argtypes = None
    return lib


def snapshot(window, path):
    subprocess.run(["import", "-window", str(window), f"ppm:{path}"], check=True, timeout=30)
    data = Path(path).read_bytes()
    _, width, height, _, pixels = data.split(maxsplit=4)
    colors = {pixels[i : i + 3] for i in range(0, len(pixels), 3)}
    return {
        "width": int(width),
        "height": int(height),
        "colors": len(colors),
        "digest": hashlib.sha256(pixels).hexdigest()[:16],
    }


def clap_gui(path, out_dir, seconds=8.0, click=None, close_timeout=15.0):
    _lib, entry, factory = clap_open(path)
    desc = factory.contents.get_plugin_descriptor(factory, 0).contents
    loop = Loop()
    host = loop.host()
    plugin = factory.contents.create_plugin(factory, C.byref(host), desc.id)
    if not plugin or not plugin.contents.init(plugin):
        raise SystemExit("create_plugin or init failed")
    ext = plugin.contents.get_extension(plugin, b"clap.gui")
    if not ext:
        raise SystemExit("plugin has no clap.gui")
    gui = C.cast(ext, C.POINTER(PluginGui)).contents
    result = {"x11": gui.is_api_supported(plugin, b"x11", False)}
    if not result["x11"] or not gui.create(plugin, b"x11", False):
        raise SystemExit("gui.create(x11) failed")
    w, h = C.c_uint32(), C.c_uint32()
    gui.get_size(plugin, C.byref(w), C.byref(h))
    result["size"] = [w.value, h.value]
    xlib = x11()
    display = xlib.XOpenDisplay(None)
    if not display:
        raise SystemExit("cannot open the X display")
    parent = xlib.XCreateSimpleWindow(
        display, xlib.XDefaultRootWindow(display), 0, 0, max(w.value, 1), max(h.value, 1), 0, 0, 0
    )
    xlib.XStoreName(C.c_void_p(display), C.c_ulong(parent), b"vstbridge editor test")
    xlib.XMapWindow(C.c_void_p(display), C.c_ulong(parent))
    xlib.XFlush(C.c_void_p(display))
    result["parent"] = parent
    result["set_parent"] = gui.set_parent(plugin, C.byref(Window(b"x11", parent)))
    result["show"] = gui.show(plugin)
    loop.run(plugin, seconds)
    result["timers"], result["fds"] = len(loop.timers), len(loop.fds)
    result["shown"] = snapshot(parent, Path(out_dir) / "shown.ppm")
    if click:
        x, y = str(round(w.value * click[0])), str(round(h.value * click[1]))
        subprocess.run(
            ["xdotool", "mousemove", "--window", str(parent), x, y, "sleep", "0.3", "click", "1"],
            check=True,
            timeout=30,
        )
        loop.run(plugin, 2.0)
        result["clicked"] = snapshot(parent, Path(out_dir) / "clicked.ppm")
    # A plugin that never returns from gui.destroy would hang the harness, as it
    # would hang a DAW. Report it and exit; yabridge's Wine host exits with us.
    watchdog = threading.Timer(close_timeout, report, (result | {"closed": False},))
    watchdog.daemon = True
    watchdog.start()
    gui.hide(plugin)
    gui.destroy(plugin)
    watchdog.cancel()
    result["closed"] = True
    plugin.contents.destroy(plugin)
    entry.deinit()
    return result


# --- VST3 audio (pluginterfaces/vst/ivstcomponent.h, ivstaudioprocessor.h, ivstevents.h) --


def tuid(*parts):
    return b"".join(part.to_bytes(4, "big") for part in parts)


IID_FUNKNOWN = tuid(0, 0, 0xC0000000, 0x00000046)
IID_HOST_APP = tuid(0x58E595CC, 0xDB2D4969, 0x8B6AAF8C, 0x36A664E5)
IID_COMPONENT = tuid(0xE831FF31, 0xF2D54301, 0x928EBBEE, 0x25697802)
IID_PROCESSOR = tuid(0x42043F99, 0xB7DA453C, 0xA569E79D, 0x9AAEC33D)
IID_EVENT_LIST = tuid(0x3A2C4214, 0x346349FE, 0xB2C4F397, 0xB9695A44)
K_OK, K_NO_INTERFACE = 0, -1
AUDIO, EVENT, INPUT, OUTPUT = 0, 1, 0, 1


class BusInfo(C.Structure):
    _fields_ = [
        ("media", C.c_int32),
        ("direction", C.c_int32),
        ("channels", C.c_int32),
        ("name", C.c_uint16 * 128),
        ("bus_type", C.c_int32),
        ("flags", C.c_uint32),
    ]


class ProcessSetup(C.Structure):
    _fields_ = [
        ("mode", C.c_int32),
        ("sample_size", C.c_int32),
        ("max_samples", C.c_int32),
        ("rate", C.c_double),
    ]


class BusBuffers(C.Structure):
    _fields_ = [
        ("channels", C.c_int32),
        ("silence", C.c_uint64),
        ("data32", C.POINTER(C.POINTER(C.c_float))),
    ]


class ProcessData(C.Structure):
    _fields_ = [
        ("mode", C.c_int32),
        ("sample_size", C.c_int32),
        ("samples", C.c_int32),
        ("num_inputs", C.c_int32),
        ("num_outputs", C.c_int32),
        ("inputs", C.POINTER(BusBuffers)),
        ("outputs", C.POINTER(BusBuffers)),
        ("in_params", C.c_void_p),
        ("out_params", C.c_void_p),
        ("in_events", C.c_void_p),
        ("out_events", C.c_void_p),
        ("context", C.c_void_p),
    ]


class ProcessContext(C.Structure):
    _fields_ = [
        ("state", C.c_uint32),
        ("rate", C.c_double),
        ("project_samples", C.c_int64),
        ("system_time", C.c_int64),
        ("continuous_samples", C.c_int64),
        ("project_music", C.c_double),
        ("bar_music", C.c_double),
        ("cycle_start", C.c_double),
        ("cycle_end", C.c_double),
        ("tempo", C.c_double),
        ("numerator", C.c_int32),
        ("denominator", C.c_int32),
        ("chord", C.c_int32),
        ("smpte", C.c_int32),
        ("fps", C.c_uint32 * 2),
        ("samples_to_clock", C.c_int32),
    ]


class NoteOn(C.Structure):
    _fields_ = [
        ("bus", C.c_int32),
        ("offset", C.c_int32),
        ("ppq", C.c_double),
        ("flags", C.c_uint16),
        ("type", C.c_uint16),
        ("pad", C.c_uint32),
        ("channel", C.c_int16),
        ("pitch", C.c_int16),
        ("tuning", C.c_float),
        ("velocity", C.c_float),
        ("length", C.c_int32),
        ("note_id", C.c_int32),
        ("tail", C.c_int32),
    ]


QUERY = C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_void_p, C.POINTER(C.c_void_p))
REF = C.CFUNCTYPE(C.c_uint32, C.c_void_p)


def method(obj, index, restype, *argtypes):
    vtable = C.cast(obj, C.POINTER(C.POINTER(C.c_void_p)))[0]
    function = C.CFUNCTYPE(restype, C.c_void_p, *argtypes)(vtable[index])
    return lambda *args: function(obj, *args)


class ComObject:
    """A COM-style object for the plugin to call back into."""

    def __init__(self, iid, *methods):
        def query(this, wanted, out):
            if C.string_at(wanted, 16) in (IID_FUNKNOWN, iid):
                out[0] = this
                return K_OK
            out[0] = None
            return K_NO_INTERFACE

        self.funcs = (QUERY(query), REF(lambda this: 1), REF(lambda this: 1), *methods)
        self.vtable = (C.c_void_p * len(self.funcs))(*[C.cast(f, C.c_void_p) for f in self.funcs])
        self.holder = C.c_void_p(C.addressof(self.vtable))
        self.ptr = C.addressof(self.holder)


def host_application():
    def get_name(this, out):
        C.memmove(out, "vstbridge-test-host\0".encode("utf-16-le"), 40)
        return K_OK

    return ComObject(
        IID_HOST_APP,
        C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_void_p)(get_name),
        C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_void_p, C.c_void_p, C.c_void_p)(
            lambda this, cid, iid, out: 3
        ),
    )


def event_list(events):
    def get(this, index, out):
        C.memmove(out, C.byref(events[index]), C.sizeof(NoteOn))
        return K_OK

    return ComObject(
        IID_EVENT_LIST,
        C.CFUNCTYPE(C.c_int32, C.c_void_p)(lambda this: len(events)),
        C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_int32, C.c_void_p)(get),
        C.CFUNCTYPE(C.c_int32, C.c_void_p, C.c_void_p)(lambda this, event: 1),
    )


def channel_buffers(channels, frames):
    data = [(C.c_float * frames)() for _ in range(channels)]
    return data, (C.POINTER(C.c_float) * channels)(*[C.cast(d, C.POINTER(C.c_float)) for d in data])


def vst3_process(path, pitch=60, wait=2.0, seconds=2.0, frames=512, rate=48000.0):
    lib = C.CDLL(str(vst3_library(path)))
    lib.ModuleEntry.restype, lib.ModuleEntry.argtypes = C.c_bool, [C.c_void_p]
    if not lib.ModuleEntry(C.c_void_p(lib._handle)):
        raise SystemExit("ModuleEntry failed")
    lib.GetPluginFactory.restype = C.c_void_p
    factory = lib.GetPluginFactory()
    info = ClassInfo()
    cid = None
    for i in range(method(factory, 4, C.c_int32)()):
        method(factory, 5, C.c_int32, C.c_int32, C.POINTER(ClassInfo))(i, C.byref(info))
        if info.category == b"Audio Module Class":
            cid = C.string_at(C.addressof(info) + ClassInfo.cid.offset, 16)
            name = info.name.decode(errors="replace")
            break
    if cid is None:
        raise SystemExit("no audio module class")
    obj = C.c_void_p()
    create = method(factory, 6, C.c_int32, C.c_char_p, C.c_char_p, C.POINTER(C.c_void_p))
    if create(cid, IID_COMPONENT, C.byref(obj)) != K_OK:
        raise SystemExit("createInstance failed")
    component = obj.value
    app = host_application()
    if method(component, 3, C.c_int32, C.c_void_p)(app.ptr) != K_OK:
        raise SystemExit("initialize failed")
    obj = C.c_void_p()
    query = method(component, 0, C.c_int32, C.c_char_p, C.POINTER(C.c_void_p))
    if query(IID_PROCESSOR, C.byref(obj)) != K_OK:
        raise SystemExit("no IAudioProcessor")
    processor = obj.value
    count = method(component, 7, C.c_int32, C.c_int32, C.c_int32)
    bus_info = method(component, 8, C.c_int32, C.c_int32, C.c_int32, C.c_int32, C.POINTER(BusInfo))
    activate = method(component, 10, C.c_int32, C.c_int32, C.c_int32, C.c_int32, C.c_uint8)
    buses = {"audio_in": count(AUDIO, INPUT), "audio_out": count(AUDIO, OUTPUT)}
    buses["event_in"] = count(EVENT, INPUT)
    if not buses["audio_out"]:
        raise SystemExit(f"no audio output: {buses}")
    for media, direction, total in (
        (AUDIO, OUTPUT, buses["audio_out"]),
        (AUDIO, INPUT, buses["audio_in"]),
        (EVENT, INPUT, buses["event_in"]),
    ):
        for index in range(total):
            activate(media, direction, index, 1 if index == 0 else 0)
    out_info = BusInfo()
    bus_info(AUDIO, OUTPUT, 0, C.byref(out_info))
    in_channels = 0
    if buses["audio_in"]:
        in_info = BusInfo()
        bus_info(AUDIO, INPUT, 0, C.byref(in_info))
        in_channels = in_info.channels
    setup = ProcessSetup(0, 0, frames, rate)
    if method(processor, 7, C.c_int32, C.POINTER(ProcessSetup))(C.byref(setup)) != K_OK:
        raise SystemExit("setupProcessing failed")
    method(component, 11, C.c_int32, C.c_uint8)(1)
    method(processor, 8, C.c_int32, C.c_uint8)(1)
    out_data, out_ptrs = channel_buffers(out_info.channels, frames)
    outputs = BusBuffers(out_info.channels, 0, out_ptrs)
    in_data, in_ptrs = channel_buffers(max(in_channels, 1), frames)
    for channel in in_data:
        for n in range(frames):
            channel[n] = 0.5 * math.sin(2 * math.pi * 440 * n / rate)
    inputs = BusBuffers(in_channels, 0, in_ptrs if in_channels else None)
    events = []
    events_obj = event_list(events)
    data = ProcessData(
        0, 0, frames, 1 if in_channels else 0, 1, C.pointer(inputs), C.pointer(outputs)
    )
    if buses["event_in"]:
        data.in_events = events_obj.ptr
    context = ProcessContext(rate=rate, tempo=120.0, numerator=4, denominator=4)
    context.state = 1 << 1 | 1 << 10  # kPlaying | kTempoValid
    data.context = C.addressof(context)
    process = method(processor, 9, C.c_int32, C.POINTER(ProcessData))
    period = frames / rate
    statuses, finite, levels = set(), True, {"before": 0.0, "note": 0.0}
    note_blocks = round(seconds / period)
    for block in range(round(wait / period) + note_blocks):
        started = block == round(wait / period)
        phase = "note" if block >= round(wait / period) else "before"
        events.clear()
        if started and buses["event_in"]:
            events.append(NoteOn(velocity=0.9, pitch=pitch, length=0, note_id=1))
        outputs.silence = 0
        context.project_samples = context.continuous_samples = block * frames
        statuses.add(process(C.byref(data)))
        for channel in out_data:
            for value in channel:
                finite &= math.isfinite(value)
                if math.isfinite(value):
                    levels[phase] = max(levels[phase], abs(value))
        time.sleep(period)
    return {
        "plugin": name,
        "buses": buses,
        "output_channels": out_info.channels,
        "statuses": sorted(statuses),
        "finite": finite,
        "peak_before_note": levels["before"],
        "peak_with_note": levels["note"],
    }


def report(result):
    print(json.dumps(result), flush=True)
    # Skip interpreter teardown: unloading the bridge while its threads run aborts.
    os._exit(0)


def main(argv):
    cmd, path, *rest = argv
    opts = dict(zip(rest[::2], rest[1::2], strict=True))
    if cmd == "clap-scan":
        result = clap_scan(path)
    elif cmd == "clap-process":
        result = clap_process(path, int(opts.get("--frames", 256)), int(opts.get("--blocks", 40)))
    elif cmd == "clap-gui":
        spec = opts.get("--click", "none")
        click = None if spec == "none" else tuple(float(v) for v in spec.split(","))
        result = clap_gui(path, opts["--out"], float(opts.get("--seconds", 8)), click)
    elif cmd == "vst3-scan":
        result = vst3_scan(path)
    elif cmd == "vst3-process":
        result = vst3_process(
            path,
            int(opts.get("--pitch", 60)),
            float(opts.get("--wait", 2)),
            frames=int(opts.get("--frames", 512)),
        )
    else:
        raise SystemExit(f"unknown command {cmd}")
    report(result)


if __name__ == "__main__":
    main(sys.argv[1:])
