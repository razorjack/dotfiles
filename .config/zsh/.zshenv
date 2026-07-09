# Set before anything modifies PATH so later prepends (and .zprofile's re-source
# of paths.sh) collapse to a single entry instead of stacking in nested shells.
typeset -U path PATH

# On the env path so all zsh shell types get the full PATH. Also sets
# HOMEBREW_PREFIX, which the per-OS fragments sourced by .profile read.
source "$HOME/.config/shell/paths.sh"

source ~/.profile

# Optional machine-local overrides (untracked). Sourced last so it can override
# anything the shared and per-OS config set. Usually absent.
[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
