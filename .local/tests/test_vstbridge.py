"""Offline tests for ~/.config/razorjack/vstbridge/vstbridge (Bash).

Every external command (wine, wineserver, yabridgectl, gdbus, rpm, sudo, dnf,
fc-list, udisksctl, ni-wine, a DAW) is a mock in a temporary PATH. Prefix paths
contain spaces and non-ASCII characters throughout.

Run: PYTHONDONTWRITEBYTECODE=1 uvx pytest -q -p no:cacheprovider ~/.local/tests/test_vstbridge.py
"""

import json
import os
import re
import shutil
import stat
import subprocess
import tarfile
import time
import tomllib
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / ".config/razorjack/vstbridge/vstbridge"
PIN = "5.1.1-59-gf1fc21e6"
ENV_KEYS = [
    "WINEPREFIX",
    "WINESERVER",
    "WINELOADER",
    "WINE",
    "WINEESYNC",
    "WINEDLLOVERRIDES",
    "DISPLAY",
    "WAYLAND_DISPLAY",
    "NI_WINE_PREFIX",
    "NI_WINE_SCALE",
]

COMMON = f"""#!/usr/bin/env python3
import json, os, signal, sys
def log(tool):
    with open(os.environ["MOCK_LOG"], "a") as f:
        f.write(json.dumps({{"tool": tool, "exe": sys.argv[0], "argv": sys.argv[1:],
                            "env": {{k: os.environ.get(k) for k in {ENV_KEYS!r}}}}}) + "\\n")
"""

WINE = (
    COMMON
    + r"""
log(os.environ.get("MOCK_WINE_TOOL", "wine"))
args = sys.argv[1:]
prefix = os.environ.get("WINEPREFIX") or os.path.expanduser("~/.wine")

def regfile(key):
    root, _, sub = key.partition("\\")
    name = "user.reg" if root.upper() in ("HKCU", "HKEY_CURRENT_USER") else "system.reg"
    return os.path.join(prefix, name), sub.replace("\\", "\\\\")

def load(path):
    header, secs, order, cur = [], {}, [], None
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.rstrip("\n")
            if line.startswith("["):
                name = line[1:line.rindex("]")]
                cur = [name, {}]
                secs[name.lower()] = cur
                order.append(name.lower())
            elif cur is None:
                header.append(line)
            elif line.startswith('"'):
                n, _, raw = line[1:].partition('"=')
                cur[1][n.lower()] = (n, raw)
    return header, secs, order

def save(path, header, secs, order):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(header).rstrip("\n") + "\n\n")
        for k in order:
            name, vals = secs[k]
            f.write(f"[{name}] 1730000000\n#time=1\n")
            for n, raw in vals.values():
                f.write(f'"{n}"={raw}\n')
            f.write("\n")

def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')

def put(key, name, typ, data):
    path, sec = regfile(key)
    header, secs, order = load(path)
    if sec.lower() not in secs:
        secs[sec.lower()] = [sec, {}]
        order.append(sec.lower())
    if typ == "REG_DWORD":
        raw = "dword:%08x" % int(data)
    elif typ == "REG_MULTI_SZ":
        raw = 'str(7):"' + "".join(esc(e) + "\\0" for e in data.split("\\0")) + '"'
    elif typ == "REG_BINARY":
        raw = "hex:" + ",".join(data[i:i + 2] for i in range(0, len(data), 2))
    else:
        raw = '"' + esc(data) + '"'
    secs[sec.lower()][1][name.lower()] = (name, raw)
    save(path, header, secs, order)

def opt(flag, default=None):
    return args[args.index(flag) + 1] if flag in args else default

if args == ["--version"]:
    print(os.environ.get("MOCK_WINE_VERSION", "wine-11.20 (Staging)"))
    sys.exit(int(os.environ.get("MOCK_WINE_VERSION_RC", "0")))
cmd = args[0] if args else ""
if cmd == "wineboot":
    if os.environ.get("MOCK_WINEBOOT_RC"):
        sys.exit(int(os.environ["MOCK_WINEBOOT_RC"]))
    for d in ("drive_c/windows/system32", "drive_c/windows/syswow64", "drive_c/windows/Fonts"):
        os.makedirs(os.path.join(prefix, d), exist_ok=True)
    if not os.path.exists(os.path.join(prefix, "system.reg")):
        with open(os.path.join(prefix, "system.reg"), "w") as f:
            f.write("WINE REGISTRY Version 2\n;; All keys relative to \\\\Machine\n\n#arch=win64\n")
        with open(os.path.join(prefix, "user.reg"), "w") as f:
            f.write("WINE REGISTRY Version 2\n;; All keys relative to \\\\User\\\\S-1-5-21-0\n"
                    "\n#arch=win64\n")
        version = "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion"
        put(version, "ProductName", "REG_SZ", "Windows 10 Pro")
        put(version, "CurrentBuild", "REG_SZ", "19045")
        put(version + "\\FontLink\\SystemLink", "Tahoma",
            "REG_MULTI_SZ", "MSGOTHIC.TTC,MS UI Gothic\\0SIMSUN.TTC,SimSun")
        with open(os.path.join(prefix, "drive_c/windows/system32/dxgi.dll"), "wb") as f:
            f.write(b"MZ" + b"\0" * 62 + b"Wine builtin DLL\0")
elif cmd == "winecfg":
    if "/v" in args:
        put("HKCU\\Software\\Wine", "Version", "REG_SZ", opt("/v"))
elif cmd == "reg":
    sub, key = args[1].lower(), args[2]
    if sub == "add":
        put(key, opt("/v"), opt("/t", "REG_SZ"), opt("/d", ""))
    elif sub == "delete":
        path, sec = regfile(key)
        header, secs, order = load(path)
        name = opt("/v").lower()
        if sec.lower() not in secs or name not in secs[sec.lower()][1]:
            sys.exit(1)
        del secs[sec.lower()][1][name]
        save(path, header, secs, order)
    elif sub == "export":
        target = args[3].replace("C:\\", "drive_c\\").replace("\\", "/")
        with open(os.path.join(prefix, target), "w") as f:
            f.write("Windows Registry Editor Version 5.00\n")
elif cmd.lower().endswith(".exe"):
    print("fixme:mock installer output", file=sys.stderr)
    if os.environ.get("MOCK_EXE_CANCEL"):
        os.kill(os.getppid(), signal.SIGINT)
        sys.exit(130)
    if os.environ.get("MOCK_EXE_INSTALL"):
        vst3 = os.path.join(prefix, "drive_c/Program Files/Common Files/VST3")
        bundle = os.path.join(vst3, os.environ["MOCK_EXE_INSTALL"])
        os.makedirs(os.path.join(bundle, "Contents/x86_64-win"), exist_ok=True)
    sys.exit(int(os.environ.get("MOCK_EXE_RC", "0")))
"""
)

WINESERVER = (
    COMMON
    + r"""
log("wineserver")
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("MOCK_WINESERVER_VERSION", "Wine version 11.20"))
elif sys.argv[1:] == ["-w"]:
    import time
    time.sleep(float(os.environ.get("MOCK_WINESERVER_WAIT", "0")))
"""
)

