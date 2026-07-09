# Interactive-only shell config: aliases, functions, prompt colours. Sourced by
# zsh (.config/zsh/.zshrc) and bash (~/.bashrc). Keep it bash-compatible.

export FZF_DEFAULT_COMMAND='
  (fd ||
   find * -name ".*" -prune -o -type f -print -o -type l -print) 2> /dev/null'
export FZF_DEFAULT_OPTS=$FZF_DEFAULT_OPTS'
--color=dark
--color fg:-1,bg:-1,hl:39,fg+:3,bg+:234,hl+:229
--color info:150,prompt:110,spinner:150,pointer:167,marker:174
'

export HISTCONTROL=ignoreboth:erasedups
export ACK_COLOR_MATCH='red'

alias grep="grep --color"
alias cici='goreman -f Procfile.test start'
alias gg=lazygit
alias be='bundle exec'

export LESS=-R
export LESS_TERMCAP_mb=$'\e[1;31m'
export LESS_TERMCAP_md=$'\e[1;36m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_so=$'\e[01;44;33m'
export LESS_TERMCAP_se=$'\e[0m'
export LESS_TERMCAP_us=$'\e[1;32m'
export LESS_TERMCAP_ue=$'\e[0m'

# Prefer a project's Rails/Rake binstub, but fall back to the real executable
# so `rails new`, or rake outside a project, still work.
rails() { if [ -x bin/rails ]; then bin/rails "$@"; else command rails "$@"; fi; }
rake()  { if [ -x bin/rake ];  then bin/rake  "$@"; else command rake  "$@"; fi; }

# Fuzzy-open a tracked dotfile in $HOME. Guard against a cancelled fzf so we
# never launch nvim with no argument.
dot() {
  local file
  file="$(cd && git ls-files | fzf)" || return
  [ -n "$file" ] && (cd && nvim "$file")
}

yt() {
    local video_link="$1"
    fabric -y "$video_link" --transcript
}

xzarchive() {
  d=${1%/}

  if [ -d "$d/log/" ]; then
    for f in "$d"/log/*.log; do [ -e "$f" ] && : > "$f"; done
  fi

  [ -d "$d/tmp/cache" ] && rm -rf "$d/tmp/cache"
  [ -d "$d/node_modules" ] && rm -rf "$d/node_modules"
  [ -d "$d/public/uploads" ] && rm -rf "$d/public/uploads"
  [ -d "$d/public/system" ] && rm -rf "$d/public/system"

  # tar -cf - "$d" | xz -T0 -9e --lzma2=dict=1Gi > "$d.tar.xz"
  tar -c "$d" | xz -T0 -9e --lzma2=dict=1Gi --verbose > "$d.tar.xz"
}

dbdump() {
  local backup_dir="${XDG_DATA_HOME:-$HOME/.local/share}/dbbackups"
  mkdir -p "$backup_dir"
  mongodump --archive --quiet | zstd -14 -T8 --long=31 | tee "$backup_dir/mongo-$(date -u +%Y-W%W).zst" "$backup_dir/mongo-$(date -u +%w).zst" > /dev/null
  pg_dumpall | zstd -14 -T8 --long=31 | tee "$backup_dir/postgres-$(date -u +%Y-W%W).zst" "$backup_dir/postgres-$(date -u +%w).zst" > /dev/null
}

dirarchive() {
  local dir="${1%/}"  # strip trailing slash
  if [[ -z "$dir" ]]; then
    echo "Usage: dirarchive <directory>" >&2
    return 1
  fi
  if [[ ! -d "$dir" ]]; then
    echo "dirarchive: '$dir' is not a directory" >&2
    return 1
  fi
  local parent base outfile
  parent="$(dirname -- "$dir")"
  base="$(basename -- "$dir")"
  outfile="${base}.tar.zst"
  tar -cf - -C "$parent" "$base" | zstd -14 -T8 --long=31 -o "$outfile"
}

dirunarchive() {
  local file="${1%}"  # as‐given name
  if [[ -z "$file" ]]; then
    echo "Usage: dirunarchive <archive> (with or without .tar.zst)" >&2
    return 1
  fi

  local archive
  if [[ -f "$file" ]]; then
    archive="$file"
  elif [[ -f "${file}.tar.zst" ]]; then
    archive="${file}.tar.zst"
  else
    echo "dirunarchive: '$file(.tar.zst)' not found" >&2
    return 1
  fi

  zstd -d --long=31 --progress -c "$archive" | tar -xf -
}

case "$OSTYPE" in
  darwin*)
    alias ls="ls -G"
    export LSCOLORS=dxfxcxdxbxegedabagacad

    tmsetup() {
      sudo tmutil addexclusion -p ~/Downloads
      sudo tmutil addexclusion -p ~/.local/share/mise
      sudo tmutil addexclusion -p ~/.npm
      sudo tmutil addexclusion -p ~/.cache
      sudo tmutil addexclusion -p ~/.dropbox
      # DB backups are performed with dbdump
      sudo tmutil addexclusion -p /opt/homebrew/var
      # Everything web browser related is considered transient and unworthy of backup
      sudo tmutil addexclusion -p "~/Library/Application Support/Google/Chrome Canary"
      sudo tmutil addexclusion -p "~/Library/Application Support/Google/Chrome"
      sudo tmutil addexclusion -p "~/Library/Application Support/BraveSoftware/Brave-Browser-Beta"

      sudo tmutil addexclusion -p "~/Library/Application Support/Telegram Desktop"
      sudo tmutil addexclusion -p "~/Library/Application Support/Spotify/PersistentCache"
      sudo tmutil addexclusion -p "~/Library/Application Support/Dropbox"
      sudo tmutil addexclusion -p "~/Library/Application Support/BraveSoftware"
      # sudo tmutil addexclusion -p

      # Exclude logs
      fd --no-ignore-vcs --exclude node_modules --exclude public/system --exclude public/uploads --exclude tmp -p -g "**/log/*.log" ~/Projects -x sudo tmutil addexclusion -p
      # Exclude tmp directories of Rails projects
      fd --no-ignore-vcs --exclude public/system --exclude public/uploads -p -g "**/*/tmp" ~/Projects -x sudo tmutil addexclusion -p
      # Exclude petabytes of data from node_modules
      fd --no-ignore-vcs --exclude public/system --exclude public/uploads -t d -g '**/node_modules' -E '**/node_modules/**/node_modules' ~/Projects -x sudo tmutil addexclusion -p
    }
    ;;
  linux*)
    alias ls="ls --color=auto"
    # Bring macOS clipboard muscle memory to Wayland (from wl-clipboard).
    if command -v wl-copy >/dev/null 2>&1; then
      alias pbcopy='wl-copy'
      alias pbpaste='wl-paste'
    fi
    ;;
esac
