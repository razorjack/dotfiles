import json
import subprocess
from types import SimpleNamespace

import pytest

LISTING = """\
device `genesys:libusb:001:004' is a Canon LiDE 210 flatbed scanner
device `escl:https://192.168.1.20:443' is a Brother MFC eSCL network scanner
device `airscan:e0:Brother' is a Brother MFC WSD network scanner
"""


def args(**kw):
    defaults = dict(device=None, dry_run=False)
    return SimpleNamespace(**{**defaults, **kw})


def scanimage(listing):
    def run(*a, **kw):
        return subprocess.CompletedProcess(a, 0, listing, "")

    return run


def test_backup_of(scan2pdf, tmp_path):
    pdf = tmp_path / "doc.pdf"
    assert scan2pdf.backup_of(pdf) == tmp_path / scan2pdf.BACKUP_DIR / "doc.pdf"


def test_shown_is_relative_when_possible(scan2pdf, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert scan2pdf.shown(tmp_path / "a" / "b.pdf") == scan2pdf.Path("a/b.pdf")
    assert scan2pdf.shown(scan2pdf.Path("/elsewhere/c.pdf")) == scan2pdf.Path("/elsewhere/c.pdf")


def test_discover_device_prefers_escl(scan2pdf, monkeypatch):
    monkeypatch.setattr(subprocess, "run", scanimage(LISTING))
    assert scan2pdf.discover_device() == "escl:https://192.168.1.20:443"


def test_discover_device_dies_without_network_scanner(scan2pdf, monkeypatch):
    monkeypatch.setattr(subprocess, "run", scanimage(LISTING.splitlines()[0]))
    with pytest.raises(SystemExit):
        scan2pdf.discover_device()


def test_device_for_uses_flag_then_cache_then_discovery(scan2pdf, tmp_path, monkeypatch):
    monkeypatch.setattr(scan2pdf, "CONFIG", tmp_path)
    monkeypatch.setattr(scan2pdf, "DEVICE_CACHE", tmp_path / "device.json")
    monkeypatch.setattr(scan2pdf, "discover_device", lambda: "escl:found")

    assert scan2pdf.device_for(args(device="escl:flag")) == "escl:flag"
    assert scan2pdf.device_for(args(dry_run=True)) == "escl:<device>"
    assert scan2pdf.device_for(args()) == "escl:found"
    assert json.loads((tmp_path / "device.json").read_text()) == {"device": "escl:found"}
    monkeypatch.setattr(scan2pdf, "discover_device", lambda: pytest.fail("cache ignored"))
    assert scan2pdf.device_for(args()) == "escl:found"


def parse(scan2pdf, monkeypatch, *argv):
    monkeypatch.setattr("sys.argv", ["scan2pdf", *argv])
    return scan2pdf.parse_args()


def test_parse_args_passthrough_and_color(scan2pdf, monkeypatch):
    parsed = parse(scan2pdf, monkeypatch, "a.pdf", "--color", "--", "--rotate-pages", "-x")
    assert parsed.files == [scan2pdf.Path("a.pdf")]
    assert parsed.ocrmypdf_args == ["--rotate-pages", "-x"]
    assert parsed.no_threshold is True


def test_parse_args_defaults(scan2pdf, monkeypatch):
    parsed = parse(scan2pdf, monkeypatch)
    assert (parsed.files, parsed.output, parsed.lang, parsed.dpi) == ([], None, "eng+pol", 300)
    assert parsed.ocrmypdf_args == []
    assert parsed.no_threshold is False


@pytest.mark.parametrize(
    "argv", [["--restore"], ["--restore", "-o", "x.pdf"], ["a.pdf", "-o", "x.pdf"]]
)
def test_parse_args_rejects_conflicting_modes(scan2pdf, monkeypatch, argv):
    with pytest.raises(SystemExit):
        parse(scan2pdf, monkeypatch, *argv)


def test_restore_puts_original_back(scan2pdf, tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"processed")
    backup = scan2pdf.backup_of(pdf)
    backup.parent.mkdir()
    backup.write_bytes(b"original")

    scan2pdf.restore(pdf)
    assert pdf.read_bytes() == b"original"
    assert not backup.parent.exists()


def test_restore_dies_without_backup(scan2pdf, tmp_path):
    with pytest.raises(SystemExit):
        scan2pdf.restore(tmp_path / "doc.pdf")


def test_process_in_place_refuses_double_processing(scan2pdf, tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"x")
    backup = scan2pdf.backup_of(pdf)
    backup.parent.mkdir()
    backup.write_bytes(b"x")
    with pytest.raises(SystemExit):
        scan2pdf.process_in_place(pdf, args())