YABRIDGECTL = (
    COMMON
    + r"""
log("yabridgectl")
state = os.environ["MOCK_YBCTL_STATE"]
dirs = open(state).read().splitlines() if os.path.exists(state) else []
cmd = sys.argv[1] if len(sys.argv) > 1 else ""
if cmd == "list":
    print("\n".join(dirs))
elif cmd == "add":
    if os.environ.get("MOCK_YBCTL_ADD_RC"):
        sys.exit(int(os.environ["MOCK_YBCTL_ADD_RC"]))
    with open(state, "a") as f:
        f.write(sys.argv[2] + "\n")
elif cmd == "sync":
    home = os.path.dirname(os.path.realpath(sys.argv[0]))
    chain = os.path.join(home, "libyabridge-chainloader-vst3.so")
    for d in dirs:
        if not d.endswith("VST3") or not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name.endswith(".vst3"):
                out = os.path.expanduser(f"~/.vst3/yabridge/{name}/Contents/x86_64-linux")
                os.makedirs(out, exist_ok=True)
                import shutil
                shutil.copy(chain, os.path.join(out, name[:-5] + ".so"))
    sys.exit(int(os.environ.get("MOCK_YBCTL_SYNC_RC", "0")))
elif cmd == "status":
    print("yabridge path: mock")
    sys.exit(int(os.environ.get("MOCK_YBCTL_STATUS_RC", "0")))
"""
)

GDBUS = (
    COMMON
    + r"""
log("gdbus")
mode = os.environ.get("MOCK_PORTAL", "fail")
args = " ".join(sys.argv[1:])
if mode == "fail":
    print("Error: GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown", file=sys.stderr)
    sys.exit(1)
legacy = mode.startswith("v1:")
value = mode[3:] if legacy else mode
if "Properties.Get" in args:
    print("(<uint32 %d>,)" % (1 if legacy else 2))
elif "Settings.ReadOne" in args:
    if legacy:
        sys.exit(1)
    print("(<uint32 %s>,)" % value)
elif "Settings.Read" in args:
    print("(<<uint32 %s>>,)" % value)
"""
)

RPM = (
    COMMON
    + r"""
log("rpm")
args = sys.argv[1:]
missing = os.environ.get("MOCK_RPM_MISSING", "").split(",")
if args[:2] == ["-q", "--quiet"]:
    sys.exit(1 if args[2] in missing else 0)
if args and args[0] == "-qf":
    print(os.environ.get("MOCK_RPM_ORIGIN", "wine-core-11.20-1.fc45 (Fedora Project)"))
    sys.exit(0)
sys.exit(1)
"""
)

SIMPLE = (
    COMMON
    + r"""
log(os.path.basename(sys.argv[0]))
name = os.path.basename(sys.argv[0]).replace("-", "_").upper()
sys.exit(int(os.environ.get("MOCK_RC_" + name, "0")))
"""
)

FCLIST = (
    COMMON
    + r"""
print(open(os.environ["MOCK_FONTS"]).read(), end="")
"""
)

ALTERNATIVES = (
    COMMON
    + r"""
group = sys.argv[-1]
dxvk = os.environ.get("MOCK_ALT_DXVK", "").split(",")
dll = group.split("(")[0].removeprefix("wine-")
arch = "x86_64-windows" if "x86-64" in group else "i386-windows"
name = ("dxvk-" if dll in dxvk and "x86-64" in group else "wine-") + dll + ".dll"
print(f"{group} - status is auto.")
print(f" link currently points to /usr/lib64/wine-wow64/wine/{arch}/{name}")
"""
)

UDISKSCTL = (
    COMMON
    + r"""
log("udisksctl")
cmd = sys.argv[1]
if cmd == "loop-setup":
    print(f"Mapped file {sys.argv[-1]} as /dev/loop7.")
elif cmd == "mount":
    print(f"Mounted /dev/loop7 at {os.environ['MOCK_ISO_DIR']}")
"""
)

NI = (
    COMMON
    + r"""
log("ni")
if sys.argv[1:2] == ["setup"]:
    import subprocess
    env = dict(os.environ, WINEPREFIX=os.environ["NI_WINE_PREFIX"])
    sys.exit(subprocess.call([os.environ["WINE"], "wineboot", "-i"], env=env))
"""
)

DAW = (
    COMMON
    + r"""
with open(os.environ["MOCK_DAW_OUT"], "w") as f:
    keys = ["WINEPREFIX", "WINELOADER", "DISPLAY"]
    json.dump({"argv": sys.argv[1:], "env": {k: os.environ.get(k) for k in keys}}, f)
"""
)

V1_TEMPLATE = """# vstbridge-managed template. Uncomment per-plugin sections as needed.
# Docs: https://github.com/robbert-vdh/yabridge#runtime-dependencies-and-known-issues

# --- FabFilter (VST2 only) ---------------------------------------------------
# VST2 FabFilter instances can only share state/presets between instances when
# hosted in one process. Irrelevant for the VST3 builds.
# ["FabFilter*"]
# group = "fabfilter"

# --- Neural DSP (Fortin Nameless Suite) ---------------------------------------
# If a Neural DSP GUI renders but ignores mouse/keyboard input (seen in REAPER,
# yabridge issue #432), try these one at a time:
# (editor_xembed used to be a third option here, but yabridge master - which
# the COPR ships - removed XEmbed support; don't cargo-cult it back.)
# ["*Nameless*", "*Fortin*", "*Archetype*", "*Neural*"]
# disable_pipes = true
# editor_force_dnd = true

# --- ujam / Gorilla Engine (JS_EXEC_FAILED) - not in the current set, but the
# canonical example of disable_pipes:
# ["ujam*"]
# disable_pipes = true
"""

EXAMPLE_LINE = re.compile(r"^# (\[|[A-Za-z0-9_./-]+ = )")


def uncomment_examples(text):
    return (
        "\n".join(line[2:] if EXAMPLE_LINE.match(line) else line for line in text.splitlines())
        + "\n"
    )


