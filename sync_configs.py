#!/usr/bin/env python3
"""
sync_configs.py — синхронизация конфигов с системы в репозиторий.

Использование:
    python3 sync_configs.py              # синхронизировать и запушить
    python3 sync_configs.py --dry-run    # показать что будет скопировано
    python3 sync_configs.py --no-push    # только обновить файлы без push
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Пути ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.resolve()
HOME = Path.home()

# ── Конфиг директории для синхронизации из ~/.config/ ────────────────────────
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

# ── Отдельные файлы из HOME ───────────────────────────────────────────────────
HOME_FILES = [
    ".zshrc",
    ".dir_colors",
    ".inputrc",
]

# ── Цвета для вывода ─────────────────────────────────────────────────────────
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


# ── Синхронизация директорий ──────────────────────────────────────────────────
def sync_config_dirs(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Конфиг директории ══{RESET}")
    for name in CONFIG_DIRS:
        src = HOME / ".config" / name
        dst = REPO_ROOT / ".config" / name
        if not src.exists():
            warn(f"Пропущено (не найдено): {src}")
            continue
        if dry_run:
            info(f"[dry-run] cp -r {src} → {dst}")
        else:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            ok(f"{name}/")


def sync_home_files(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Файлы из HOME ══{RESET}")
    for name in HOME_FILES:
        src = HOME / name
        dst = REPO_ROOT / name
        if not src.exists():
            warn(f"Пропущено (не найдено): {src}")
            continue
        if dry_run:
            info(f"[dry-run] cp {src} → {dst}")
        else:
            shutil.copy2(src, dst)
            ok(name)


def sync_wallpapers(dry_run: bool) -> None:
    print(f"\n{CYAN}══ Обои ══{RESET}")
    src_dir = HOME / "Pictures" / "Wallpaper"
    dst_dir = REPO_ROOT / "Pictures" / "Wallpapers"

    if not src_dir.exists():
        warn(f"Каталог обоев не найден: {src_dir}")
        return

    wallpapers = list(src_dir.glob("*.jpg")) + list(src_dir.glob("*.png")) + list(src_dir.glob("*.jpeg"))
    if not wallpapers:
        warn("Обои не найдены в ~/Pictures/Wallpapers/")
        return

    if dry_run:
        info(f"[dry-run] cp {len(wallpapers)} файлов → {dst_dir}")
        for w in wallpapers:
            info(f"  {w.name}")
    else:
        dst_dir.mkdir(parents=True, exist_ok=True)
        for w in wallpapers:
            shutil.copy2(w, dst_dir / w.name)
        ok(f"{len(wallpapers)} обоев скопировано → Pictures/Wallpapers/")


# ── Git операции ──────────────────────────────────────────────────────────────
def git_push() -> None:
    print(f"\n{CYAN}══ Git ══{RESET}")

    result = run(["git", "status", "--porcelain"], check=False)
    if not result.stdout.strip():
        ok("Нет изменений для коммита")
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
        error(f"git push завершился с ошибкой:\n{result.stderr}")
        sys.exit(1)


# ── Точка входа ───────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(description="Синхронизация dotfiles с системы в репозиторий")
    parser.add_argument("--dry-run", action="store_true", help="Показать что будет скопировано без реальных действий")
    parser.add_argument("--no-push", action="store_true", help="Обновить файлы без push на GitHub")
    args = parser.parse_args()

    print(f"\n{GREEN}╔══════════════════════════════════╗{RESET}")
    print(f"{GREEN}║      dotfiles sync_configs.py    ║{RESET}")
    print(f"{GREEN}╚══════════════════════════════════╝{RESET}")

    if args.dry_run:
        print(f"\n{YELLOW}Режим dry-run: изменения не будут применены{RESET}")

    # Убедиться что мы в корне репозитория
    import os
    os.chdir(REPO_ROOT)

    sync_config_dirs(args.dry_run)
    sync_home_files(args.dry_run)
    sync_wallpapers(args.dry_run)

    if not args.dry_run and not args.no_push:
        git_push()
    elif args.dry_run:
        print(f"\n{YELLOW}Dry-run завершён. Запустите без --dry-run для применения.{RESET}")
    else:
        print(f"\n{YELLOW}Файлы обновлены. Push пропущен (--no-push).{RESET}")

    print(f"\n{GREEN}Готово!{RESET}\n")


if __name__ == "__main__":
    main()
