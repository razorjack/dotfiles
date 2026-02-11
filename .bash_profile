[[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"

[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile

mise_shims="${MISE_DATA_DIR:-$HOME/.local/share/mise}/shims"
[[ -d "$mise_shims" ]] && export PATH="$mise_shims:$PATH"
unset mise_shims

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}

_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
eval "$(direnv hook bash)"

HISTSIZE=10000
HISTFILESIZE=1000000

source ~/.config/bash/bundler-exec.sh
source ~/.config/bash/fastprompt.sh
if [ -e /Users/razorjack/.nix-profile/etc/profile.d/nix.sh ]; then . /Users/razorjack/.nix-profile/etc/profile.d/nix.sh; fi # added by Nix installer
