command -v fzf >/dev/null && eval "$(fzf --bash)"
if [ -f "$HOME/.config/fabric/fabric-bootstrap.inc" ]; then . "$HOME/.config/fabric/fabric-bootstrap.inc"; fi