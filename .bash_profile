source "$HOME/.config/shell/paths.sh"

[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile

command -v fzf >/dev/null && eval "$(fzf --bash)"

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}

_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
eval "$(direnv hook bash)"

HISTSIZE=10000
HISTFILESIZE=1000000

source ~/.config/bash/fastprompt.sh
if [ -e "$HOME/.nix-profile/etc/profile.d/nix.sh" ]; then . "$HOME/.nix-profile/etc/profile.d/nix.sh"; fi # added by Nix installer