def executable(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


class VB:
    def __init__(self, tmp):
        self.tmp = tmp
        self.home = tmp / "home"
        self.bin = tmp / "bin"
        self.root = tmp / "Präfixe mit Leerzeichen"
        self.runner = executable(tmp / "runners/main/bin/wine", WINE)
        executable(tmp / "runners/main/bin/wineserver", WINESERVER)
        self.alt = executable(tmp / "runners/wine 9.21/bin/wine", WINE)
        executable(tmp / "runners/wine 9.21/bin/wineserver", WINESERVER)
        executable(
            self.bin / "wine", WINE.replace('os.environ.get("MOCK_WINE_TOOL", "wine")', '"syswine"')
        )
        executable(self.bin / "alternatives", ALTERNATIVES)
        for name, text in {
            "gdbus": GDBUS,
            "rpm": RPM,
            "fc-list": FCLIST,
            "udisksctl": UDISKSCTL,
            "ni": NI,
        }.items():
            executable(self.bin / name, text)
        for name in ("sudo", "dnf", "flatpak", "winetricks", "native-access", "findmnt"):
            executable(self.bin / name, SIMPLE)
        self.fonts = tmp / "host fonts"
        self.fonts.mkdir()
        listing = []
        for name in (
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
            "NotoSansSymbols2-Regular.ttf",
            "LiberationSans-Regular.ttf",
            "LiberationSerif-Regular.ttf",
            "LiberationMono-Regular.ttf",
        ):
            (self.fonts / name).write_bytes(name.encode() * 10)
            listing.append(str(self.fonts / name))
        (tmp / "fonts.txt").write_text("\n".join(listing) + "\n")
        self.loader = self.home / ".local/share/vstbridge/wineloader"
        self.env = {
            "HOME": str(self.home),
            "PATH": f"{self.bin}:/usr/bin:/bin",
            "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.home / ".local/share"),
            "XDG_STATE_HOME": str(self.home / ".local/state"),
            "DISPLAY": ":99",
            "WAYLAND_DISPLAY": "wayland-9",
            "XDG_SESSION_TYPE": "wayland",
            "MOCK_LOG": str(tmp / "calls.jsonl"),
            "MOCK_FONTS": str(tmp / "fonts.txt"),
            "MOCK_YBCTL_STATE": str(tmp / "ybctl-dirs"),
            "SHELL": "/bin/bash",
            "MOCK_PORTAL": "fail",
        }
        self.home.mkdir()
        self.conf()

    def px(self, name):
        return self.root / name

    def conf(self, extra="", fab_profile="baseline", kilo_esync="off", unknown="system", ni=False):
        text = f"""
[general]
unknown_prefix = {unknown}
new_prefix_dpi = 144
theme = auto

[bridge]
source = local
pin = {PIN}

[profile baseline]
runner = {self.runner}
graphics = wined3d

[profile alt]
runner = {self.alt}
graphics = wined3d

[profile giang17]
runner = {self.runner}
graphics = giang17
evidence = test

[prefix fabfilter]
path = {self.px("fab filter")}
profile = {fab_profile}

[prefix kilohearts]
path = {self.px("kilohearts")}
profile = baseline
esync = {kilo_esync}
"""
        if ni:
            text += f"""
[prefix ni]
path = {self.px("ni wine")}
profile = baseline
backend = ni-wine
ni_scale = 1.5
"""
        path = self.home / ".config/vstbridge/vstbridge.conf"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + extra)

    def run(self, *args, env=None, script=None, timeout=60):
        full = dict(self.env, **(env or {}))
        return subprocess.run(
            [str(script or SCRIPT), *args],
            env=full,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def ok(self, *args, **kw):
        result = self.run(*args, **kw)
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    def calls(self, tool=None):
        path = Path(self.env["MOCK_LOG"])
        if not path.exists():
            return []
        entries = [json.loads(line) for line in path.read_text().splitlines()]
        return [e for e in entries if tool is None or e["tool"] == tool]

    def clear(self):
        Path(self.env["MOCK_LOG"]).unlink(missing_ok=True)

    def wine(self, prefix, *args, runner=None):
        env = dict(self.env, WINEPREFIX=str(prefix))
        subprocess.run([str(runner or self.runner), *args], env=env, check=True)

    def exe(self, name):
        path = self.tmp / name
        path.write_bytes(b"MZ")
        return str(path)

    def install_bridge(self, describe=PIN):
        build = self.tmp / f"build-{describe}"
        (build / "yabridge").mkdir(parents=True)
        for name in (
            "yabridge-host.exe",
            "yabridge-host.exe.so",
            "libyabridge-chainloader-vst2.so",
            "libyabridge-chainloader-vst3.so",
            "libyabridge-chainloader-clap.so",
            "libyabridge-vst2.so",
            "libyabridge-vst3.so",
            "libyabridge-clap.so",
        ):
            (build / "yabridge" / name).write_bytes(
                b"\x7fELF " + name.encode() + b" yabridge " + describe.encode()
            )
        executable(build / "yabridgectl/yabridgectl", YABRIDGECTL)
        archives = []
        for top in ("yabridge", "yabridgectl"):
            archive = self.tmp / f"{top}-{describe}.tar.gz"
            with tarfile.open(archive, "w:gz") as tar:
                tar.add(build / top, arcname=top)
            archives.append(str(archive))
        return archives


def reg(px, root, key, name):
    path = Path(px) / ("user.reg" if root == "HKCU" else "system.reg")
    want, section = key.replace("\\", "\\\\").lower(), None
    for line in path.read_text().splitlines():
        if line.startswith("["):
            section = line[1 : line.rindex("]")].lower()
        elif section == want and line.lower().startswith(f'"{name.lower()}"='):
            return line.split("=", 1)[1]
    return None


@pytest.fixture
def vb(tmp_path):
    return VB(tmp_path)


@pytest.fixture
def ready(vb):
    """Bridge installed and active, prefixes created by setup."""
    vb.ok("bridge", "install", *vb.install_bridge(), "--origin", "test build")
    vb.ok("bridge", "use", PIN)
    vb.ok("setup")
    vb.clear()
    return vb


# --- static checks and configuration ----------------------------------------------------


def test_bash_syntax_and_shellcheck():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
    if shutil.which("shellcheck"):
        subprocess.run(
            ["shellcheck", "--shell=bash", "--severity=warning", str(SCRIPT)], check=True
        )


def test_builtin_config_and_every_example_parse(vb):
    (vb.home / ".config/vstbridge/vstbridge.conf").unlink()
    vb.ok("config", "check")
    text = vb.ok("config", "show").stdout
    expanded = uncomment_examples(text)
    for section in (
        "[profile giang17]",
        "[profile legacy]",
        "[profile dxvk]",
        "[prefix ni-legacy]",
        "[daw reaper]",
    ):
        assert section in expanded
    (vb.tmp / "examples.conf").write_text(expanded)
    vb.ok("config", "check", str(vb.tmp / "examples.conf"))


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("rule = vst3 | {Rift,Morph}* | editor_disable_host_scaling = true", "alternation"),
        ("rule = vst3 | Fortin* | editor_xembed = true", "removed"),
        ('rule = vst2 | ["*Nameless*", "*Fortin*"] | disable_pipes = true', "quotes"),
    ],
)
def test_invalid_yabridge_rules_are_rejected(vb, line, message):
    vb.conf(extra=f"\n[yabridge]\n{line}\n")
    result = vb.run("config", "check")
    assert result.returncode == 1
    assert message in result.stderr


def test_fallback_profile_needs_evidence(vb):
    vb.conf(extra=f"\n[profile dxvk]\nrunner = {vb.runner}\ngraphics = dxvk\n")
    result = vb.run("config", "check")
    assert result.returncode == 1 and "needs 'evidence ='" in result.stderr


# --- setup ------------------------------------------------------------------------------


def test_setup_plan_is_repeatable_and_changes_nothing(vb):
    env = {"MOCK_RPM_MISSING": "wine,cabextract"}
    first = vb.run("setup", "--plan", env=env)
    second = vb.run("setup", "--plan", env=env)
    assert first.stdout == second.stdout
    assert "would: sudo dnf install --exclude=wine-dxvk* wine cabextract" in first.stdout
    assert "would: [fabfilter] create" in first.stdout
    assert not vb.root.exists()
    assert not (vb.home / ".local/share/vstbridge").exists()
    assert not vb.calls("sudo") and not vb.calls("wine")


