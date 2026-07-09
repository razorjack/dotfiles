# macOS-specific environment. Sourced from ~/.profile after common.sh. Env only;
# interactive bits (ls colours, tmsetup) live in interactive.sh.

export HOMEBREW_INSTALL_BADGE="🔫  💪"
export HOMEBREW_NO_AUTO_UPDATE=1

# Where .zshrc finds zsh-syntax-highlighting / zsh-completions. HOMEBREW_PREFIX
# is already set: paths.sh runs before ~/.profile on both zsh and bash.
export RZR_PREFIX=$HOMEBREW_PREFIX
