source ~/.profile

if [[ "$USER" == "root" ]]
then
  export PS1="\e[1;31m\]\u \[\e[1;33m\]\w\[\e[0m\] ";
else
  export PS1="\[\e[1;33m\]\w\[\e[0m\] ";
fi

# 100% pure Bash (no forking) function to determine the name of the current git branch
# https://gist.github.com/wolever/6525437
gitbranch() {
  export GITBRANCH=""

  local repo="" # "${_GITBRANCH_LAST_REPO-}"
  local gitdir=""
  [[ ! -z "$repo" ]] && gitdir="$repo/.git"

  # If we don't have a last seen git repo, or we are in a different directory
  if [[ -z "$repo" || "$PWD" != "$repo"* || ! -e "$gitdir" ]]; then
    local cur="$PWD"
    while [[ ! -z "$cur" ]]; do
      if [[ -e "$cur/.git" ]]; then
        repo="$cur"
        gitdir="$cur/.git"
        break
      fi
      cur="${cur%/*}"
    done
  fi

  if [[ -z "$gitdir" ]]; then
    # unset _GITBRANCH_LAST_REPO
    return 0
  fi
  # export _GITBRANCH_LAST_REPO="${repo}"
  local head=""
  local branch=""
  read head < "$gitdir/HEAD"
  case "$head" in
    ref:*)
      branch="${head##*/}"
      ;;
    "")
      branch=""
      ;;
    *)
      branch="d:${head:0:7}"
      ;;
  esac
  if [[ -z "$branch" ]]; then
    return 0
  fi
  export GITBRANCH="$branch"
}

PS1_green='\[\e[32m\]'
PS1_blue='\[\e[34m\]'
PS1_reset='\[\e[0m\]'
_mk_prompt() {
  # Change the window title of X terminals 
  case $TERM in
    xterm*|rxvt*|Eterm)
      echo -ne "\033]0;${USER}@${HOSTNAME%%.*}:${PWD/$HOME/~}\007"
      ;;
    screen)
      echo -ne "\033_${USER}@${HOSTNAME%%.*}:${PWD/$HOME/~}\033\\"
      ;;
  esac

  # Un-screw virtualenv stuff
  if [[ ! -z "${_OLD_VIRTUAL_PS1-}" ]]; then
    export PS1="$_OLD_VIRTUAL_PS1"
    unset _OLD_VIRTUAL_PS1
  fi

  if [[ -z "${_MK_PROMPT_ORIG_PS1-}" ]]; then
    export _MK_PROMPT_ORIG_PS1="$PS1"
  fi

  local prefix=()
  local jobcount="$(jobs -p | wc -l)"
  if [[ "$jobcount" -gt 0 ]]; then
    local job="${jobcount##* } job"
    [[ "$jobcount" -gt 1 ]] && job="${job}s"
    prefix+=("$job")
  fi

  gitbranch
  if [[ ! -z "$GITBRANCH" ]]; then
    prefix+=("${PS1_green}$GITBRANCH${PS1_reset}")
  fi

  local virtualenv="${VIRTUAL_ENV##*/}"
  if [[ ! -z "$virtualenv" ]]; then
    prefix+=("${PS1_blue}$virtualenv${PS1_reset}")
  fi

  PS1="$_MK_PROMPT_ORIG_PS1"
  if [[ ! -z "$prefix" ]]; then
    PS1="[${prefix[@]}] $PS1"
  fi

  export PS1
}
export PROMPT_COMMAND=_mk_prompt

if [ -f /usr/local/share/bash-completion/bash_completion ]; then
  . /usr/local/share/bash-completion/bash_completion
fi

[ -f ~/.fzf.bash ] && source ~/.fzf.bash

_fzf_compgen_path() {
  fd --hidden --follow --exclude ".git" . "$1"
}

_fzf_compgen_dir() {
  fd --type d --hidden --follow --exclude ".git" . "$1"
}
[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"

eval "$(direnv hook bash)"
