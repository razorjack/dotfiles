# Dotfiles Configuration Guide

> **The repo root is `$HOME`.** Never walk, glob, or recursively search the home directory. Use `git ls-files` to enumerate the repo.

## Strict Rules

- **NEVER push to git**: Do not run `git push` under any circumstances. Commits can be created when requested, but pushing to remote is strictly forbidden.

## System Requirements

- **Operating Systems**: Dual OS setup (macOS + Linux Fedora KDE)
- New scripts and configurations should be compatible with both operating systems

## Directory Structure & XDG Compliance

- **Config Location**: Prefer `~/.config/` for tool configurations that support XDG Base Directory Specification
- **Environment Variables**: If a tool requires an environment variable to point to a config in `.config/`, set it in `~/.zshenv`
- **Git Strategy**: This repo uses a whitelist approach – everything is ignored by default (`/*`), and tracked paths are re-included with `!` chains in `.gitignore`
- **Git Repository Root**: `~/` (home directory), not `~/.config/`. Always run git commands from `~/` to avoid path issues.
- **Brewfile Location**: `~/.config/razorjack/Brewfile` (not `~/Brewfile` - follows XDG organization)

### Adding New Files to Git

Add a `!` re-include chain to `~/.gitignore` for the new path, re-including every parent directory too (follow the chains already there). Plain `git add` then works, no `-f` needed.

Verify a path is tracked with `git check-ignore -v <path>` (no output means it is not ignored).

## Configuration File Locations

Quick reference for common configurations:

- **Git**: `~/.config/git/config` - aliases, user info, merge/diff settings
- **Zsh**: `~/.zshenv` sets `ZDOTDIR=~/.config/zsh`, so all other zsh files (`.zshrc`, `.zprofile`, `.zlogin`) are loaded from `~/.config/zsh/`, **not** `~/`. The `~/.zprofile` file is NOT sourced.
- **Neovim**: `~/.config/nvim/` - LazyVim configuration
- **Ghostty**: `~/.config/ghostty/` - terminal emulator config
- **Kitty**: `~/.config/kitty/` - terminal emulator config
- **Karabiner**: `~/.config/karabiner/` - keyboard customization
- **Lazygit**: `~/.config/jesseduffield/lazygit/config.yml` – git TUI configuration
- **Mise**: `~/.config/mise/` or `~/.mise.toml` - version manager config
- **Brewfile**: `~/.config/razorjack/Brewfile` - Homebrew package list

## Shell & Terminal

- **Shell**: zsh (preferred)
- **Terminal Emulators**:
  - Primary: ghostty
  - Secondary: kitty

### Shell Loading Chain

**`~/.profile`** is a thin loader: it sources the shared `~/.config/shell/common.sh`, then the per-OS fragment (`darwin.sh` on macOS, `linux.sh` on Linux) chosen by `uname -s`. All three **must stay bash-compatible** (sourced by both zsh and bash) – no zsh-only syntax like glob qualifiers.

**`~/.customenv`** is an **untracked** per-machine overlay (not in git) – the home for machine-specific env. On macOS it sets `RZR_PREFIX=$HOMEBREW_PREFIX`; on Fedora (no Homebrew) it should set `RZR_PREFIX=/usr`. `RZR_PREFIX` is used by `.zshrc` for p10k and zsh-syntax-highlighting.

**Zsh** (all shell types):
```
~/.zshenv → brew shellenv → ~/.config/zsh/.zshenv → ~/.customenv + ~/.profile + mise shims
```
- Login shells also source `~/.config/zsh/.zprofile` (re-prepends mise shims after macOS `path_helper`)
- Interactive shells also source `~/.config/zsh/.zshrc` (completions, keybindings, prompt, zoxide, atuin)

**Bash** (login):
```
~/.bash_profile → brew shellenv → ~/.customenv + ~/.profile → mise shims prepend
```

### Mise Activation Strategy

**Shims-only, everywhere** – never use `mise activate zsh`/`mise activate bash` (mixed-mode PATH conflicts where install paths override shims, breaking per-project version resolution). Interactive shells use shims too, not `mise activate`.
- **Shims prepend**: `~/.config/zsh/.zshenv` (zsh, all shell types), `~/.bash_profile` (bash)
- **Shims re-prepend** (macOS login shells): `~/.config/zsh/.zprofile` (counteracts `path_helper`)

Mise manages **all** language runtimes (Ruby, Node, ...). Never add a brew-installed runtime (`node@X`, `ruby`, etc.) to PATH – it shadows the mise shims and breaks per-project versions.

## Development Environment

- **Primary Languages**: Ruby, JavaScript
- **Version Manager**: `mise` (manages both Ruby and Node.js installations)
- **Editor**: Neovim with LazyVim
- **Git TUI**: Lazygit (aliased as `gg`)

## Preferred CLI Tools

When implementing features or scripts, prefer these modern alternatives:

| Tool | Purpose | Notes |
|------|---------|-------|
| `rg` (ripgrep) | Text search | Faster grep alternative |
| `fd` | File finding | Modern find replacement |
| `fzf` | Fuzzy finder | Use for interactive selection (e.g., `git sw` for branch selection) |
| `mise` | Version manager | Replaces rbenv/nvm; manages ALL runtimes |
| `zoxide` | Directory jumping | Replaces `z`; the `z` command is zoxide |
| `atuin` | Shell history | Owns `^R`; local-only, no sync |
| `bat` | File viewer | Cat alternative with syntax highlighting |
| `eza` | Directory listing | Modern ls replacement |
| `delta` | Git diff | Enhanced diff viewer |

## Design Patterns

- **Interactive Commands**: When interaction is required, consider using `fzf` for fuzzy finding
- **Font**: Monaspace Neon (ligatures disabled)
- **Color Theme**: OneDark / dark themes preferred across tools