def test_setup_creates_prefixes_without_copr(vb):
    result = vb.run("setup", env={"MOCK_RPM_MISSING": "wine"})
    assert result.returncode == 0, result.stderr
    sudo = [" ".join(c["argv"]) for c in vb.calls("sudo")]
    assert sudo == ["dnf install -y --exclude=wine-dxvk* wine"]
    assert not any("copr" in " ".join(c["argv"]) for c in vb.calls())
    px = vb.px("fab filter")
    assert reg(px, "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000090"
    assert reg(px, "HKCU", r"Software\Wine\DllOverrides", "winemenubuilder.exe") == '""'
    assert reg(px, "HKCU", r"Software\Wine", "Version") == '"win10"'
    assert (px / ".vstbridge-prefix").read_text().startswith("profile=baseline\n")
    tahoma = reg(
        px, "HKLM", r"Software\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink", "Tahoma"
    )
    assert tahoma.startswith('str(7):"DejaVuSans.ttf,DejaVu Sans\\0NotoSansSymbols2-Regular.ttf')
    assert "MSGOTHIC.TTC,MS UI Gothic" in tahoma and "SIMSUN.TTC" in tahoma
    assert (
        reg(px, "HKLM", r"Software\Microsoft\Windows NT\CurrentVersion\FontSubstitutes", "Arial")
        == '"Liberation Sans"'
    )
    assert "yabridge: no active build" in result.stderr


def test_wineboot_failure_is_reported(vb):
    result = vb.run("setup", env={"MOCK_WINEBOOT_RC": "1"})
    assert result.returncode == 1
    assert "wineboot -i failed" in result.stderr
    assert not (vb.px("fab filter") / ".vstbridge-prefix").exists()


def test_user_dll_overrides_and_environment_overrides_are_preserved(vb):
    px = vb.px("fab filter")
    vb.wine(px, "wineboot", "-i")
    vb.wine(
        px,
        "reg",
        "add",
        r"HKCU\Software\Wine\DllOverrides",
        "/v",
        "winemenubuilder.exe",
        "/t",
        "REG_SZ",
        "/d",
        "native",
        "/f",
    )
    vb.wine(
        px,
        "reg",
        "add",
        r"HKCU\Software\Wine\DllOverrides",
        "/v",
        "d3dcompiler_47",
        "/t",
        "REG_SZ",
        "/d",
        "native",
        "/f",
    )
    vb.ok("migrate", "fabfilter")
    vb.clear()
    vb.ok("setup", env={"WINEDLLOVERRIDES": "mshtml=d"})
    assert reg(px, "HKCU", r"Software\Wine\DllOverrides", "winemenubuilder.exe") == '"native"'
    assert reg(px, "HKCU", r"Software\Wine\DllOverrides", "d3dcompiler_47") == '"native"'
    boot = [c for c in vb.calls("wine") if c["argv"][:1] == ["wineboot"]]
    assert boot and boot[0]["env"]["WINEDLLOVERRIDES"] == "mshtml=d;winemenubuilder.exe=d"
    vb.clear()
    vb.conf(extra=f"\n[prefix extra]\npath = {vb.px('extra')}\nprofile = baseline\n")
    vb.ok("setup", env={"WINEDLLOVERRIDES": "winemenubuilder.exe=n"})
    boot = [c for c in vb.calls("wine") if c["argv"][:1] == ["wineboot"]]
    assert boot[0]["env"]["WINEDLLOVERRIDES"] == "winemenubuilder.exe=n"


def test_existing_prefix_dpi_is_preserved_unless_configured(vb):
    px = vb.px("fab filter")
    vb.wine(px, "wineboot", "-i")
    vb.wine(
        px,
        "reg",
        "add",
        r"HKCU\Control Panel\Desktop",
        "/v",
        "LogPixels",
        "/t",
        "REG_DWORD",
        "/d",
        "96",
        "/f",
    )
    assert vb.run("install", "fabfilter", vb.exe("x.exe")).returncode == 1
    vb.ok("migrate", "fabfilter")
    vb.ok("setup")
    vb.ok("appearance", "apply")
    assert reg(px, "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000060"
    assert (
        reg(vb.px("kilohearts"), "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000090"
    )
    text = (vb.home / ".config/vstbridge/vstbridge.conf").read_text()
    (vb.home / ".config/vstbridge/vstbridge.conf").write_text(
        text.replace("profile = baseline\n", "profile = baseline\ndpi = 120\n", 1)
    )
    vb.ok("appearance", "apply", "fabfilter")
    assert reg(px, "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000078"
    vb.ok("appearance", "restore", "fabfilter")
    assert reg(px, "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000060"


# --- appearance -------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("portal", "expected"),
    [("1", "dword:00000000"), ("2", "dword:00000001"), ("v1:1", "dword:00000000")],
)
def test_portal_color_scheme_sets_theme_flags(vb, portal, expected):
    vb.ok("setup")
    vb.ok("appearance", "apply", env={"MOCK_PORTAL": portal})
    px = vb.px("fab filter")
    key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    assert reg(px, "HKCU", key, "AppsUseLightTheme") == expected
    assert reg(px, "HKCU", key, "SystemUsesLightTheme") == expected


def test_theme_changes_twice_then_restores_the_original(vb):
    vb.ok("setup", env={"MOCK_PORTAL": "fail"})
    px = vb.px("fab filter")
    key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    for portal in ("1", "2", "1"):
        result = vb.ok("appearance", "apply", "fabfilter", env={"MOCK_PORTAL": portal})
        assert "awk: warning" not in result.stderr
    assert len((px / ".vstbridge-appearance").read_text().splitlines()) == 2
    vb.ok("appearance", "restore", "fabfilter")
    assert reg(px, "HKCU", key, "AppsUseLightTheme") is None
    assert reg(px, "HKCU", key, "SystemUsesLightTheme") is None


@pytest.mark.parametrize("portal", ["fail", "0"])
def test_unknown_portal_preference_preserves_settings(vb, portal):
    vb.ok("setup", env={"MOCK_PORTAL": "1"})
    px = vb.px("fab filter")
    key = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    vb.clear()
    status = vb.ok("appearance", "status", env={"MOCK_PORTAL": portal}).stdout
    assert ("unavailable" if portal == "fail" else "none") in status
    vb.ok("appearance", "apply", env={"MOCK_PORTAL": portal})
    assert reg(px, "HKCU", key, "AppsUseLightTheme") == "dword:00000000"
    assert not [c for c in vb.calls("wine") if c["argv"][:1] == ["reg"]]
    vb.ok("appearance", "restore", "fabfilter")
    assert reg(px, "HKCU", key, "AppsUseLightTheme") is None


# --- install, run, finalization ---------------------------------------------------------


def test_installer_failure_with_finalizer_failure_keeps_installer_status(ready):
    result = ready.run(
        "install",
        "fabfilter",
        ready.exe("setup.exe"),
        env={"MOCK_EXE_RC": "5", "MOCK_YBCTL_SYNC_RC": "1"},
    )
    assert result.returncode == 5
    assert "install exited with status 5" in result.stderr
    assert "finalization also failed: yabridge sync" in result.stderr


def test_run_failure_still_finalizes(ready):
    result = ready.run("run", "fabfilter", str(ready.tmp / "manager.exe"), env={"MOCK_EXE_RC": "7"})
    assert result.returncode == 7
    tools = [c["tool"] + ":" + (c["argv"][0] if c["argv"] else "") for c in ready.calls()]
    exe = tools.index("wine:" + str(ready.tmp / "manager.exe"))
    assert "wineserver:-w" in tools[exe:]
    assert "yabridgectl:sync" in tools[exe:]


def test_finalizer_failure_alone_returns_3(ready):
    result = ready.run(
        "run", "fabfilter", str(ready.tmp / "ok.exe"), env={"MOCK_YBCTL_SYNC_RC": "1"}
    )
    assert result.returncode == 3


def test_cancelled_installer_returns_130_after_finalizing(ready):
    result = ready.run("install", "fabfilter", ready.exe("setup.exe"), env={"MOCK_EXE_CANCEL": "1"})
    assert result.returncode == 130
    assert "cancelled" in result.stderr
    assert any(c["argv"][:1] == ["sync"] for c in ready.calls("yabridgectl"))


def test_persistent_wineserver_times_out_without_killing(ready):
    ready.conf(extra="")
    text = (ready.home / ".config/vstbridge/vstbridge.conf").read_text()
    (ready.home / ".config/vstbridge/vstbridge.conf").write_text(
        text.replace("esync = off", "esync = off\nsettle = 1")
    )
    start = time.monotonic()
    result = ready.run(
        "run", "kilohearts", str(ready.tmp / "installer.exe"), env={"MOCK_WINESERVER_WAIT": "10"}
    )
    assert time.monotonic() - start < 8
    assert result.returncode == 0, result.stderr
    assert (
        "[kilohearts] run: Wine processes in this prefix were still running after 1s"
        in result.stderr
    )
    assert not any("-k" in c["argv"] for c in ready.calls("wineserver"))


def test_installed_plugin_is_registered_and_counted(ready):
    ready.ok(
        "install",
        "fabfilter",
        ready.exe("proq.exe"),
        env={"MOCK_EXE_INSTALL": "FabFilter Pro-Q 4.vst3"},
    )
    paths = ready.ok("paths").stdout
    assert "VST3 " + str(ready.px("fab filter")) in paths
    assert "(1)" in paths
    assert "CLAP" in paths and "does not load CLAP" in paths


def test_tricks_refuses_dxvk_outside_dxvk_profiles(ready):
    result = ready.run("tricks", "fabfilter", "dxvk")
    assert result.returncode == 1 and "not a dxvk profile" in result.stderr
    assert not ready.calls("winetricks")


def test_native_access_exe_is_not_run_directly(vb):
    vb.conf(ni=True)
    result = vb.run("run", "ni", str(vb.tmp / "Native Access.exe"))
    assert result.returncode == 1 and "vstbridge ni native-access" in result.stderr


# --- dispatcher and launch ---------------------------------------------------------------


def loader_call(vb, prefix, *args, env=None):
    vb.clear()
    full = dict(vb.env, **(env or {}))
    if prefix is not None:
        full["WINEPREFIX"] = str(prefix)
    result = subprocess.run([str(vb.loader), *args], env=full, capture_output=True, text=True)
    return result, vb.calls()


def test_dispatcher_pairs_runner_and_wineserver(vb):
    vb.conf(fab_profile="alt")
    vb.ok("setup")
    result, calls = loader_call(vb, vb.px("fab filter"), "plugin.exe")
    assert result.returncode == 0, result.stderr
    assert calls[0]["exe"] == str(vb.alt)
    assert calls[0]["env"]["WINESERVER"] == str(vb.alt.parent / "wineserver")
    assert calls[0]["env"]["WAYLAND_DISPLAY"] is None
    result, calls = loader_call(vb, vb.px("kilohearts"), "plugin.exe")
    assert calls[0]["exe"] == str(vb.runner)


def test_dispatcher_esync_policy(vb):
    vb.ok("setup")
    _, calls = loader_call(vb, vb.px("kilohearts"), "x.exe", env={"WINEESYNC": "1"})
    assert calls[0]["env"]["WINEESYNC"] == "0"
    _, calls = loader_call(vb, vb.px("fab filter"), "x.exe", env={"WINEESYNC": "0"})
    assert calls[0]["env"]["WINEESYNC"] == "0"


def test_dispatcher_unknown_prefix_fallback(vb):
    vb.ok("setup")
    _, calls = loader_call(vb, vb.tmp / "other prefix", "x.exe")
    assert calls[0]["tool"] == "syswine" and calls[0]["env"]["WINESERVER"] is None
    _, calls = loader_call(vb, None, "--version")
    assert calls[0]["exe"] == str(vb.runner)
    vb.conf(unknown="fail")
    vb.run("sync")
    result, calls = loader_call(vb, vb.tmp / "other prefix", "x.exe")
    assert result.returncode == 127 and "not a managed prefix" in result.stderr and not calls


def test_doctor_reports_esync_zero_as_disabled(ready):
    out = ready.run("doctor", env={"WINEESYNC": "0"}).stdout
    assert "[fabfilter] esync policy inherit -> WINEESYNC=0 (disabled)" in out
    ready.conf(kilo_esync="inherit")
    result = ready.run("doctor", env={"WINEESYNC": "1"})
    assert result.returncode == 1 and "Kilohearts plugins leak file descriptors" in result.stdout


def make_daw(vb):
    daw = executable(vb.tmp / "My DAWs ü/bitwig studio", DAW)
    vb.conf(extra=f"\n[daw bitwig]\nexec = {daw}\n")
    vb.env["MOCK_DAW_OUT"] = str(vb.tmp / "daw.json")
    return daw


def test_launch_preserves_arguments_and_drops_wineprefix(vb):
    make_daw(vb)
    args = ["a b", "--flag=x y", "ü", "$HOME", "", "*"]
    vb.ok("launch", "bitwig", "--", *args, env={"WINEPREFIX": "/somewhere"})
    out = json.loads((vb.tmp / "daw.json").read_text())
    assert out["argv"] == args
    assert out["env"]["WINEPREFIX"] is None
    assert out["env"]["WINELOADER"] == str(vb.loader)
    assert out["env"]["DISPLAY"] == ":99"


def test_launch_requires_display(vb):
    make_daw(vb)
    result = vb.run("launch", "bitwig", env={"DISPLAY": ""})
    assert result.returncode == 1 and "XWayland" in result.stderr


def desktop_exec_argv(exec_value, files):
    """Exec key parsing per the Desktop Entry spec: string unescape, then quoting rules."""
    value = re.sub(
        r"\\(.)",
        lambda m: {"s": " ", "n": "\n", "t": "\t", "r": "\r", "\\": "\\"}.get(
            m.group(1), m.group(0)
        ),
        exec_value,
    )
    argv, cur, i, quoted, started = [], "", 0, False, False
    while i < len(value):
        c = value[i]
        if quoted:
            if c == "\\" and value[i + 1] in '"`$\\':
                cur += value[i + 1]
                i += 1
            elif c == '"':
                quoted = False
            else:
                cur += c
        elif c == '"':
            quoted = started = True
        elif c == " ":
            if started:
                argv.append(cur)
            cur, started = "", False
        else:
            cur += c
            started = True
        i += 1
    if started:
        argv.append(cur)
    out = []
    for a in argv:
        if a == "%F":
            out.extend(files)
        else:
            out.append(a.replace("%%", "%"))
    return out


def test_desktop_entry_round_trips_arguments(vb):
    make_daw(vb)
    weird = vb.tmp / 'scripts "100%" $dir & ü'
    weird.mkdir()
    script = weird / "vstbridge"
    shutil.copy(SCRIPT, script)
    vb.ok("desktop", "install", "bitwig", script=script)
    entry = (vb.home / ".local/share/applications/vstbridge-bitwig.desktop").read_text()
    assert "X-Vstbridge-Managed=true" in entry
    exec_value = re.search(r"^Exec=(.*)$", entry, re.M).group(1)
    files = ["/tmp/my project.bwproject", "ü $x.bwproject"]
    argv = desktop_exec_argv(exec_value, files)
    assert argv[0] == str(script)
    subprocess.run(argv, env=vb.env, check=True, capture_output=True)
    assert json.loads((vb.tmp / "daw.json").read_text())["argv"] == files


def test_desktop_install_does_not_overwrite_foreign_files(vb):
    make_daw(vb)
    target = vb.home / ".local/share/applications/vstbridge-bitwig.desktop"
    target.parent.mkdir(parents=True)
    target.write_text("[Desktop Entry]\nName=mine\n")
    result = vb.run("desktop", "install", "bitwig")
    assert "was not written by vstbridge" in result.stderr
    assert target.read_text() == "[Desktop Entry]\nName=mine\n"


# --- fonts ------------------------------------------------------------------------------


def test_font_repair_without_prefixes_is_a_noop(vb):
    result = vb.ok("fix-fonts")
    assert "nothing to repair" in result.stdout
    assert not (vb.home / ".local/share/vstbridge").exists()


def test_repeated_font_setup_is_idempotent(vb):
    vb.ok("setup")
    fonts = vb.px("fab filter") / "drive_c/windows/Fonts"
    before = {p.name: p.stat().st_mtime_ns for p in fonts.iterdir()}
    vb.clear()
    vb.ok("fix-fonts")
    vb.ok("fix-fonts")
    assert not [c for c in vb.calls("wine") if c["argv"][:1] == ["reg"]]
    assert {p.name: p.stat().st_mtime_ns for p in fonts.iterdir()} == before


def test_font_copy_skips_the_same_file(vb):
    vb.ok("setup")
    fonts = vb.px("fab filter") / "drive_c/windows/Fonts"
    target = fonts / "DejaVuSans.ttf"
    target.unlink()
    os.link(vb.fonts / "DejaVuSans.ttf", target)
    (fonts / "NotoSansSymbols2-Regular.ttf").unlink()
    (fonts / "NotoSansSymbols2-Regular.ttf").symlink_to(vb.fonts / "NotoSansSymbols2-Regular.ttf")
    result = vb.ok("fix-fonts", "fabfilter")
    assert "same file" not in result.stderr
    assert target.samefile(vb.fonts / "DejaVuSans.ttf")


def test_fix_fonts_repairs_missing_files_and_reset_fontlink(vb):
    vb.ok("setup")
    px = vb.px("fab filter")
    (px / "drive_c/windows/Fonts/DejaVuSans.ttf").unlink()
    vb.wine(
        px,
        "reg",
        "add",
        r"HKLM\Software\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink",
        "/v",
        "Tahoma",
        "/t",
        "REG_MULTI_SZ",
        "/d",
        "MSGOTHIC.TTC,MS UI Gothic\\0USER.TTF,User Font",
        "/f",
    )
    vb.ok("fix-fonts")
    assert (px / "drive_c/windows/Fonts/DejaVuSans.ttf").exists()
    tahoma = reg(
        px, "HKLM", r"Software\Microsoft\Windows NT\CurrentVersion\FontLink\SystemLink", "Tahoma"
    )
    entries = [
        "DejaVuSans.ttf,DejaVu Sans",
        "NotoSansSymbols2-Regular.ttf,Noto Sans Symbols2",
        "MSGOTHIC.TTC,MS UI Gothic",
        "USER.TTF,User Font",
    ]
    assert tahoma == 'str(7):"' + "".join(e + "\\0" for e in entries) + '"'


def test_missing_host_font_is_not_reported_as_complete(vb):
    vb.ok("setup")
    (vb.tmp / "fonts.txt").write_text(str(vb.fonts / "DejaVuSans.ttf") + "\n")
    result = vb.run("fix-fonts")
    assert result.returncode == 1
    assert "google-noto-sans-symbols-2-fonts" in result.stderr


def test_segoe_import_and_ui_font_restore(vb):
    vb.ok("setup")
    win = vb.tmp / "Windows Fonts"
    win.mkdir()
    (win / "segoeui.ttf").write_bytes(b"segoe")
    (win / "arial.ttf").write_bytes(b"arial")
    vb.ok("fonts", "import-segoe", "fabfilter", str(win), "--ui-font")
    px = vb.px("fab filter")
    assert (px / "drive_c/windows/Fonts/segoeui.ttf").exists()
    assert not (px / "drive_c/windows/Fonts/arial.ttf").exists()
    caption = reg(px, "HKCU", r"Control Panel\Desktop\WindowMetrics", "CaptionFont")
    assert caption.startswith("hex:ee,ff,ff,ff")  # -18: 9 pt at 144 DPI
    assert len(caption[4:].split(",")) == 92
    vb.ok("appearance", "restore", "fabfilter")
    assert reg(px, "HKCU", r"Control Panel\Desktop\WindowMetrics", "CaptionFont") is None


# --- yabridge.toml ----------------------------------------------------------------------


def test_yabridge_toml_files_and_examples_are_valid(ready):
    toml_dir = ready.home / ".vst/yabridge"
    toml_dir.mkdir(parents=True, exist_ok=True)
    rules = (
        "\n[yabridge]\n"
        'rule = vst2 | FabFilter* | group = "fabfilter"\n'
        "rule = vst3 | Rift.vst3 | editor_disable_host_scaling = true\n"
    )
    ready.conf(extra=rules)
    ready.ok("sync")
    for fmt in ("vst", "vst3", "clap"):
        path = ready.home / f".{fmt}/yabridge/yabridge.toml"
        tomllib.loads(path.read_text())
        tomllib.loads(
            uncomment_examples(path.read_text()).replace(
                '["FabFilter*"]\ngroup = "fabfilter"\n', "", 1
            )
            if fmt == "vst"
            else uncomment_examples(path.read_text())
        )
    vst2 = tomllib.loads((ready.home / ".vst/yabridge/yabridge.toml").read_text())
    assert vst2 == {"FabFilter*": {"group": "fabfilter"}}
    vst3 = tomllib.loads((ready.home / ".vst3/yabridge/yabridge.toml").read_text())
    assert vst3 == {"Rift.vst3": {"editor_disable_host_scaling": True}}


def test_yabridge_toml_preserves_user_sections_and_skips_duplicates(ready):
    path = ready.home / ".vst/yabridge/yabridge.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('# mine\n["FabFilter*"]\ngroup = "mine"\n\n["Other.so"]\nhide_daw = true\n')
    ready.conf(extra='\n[yabridge]\nrule = vst2 | FabFilter* | group = "fabfilter"\n')
    result = ready.ok("sync")
    assert "already has a section" in result.stderr
    first = path.read_text()
    assert tomllib.loads(first) == {"FabFilter*": {"group": "mine"}, "Other.so": {"hide_daw": True}}
    ready.ok("sync")
    assert path.read_text() == first


def test_v1_template_is_replaced_with_backup(ready):
    import hashlib

    assert hashlib.sha256(V1_TEMPLATE.encode()).hexdigest() in SCRIPT.read_text()
    path = ready.home / ".vst3/yabridge/yabridge.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(V1_TEMPLATE)
    ready.ok("sync")
    assert (path.parent / "yabridge.toml.vstbridge-v1").read_text() == V1_TEMPLATE
    assert "Nameless" not in path.read_text()
    tomllib.loads(uncomment_examples(path.read_text()))


# --- doctor -----------------------------------------------------------------------------


def test_doctor_fails_when_wine_version_fails(ready):
    result = ready.run("doctor", env={"MOCK_WINE_VERSION_RC": "1"})
    assert result.returncode == 1
    assert "--version' failed" in result.stdout
    assert "no problems" not in result.stdout + result.stderr


def test_doctor_fails_when_yabridgectl_status_fails(ready):
    result = ready.run("doctor", env={"MOCK_YBCTL_STATUS_RC": "2"})
    assert result.returncode == 1
    assert "yabridgectl status failed" in result.stdout


def test_doctor_is_read_only_and_passes_on_a_good_setup(ready):
    snapshot = {p: p.stat().st_mtime_ns for p in ready.root.rglob("*") if p.is_file()}
    result = ready.run("doctor")
    assert result.returncode == 0, result.stdout + result.stderr
    assert not [c for c in ready.calls("wine") if c["argv"] != ["--version"]]
    assert not [c for c in ready.calls("yabridgectl") if c["argv"] != ["status"]]
    assert {p: p.stat().st_mtime_ns for p in ready.root.rglob("*") if p.is_file()} == snapshot


def test_doctor_detects_fedora_dxvk_with_builtin_signature(ready):
    px = ready.px("fab filter")
    (px / "drive_c/windows/system32/d3d11.dll").write_bytes(b"MZ Wine builtin DLL\0 DXVK 2.7.1")
    out = ready.run("doctor", env={"MOCK_ALT_DXVK": "dxgi,d3d11"}).stdout
    assert "the system's alternatives select DXVK for d3d11(x86-64) dxgi(x86-64)" in out
    assert "system32/d3d11.dll (DXVK)" in out
    assert "sudo dnf remove 'wine-dxvk*'" in out
    ready.conf(fab_profile="giang17")
    marker = px / ".vstbridge-prefix"
    marker.write_text(marker.read_text().replace("profile=baseline", "profile=giang17"))
    assert ready.run("doctor", env={"MOCK_ALT_DXVK": "dxgi"}).returncode == 1
    assert "wine-dxvk" in ready.run("setup", env={"MOCK_ALT_DXVK": "dxgi"}).stderr


def test_doctor_detects_dxvk_in_giang17_profile(ready):
    px = ready.px("fab filter")
    (px / "drive_c/windows/system32/dxgi.dll").write_bytes(b"MZ native DXVK build")
    ready.wine(
        px,
        "reg",
        "add",
        r"HKCU\Software\Wine\DllOverrides",
        "/v",
        "dxgi",
        "/t",
        "REG_SZ",
        "/d",
        "native",
        "/f",
    )
    out = ready.run("doctor").stdout
    assert "warn    [fabfilter] wined3d profile with replaced DLLs: system32/dxgi.dll (DXVK)" in out
    (px / ".vstbridge-prefix").write_text(
        (px / ".vstbridge-prefix").read_text().replace("profile=baseline", "profile=giang17")
    )
    ready.conf(fab_profile="giang17")
    result = ready.run("doctor")
    assert result.returncode == 1
    assert "FAIL    [fabfilter] giang17 profile" in result.stdout
    assert "wineboot -u" in result.stdout
    assert (px / "drive_c/windows/system32/dxgi.dll").exists()


def test_doctor_detects_stale_wrappers_and_shadowing(ready):
    ready.ok("install", "fabfilter", ready.exe("proq.exe"), env={"MOCK_EXE_INSTALL": "Pro-Q.vst3"})
    assert "1 generated plugin wrappers match" in ready.run("doctor").stdout
    wrapper = next((ready.home / ".vst3/yabridge").rglob("*.so"))
    wrapper.write_bytes(b"older chainloader")
    executable(ready.bin / "yabridge-host.exe", "#!/bin/sh\n")
    result = ready.run("doctor")
    assert "1 of 1 generated plugin wrappers come from another yabridge build" in result.stdout
    assert "several yabridge installations are visible" in result.stdout
    assert result.returncode == 1


# --- bridge, migration, NI, images -------------------------------------------------------


def test_bridge_install_requires_pin_and_never_overwrites(vb):
    archives = vb.install_bridge("5.1.1-60-gabcdef12")
    result = vb.run("bridge", "install", *archives)
    assert result.returncode == 1 and "not the pinned revision" in result.stderr
    tmpdir = vb.tmp / "mktemp"
    tmpdir.mkdir()
    result = vb.ok(
        "bridge",
        "install",
        *archives,
        "--accept-unpinned",
        "--origin",
        "reviewed fork",
        env={"TMPDIR": str(tmpdir)},
    )
    assert "unbound variable" not in result.stderr
    assert not list(tmpdir.iterdir())
    origin = (vb.home / ".local/share/vstbridge/bridges/5.1.1-60-gabcdef12/ORIGIN").read_text()
    assert "origin: reviewed fork" in origin and "sha256=" in origin
    assert vb.run("bridge", "install", *archives, "--accept-unpinned").returncode == 1


def test_bridge_use_moves_existing_install_aside(vb):
    existing = vb.home / ".local/share/yabridge"
    existing.mkdir(parents=True)
    (existing / "yabridgectl").write_text("old")
    vb.ok("bridge", "install", *vb.install_bridge())
    vb.ok("bridge", "use", PIN)
    assert existing.is_symlink()
    moved = list((vb.home / ".local/share/vstbridge/bridges").glob("preexisting-*"))
    assert len(moved) == 1 and (moved[0] / "yabridgectl").read_text() == "old"


def test_runner_change_requires_explicit_migration(ready):
    ready.conf(fab_profile="alt")
    result = ready.run("install", "fabfilter", ready.exe("x.exe"))
    assert result.returncode == 1 and "migration" in result.stderr
    px = ready.px("fab filter")
    before = (px / ".vstbridge-prefix").read_text()
    ready.ok("migrate", "fabfilter", "--plan")
    assert (px / ".vstbridge-prefix").read_text() == before
    assert not (px / ".vstbridge-backup").exists()
    ready.ok("migrate", "fabfilter")
    assert "profile=alt" in (px / ".vstbridge-prefix").read_text()
    backups = list((px / ".vstbridge-backup").iterdir())
    assert (backups[0] / "user.reg").exists() and (
        backups[0] / ".vstbridge-prefix"
    ).read_text() == before


def test_ni_helper_environment(vb):
    vb.conf(ni=True)
    result = vb.run("ni", "setup")  # prefix created; registration waits for a bridge
    assert result.returncode == 0 and "registration skipped" in result.stderr + result.stdout
    vb.ok("bridge", "install", *vb.install_bridge())
    vb.ok("bridge", "use", PIN)
    vb.ok("ni", "setup")
    px = vb.px("ni wine")
    assert reg(px, "HKCU", r"Control Panel\Desktop", "LogPixels") == "dword:00000090"
    assert (px / ".vstbridge-prefix").exists()
    vb.clear()
    result = vb.ok("ni", "native-access")
    call = vb.calls("native-access")[0]["env"]
    assert call["NI_WINE_PREFIX"] == str(px) and call["WINE"] == str(vb.runner)
    assert call["NI_WINE_SCALE"] is None and "fractional" in result.stderr
    helper = vb.tmp / "helper"
    helper.mkdir()
    (helper / "launch.py").write_text('scale = float(os.environ.get("NI_WINE_SCALE", "1"))\n')
    vb.clear()
    vb.ok("ni", "native-access", env={"VSTBRIDGE_NI_HELPER_DIR": str(helper)})
    assert vb.calls("native-access")[0]["env"]["NI_WINE_SCALE"] == "1.5"
    result = vb.run("ni", "native-access", env={"NI_WINE_PREFIX": str(vb.tmp / "elsewhere")})
    assert result.returncode == 1 and "does not repoint" in result.stderr
    vb.clear()
    result = vb.ok("ni-postinstall")
    assert "deprecated" in result.stderr and vb.calls("ni")[0]["argv"] == ["doctor"]


def test_iso_requires_explicit_installer_and_cleans_up(ready):
    iso_dir = ready.tmp / "mounted image"
    (iso_dir / "Kontakt Library").mkdir(parents=True)
    (iso_dir / "Kontakt Library/Setup.exe").write_bytes(b"MZ")
    (iso_dir / "autorun.exe").write_bytes(b"MZ")
    image = ready.tmp / "library ü.iso"
    image.write_bytes(b"iso")
    env = {"MOCK_ISO_DIR": str(iso_dir)}
    result = ready.run("iso", "fabfilter", str(image), env=env)
    assert result.returncode == 2 and "Kontakt Library/Setup.exe" in result.stdout
    assert not [c for c in ready.calls("wine") if c["argv"] and c["argv"][0].endswith(".exe")]
    ops = [c["argv"][0] for c in ready.calls("udisksctl")]
    assert ops == ["loop-setup", "mount", "unmount", "loop-delete"]
    assert ready.calls("udisksctl")[0]["argv"][:2] == ["loop-setup", "-r"]
    ready.clear()
    result = ready.run(
        "iso",
        "fabfilter",
        str(image),
        "--exe",
        "Kontakt Library/Setup.exe",
        env=dict(env, MOCK_EXE_RC="4"),
    )
    assert result.returncode == 4
    assert any(
        c["argv"][:1] == [str(iso_dir / "Kontakt Library/Setup.exe")] for c in ready.calls("wine")
    )
    assert [c["argv"][0] for c in ready.calls("udisksctl")][-2:] == ["unmount", "loop-delete"]


def test_program_output_goes_to_a_log_and_missing_bridge_is_not_a_failure(vb):
    vb.ok("setup")
    result = vb.run("run", "fabfilter", vb.exe("ok.exe"))
    assert result.returncode == 0, result.stderr
    assert "registration skipped" in result.stdout + result.stderr
    logs = list((vb.home / ".local/state/vstbridge/logs").glob("fabfilter-run-*.log"))
    assert len(logs) == 1
    failed = vb.run("run", "fabfilter", vb.exe("bad.exe"), env={"MOCK_EXE_RC": "9"})
    assert failed.returncode == 9 and "last lines of" in failed.stderr


def test_graphics_reset_renames_replaced_dlls_and_drops_overrides(ready):
    px = ready.px("fab filter")
    system32 = px / "drive_c/windows/system32"
    (system32 / "d3d8.dll").write_bytes(b"MZ Wine builtin DLL\0 DXVK 2.7.1")
    (system32 / "d3d11.dll").write_bytes(b"MZ third-party")
    for dll in ("dxgi", "d3dcompiler_47"):
        ready.wine(
            px,
            "reg",
            "add",
            r"HKCU\Software\Wine\DllOverrides",
            "/v",
            dll,
            "/t",
            "REG_SZ",
            "/d",
            "native",
            "/f",
        )
    assert (
        ready.run("graphics", "reset", "fabfilter", env={"MOCK_ALT_DXVK": "dxgi"}).returncode == 1
    )
    ready.ok("graphics", "reset", "fabfilter", "--plan")
    assert (system32 / "d3d8.dll").exists()
    ready.ok("graphics", "reset", "fabfilter")
    assert not (system32 / "d3d8.dll").exists() and not (system32 / "d3d11.dll").exists()
    assert len(list(system32.glob("d3d8.dll.vstbridge-*"))) == 1
    assert reg(px, "HKCU", r"Software\Wine\DllOverrides", "dxgi") is None
    assert reg(px, "HKCU", r"Software\Wine\DllOverrides", "d3dcompiler_47") == '"native"'
    assert "dxgi\tnative" in (px / ".vstbridge-graphics-overrides").read_text()
    assert "Wine's own D3D/DXGI" in ready.run("doctor").stdout


def test_sync_verifies_in_a_managed_prefix_and_never_creates_dot_wine(vb):
    vb.ok("bridge", "install", *vb.install_bridge())
    vb.ok("bridge", "use", PIN)
    syncs = [c for c in vb.calls("yabridgectl") if c["argv"][:1] == ["sync"]]
    assert syncs and all(c["argv"] == ["sync", "--no-verify"] for c in syncs)
    vb.ok("setup")
    vb.clear()
    vb.ok("sync")
    syncs = [c for c in vb.calls("yabridgectl") if c["argv"][:1] == ["sync"]]
    assert [c["argv"] for c in syncs] == [["sync"]]
    assert syncs[0]["env"]["WINEPREFIX"] == str(vb.px("fab filter"))
    assert syncs[0]["env"]["WINELOADER"] == str(vb.loader)
    assert not (vb.home / ".wine").exists()


def test_doctor_warns_about_non_ascii_paths_and_duplicate_plugins(ready):
    out = ready.run("doctor").stdout
    assert "[fabfilter] path contains non-ASCII characters" in out
    for name in ("fabfilter", "kilohearts"):
        ready.ok("install", name, ready.exe(f"{name}.exe"), env={"MOCK_EXE_INSTALL": "Same.vst3"})
    out = ready.run("doctor").stdout
    assert "vst3 'Same.vst3' is installed in prefixes fabfilter and kilohearts" in out
    assert out.count("'Same.vst3'") == 1


def test_ascii_prefix_paths_do_not_warn(vb):
    vb.root = vb.tmp / "ascii prefixes"
    vb.conf()
    vb.ok("setup")
    assert "non-ASCII" not in vb.run("doctor").stdout


def test_registry_writes_wait_for_wineserver_to_save(ready):
    ready.ok("appearance", "apply", "fabfilter", env={"MOCK_PORTAL": "2"})
    waits = [c for c in ready.calls("wineserver") if c["argv"] == ["-w"]]
    assert str(ready.px("fab filter")) in [c["env"]["WINEPREFIX"] for c in waits]
    ready.clear()
    ready.ok("doctor")
    assert not [c for c in ready.calls("wineserver") if c["argv"] == ["-w"]]


def test_doctor_and_setup_report_missing_realtime_limits(vb):
    limit = ["prlimit", "--memlock=1048576:1048576", "--rtprio=0:0", "--", str(SCRIPT)]
    full = dict(vb.env)
    plan = subprocess.run([*limit, "setup", "--plan"], env=full, capture_output=True, text=True)
    assert "realtime limits for yabridge" in plan.stderr and "95-audio.conf" in plan.stderr
    doctor = subprocess.run([*limit, "doctor"], env=full, capture_output=True, text=True)
    assert "realtime limits missing (memlock 1024 KiB, rtprio 0)" in doctor.stdout
