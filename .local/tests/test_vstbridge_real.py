"""Real-Wine tests for ~/.config/razorjack/vstbridge/vstbridge.

These use Fedora's Wine, the pinned yabridge build and a free plugin (Airwindows
Consolidated, MIT). Everything runs in a temporary HOME, so the user's prefixes,
yabridgectl configuration and ~/.wine stay untouched. A run takes a few minutes.

Opt in with VSTBRIDGE_REAL=1. The inputs live in ~/.cache/vstbridge-tests (or
VSTBRIDGE_REAL_INPUTS) and are checked against the hashes below:

  yabridge{,ctl}-5.1.1-59-gf1fc21e6.tar.gz.zip
      https://nightly.link/robbert-vdh/yabridge/actions/runs/41351703537/<name>
  AirwindowsConsolidated-2026-10-31-d013e10-Windows{-64bit-setup.exe,.zip}
      https://github.com/baconpaul/airwin2rack/releases/tag/DAWPlugin

The temporary HOME and prefixes are deleted afterwards unless VSTBRIDGE_REAL_KEEP=1.

Run: VSTBRIDGE_REAL=1 PYTHONDONTWRITEBYTECODE=1 uvx pytest -q -p no:cacheprovider \
         ~/.local/tests/test_vstbridge_real.py
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
SCRIPT = TESTS.parents[1] / ".config/razorjack/vstbridge/vstbridge"
HOST = TESTS / "vstbridge_host.py"
PIN = "5.1.1-59-gf1fc21e6"
INPUTS = Path(os.environ.get("VSTBRIDGE_REAL_INPUTS", Path.home() / ".cache/vstbridge-tests"))
AIR = "AirwindowsConsolidated-2026-10-31-d013e10-Windows"
FILES = {
    f"yabridge-{PIN}.tar.gz.zip": (
        "5b8111f10a0e9ad65dc80bc28848bac4a7469c87bbe5f8af7e43b02707767a46"
    ),
    f"yabridgectl-{PIN}.tar.gz.zip": (
        "c9018906e94eb39f092ad224f285d02ad00c644809e3b177df0ab92ad379caf0"
    ),
    f"{AIR}-64bit-setup.exe": "a3ddb348b6ad9c9e1ec69c4f43ddaaab72a856e3aa068f1eb8bea2e639bc2aa5",
    f"{AIR}.zip": "a21a0df8b0e47a96b4932fed3c05490c3f208fad84eb2fc73f4ca570dd34f292",
}
PLUGIN = "Airwindows (with BaconPaul and members of the Surge Synth Team)/Airwindows Consolidated"
COMMON = "drive_c/Program Files/Common Files"
UNICODE_DIR = "Unicode copy"

pytestmark = [
    pytest.mark.skipif(os.environ.get("VSTBRIDGE_REAL") != "1", reason="set VSTBRIDGE_REAL=1"),
    pytest.mark.skipif(not Path("/usr/bin/wine").exists(), reason="Fedora Wine is not installed"),
]


class Env:
    def __init__(self, base):
        self.base = base
        self.home = base / "home"
        self.plain = base / "prefixes/plain"
        self.unicode = base / "prefixes/unicode ü"
        self.loader = self.home / ".local/share/vstbridge/wineloader"
        keep = (
            *("DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY"),
            *("XDG_RUNTIME_DIR", "DBUS_SESSION_BUS_ADDRESS"),
        )
        path = [p for p in os.environ["PATH"].split(":") if "yabridge" not in p]
        self.env = {k: os.environ[k] for k in keep if k in os.environ} | {
            "HOME": str(self.home),
            "PATH": ":".join(path),
            "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.home / ".local/share"),
            "XDG_STATE_HOME": str(self.home / ".local/state"),
            "XDG_CACHE_HOME": str(self.home / ".cache"),
            "XDG_SESSION_TYPE": os.environ.get("XDG_SESSION_TYPE", "x11"),
        }
        self.home.mkdir(parents=True)
        self.conf("dark")

    def conf(self, theme):
        path = self.home / ".config/vstbridge/vstbridge.conf"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"""
[general]
unknown_prefix = fail
new_prefix_dpi = 144
theme = {theme}

[bridge]
source = local
pin = {PIN}

[profile baseline]
runner = /usr/bin/wine
graphics = wined3d
origin = Fedora wine

[prefix plain]
path = {self.plain}
profile = baseline

