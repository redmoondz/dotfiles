# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

zstyle ':omz:update' mode auto 
zstyle ':omz:update' frequency 7

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

ENABLE_CORRECTION="true"

plugins=(
  #Version control
  git 
  # Cloud & Infrastructure
  docker
  docker-compose
  kubectl
  helm
  terraform
  aws
  gcloud
  azure
  ansible

  # Programming Languages & Tools
  python
  pip
  node
  npm
  yarn
  golang
  rust

  # Productivity Boosters
  sudo              # Press ESC twice to add sudo to previous command
  extract           # Universal archive extractor (works with .tar, .zip, .gz, etc.)
  z                 # Jump to frequently used directories
  history           # Enhanced history commands
  command-not-found # Suggests package to install for missing commands
  vscode            # VS Code aliases and shortcuts

  # Community Plugins
  zsh-autosuggestions
  zsh-syntax-highlighting 
  zsh-history-substring-search
  zsh-interactive-cd
)

source $ZSH/oh-my-zsh.sh

# History substring search keybindings (arrows)
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='nvim'
else
  export EDITOR='nvim'
fi

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

fastfetch
export PATH="$HOME/.local/bin:$PATH"

# Added by LM Studio CLI (lms)
export PATH="$PATH:/home/rdmoon/.lmstudio/bin"
# End of LM Studio CLI section

alias cpl='copilot'
