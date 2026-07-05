# macOS-specific shell config. Sourced from ~/.profile after common.sh.

export HOMEBREW_INSTALL_BADGE="🔫  💪"
export HOMEBREW_NO_AUTO_UPDATE=1

# BSD ls colours
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
