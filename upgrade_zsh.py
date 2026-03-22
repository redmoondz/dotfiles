#!/usr/bin/env python3
"""
zsh_setup.py — Automated Zsh Plugin Installer & .zshrc Configurator
Plugin manager : Oh My Zsh
Plugins        : zsh-autosuggestions, zsh-syntax-highlighting,
                 zsh-history-substring-search, fzf
Existing installs are REMOVED and reinstalled from scratch.
"""

import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

# ─── Colors ───────────────────────────────────────────────────────────────────

RESET   = "\033[0m"
BOLD    = "\033[1m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
CYAN    = "\033[36m"
RED     = "\033[31m"
MAGENTA = "\033[35m"

def info(msg):      print(f"{CYAN}[INFO]{RESET}       {msg}")
def ok(msg):        print(f"{GREEN}[OK]{RESET}         {msg}")
def warn(msg):      print(f"{YELLOW}[WARN]{RESET}       {msg}")
def error(msg):     print(f"{RED}[ERR]{RESET}        {msg}")
def reinstall(msg): print(f"{MAGENTA}[REINSTALL]{RESET}  {msg}")
def header(msg):    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}\n{BOLD}  {msg}{RESET}\n{'─'*60}")

# ─── Paths ────────────────────────────────────────────────────────────────────

HOME        = Path.home()
ZSHRC       = HOME / ".zshrc"
ZSH_CUSTOM  = HOME / ".oh-my-zsh" / "custom"
OMZ_DIR     = HOME / ".oh-my-zsh"
PLUGINS_DIR = ZSH_CUSTOM / "plugins"
FZF_DIR     = HOME / ".fzf"

# ─── Plugin registry ──────────────────────────────────────────────────────────

PLUGINS = {
    "zsh-autosuggestions": {
        "repo": "https://github.com/zsh-users/zsh-autosuggestions",
        "dest": PLUGINS_DIR / "zsh-autosuggestions",
        "desc": "Fish-like inline suggestions from history",
    },
    "zsh-syntax-highlighting": {
        "repo": "https://github.com/zsh-users/zsh-syntax-highlighting",
        "dest": PLUGINS_DIR / "zsh-syntax-highlighting",
        "desc": "Real-time syntax highlighting in the shell",
    },
    "zsh-history-substring-search": {
        "repo": "https://github.com/zsh-users/zsh-history-substring-search",
        "dest": PLUGINS_DIR / "zsh-history-substring-search",
        "desc": "Up/down arrow searches history by substring",
    },
}

# Markers that identify zsh_setup-owned blocks inside .zshrc
ZSHRC_MARKERS = [
    "# zsh_setup: plugins list",
    "# zsh_setup: history config",
    "# zsh_setup: syntax highlighting colors",
    "# zsh_setup: history-substring-search keybindings",
    "# zsh_setup: fzf",
    "# zsh_setup: zsh-autosuggestions config",
]

# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a subprocess; exit the script on non-zero return code."""
    result = subprocess.run(cmd, capture_output=capture, text=True, env=os.environ)
    if result.returncode != 0 and not capture:
        error(f"Command failed: {' '.join(str(c) for c in cmd)}")
        if result.stderr:
            print(result.stderr.strip())
        sys.exit(1)
    return result


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def remove_dir(path: Path):
    """Recursively delete a directory."""
    if path.exists():
        reinstall(f"Removing {path} …")
        shutil.rmtree(path)
        ok(f"  Removed.")


def backup_zshrc():
    """Create a timestamped backup of ~/.zshrc."""
    if ZSHRC.exists():
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = HOME / f".zshrc.bak.{stamp}"
        shutil.copy2(ZSHRC, backup)
        warn(f"Backed up .zshrc → {backup}")


def strip_zshrc_blocks():
    """
    Remove all zsh_setup-owned sections from .zshrc so they can be
    rewritten cleanly.  A section runs from its marker line to the next
    blank line (or EOF).
    """
    if not ZSHRC.exists():
        return

    text = ZSHRC.read_text()
    escaped = [re.escape(m) for m in ZSHRC_MARKERS]
    pattern = (
        r"(?m)^(?:"
        + "|".join(escaped)
        + r").*?(?=\n{2,}|\Z)"
    )
    cleaned = re.sub(pattern, "", text, flags=re.DOTALL)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    ZSHRC.write_text(cleaned)
    ok("  Cleared previous zsh_setup blocks from .zshrc.")


