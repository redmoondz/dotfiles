#!/usr/bin/env python3
"""
sync_configs.py — sync configs from the system to the repository.

Usage:
    python3 sync_configs.py              # sync and push
    python3 sync_configs.py --dry-run    # show what will be copied
    python3 sync_configs.py --no-push    # update files without pushing
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()

# ── Config directories to sync from ~/.config/ ─────────────────────────────────────
CONFIG_DIRS = [
    "alacritty",
    "dunst",
    "easyeffects",
    "fastfetch",
    "gtk-3.0",
    "hypr",
    "nvim",
    "rofi",
    "swaylock",
    "voxtype",
    "waybar",
    "zathura",
]

# ── Standalone files from HOME ─────────────────────────────────────────────────────
HOME_FILES = [
    ".zshrc",
    ".dir_colors",
    ".inputrc",
]

# ── Output colors ───────────────────────────────────────────────────────────────────
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
RESET = "\033[0m"


def info(msg: str) -> None:
    print(f"{CYAN}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"{GREEN}✓{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"{YELLOW}⚠{RESET} {msg}")


def error(msg: str) -> None:
    print(f"{RED}✗{RESET} {msg}", file=sys.stderr)


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


# ── Directory sync ──────────────────────────────────────────────────────────────────
def sync_config_dirs(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Config directories ══{RESET}")
    for name in CONFIG_DIRS:
        src = HOME / ".config" / name
        dst = REPO_ROOT / ".config" / name
        if not src.exists():
            warn(f"Skipped (not found): {src}")
            continue
        if dry_run:
            info(f"[dry-run] cp -r {src} → {dst}")
        else:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            ok(f"{name}/")


def sync_home_files(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Files from HOME ══{RESET}")
    for name in HOME_FILES:
        src = HOME / name
        dst = REPO_ROOT / name
        if not src.exists():
            warn(f"Skipped (not found): {src}")
            continue
        if dry_run:
            info(f"[dry-run] cp {src} → {dst}")
        else:
            shutil.copy2(src, dst)
            ok(name)


def sync_wallpapers(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Wallpapers ══{RESET}")
    src_dir = HOME / "Pictures" / "Wallpaper"
    dst_dir = REPO_ROOT / "Pictures" / "Wallpapers"

    if not src_dir.exists():
        warn(f"Wallpaper directory not found: {src_dir}")
        return

    wallpapers = list(src_dir.glob("*.jpg")) + list(src_dir.glob("*.png")) + list(src_dir.glob("*.jpeg"))
    if not wallpapers:
        warn("No wallpapers found in ~/Pictures/Wallpapers/")
        return

    if dry_run:
        info(f"[dry-run] cp {len(wallpapers)} files → {dst_dir}")
        for w in wallpapers:
            info(f"  {w.name}")
    else:
        dst_dir.mkdir(parents=True, exist_ok=True)
        for w in wallpapers:
            shutil.copy2(w, dst_dir / w.name)
        ok(f"{len(wallpapers)} wallpapers copied → Pictures/Wallpapers/")


# ── Git operations ──────────────────────────────────────────────────────────────────
def git_push() -> None:
    print(f"\n{CYAN}══ Git ══{RESET}")

    result = run(["git", "status", "--porcelain"], check=False)
    if not result.stdout.strip():
        ok("No changes to commit")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Auto-sync: {timestamp}"

    run(["git", "add", "-A"])
    ok("git add -A")

    run(["git", "commit", "-m", commit_msg])
    ok(f'git commit: "{commit_msg}"')

    result = run(["git", "push", "origin", "main"], check=False)
    if result.returncode == 0:
        ok("git push origin main")
    else:
        error(f"git push failed:\n{result.stderr}")
        sys.exit(1)


# ── Entry point ─────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Sync dotfiles from the system to the repository")
    parser.add_argument("--dry-run", action="store_true", help="Show what will be copied without making real changes")
    parser.add_argument("--no-push", action="store_true", help="Update files without pushing to GitHub")
    args = parser.parse_args()

    print(f"\n{GREEN}╔══════════════════════════════════╗{RESET}")
    print(f"{GREEN}║      dotfiles sync_configs.py    ║{RESET}")
    print(f"{GREEN}╚══════════════════════════════════╝{RESET}")

    if args.dry_run:
        print(f"\n{YELLOW}Dry-run mode: no changes will be applied{RESET}")

    # Make sure we are in the repository root
    import os
    os.chdir(REPO_ROOT)

    sync_config_dirs(args.dry_run)
    sync_home_files(args.dry_run)
    sync_wallpapers(args.dry_run)

    if not args.dry_run and not args.no_push:
        git_push()
    elif args.dry_run:
        print(f"\n{YELLOW}Dry-run complete. Run without --dry-run to apply changes.{RESET}")
    else:
        print(f"\n{YELLOW}Files updated. Push skipped (--no-push).{RESET}")

    print(f"\n{GREEN}Done!{RESET}\n")


if __name__ == "__main__":
    main()
