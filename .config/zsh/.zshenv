# Set before anything modifies PATH so later prepends (and .zprofile's re-source
# of paths.sh) collapse to a single entry instead of stacking in nested shells.
typeset -U path PATH

# On the env path so all zsh shell types get the full PATH. Also sets
# HOMEBREW_PREFIX, which .customenv reads next.
source "$HOME/.config/shell/paths.sh"

[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile
