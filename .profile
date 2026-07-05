# Loader for the shared shell config plus the per-OS fragment. Sourced by zsh
# (via ~/.config/zsh/.zshenv) and bash (via ~/.bash_profile), so keep it
# bash-compatible.
. "$HOME/.config/shell/common.sh"
case "$(uname -s)" in
  Darwin) . "$HOME/.config/shell/darwin.sh" ;;
  Linux)  . "$HOME/.config/shell/linux.sh" ;;
esac
