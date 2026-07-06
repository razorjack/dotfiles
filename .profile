# Loader for the shared shell config plus the per-OS fragment. Sourced by zsh
# (via ~/.config/zsh/.zshenv) and bash (via ~/.bash_profile), so keep it
# bash-compatible.
# $OSTYPE is a shell builtin (no uname fork, and works before PATH is set up).
. "$HOME/.config/shell/common.sh"
case "$OSTYPE" in
  darwin*) . "$HOME/.config/shell/darwin.sh" ;;
  linux*)  . "$HOME/.config/shell/linux.sh" ;;
esac
