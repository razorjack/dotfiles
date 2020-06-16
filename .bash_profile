source ~/.profile

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}

_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"

eval "$(direnv hook bash)"

HISTSIZE=10000
HISTFILESIZE=1000000

source ~/.config/bash/bundler-exec.sh
source ~/.config/bash/fastprompt.sh
