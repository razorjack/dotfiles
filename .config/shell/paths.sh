# Single source of truth for PATH, sourced on the env path by both zsh
# (.config/zsh/.zshenv) and bash (~/.bash_profile). Bash-compatible; every entry
# guarded so it stays valid on Fedora (no Homebrew).

# Cache brew shellenv (its output depends only on the prefix) and re-fork brew
# only when the binary is newer; `eval "$(brew shellenv)"` costs ~25 ms/shell.
# `shellenv sh` is POSIX (the no-arg form emits zsh syntax that breaks bash); the
# dropped zsh completions fpath entry is re-added in .config/zsh/.zshrc.
if [ -x /opt/homebrew/bin/brew ]; then
  brew_cache="$HOME/.cache/brew-shellenv.sh"
  if [ ! -r "$brew_cache" ] || [ /opt/homebrew/bin/brew -nt "$brew_cache" ]; then
    mkdir -p "$HOME/.cache" && /opt/homebrew/bin/brew shellenv sh > "$brew_cache"
  fi
  . "$brew_cache"
  unset brew_cache
fi

# Prepend after brew (its path_helper would otherwise reorder these below the
# system paths), lowest priority first, so the final order is:
#   mise shims > ~/.local/bin > ~/.yarn/bin > postgres@16 > brew > system

# postgres@16 is keg-only; the build flags let non-interactive shells compile the
# pg gem (agents build gems without an interactive shell).
if [ -d /opt/homebrew/opt/postgresql@16 ]; then
  export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
  export LDFLAGS="-L/opt/homebrew/opt/postgresql@16/lib"
  export CPPFLAGS="-I/opt/homebrew/opt/postgresql@16/include"
  export PKG_CONFIG_PATH="/opt/homebrew/opt/postgresql@16/lib/pkgconfig"
fi

[ -d "$HOME/.yarn/bin" ] && export PATH="$HOME/.yarn/bin:$PATH"
[ -d "$HOME/.local/bin" ] && export PATH="$HOME/.local/bin:$PATH"

# Shims stay highest so per-project runtime versions always win (shims-only).
mise_shims="${MISE_DATA_DIR:-$HOME/.local/share/mise}/shims"
[ -d "$mise_shims" ] && export PATH="$mise_shims:$PATH"
unset mise_shims

jetbrains_scripts="$HOME/Library/Application Support/JetBrains/Toolbox/scripts"
[ -d "$jetbrains_scripts" ] && export PATH="$PATH:$jetbrains_scripts"
unset jetbrains_scripts
