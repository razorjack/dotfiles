# Dotfiles Configuration Guide

## Strict Rules

- **NEVER push to git**: Do not run `git push` under any circumstances. Commits can be created when requested, but pushing to remote is strictly forbidden.

## System Requirements

- **Operating Systems**: Dual OS setup (macOS + Linux Fedora KDE)
- New scripts and configurations should be compatible with both operating systems

## Directory Structure & XDG Compliance

- **Config Location**: Prefer `~/.config/` for tool configurations that support XDG Base Directory Specification
- **Environment Variables**: If a tool requires an environment variable to point to a config in `.config/`, set it in `~/.zshenv`
- **Git Strategy**: This repo uses a whitelist approach - everything is ignored by default (`*`), specific files are whitelisted with `!` patterns in `.gitignore`
- **Git Repository Root**: `~/` (home directory), not `~/.config/`. Always run git commands from `~/` to avoid path issues.
- **Brewfile Location**: `~/.config/razorjack/Brewfile` (not `~/Brewfile` - follows XDG organization)

### Adding New Files to Git

Due to the whitelist approach, adding new files requires special handling:

1. **Add whitelist pattern to `~/.gitignore`**: Add `!<path>` pattern (e.g., `!.config/CLAUDE.md`)
2. **Always use `git add -f`** until first commit: `git add -f <path>` (e.g., `git add -f ~/.config/CLAUDE.md`)

**Critical**: Even with the `!` pattern in `.gitignore`, git requires `-f` (force) for ALL operations on the new file until after the first commit. This includes:
- Initial add
- Re-staging after edits
- Any modifications before first commit

After the file is committed once, it will be tracked normally and `-f` is no longer needed. Always run git commands from `~/` (repo root).

## Configuration File Locations

Quick reference for common configurations:

- **Git**: `~/.config/git/config` - aliases, user info, merge/diff settings
- **Zsh**: `~/.zshrc`, `~/.zshenv` - shell configuration, environment variables
- **Neovim**: `~/.config/nvim/` - LazyVim configuration
- **Ghostty**: `~/.config/ghostty/` - terminal emulator config
- **Kitty**: `~/.config/kitty/` - terminal emulator config
- **Karabiner**: `~/.config/karabiner/` - keyboard customization
- **Lazygit**: `~/.config/lazygit/` - git TUI configuration
- **Mise**: `~/.config/mise/` or `~/.mise.toml` - version manager config
- **Brewfile**: `~/.config/razorjack/Brewfile` - Homebrew package list

## Shell & Terminal

- **Shell**: zsh (preferred)
- **Terminal Emulators**:
  - Primary: ghostty
  - Secondary: kitty

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
| `mise` | Version manager | Replaces rbenv/nvm |
| `bat` | File viewer | Cat alternative with syntax highlighting |
| `eza` | Directory listing | Modern ls replacement |
| `delta` | Git diff | Enhanced diff viewer |

## Design Patterns

- **Interactive Commands**: When interaction is required, consider using `fzf` for fuzzy finding
- **Font**: Monaspace Neon (ligatures disabled)
- **Color Theme**: OneDark / dark themes preferred across tools
