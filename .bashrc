# Interactive bash config: auto-sourced by non-login interactive bash and by
# .bash_profile for interactive login shells. Shared interactive bits (aliases,
# functions, LESS colours) live in interactive.sh.
source "$HOME/.config/shell/interactive.sh"

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

if [ -f "$HOME/.config/fabric/fabric-bootstrap.inc" ]; then . "$HOME/.config/fabric/fabric-bootstrap.inc"; fi
