# Redirect Git to your dotfiles path
export GIT_CONFIG_GLOBAL="$HOME/brahmand5/dotfiles/gitconfig"

# Function to check for syntax errors (prevents breaking your git flow)
function gitconfig-check() {
    git config --list --file ~/dotfiles/gitconfig > /dev/null
    if [[ $? -eq 0 ]]; then
        echo "Gitconfig looks good (Size: $(stat -c%s ~/dotfiles/gitconfig) bytes)"
    else
        echo "Error in Gitconfig syntax!"
    fi
}

# Quickly edit the gitconfig in your dotfiles
alias gitconfig-edit='$EDITOR ~/brahmand5/dotfiles/gitconfig && gitconfig-check'
