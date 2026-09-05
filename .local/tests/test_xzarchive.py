import tarfile

import pytest


def test_archive_excludes_generated_files_without_changing_source(xzarchive, tmp_path):
    source = tmp_path / "project with spaces"
    files = [
        "app/main.rb",
        "log/development.log",
        "log/keep.txt",
        "tmp/cache/data",
        "node_modules/pkg/index.js",
        "public/uploads/photo.jpg",
        "public/system/file",
    ]
    for name in files:
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(name)
    dest = xzarchive.archive(source)
    with tarfile.open(dest) as archive:
        names = archive.getnames()
    assert f"{source.name}/app/main.rb" in names
    assert f"{source.name}/log/keep.txt" in names
    assert not any(
        name in names
        for name in [f"{source.name}/{name}" for name in files[1:] if name != "log/keep.txt"]
    )
    assert all((source / name).read_text() == name for name in files)


def test_failed_archive_preserves_previous_output(xzarchive, tmp_path, monkeypatch):
    source = tmp_path / "project"
    source.mkdir()
    dest = tmp_path / "project.tar.xz"
    dest.write_bytes(b"previous archive")

    def fail(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(tarfile.TarFile, "add", fail)
    with pytest.raises(OSError, match="disk full"):
        xzarchive.archive(source)
    assert dest.read_bytes() == b"previous archive"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["project", "project.tar.xz"]


def test_archive_rejects_root_and_missing_directory(xzarchive, tmp_path):
    with pytest.raises(ValueError):
        xzarchive.archive(type(tmp_path)(tmp_path.anchor))
    with pytest.raises(FileNotFoundError):
        xzarchive.archive(tmp_path / "missing")


def test_empty_argument_does_not_archive_current_directory(xzarchive, monkeypatch):
    monkeypatch.setattr("sys.argv", ["xzarchive", ""])
    with pytest.raises(SystemExit) as error:
        xzarchive.xzarchive()
    assert error.value.code == 2
