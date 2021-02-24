export HOMEBREW_INSTALL_BADGE="🔫  💪"
export FZF_DEFAULT_COMMAND='
  (fd ||
   find * -name ".*" -prune -o -type f -print -o -type l -print) 2> /dev/null'
export FZF_DEFAULT_OPTS=$FZF_DEFAULT_OPTS'
--color=dark
--color fg:-1,bg:-1,hl:39,fg+:3,bg+:234,hl+:229
--color info:150,prompt:110,spinner:150,pointer:167,marker:174
'

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

xzarchive() {
  archive_target=${1%/}

  if [ -d "$archive_target/log/" ]; then
    :> "$archive_target/log/*.log"
  fi

  if [ -d "$archive_target/tmp/cache" ]; then
    rm -rf "$archive_target/tmp/cache"
  fi

  if [ -d "$archive_target/node_modules" ]; then
    rm -rf "$archive_target/node_modules"
  fi

  if [ -d "$archive_target/public/uploads" ]; then
    rm -rf "$archive_target/public/uploads"
  fi

  if [ -d "$archive_target/public/system" ]; then
    rm -rf "$archive_target/public/system"
  fi

  tar -c "$archive_target" | xz -3 --lzma2=preset=3,dict=512Mi --verbose > "$archive_target.tar.xz"
}

if which rbenv > /dev/null; then eval "$(rbenv init - --no-rehash)"; fi

alias cici='goreman -f Procfile.test start'
alias dot='(cd && nvim $(git ls-files | fzf))'
alias gg=lazygit

export LESS=-R
export LESS_TERMCAP_mb="$(printf '%b' '[1;31m')"
export LESS_TERMCAP_md="$(printf '%b' '[1;36m')"
export LESS_TERMCAP_me="$(printf '%b' '[0m')"
export LESS_TERMCAP_so="$(printf '%b' '[01;44;33m')"
export LESS_TERMCAP_se="$(printf '%b' '[0m')"
export LESS_TERMCAP_us="$(printf '%b' '[1;32m')"
export LESS_TERMCAP_ue="$(printf '%b' '[0m')"
export HOMEBREW_NO_AUTO_UPDATE=1
