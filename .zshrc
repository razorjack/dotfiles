fpath=($fpath $HOME/.zsh/functions $HOME/.zsh/completions)
typeset -U fpath
setopt promptsubst
autoload -U promptinit
promptinit
prompt grb

autoload -U compinit
compinit

autoload -U auto_bundle_exec
auto_bundle_exec
# enable case insensitive completions
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'


export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/usr/local/sbin
[[ -s "/Users/razorjack/.rvm/scripts/rvm" ]] && source "/Users/razorjack/.rvm/scripts/rvm"
export ACK_COLOR_MATCH='red'


PATH=$PATH:$HOME/.rvm/bin # Add RVM to PATH for scripting

# moar colors
alias grep="grep --color"
alias ls="ls -G"
export LSCOLORS=dxfxcxdxbxegedabagacad
