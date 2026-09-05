import subprocess


def test_inventory_excludes_documents(dotcheck, tmp_path, monkeypatch):
    monkeypatch.setattr(
        dotcheck,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            ".config/zsh/.zshrc\0Desktop/notes.txt\0Documents/report.pdf\0.local/bin/narrate\0",
            "",
        ),
    )
    assert dotcheck.inventory(tmp_path) == [".config/zsh/.zshrc", ".local/bin/narrate"]


def test_read_sources_never_follows_untracked_symlinks(dotcheck, tmp_path):
    private = tmp_path / "private"
    private.write_text("private data")
    config = tmp_path / ".config"
    config.mkdir()
    (config / "link").symlink_to(private)
    sources, problems = dotcheck.read_sources(tmp_path, [".config/link"])
    assert sources == {}
    assert "symlink target is not tracked" in problems[0]


def test_includes_accept_alternates_and_detect_missing_assets(dotcheck):
    sources = {".config/ghostty/config": "config-file = ?linux.conf\n"}
    names = [*sources, ".config/ghostty/linux.conf##os.Linux"]
    assert dotcheck.check_references(sources, names) == []
    assert "no tracked file or alternate" in dotcheck.check_references(sources, list(sources))[0]


def test_alternates_reject_regular_files_without_changing_them(dotcheck, tmp_path):
    path = tmp_path / "config"
    path.write_text("local file")
    names = ["config##os.Linux"]
    assert dotcheck.check_alternates(tmp_path, names, "Linux")
    assert path.read_text() == "local file"
    path.unlink()
    path.symlink_to("config##os.Linux")
    assert dotcheck.check_alternates(tmp_path, names, "Linux") == []
    assert dotcheck.check_alternates(tmp_path, names, "Darwin")


def test_missing_dependency_declarations(dotcheck):
    problems = dotcheck.check_dependencies({}, installed=False)
    assert "git-lfs: Brewfile is missing git-lfs" in problems
    assert "git-lfs: setup_linux is missing git-lfs" in problems


def startup_sources(dotcheck):
    return {name: (dotcheck.ROOT / name).read_text() for name in dotcheck.STARTUP_FILES}


def test_current_shell_startup(dotcheck):
    assert dotcheck.check_startup(startup_sources(dotcheck)) == []


def test_startup_detects_fzf_overriding_atuin(dotcheck):
    sources = startup_sources(dotcheck)
    name = ".config/zsh/.zshrc"
    atuin = "_cache_tool_init atuin    atuin init zsh --disable-up-arrow\n"
    sources[name] = (
        sources[name]
        .replace(atuin, "")
        .replace(
            "_cache_tool_init starship starship init zsh",
            atuin + "_cache_tool_init starship starship init zsh",
        )
    )
    assert any(
        "Atuin does not own Ctrl-R" in problem for problem in dotcheck.check_startup(sources)
    )


def test_startup_detects_late_completions(dotcheck):
    sources = startup_sources(dotcheck)
    name = ".config/zsh/.zshrc"
    line = next(
        line
        for line in sources[name].splitlines(True)
        if 'fpath=("$RZR_PREFIX/share/zsh-completions"' in line
    )
    sources[name] = (
        sources[name].replace(line, "").replace("unset _zdump\n", "unset _zdump\n" + line)
    )
    assert any("completions did not load" in problem for problem in dotcheck.check_startup(sources))
