function reverse_history_search
  history | fzf --no-sort | read -l command
  if test $command
    commandline -rb $command
  end
end
bind \cr reverse_history_search

eval (direnv hook fish)

set -x PATH $HOME/.rbenv/shims $PATH
rbenv rehash

set -x LC_ALL en_US.UTF-8
set -x LANG en_US.UTF-8

export HOMEBREW_INSTALL_BADGE="🔫  💪"
export FZF_DEFAULT_COMMAND='
  (ag -g "" ||
   find * -name ".*" -prune -o -type f -print -o -type l -print) 2> /dev/null'

export GOPATH="$HOME/.golang"
export HISTCONTROL=ignoreboth:erasedups
