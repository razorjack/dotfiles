# macOS /etc/zprofile runs path_helper which reorders PATH, pushing /usr/bin
# ahead of mise shims. Re-prepend shims so they take precedence again.
mise_shims="${MISE_DATA_DIR:-$HOME/.local/share/mise}/shims"
[[ -d "$mise_shims" ]] && export PATH="$mise_shims:$PATH"
unset mise_shims

# Added by Toolbox App
export PATH="$PATH:/Users/razorjack/Library/Application Support/JetBrains/Toolbox/scripts"
