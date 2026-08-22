"""Shared look and helpers for command line tools.

    from rzr import cli, info, ok, die, run, status, progress

OneDark palette, one set of message shapes, one progress bar style, one
help format. Scripts refer to semantic styles (path, num, cmd, ...) and
never to colors.
"""

import argparse
import subprocess
import sys
from functools import wraps
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.theme import Theme
from rich.traceback import install as pretty_tracebacks
from rich_argparse import RawDescriptionRichHelpFormatter

BLUE, PURPLE, CYAN, GREEN, YELLOW, RED, FG, DIM = (
    "#61afef", "#c678dd", "#56b6c2", "#98c379", "#e5c07b", "#e06c75", "#abb2bf", "#5c6370",
)

theme = Theme({
    "title": f"bold {BLUE}",
    "accent": PURPLE,
    "path": CYAN,
    "num": YELLOW,
    "cmd": DIM,
    "muted": DIM,
    "ok": GREEN,
    "warn": YELLOW,
    "err": f"bold {RED}",
    "bar.complete": BLUE,
    "bar.finished": GREEN,
    "bar.pulse": PURPLE,
    "progress.percentage": YELLOW,
    "progress.remaining": DIM,
    "progress.download": CYAN,
    "progress.data.speed": DIM,
    "argparse.args": CYAN,
    "argparse.metavar": YELLOW,
    "argparse.groups": f"bold {BLUE}",
    "argparse.prog": f"bold {PURPLE}",
    "argparse.syntax": "bold",
    "argparse.default": DIM,
    "argparse.help": FG,
    "argparse.text": FG,
})

out = Console(theme=theme, highlight=False)
err = Console(theme=theme, highlight=False, stderr=True)
pretty_tracebacks(console=err, width=out.width, suppress=[argparse])


def info(msg):
    out.print(f"[muted]▸[/] {msg}")


def ok(msg):
    out.print(f"[ok]✓[/] {msg}")


def warn(msg):
    err.print(f"[warn]![/] {msg}")


def fail(msg):
    err.print(f"[err]✗[/] {msg}")


def die(msg, code=1):
    fail(msg)
    sys.exit(code)


def status(msg):
    return out.status(msg, spinner="dots", spinner_style="accent")


def progress(*, bytes=False, transient=True, disable=False):
    columns = [
        SpinnerColumn(spinner_name="dots", style="accent", finished_text="[ok]✓[/]"),
        TextColumn("{task.description}"),
        BarColumn(bar_width=30),
        *([DownloadColumn(), TransferSpeedColumn()] if bytes else [MofNCompleteColumn()]),
        TimeRemainingColumn(),
    ]
    return Progress(*columns, console=out, transient=transient, disable=disable or not out.is_terminal)


def run(cmd, *, quiet=True, dry_run=False, **kw):
    cmd = [str(c) for c in cmd]
    if dry_run:
        shown = [Path(cmd[0]).name, *cmd[1:]]
        out.print(f"[cmd]$ {' '.join(shown)}[/]", soft_wrap=True)
        return subprocess.CompletedProcess(cmd, 0, "", "")
    result = subprocess.run(cmd, capture_output=quiet, text=True, **kw)
    if result.returncode:
        fail(f"[cmd]{cmd[0]}[/] exited with {result.returncode}")
        if quiet and result.stderr.strip():
            err.print(result.stderr.rstrip(), style="muted", markup=False)
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def cli(prog, description, epilog=None):
    return argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog=epilog,
        formatter_class=RawDescriptionRichHelpFormatter,
    )


def main(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except KeyboardInterrupt:
            err.print()
            sys.exit(130)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    return wrapper
