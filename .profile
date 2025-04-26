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

tmsetup() {
  sudo tmutil addexclusion -p ~/Downloads
  sudo tmutil addexclusion -p ~/.rbenv
  sudo tmutil addexclusion -p ~/.npm
  # Exclude logs
  fd --no-ignore-vcs --exclude node_modules --exclude public/system --exclude public/uploads --exclude tmp -p -g "**/log/*.log" ~/Projects -x sudo tmutil addexclusion -p
  # Exclude tmp directories of Rails projects
  fd --no-ignore-vcs --exclude public/system --exclude public/uploads -p -g "**/*/tmp" ~/Projects -x sudo tmutil addexclusion -p
}

dbdump() {
  local backup_dir="${XDG_DATA_HOME:-$HOME/.local/share}/dbbackups"
  mkdir -p "$backup_dir"
  mongodump --archive --quiet | zstd -14 -T8 --long=31 | tee "$backup_dir/mongo-$(date -u +%Y-W%W).zst" "$backup_dir/mongo-$(date -u +%w).zst" > /dev/null
  pg_dumpall | zstd -14 -T8 --long=31 | tee "$backup_dir/postgres-$(date -u +%Y-W%W).zst" "$backup_dir/postgres-$(date -u +%w).zst" > /dev/null
}

command -v mise >/dev/null && eval "$(mise activate --shims)"

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

export NVM_DIR="$HOME/.nvm"
[ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