def append_block(block: str):
    """Unconditionally append a config block to ~/.zshrc."""
    with ZSHRC.open("a") as f:
        f.write(f"\n{block}\n")

# ─── Step 1: Prerequisites ────────────────────────────────────────────────────

def check_prerequisites():
    header("Step 1/5 — Checking prerequisites")
    required = ["git", "curl", "zsh"]
    missing = [c for c in required if not command_exists(c)]
    if missing:
        error(f"Missing required tools: {', '.join(missing)}")
        error("Install them first, e.g.:  sudo apt install git curl zsh")
        sys.exit(1)
    ok(run(["zsh",  "--version"], capture=True).stdout.strip())
    ok(run(["git",  "--version"], capture=True).stdout.strip())
    ok(run(["curl", "--version"], capture=True).stdout.splitlines()[0])

# ─── Step 2: Oh My Zsh ───────────────────────────────────────────────────────

def install_oh_my_zsh():
    header("Step 2/5 — Oh My Zsh")
    if OMZ_DIR.exists():
        reinstall("Oh My Zsh already present — upgrading to latest …")
        upgrade = OMZ_DIR / "tools" / "upgrade.sh"
        if upgrade.exists():
            run(["bash", str(upgrade)])
            ok("Oh My Zsh upgraded.")
        else:
            warn("Upgrade script not found — doing a fresh reinstall.")
            remove_dir(OMZ_DIR)
            _fresh_omz_install()
        return
    _fresh_omz_install()


def _fresh_omz_install():
    info("Downloading Oh My Zsh installer …")
    script = HOME / ".omz_install.sh"
    run(["curl", "-fsSL",
         "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh",
         "-o", str(script)])
    script.chmod(0o755)
    run(["bash", str(script), "--unattended"])
    script.unlink(missing_ok=True)
    ok("Oh My Zsh installed.")

# ─── Step 3: Zsh plugins ─────────────────────────────────────────────────────

def install_plugins():
    header("Step 3/5 — Zsh plugins  [reinstall mode]")
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    for name, cfg in PLUGINS.items():
        dest: Path = cfg["dest"]
        info(f"[{name}]  {cfg['desc']}")
        remove_dir(dest)                                          # always wipe
        info(f"  Cloning {cfg['repo']} …")
        run(["git", "clone", "--depth=1", cfg["repo"], str(dest)])
        ok(f"  Installed → {dest}")

# ─── Step 4: fzf ─────────────────────────────────────────────────────────────

def install_fzf():
    header("Step 4/5 — fzf  [reinstall mode]")
    remove_dir(FZF_DIR)                                           # always wipe
    info("Cloning fzf …")
    run(["git", "clone", "--depth=1",
         "https://github.com/junegunn/fzf.git", str(FZF_DIR)])
    ok(f"fzf cloned → {FZF_DIR}")

    install_script = FZF_DIR / "install"
    if install_script.exists():
        info("Running fzf installer (zsh completion + key-bindings) …")
        run([str(install_script),
             "--no-bash", "--no-fish", "--completion", "--key-bindings"])
        ok("fzf installed.")
    else:
        warn("fzf install script not found — skipping.")

# ─── Step 5: Configure .zshrc ────────────────────────────────────────────────

