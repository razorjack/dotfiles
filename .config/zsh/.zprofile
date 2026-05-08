# macOS /etc/zprofile runs path_helper which reorders PATH, pushing /usr/bin
# ahead of homebrew and mise shims. Re-prepend both so they win again
# (brew first, then mise shims on top so mise stays highest priority).
[[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"
mise_shims="${MISE_DATA_DIR:-$HOME/.local/share/mise}/shims"
[[ -d "$mise_shims" ]] && export PATH="$mise_shims:$PATH"
unset mise_shims

# Added by Toolbox App
export PATH="$PATH:/Users/razorjack/Library/Application Support/JetBrains/Toolbox/scripts"
