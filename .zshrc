# If you come from bash you might have to change your $PATH.
# export PATH=$HOME/bin:$HOME/.local/bin:/usr/local/bin:$PATH

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time Oh My Zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Add wisely, as too many plugins slow down shell startup.
plugins=(
  git
  zsh-autosuggestions
  zsh-syntax-highlighting
  zsh-history-substring-search
  fzf
)

source $ZSH/oh-my-zsh.sh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
if [[ -n $SSH_CONNECTION ]]; then
  export EDITOR='micro'
else
  export EDITOR='nvim'
fi

# Compilation flags
# export ARCHFLAGS="-arch $(uname -m)"

# Set personal aliases, overriding those provided by Oh My Zsh libs,
# plugins, and themes. Aliases can be placed here, though Oh My Zsh
# users are encouraged to define aliases within a top-level file in
# the $ZSH_CUSTOM folder, with .zsh extension. Examples:
# - $ZSH_CUSTOM/aliases.zsh
# - $ZSH_CUSTOM/macos.zsh
# For a full list of active aliases, run `alias`.
#
# Example aliases
# alias zshconfig="mate ~/.zshrc"
# alias ohmyzsh="mate ~/.oh-my-zsh"

alias saver="powerprofilesctl set power-saver"
alias balanced="powerprofilesctl set balanced"
alias perf="powerprofilesctl set performance"

[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# zsh_setup: history config
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
setopt HIST_IGNORE_DUPS        # Skip consecutive duplicate commands
setopt HIST_IGNORE_ALL_DUPS    # Remove older duplicate if a new one is added
setopt HIST_IGNORE_SPACE       # Don't record commands prefixed with a space
setopt HIST_FIND_NO_DUPS       # No duplicates when navigating history
setopt HIST_REDUCE_BLANKS      # Strip extra blanks before recording
setopt SHARE_HISTORY           # Share history across all open sessions
setopt INC_APPEND_HISTORY      # Write each command immediately, not on exit
setopt EXTENDED_HISTORY        # Store ISO timestamp alongside each entry

# zsh_setup: syntax highlighting colors
ZSH_HIGHLIGHT_HIGHLIGHTERS=(main brackets pattern)
ZSH_HIGHLIGHT_STYLES[command]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=blue,bold'
ZSH_HIGHLIGHT_STYLES[alias]='fg=magenta,bold'
ZSH_HIGHLIGHT_STYLES[function]='fg=blue'
ZSH_HIGHLIGHT_STYLES[precommand]='fg=cyan,underline'
ZSH_HIGHLIGHT_STYLES[path]='fg=green'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg=green,bold'
ZSH_HIGHLIGHT_STYLES[path_prefix]='fg=green,underline'
ZSH_HIGHLIGHT_STYLES[globbing]='fg=yellow,bold'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg=yellow'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=green'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=green'
ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=cyan'
ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg=cyan,bold'
ZSH_HIGHLIGHT_STYLES[assign]='fg=white'
ZSH_HIGHLIGHT_STYLES[redirection]='fg=yellow,bold'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=red,bold'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=red,bold,underline'
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=magenta'
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=green,underline'
ZSH_HIGHLIGHT_STYLES[bracket-level-1]='fg=blue,bold'
ZSH_HIGHLIGHT_STYLES[bracket-level-2]='fg=green,bold'
ZSH_HIGHLIGHT_STYLES[bracket-level-3]='fg=magenta,bold'
ZSH_HIGHLIGHT_STYLES[bracket-error]='fg=red,bold'

# zsh_setup: history-substring-search keybindings
bindkey '^[[A' history-substring-search-up    # ↑ arrow
bindkey '^[[B' history-substring-search-down  # ↓ arrow
bindkey '^P'   history-substring-search-up    # Ctrl-P
bindkey '^N'   history-substring-search-down  # Ctrl-N
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_FOUND='bg=cyan,fg=black,bold'
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_NOT_FOUND='bg=red,fg=white,bold'
HISTORY_SUBSTRING_SEARCH_GLOBBING_FLAGS='i'   # case-insensitive

# zsh_setup: fzf
[ -f "$HOME/.fzf.zsh" ] && source "$HOME/.fzf.zsh"
export FZF_DEFAULT_OPTS='
  --height 40% --layout=reverse --border
  --color=dark
  --color=fg:-1,bg:-1,hl:#5fff87,fg+:-1,bg+:-1,hl+:#ffaf5f
  --color=info:#af87ff,prompt:#5fff87,pointer:#ff87d7,marker:#ff87d7
  --bind=ctrl-j:preview-down,ctrl-k:preview-up
'
# Ctrl-R → fuzzy history  |  Ctrl-T → fuzzy file  |  Alt-C → fuzzy cd

# zsh_setup: zsh-autosuggestions config
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=240'
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=40
ZSH_AUTOSUGGEST_USE_ASYNC=1
bindkey '^ ' autosuggest-accept       # Ctrl+Space → accept full suggestion
bindkey '^]' autosuggest-accept-word  # Ctrl+]     → accept next word

fastfetch