[prefix unicode]
path = {self.unicode}
profile = baseline
""")

    def run(self, *args, env=None, timeout=600):
        return subprocess.run(
            [str(SCRIPT), *args],
            env=self.env | (env or {}),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def ok(self, *args, **kw):
        result = self.run(*args, **kw)
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    def host(self, *args):
        result = subprocess.run(
            [sys.executable, "-I", str(HOST), *args],
            env=self.env,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=300,
        )
        lines = result.stdout.strip().splitlines()
        assert result.returncode == 0 and lines, result.stdout + result.stderr[-3000:]
        return json.loads(lines[-1])

    def wrapper(self, fmt, rel):
        return self.home / f".{fmt}/yabridge/{rel}.{fmt}"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def reg_values(px, key):
    """Values of one key in user.reg, with hex continuation lines joined."""
    text = (Path(px) / "user.reg").read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"\\\n\s*", "", text)
    want, values, inside = key.replace("\\", "\\\\").lower(), {}, False
    for line in text.splitlines():
        if line.startswith("["):
            inside = line[1 : line.rindex("]")].lower() == want
        elif inside and line.startswith('"') and "=" in line:
            name, value = line.split("=", 1)
            values[name.strip('"').lower()] = value
    return values


def logfont(height, face):
    data = height.to_bytes(4, "little", signed=True) + bytes(12) + (400).to_bytes(4, "little")
    data += bytes([0, 0, 0, 1, 0, 0, 0, 0]) + face.encode("utf-16-le").ljust(64, b"\0")
    return "hex:" + ",".join(f"{b:02x}" for b in data)


@pytest.fixture(scope="module")
def inputs():
    missing = [name for name in FILES if not (INPUTS / name).is_file()]
    if missing:
        pytest.skip(f"missing in {INPUTS}: {', '.join(missing)}")
    for name, digest in FILES.items():
        assert sha256(INPUTS / name) == digest, f"{name} does not match its pinned sha256"
    return INPUTS


@pytest.fixture(scope="module")
def env(tmp_path_factory, inputs):
    e = Env(tmp_path_factory.mktemp("vstbridge-real"))
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
    sockets = set(runtime.glob("yabridge-Airwindows*"))
    archives = [str(inputs / name) for name in FILES if name.startswith("yabridge")]
    e.ok("bridge", "install", *archives, "--origin", "CI run 41351703537")
    e.ok("bridge", "use", PIN)
    e.ok("setup", timeout=900)
    yield e
    subprocess.run(["wineserver", "-k"], env=e.env | {"WINEPREFIX": str(e.plain)}, check=False)
    subprocess.run(["wineserver", "-k"], env=e.env | {"WINEPREFIX": str(e.unicode)}, check=False)
    # vstbridge_host.py exits without unloading the bridge, which leaves yabridge's socket
    # directories behind.
    for path in set(runtime.glob("yabridge-Airwindows*")) - sockets:
        shutil.rmtree(path, ignore_errors=True)
    if os.environ.get("VSTBRIDGE_REAL_KEEP") != "1":
        shutil.rmtree(e.base, ignore_errors=True)


@pytest.fixture(scope="module")
def plugins(env, inputs):
    env.ok(
        "install",
        "plain",
        str(inputs / f"{AIR}-64bit-setup.exe"),
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/SP-",
        timeout=900,
    )
    with zipfile.ZipFile(inputs / f"{AIR}.zip") as z:
        for member in z.namelist():
            if member.startswith("Airwindows Consolidated.vst3/"):
                z.extract(member, env.unicode / COMMON / "VST3" / UNICODE_DIR)
            elif member == "Airwindows Consolidated.clap":
                z.extract(member, env.unicode / COMMON / "CLAP" / UNICODE_DIR)
    env.ok("sync")
    return env


# --- bridge and prefixes -----------------------------------------------------------------


def test_bridge_is_the_pinned_build(env):
    out = env.ok("bridge", "status").stdout
    assert PIN in out
    assert (env.home / ".local/share/yabridge").resolve().name == PIN


def test_new_prefixes_are_marked_64_bit_and_at_144_dpi(env):
    for px in (env.plain, env.unicode):
        assert (px / ".vstbridge-prefix").is_file()
        assert reg_values(px, r"Control Panel\Desktop")["logpixels"] == "dword:00000090"
    out = env.ok("prefixes").stdout
    assert "plain" in out and "unicode" in out


def test_setup_is_idempotent_and_keeps_a_changed_dpi(env):
    subprocess.run(
        [
            *("wine", "reg", "add", r"HKCU\Control Panel\Desktop"),
            *("/v", "LogPixels", "/t", "REG_DWORD", "/d", "120", "/f"),
        ],
        env=env.env | {"WINEPREFIX": str(env.plain), "WINEDEBUG": "-all"},
        capture_output=True,
        check=True,
    )
    subprocess.run(["wineserver", "-w"], env=env.env | {"WINEPREFIX": str(env.plain)}, check=True)
    plan = env.ok("plan").stdout
    assert "create" not in plan.lower()
    env.ok("setup", timeout=900)
    assert reg_values(env.plain, r"Control Panel\Desktop")["logpixels"] == "dword:00000078"


def test_dispatcher_runs_the_profile_runner_and_rejects_unknown_prefixes(env, tmp_path):
    for px in (env.plain, env.unicode):
        result = subprocess.run(
            [str(env.loader), "--version"],
            env=env.env | {"WINEPREFIX": str(px)},
            capture_output=True,
            text=True,
            check=True,
        )
        assert result.stdout.startswith("wine-")
    result = subprocess.run(
        [str(env.loader), "wineboot", "--init"],
        env=env.env | {"WINEPREFIX": str(tmp_path / "unknown")},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 127 and "not a managed prefix" in result.stderr
    assert not (tmp_path / "unknown").exists()


# --- appearance and fonts ----------------------------------------------------------------

PERSONALIZE = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"


def test_theme_follows_configuration_and_restores(env):
    assert reg_values(env.plain, PERSONALIZE)["appsuselighttheme"] == "dword:00000000"
    env.conf("light")
    try:
        env.ok("appearance", "apply", "plain")
        values = reg_values(env.plain, PERSONALIZE)
        assert values["appsuselighttheme"] == values["systemuseslighttheme"] == "dword:00000001"
        backup = (env.plain / ".vstbridge-appearance").read_text().splitlines()
        originals = {line.split("\t")[1].lower(): line.split("\t")[2] for line in backup}
        env.ok("appearance", "restore", "plain")
        values = reg_values(env.plain, PERSONALIZE)
        for name, orig in originals.items():
            if orig == "ABSENT":
                assert name not in values
            else:
                assert values[name] == f"dword:{int(orig, 0):08x}"
    finally:
        env.conf("dark")
    env.ok("appearance", "apply", "plain")


def test_fonts_are_complete_and_repair_is_idempotent(env):
    fonts = env.plain / "drive_c/windows/Fonts"
    before = sorted(p.name for p in fonts.iterdir())
    plan = env.ok("fix-fonts", "plain", "--plan").stdout
    assert "would: copy" not in plan
    env.ok("fix-fonts", "plain")
    assert sorted(p.name for p in fonts.iterdir()) == before


def test_segoe_import_sets_logfont_and_restore_reverts_it(env, tmp_path):
    source = tmp_path / "windows fonts"
    source.mkdir()
    shutil.copy("/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf", source / "segoeui.ttf")
    key = r"Control Panel\Desktop\WindowMetrics"
    original = reg_values(env.unicode, key)
    env.ok("fonts", "import-segoe", "unicode", str(source), "--ui-font")
    dpi = int(reg_values(env.unicode, r"Control Panel\Desktop")["logpixels"].split(":")[1], 16)
    values = reg_values(env.unicode, key)
    expected = logfont(-((9 * dpi + 36) // 72), "Segoe UI")
    for metric in ("captionfont", "smcaptionfont", "menufont", "statusfont", "messagefont"):
        assert values[metric] == expected
    assert (env.unicode / "drive_c/windows/Fonts/segoeui.ttf").is_file()
    env.ok("appearance", "restore", "unicode")
    restored = reg_values(env.unicode, key)
    for metric in ("captionfont", "menufont", "messagefont"):
        assert restored.get(metric) == original.get(metric)


# --- plugins through the real bridge -----------------------------------------------------


def test_installer_bridges_vst3_and_clap(plugins):
    assert plugins.wrapper("vst3", PLUGIN).is_dir()
    assert plugins.wrapper("clap", PLUGIN).is_file()
    assert plugins.wrapper("vst3", f"{UNICODE_DIR}/Airwindows Consolidated").is_dir()
    logs = list((plugins.home / ".local/state/vstbridge/logs").glob("plain-install-*.log"))
    assert logs


def test_clap_scans_and_processes_audio(plugins):
    wrapper = str(plugins.wrapper("clap", PLUGIN))
    scan = plugins.host("clap-scan", wrapper)
    assert [p["vendor"] for p in scan["plugins"]] == ["Airwindows"]
    audio = plugins.host("clap-process", wrapper, "--frames", "512", "--blocks", "20")
    assert audio["finite"] and audio["frames"] == 10240
    assert audio["peak_in"] == pytest.approx(0.5, abs=1e-3)
    assert 0 not in audio["statuses"]  # CLAP_PROCESS_ERROR


def test_vst3_scans_from_an_ascii_prefix(plugins):
    scan = plugins.host("vst3-scan", str(plugins.wrapper("vst3", PLUGIN)))
    assert scan["vendor"] == "Airwindows"
    assert "Audio Module Class" in [c["category"] for c in scan["classes"]]


def test_clap_works_from_a_non_ascii_prefix(plugins):
    rel = f"{UNICODE_DIR}/Airwindows Consolidated"
    assert plugins.host("clap-scan", str(plugins.wrapper("clap", rel)))["plugins"]


@pytest.mark.xfail(
    strict=True,
    reason=f"yabridge {PIN}: wstring_convert::from_bytes for non-ASCII prefix paths",
)
def test_vst3_from_a_non_ascii_prefix(plugins):
    rel = f"{UNICODE_DIR}/Airwindows Consolidated"
    assert plugins.host("vst3-scan", str(plugins.wrapper("vst3", rel)))["classes"]


# --- plugin editor on a virtual X display ----------------------------------------------

NEXT_PRESET = "0.962,0.073"  # the down arrow next to the effect name, as a fraction of the editor


@pytest.fixture(scope="module")
def editor(plugins, tmp_path_factory):
    missing = [t for t in ("xvfb-run", "xdotool", "import") if not shutil.which(t)]
    if missing:
        pytest.skip(f"needs {', '.join(missing)} (sudo dnf install xorg-x11-server-Xvfb xdotool)")
    out = tmp_path_factory.mktemp("editor")
    env = {
        k: v
        for k, v in plugins.env.items()
        if k not in ("DISPLAY", "WAYLAND_DISPLAY", "XAUTHORITY")
    }
    result = subprocess.run(
        [
            *("xvfb-run", "-a", "-s", "-screen 0 1920x1080x24"),
            *(sys.executable, "-I", str(HOST), "clap-gui", str(plugins.wrapper("clap", PLUGIN))),
            *("--out", str(out), "--seconds", "6", "--click", NEXT_PRESET),
        ],
        env=env,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=180,
    )
    lines = [line for line in result.stdout.splitlines() if line.startswith("{")]
    assert result.returncode == 0 and lines, result.stdout[-3000:] + result.stderr[-3000:]
    return json.loads(lines[-1])


def test_clap_editor_embeds_and_renders(editor):
    assert editor["x11"] and editor["set_parent"] and editor["show"]
    assert [editor["shown"]["width"], editor["shown"]["height"]] == editor["size"]
    assert editor["shown"]["colors"] > 100


@pytest.mark.xfail(
    strict=True,
    reason="Wine 11.20 + JUCE 8 Direct2D editor: the click reaches Wine, the editor never repaints",
)
def test_clap_editor_responds_to_a_click(editor):
    assert editor["clicked"]["digest"] != editor["shown"]["digest"]


@pytest.mark.xfail(
    strict=True,
    reason="Wine 11.20 + JUCE 8 Direct2D editor: gui.destroy waits forever inside the plugin",
)
def test_clap_editor_closes(editor):
    assert editor["closed"]


# --- diagnostics -------------------------------------------------------------------------


def test_doctor_passes_and_reports_the_non_ascii_prefix(plugins):
    result = plugins.run("doctor")
    assert result.returncode == 0, result.stdout + result.stderr
    assert re.search(r"\b0 fail\b", result.stdout)
    assert "[unicode] path contains non-ASCII characters" in result.stdout
    assert "plugin wrappers match" in result.stdout


def test_manifest_records_the_setup(plugins):
    plugins.ok("manifest", "--write")
    manifests = list((plugins.home / ".local/state/vstbridge").glob("manifest-*.txt"))
    assert manifests
    text = manifests[0].read_text()
    assert PIN in text and "plain:" in text and "dpi=" in text


def test_no_default_wine_prefix_was_created(plugins):
    assert not (plugins.home / ".wine").exists()
