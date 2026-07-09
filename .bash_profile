source "$HOME/.config/shell/paths.sh"

source ~/.profile

# Optional machine-local overrides (untracked). Sourced last so it can override
# anything the shared and per-OS config set. Usually absent.
[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"

# bash auto-sources .bashrc only for non-login interactive shells, so do it here
# for interactive login shells too.
case $- in *i*) [ -r "$HOME/.bashrc" ] && . "$HOME/.bashrc" ;; esac

if [ -e "$HOME/.nix-profile/etc/profile.d/nix.sh" ]; then . "$HOME/.nix-profile/etc/profile.d/nix.sh"; fi # added by Nix installer
