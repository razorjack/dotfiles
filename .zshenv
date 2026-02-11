# Homebrew must be on PATH before anything else so that brew-installed
# tools (mise, etc.) are available in non-interactive shells too.
[[ -x /opt/homebrew/bin/brew ]] && eval "$(/opt/homebrew/bin/brew shellenv)"

export ZDOTDIR=~/.config/zsh
source $ZDOTDIR/.zshenv

export RIPGREP_CONFIG_PATH=~/.config/ripgrep/config
export AG_CONFIG_PATH=~/.config/ag/ignore
export ACKRC=~/.config/ack/ackrc
export PSQLRC=~/.config/psql/psqlrc
export INPUTRC=~/.config/readline/inputrc
export GEMRC=~/.config/gem/gemrc
