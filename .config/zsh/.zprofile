# macOS /etc/zprofile runs path_helper on login, which reorders PATH and pushes
# system dirs above homebrew and the mise shims. Re-source paths.sh to restore
# our priority (mise shims highest). typeset -U path in .zshenv keeps it deduped.
source "$HOME/.config/shell/paths.sh"
