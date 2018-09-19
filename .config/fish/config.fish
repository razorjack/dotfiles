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

set -x HOMEBREW_INSTALL_BADGE "🔫  💪"
set -x FZF_DEFAULT_COMMAND 'ag -g ""'

set -x GOPATH "$HOME/.golang"
set -x HISTCONTROL ignoreboth:erasedups
set -x DIRENV_LOG_FORMAT ''

set fish_greeting
