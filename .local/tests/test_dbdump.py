import datetime
import os
import sys

import pytest

NOW = datetime.datetime(2026, 9, 5, tzinfo=datetime.UTC)


def test_failed_second_dump_preserves_all_previous_backups(dbdump, tmp_path, monkeypatch):
    previous = tmp_path / "mongo-6.zst"
    previous.write_bytes(b"previous backup")

    def dump(command, dest):
        dest.write_bytes(b"incomplete dump")
        if command[0] == "pg_dumpall":
            raise RuntimeError("connection failed")

    monkeypatch.setattr(dbdump, "dump", dump)
    with pytest.raises(RuntimeError, match="connection failed"):
        dbdump.backup(tmp_path, NOW)
    assert previous.read_bytes() == b"previous backup"
    assert list(tmp_path.iterdir()) == [previous]


def test_backup_publishes_complete_private_files(dbdump, tmp_path, monkeypatch):
    monkeypatch.setattr(dbdump, "dump", lambda command, dest: dest.write_bytes(command[0].encode()))
    files = dbdump.backup(tmp_path, NOW)
    assert {path.name for path in files} == {
        "mongo-2026-W35.zst",
        "mongo-6.zst",
        "postgres-2026-W35.zst",
        "postgres-6.zst",
    }
    for path in files:
        assert path.read_bytes() == (
            b"mongodump" if path.name.startswith("mongo") else b"pg_dumpall"
        )
        assert path.stat().st_mode & 0o777 == 0o600


def test_dump_checks_producer_exit_status(dbdump, tmp_path, monkeypatch):
    compressor = tmp_path / "zstd"
    compressor.write_text("#!/bin/sh\ncat\n")
    compressor.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}/usr/bin:/bin")
    with pytest.raises(RuntimeError, match="exited with 7"):
        dbdump.dump(
            [sys.executable, "-c", "print('partial'); raise SystemExit(7)"], tmp_path / "dump"
        )


def test_dump_checks_compressor_exit_status(dbdump, tmp_path, monkeypatch):
    compressor = tmp_path / "zstd"
    compressor.write_text("#!/bin/sh\nexit 9\n")
    compressor.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(RuntimeError, match="zstd exited with 9"):
        dbdump.dump([sys.executable, "-c", "import time; time.sleep(30)"], tmp_path / "dump")
