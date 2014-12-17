fpath=($fpath $HOME/.zsh/functions $HOME/.zsh/completions)
typeset -U fpath
setopt promptsubst
autoload -U promptinit
promptinit
prompt pure
PURE_GIT_PULL=0

autoload -U compinit
compinit

autoload -U auto_bundle_exec
auto_bundle_exec
# enable case insensitive completions
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/usr/local/sbin:$PATH
export ACK_COLOR_MATCH='red'
export EDITOR='vim'

# moar colors
alias grep="grep --color"
alias ls="ls -G"
export LSCOLORS=dxfxcxdxbxegedabagacad

# history setup
HISTFILE=$HOME/.history
HISTSIZE=10000
SAVEHIST=10000

setopt append_history
setopt extended_history
setopt hist_expire_dups_first
setopt hist_ignore_dups # ignore duplication command history list
setopt hist_ignore_space
setopt hist_verify
setopt inc_append_history
setopt share_history # share command history data

### Added by the Heroku Toolbelt
export PATH="/usr/local/heroku/bin:$PATH"

OCLINT_HOME=/opt/oclint
export PATH=$OCLINT_HOME/bin:$PATH

source ~/.profile

PATH=$HOME/.rvm/bin:$PATH # Add RVM to PATH for scripting

export VAGRANT_DEFAULT_PROVIDER=parallels
source `brew --prefix`/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source `brew --prefix`/etc/profile.d/z.sh
fpath=(/usr/local/share/zsh-completions $fpath)

# Taken from https://github.com/bkzl/dotfiles/blob/master/zshrc
fancy-ctrl-z () {
  if [[ $#BUFFER -eq 0 ]]; then
    fg
    zle redisplay
  else
    zle push-input
    zle clear-screen
  fi
}
zle -N fancy-ctrl-z
bindkey '^Z' fancy-ctrl-z