def configure_zshrc():
    header("Step 5/5 — Configuring .zshrc  [reinstall: full rewrite]")
    backup_zshrc()
    strip_zshrc_blocks()      # remove stale zsh_setup sections

    # ── 5a. plugins=() ───────────────────────────────────────────────────────
    new_plugins_line = (
        "plugins=(\n"
        "  git\n"
        "  zsh-autosuggestions\n"
        "  zsh-syntax-highlighting\n"
        "  zsh-history-substring-search\n"
        "  fzf\n"
        ")"
    )
    text = ZSHRC.read_text() if ZSHRC.exists() else ""
    if "plugins=(" in text:
        text = re.sub(r"plugins=\([^)]*\)", new_plugins_line, text, flags=re.DOTALL)
        ZSHRC.write_text(text)
        ok("  Patched existing plugins=() block.")
    else:
        append_block(f"# zsh_setup: plugins list\n{new_plugins_line}")
        ok("  Appended plugins=() block.")

    # ── 5b. History ───────────────────────────────────────────────────────────
    append_block("""\
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
setopt EXTENDED_HISTORY        # Store ISO timestamp alongside each entry""")
    ok("  History settings written.")

    # ── 5c. Syntax highlighting colour theme ──────────────────────────────────
    append_block("""\
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
ZSH_HIGHLIGHT_STYLES[bracket-error]='fg=red,bold'""")
    ok("  Syntax highlighting colours written.")

    # ── 5d. History-substring-search keybindings ──────────────────────────────
    append_block("""\
# zsh_setup: history-substring-search keybindings
bindkey '^[[A' history-substring-search-up    # ↑ arrow
bindkey '^[[B' history-substring-search-down  # ↓ arrow
bindkey '^P'   history-substring-search-up    # Ctrl-P
bindkey '^N'   history-substring-search-down  # Ctrl-N
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_FOUND='bg=cyan,fg=black,bold'
HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_NOT_FOUND='bg=red,fg=white,bold'
HISTORY_SUBSTRING_SEARCH_GLOBBING_FLAGS='i'   # case-insensitive""")
    ok("  History-substring-search keybindings written.")

    # ── 5e. fzf ───────────────────────────────────────────────────────────────
    append_block(r"""# zsh_setup: fzf
[ -f "$HOME/.fzf.zsh" ] && source "$HOME/.fzf.zsh"
export FZF_DEFAULT_OPTS='
  --height 40% --layout=reverse --border
  --color=dark
  --color=fg:-1,bg:-1,hl:#5fff87,fg+:-1,bg+:-1,hl+:#ffaf5f
  --color=info:#af87ff,prompt:#5fff87,pointer:#ff87d7,marker:#ff87d7
  --bind=ctrl-j:preview-down,ctrl-k:preview-up
'
# Ctrl-R → fuzzy history  |  Ctrl-T → fuzzy file  |  Alt-C → fuzzy cd""")
    ok("  fzf integration written.")

    # ── 5f. zsh-autosuggestions ───────────────────────────────────────────────
    append_block("""\
# zsh_setup: zsh-autosuggestions config
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=240'
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=40
ZSH_AUTOSUGGEST_USE_ASYNC=1
bindkey '^ ' autosuggest-accept       # Ctrl+Space → accept full suggestion
bindkey '^]' autosuggest-accept-word  # Ctrl+]     → accept next word""")
    ok("  zsh-autosuggestions config written.")

# ─── Summary ──────────────────────────────────────────────────────────────────

def print_summary():
    header("Reinstall complete! 🎉")
    print(f"""
  {GREEN}Reinstalled:{RESET}
    • Oh My Zsh                       {OMZ_DIR}
    • zsh-autosuggestions             {PLUGINS_DIR}/zsh-autosuggestions
    • zsh-syntax-highlighting         {PLUGINS_DIR}/zsh-syntax-highlighting
    • zsh-history-substring-search    {PLUGINS_DIR}/zsh-history-substring-search
    • fzf                             {FZF_DIR}

  {GREEN}~/.zshrc sections rewritten:{RESET}
    • plugins=()  (git, autosuggestions, highlighting, history-search, fzf)
    • History     (50 000 lines · dedup · timestamps · cross-session share)
    • Syntax highlighting  (main + bracket highlighters, full colour theme)
    • History-substring-search  (↑↓ / Ctrl-P/N · coloured match highlight)
    • fzf         (Ctrl-R · Ctrl-T · Alt-C · custom dark colour scheme)
    • zsh-autosuggestions  (async · Ctrl+Space full · Ctrl+] word accept)

  {YELLOW}Apply the new config:{RESET}
    {BOLD}exec zsh{RESET}   — replace the current shell with a fresh zsh session
    — or simply open a new terminal window.
""")

# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{BOLD}{CYAN}  Zsh Plugin Installer & .zshrc Configurator{RESET}")
    print(f"  Mode   : {MAGENTA}REINSTALL{RESET} — existing installs will be removed first")
    print(f"  Manager: Oh My Zsh")
    print(f"  User   : {os.getenv('USER', 'unknown')}  |  Home: {HOME}\n")

    check_prerequisites()
    install_oh_my_zsh()
    install_plugins()
    install_fzf()
    configure_zshrc()
    print_summary()


if __name__ == "__main__":
    main()
