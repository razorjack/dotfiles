# set PATH to include rbenv if it exists
if [ -d "$HOME/.rbenv" ]; then
    export PATH="$HOME/.rbenv/bin:$PATH"
    eval "$(rbenv init -)"
fi

export HOMEBREW_INSTALL_BADGE=☕️
export FZF_DEFAULT_COMMAND='
  (git ls-files . -co --exclude-standard ||
   find * -name ".*" -prune -o -type f -print -o -type l -print) 2> /dev/null'
