[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile

# Activate mise shims for all zsh shells (non-interactive included).
# For login shells, .zprofile re-prepends shims after path_helper reorders PATH.
command -v mise >/dev/null && eval "$(mise activate --shims)"
