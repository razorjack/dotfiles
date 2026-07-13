# Dotfiles Configuration Guide

> **The repo's worktree is `$HOME`**, managed by **yadm** (git dir: `~/.local/share/yadm/repo.git` – there is no `~/.git`). Never walk, glob, or recursively search the home directory. Use `yadm ls-files` to enumerate the repo. A plain git clone of the same repo, at any location, may be used for authoring; if you are working in one now (the cwd is a dotfiles checkout that is not `$HOME`), that's it.

## Strict Rules

- **NEVER push to git**: Do not run `git push` or `yadm push` under any circumstances. Commits can be created when requested, but pushing to remote is strictly forbidden.
- **In `$HOME`, never edit through a yadm-generated symlink** (e.g. `~/.config/ghostty/linux.conf`): editors that save via rename replace the symlink with a regular file, and the next yadm command silently clobbers it. Edit the `##os.Linux` variant file instead.

## System Requirements

- **Operating Systems**: Dual OS setup (macOS + Linux Fedora KDE)
- New scripts and configurations should be compatible with both operating systems

## Directory Structure & XDG Compliance

- **Config Location**: Prefer `~/.config/` for tool configurations that support XDG Base Directory Specification
- **Environment Variables**: If a tool requires an environment variable to point to a config in `.config/`, set it in `~/.zshenv`
- **Git Strategy**: This repo uses a whitelist approach – everything is ignored by default (`/*`), and tracked paths are re-included with `!` chains in `.gitignore`
- **yadm**: `$HOME` is the worktree; the git dir is `~/.local/share/yadm/repo.git`. Use `yadm <git-subcommand>` for all repo operations in `$HOME` (`yadm status`, `yadm add`, `yadm diff`, ...). The `yadm` binary is vendored in the repo at `~/.local/bin/yadm`. `yadm status` hides untracked files (`status.showUntrackedFiles no`); use `yadm status -uall` when adding something new.
- **OS divergence**: files that must differ per OS are yadm *alternates* – `file##os.Linux` (and `##os.Darwin` if ever needed). On a matching machine, yadm creates the plain `file` as a symlink to the variant; on the other OS the plain name simply doesn't exist. All variants are checked out on every machine – only the symlink is conditional.
- **Authoring clone (optional)**: a plain git checkout of the same repo may exist at any location – even an ephemeral one (clone, work, push, delete). No yadm runs there, so no symlinks: alternates are just files. Prefer such a clone for agent-driven or multi-file work; sync via push/pull (`yadm pull` in `$HOME`). Its location is never referenced by any script or config, so it can move freely.
- **Brewfile Location**: `~/.config/razorjack/Brewfile` (not `~/Brewfile` - follows XDG organization)

### Adding New Files to Git

Add a `!` re-include chain to `~/.gitignore` for the new path, re-including every parent directory too (follow the chains already there). Plain `yadm add` (or `git add` in the authoring clone) then works, no `-f` needed.

**Trap**: re-include rules match the literal filename, so an alternate needs its full suffixed name in the chain (`!/.config/ghostty/linux.conf##os.Linux`) – a rule for the plain name will NOT match it and the file is silently ignored.

Verify with `git check-ignore -v <path>`: no output means not ignored; output starting with `!` means re-included (tracked-eligible). Confirm with `git add --dry-run <path>`.

### Making a Change

Two equivalent routes; both end in git, never in copying files between the trees:

- **Live in `$HOME`**: edit the file (for an alternate: the `##os.Linux` variant, never the plain-name symlink), then `yadm add <path> && yadm commit`. After the user pushes, any authoring clone catches up with `git pull`.
- **In an authoring clone** (preferred for agent-driven or multi-file work): edit, `git add`, `git commit`. After the user pushes, `yadm pull` in `$HOME` deploys it (and re-runs `yadm alt`).

The old workflow of mirroring edits into `$HOME` by hand is retired – a hand-copied file can silently replace a yadm-generated symlink and break an alternate.

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

### Terminal Config: Linux/KDE Overrides via yadm Alternates

The `ghostty` and `kitty` configs are **shared across macOS + Linux**. KDE Plasma 6 uses 1.5 *fractional* scaling, which renders fonts and GTK chrome ~1.3x larger than macOS's "150%" HiDPI (macOS supersamples then downscales). There is **no per-app scaling on Plasma 6 Wayland** (Wayland core is integer-only), so the fix is to shrink the font + chrome, and it must be Linux-only.

Cross-platform keys (`font-size`, `window-decoration`) can't differ per-OS in the shared config, so the Linux tweaks live in **tracked yadm alternates** included by an inert line in the shared config:

- **Ghostty**: shared `config` ends with `config-file = ?linux.conf`. On Linux, yadm links `linux.conf` -> `linux.conf##os.Linux` (tracked: `font-size`, `window-decoration = none`, `gtk-custom-css = ghostty-linux.css`, keyd-companion keybinds); `ghostty-linux.css##os.Linux` shrinks the GTK tab bar. On macOS neither symlink exists, so the optional include is a no-op.
- **Kitty**: shared `kitty.conf` ends with `globinclude linux-local.conf`. On Linux, yadm links `linux-local.conf` -> `linux-local.conf##os.Linux` (tracked: `font_size`, ctrl+c/v maps). Silent when absent on macOS.

Rule of thumb: platform-prefixed keys (`macos-*`, `gtk-*`) are inert on the other OS and may go in the shared config; genuinely cross-platform keys that must differ go in the `##os.Linux` alternates. Edit the alternates directly (never through the plain-name symlink); on a fresh machine yadm recreates the symlinks automatically.

### Shell Loading Chain

**`~/.profile`** is a thin loader: it sources the shared `~/.config/shell/common.sh`, then the per-OS fragment (`darwin.sh` on macOS, `linux.sh` on Linux) chosen by `uname -s`. All three **must stay bash-compatible** (sourced by both zsh and bash) – no zsh-only syntax like glob qualifiers.

**`RZR_PREFIX`** (used by `.zshrc` for zsh-syntax-highlighting and zsh-completions) is set per-OS: `$HOMEBREW_PREFIX` in `shell/darwin.sh`, `/usr` in `shell/linux.sh`.

**`~/.customenv`** is an optional, **untracked** escape hatch for truly machine-specific env, sourced last (after `~/.profile`) so it can override anything. It is normally absent – per-OS values belong in `shell/darwin.sh` / `shell/linux.sh` instead.

**Zsh** (all shell types):
```
~/.zshenv → brew shellenv → ~/.config/zsh/.zshenv → ~/.profile → ~/.customenv (if present) + mise shims
```
- Login shells also source `~/.config/zsh/.zprofile` (re-prepends mise shims after macOS `path_helper`)
- Interactive shells also source `~/.config/zsh/.zshrc` (completions, keybindings, starship prompt, zoxide, atuin)

**Bash** (login):
```
~/.bash_profile → brew shellenv → ~/.profile → ~/.customenv (if present) → mise shims prepend
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
| `starship` | Shell prompt | Replaces powerlevel10k; config in `~/.config/starship.toml` |
| `bat` | File viewer | Cat alternative with syntax highlighting |
| `eza` | Directory listing | Modern ls replacement |
| `delta` | Git diff | Enhanced diff viewer |

## Design Patterns

- **Interactive Commands**: When interaction is required, consider using `fzf` for fuzzy finding
- **Font**: Monaspace Neon (ligatures disabled)
- **Color Theme**: OneDark / dark themes preferred across tools
