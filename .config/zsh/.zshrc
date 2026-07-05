# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

function set-title-precmd() {
  printf "\e]2;%s\a" "${PWD/#$HOME/~}"
}

function set-title-preexec() {
  printf "\e]2;%s\a" "$1"
}

autoload -Uz add-zsh-hook
add-zsh-hook precmd set-title-precmd
add-zsh-hook preexec set-title-preexec

fpath=($fpath $HOME/.zsh/functions $HOME/.zsh/completions)
typeset -U fpath
setopt promptsubst

autoload -Uz compinit
zstyle ':completion:*' menu select
# Rebuild the dump if it is missing or older than 24h, else take the -C fast
# path. ZDOTDIR is set, so the real dump lives at $ZDOTDIR/.zcompdump. The glob
# qualifier (N.mh-24) only matches a regular file modified in the last 24h;
# filename generation must happen in this array assignment, not inside [[ ]].
_zdump=(${ZDOTDIR:-$HOME}/.zcompdump(N.mh-24))
if (( $#_zdump )); then
  compinit -C
else
  compinit
fi
unset _zdump

autoload -U auto_bundle_exec
auto_bundle_exec
autoload -U auto_spring_or_bundle_exec
auto_spring_or_bundle_exec

# enable case insensitive completions
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=*' 'l:|=* r:|=*'

# history setup
HISTFILE=$HOME/.history
HISTSIZE=1000000
SAVEHIST=1000000

setopt BANG_HIST                 # Treat the '!' character specially during expansion.
setopt EXTENDED_HISTORY          # Write the history file in the ":start:elapsed;command" format.
setopt INC_APPEND_HISTORY        # Write to the history file immediately, not when the shell exits.
setopt SHARE_HISTORY             # Share history between all sessions.
setopt HIST_EXPIRE_DUPS_FIRST    # Expire duplicate entries first when trimming history.
setopt HIST_IGNORE_DUPS          # Don't record an entry that was just recorded again.
setopt HIST_IGNORE_ALL_DUPS      # Delete old recorded entry if new entry is a duplicate.
setopt HIST_FIND_NO_DUPS         # Do not display a line previously found.
setopt HIST_IGNORE_SPACE         # Don't record an entry starting with a space.
setopt HIST_SAVE_NO_DUPS         # Don't write duplicate entries in the history file.
setopt HIST_REDUCE_BLANKS        # Remove superfluous blanks before recording entry.
setopt HIST_VERIFY               # Don't execute immediately upon history expansion.

# Cap the buffer length the syntax highlighter re-scans on every keystroke.
# Without this, ^R (history-incremental-search-backward) hangs after 1-2 chars.
ZSH_HIGHLIGHT_MAXLENGTH=200
source $RZR_PREFIX/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
source $RZR_PREFIX/etc/profile.d/z.sh
export ZSH_HIGHLIGHT_HIGHLIGHTERS_DIR=$RZR_PREFIX/share/zsh-syntax-highlighting/highlighters
[[ -d "$RZR_PREFIX/share/zsh-completions" ]] && fpath=("$RZR_PREFIX/share/zsh-completions" $fpath)

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

bindkey -v

autoload -U edit-command-line
zle -N edit-command-line
bindkey '^xe' edit-command-line
bindkey '^x^e' edit-command-line

eval "$(direnv hook zsh)"

autoload edit-command-line; zle -N edit-command-line
bindkey '^e' edit-command-line

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

export PATH="$HOME/.yarn/bin:$HOME/.config/yarn/global/node_modules/.bin:$PATH"
source $RZR_PREFIX/share/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
source ~/.config/zsh/p10k.zsh
bindkey '^R' history-incremental-search-backward
export PATH="$HOME/.local/bin:$PATH"

if [[ -d /opt/homebrew/opt/postgresql@16 ]]; then
  export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
  export LDFLAGS="-L/opt/homebrew/opt/postgresql@16/lib"
  export CPPFLAGS="-I/opt/homebrew/opt/postgresql@16/include"
  export PKG_CONFIG_PATH="/opt/homebrew/opt/postgresql@16/lib/pkgconfig"
fi

yt() {
    local video_link="$1"
    fabric -y "$video_link" --transcript
}

[ -f ~/.config/op/plugins.sh ] && source ~/.config/op/plugins.sh
