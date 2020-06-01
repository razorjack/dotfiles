export HOMEBREW_INSTALL_BADGE="🔫  💪"
export FZF_DEFAULT_COMMAND='
  (fd ||
   find * -name ".*" -prune -o -type f -print -o -type l -print) 2> /dev/null'

export HISTCONTROL=ignoreboth:erasedups

# moar colors
alias grep="grep --color"
alias ls="ls -G"
export LSCOLORS=dxfxcxdxbxegedabagacad

export ACK_COLOR_MATCH='red'
export EDITOR='nvim'

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/usr/local/sbin:~/bin:$PATH
export DIRENV_LOG_FORMAT=''

export RIPGREP_CONFIG_PATH=$HOME/.ripgreprc

function xzarchive() {
  archive_target=${1%/}

  if [ -d $archive_target/log/ ]; then
    :> $archive_target/log/*.log
  fi

  if [ -d $archive_target/tmp/cache ]; then
    rm -rf $archive_target/tmp/cache
  fi

  if [ -d $archive_target/node_modules ]; then
    rm -rf $archive_target/node_modules
  fi

  if [ -d $archive_target/public/uploads ]; then
    rm -rf $archive_target/public/uploads
  fi

  if [ -d $archive_target/public/system ]; then
    rm -rf $archive_target/public/system
  fi

  tar -c "$archive_target" | xz -3 --lzma2=preset=3,dict=512Mi --verbose > "$archive_target.tar.xz"
}

if which rbenv > /dev/null; then eval "$(rbenv init - --no-rehash)"; fi

alias cici='goreman -f Procfile.test start'
