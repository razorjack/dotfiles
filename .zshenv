[[ -s "$HOME/.customenv" ]] && source "$HOME/.customenv"
source ~/.profile
if [ -e /Users/razorjack/.nix-profile/etc/profile.d/nix.sh ]; then . /Users/razorjack/.nix-profile/etc/profile.d/nix.sh; fi # added by Nix installer
