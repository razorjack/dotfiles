[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile

# Prepend mise shims for all zsh shells so non-login shells resolve tools
# through mise too. For login shells, .zprofile still re-prepends shims after
# path_helper reorders PATH.
mise_shims="${MISE_DATA_DIR:-$HOME/.local/share/mise}/shims"
[[ -d "$mise_shims" ]] && export PATH="$mise_shims:$PATH"
unset mise_shims
