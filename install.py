#!/usr/bin/env python3
"""
install.py — dotfiles installer for redmoondz in a single command.

Usage:
    curl -sL https://raw.githubusercontent.com/redmoondz/dotfiles/main/install.py \
         -o /tmp/install.py && python3 /tmp/install.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────────────────
REPO_URL = "https://github.com/redmoondz/dotfiles.git"
REPO_BRANCH = "main"
INSTALL_DIR = Path(tempfile.mkdtemp()) / "dotfiles"

HOME = Path.home()
CONFIG_DIR = HOME / ".config"
PICTURES_DIR = HOME / "Pictures" / "Wallpapers"

VOXTYPE_MODELS_DIR = HOME / ".local" / "share" / "voxtype" / "models"
VOXTYPE_MODELS = {
    "large-v3-turbo": {
        "file": "ggml-large-v3-turbo.bin",
        "size": "~1.6 GB",
        "desc": "Multilingual (EN+RU), high quality — as in the current configuration",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin",
    },
    "base.en": {
        "file": "ggml-base.en.bin",
        "size": "~141 MB",
        "desc": "English only, fast download",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
    },
}

# ── Colors ─────────────────────────────────────────────────────────────────────────────────────
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ── Helper functions ─────────────────────────────────────────────────────────────────────────
def banner() -> None:
    print(f"""
{GREEN}{BOLD}
  ██████╗  ██████╗ ████████╗███████╗██╗██╗     ███████╗███████╗
  ██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██║██║     ██╔════╝██╔════╝
  ██║  ██║██║   ██║   ██║   █████╗  ██║██║     █████╗  ███████╗
  ██║  ██║██║   ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
  ██████╔╝╚██████╔╝   ██║   ██║     ██║███████╗███████╗███████║
  ╚═════╝  ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝
{RESET}
  {CYAN}Hyprland rice installer by redmoondz{RESET}
  {CYAN}https://github.com/redmoondz/dotfiles{RESET}
""")


def info(msg: str) -> None:
    print(f"  {CYAN}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"  {GREEN}✓{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}⚠{RESET} {msg}")


def error(msg: str) -> None:
    print(f"  {RED}✗{RESET} {msg}", file=sys.stderr)


def header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}━━━ {title} ━━━{RESET}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {YELLOW}?{RESET} {prompt}{suffix}: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def choose(prompt: str, options: list[tuple[str, str]]) -> int:
    """Show selection menu, return index of chosen option (0-based)."""
    print(f"\n  {YELLOW}?{RESET} {prompt}\n")
    for i, (label, desc) in enumerate(options, 1):
        print(f"    {CYAN}[{i}]{RESET} {label}")
        if desc:
            print(f"        {desc}")
    while True:
        try:
            answer = input(f"\n  Choice [1-{len(options)}]: ").strip()
            idx = int(answer) - 1
            if 0 <= idx < len(options):
                return idx
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        print(f"  {RED}Enter a number from 1 to {len(options)}{RESET}")


def run(cmd: list[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, **kwargs)


def run_sudo(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return run(["sudo"] + cmd, check=check)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


# ── Step 0: Checks ──────────────────────────────────────────────────────────────────
def step_check() -> None:
    header("Step 0: Environment checks")

    # Arch Linux
    if not Path("/etc/arch-release").exists():
        error("This is not Arch Linux. The installer only supports Arch Linux.")
        sys.exit(1)
    ok("Arch Linux detected")

    # Python version
    if sys.version_info < (3, 8):
        error(f"Python 3.8+ required, found {sys.version}")
        sys.exit(1)
    ok(f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Permissions (not root)
    if os.geteuid() == 0:
        error("Do not run the installer as root. Use a regular user.")
        sys.exit(1)
    ok(f"User: {os.environ.get('USER', 'unknown')}")

    # git
    if not command_exists("git"):
        error("git is not installed. Install it first: sudo pacman -S git")
        sys.exit(1)
    ok("git found")


# ── Step 1: Install yay ─────────────────────────────────────────────────────────────
def step_install_yay() -> None:
    header("Step 1: AUR helper (yay)")

    if command_exists("yay"):
        ok("yay already installed")
        return

    info("Installing yay...")
    run_sudo(["pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"])

    yay_dir = Path(tempfile.mkdtemp()) / "yay-install"
    run(["git", "clone", "https://aur.archlinux.org/yay.git", str(yay_dir)])
    run(["makepkg", "-si", "--noconfirm"], cwd=yay_dir)
    ok("yay installed")


# ── Step 2: Choose install type ─────────────────────────────────────────────────────
def step_choose_install_type() -> str:
    header("Step 2: Install type")

    choice = choose(
        "Choose a package set to install:",
        [
            ("Minimal", "Rice packages only (~35 packages: Hyprland, Waybar, Rofi, etc.)"),
            ("Full", "All packages from the source system (~230+ packages)"),
        ],
    )
    install_type = "minimal" if choice == 0 else "full"
    ok(f"Selected: {install_type}")
    return install_type


# ── Step 4: Install packages ────────────────────────────────────────────────────────
def step_install_packages(install_type: str) -> None:
    header(f"Step 4: Installing packages ({install_type})")

    pacman_file = INSTALL_DIR / "packages" / f"{install_type}_pacman.txt"
    aur_file = INSTALL_DIR / "packages" / f"{install_type}_aur.txt"

    # Pacman packages
    if pacman_file.exists():
        packages = [p.strip() for p in pacman_file.read_text().splitlines() if p.strip()]
        info(f"Installing {len(packages)} packages via pacman...")
        result = run_sudo(
            ["pacman", "-S", "--needed", "--noconfirm"] + packages,
            check=False,
        )
        if result.returncode != 0:
            warn("Some pacman packages failed to install. Trying one by one...")
            failed = []
            for pkg in packages:
                r = run_sudo(
                    ["pacman", "-S", "--needed", "--noconfirm", pkg],
                    check=False,
                )
                if r.returncode != 0:
                    failed.append(pkg)
            if failed:
                warn(f"Failed to install: {', '.join(failed)}")
            else:
                ok(f"{len(packages)} pacman packages installed")
        else:
            ok(f"{len(packages)} pacman packages installed")
    else:
        warn(f"Package file not found: {pacman_file}")

    # AUR packages
    if aur_file.exists():
        aur_packages = [p.strip() for p in aur_file.read_text().splitlines() if p.strip()]
        info(f"Installing {len(aur_packages)} AUR packages via yay...")
        result = run(
            ["yay", "-S", "--needed", "--noconfirm"] + aur_packages,
            check=False,
        )
        if result.returncode != 0:
            warn("Some AUR packages failed to install. Trying one by one...")
            failed = []
            for pkg in aur_packages:
                r = run(
                    ["yay", "-S", "--needed", "--noconfirm", pkg],
                    check=False,
                )
                if r.returncode != 0:
                    failed.append(pkg)
            if failed:
                warn(f"Failed to install: {', '.join(failed)}")
            else:
                ok(f"{len(aur_packages)} AUR packages installed")
        else:
            ok(f"{len(aur_packages)} AUR packages installed")
    else:
        warn(f"AUR file not found: {aur_file}")


# ── Step 3: Clone repository ────────────────────────────────────────────────────────
def step_clone_repo() -> None:
    header("Step 3: Clone repository")

    info(f"Cloning {REPO_URL} (branch {REPO_BRANCH})...")
    run(["git", "clone", "--branch", REPO_BRANCH, REPO_URL, str(INSTALL_DIR)])
    ok(f"Repository cloned to {INSTALL_DIR}")


# ── Step 5: Copy configs ────────────────────────────────────────────────────────────
def step_copy_configs() -> None:
    header("Step 5: Copy configs")

    # .config directories
    src_config = INSTALL_DIR / ".config"
    if src_config.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for item in src_config.iterdir():
            dst = CONFIG_DIR / item.name
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            shutil.copytree(item, dst) if item.is_dir() else shutil.copy2(item, dst)
        ok(".config/ copied")

    # Files from repository root
    for name in [".zshrc", ".bashrc", ".dir_colors", ".inputrc"]:
        src = INSTALL_DIR / name
        if src.exists():
            shutil.copy2(src, HOME / name)
            ok(name)


# ── Step 6: Copy wallpapers ─────────────────────────────────────────────────────────
def step_copy_wallpapers() -> None:
    header("Step 6: Wallpapers")

    src_wallpapers = INSTALL_DIR / "Pictures" / "Wallpapers"
    if not src_wallpapers.exists():
        warn("Wallpaper directory not found in repository")
        return

    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for wp in src_wallpapers.iterdir():
        if wp.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            shutil.copy2(wp, PICTURES_DIR / wp.name)
            count += 1
    ok(f"{count} wallpapers copied → ~/Pictures/Wallpapers/")


# ── Step 7: Setup Voxtype ───────────────────────────────────────────────────────────
def step_setup_voxtype() -> None:
    header("Step 7: Voxtype (voice input)")

    if not command_exists("voxtype"):
        warn("voxtype is not installed. Skipping setup.")
        info("Install manually: yay -S voxtype")
        return

    ok("voxtype installed")
    VOXTYPE_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Check already downloaded models
    existing_models = list(VOXTYPE_MODELS_DIR.glob("ggml-*.bin"))
    if existing_models:
        ok(f"Models found: {len(existing_models)}")
        for m in existing_models:
            info(f"  {m.name} ({m.stat().st_size // (1024*1024)} MB)")
        download = ask("Download an additional model? [y/N]", "N").lower() == "y"
    else:
        info("No Whisper models found")
        download = True

    if download:
        model_choices = list(VOXTYPE_MODELS.items())
        idx = choose(
            "Select a model to download:",
            [(name, f"{info_['size']} — {info_['desc']}") for name, info_ in model_choices],
        )
        model_name, model_info = model_choices[idx]
        model_path = VOXTYPE_MODELS_DIR / model_info["file"]

        if model_path.exists():
            ok(f"Model already downloaded: {model_info['file']}")
        else:
            print(f"\n  {YELLOW}Downloading {model_info['file']} ({model_info['size']})...{RESET}")
            print(f"  URL: {model_info['url']}\n")

            try:
                # Download with progress
                def show_progress(count, block_size, total_size):
                    if total_size > 0:
                        percent = min(count * block_size * 100 // total_size, 100)
                        mb_done = count * block_size // (1024 * 1024)
                        mb_total = total_size // (1024 * 1024)
                        print(f"\r  Downloaded: {mb_done}/{mb_total} MB ({percent}%)   ", end="", flush=True)

                urllib.request.urlretrieve(model_info["url"], model_path, show_progress)
                print()
                ok(f"Model downloaded: {model_info['file']}")
            except Exception as e:
                error(f"Download error: {e}")
                info(f"Download manually:\n    wget -O {model_path} {model_info['url']}")

        # Update config.toml with the selected model
        voxtype_config = CONFIG_DIR / "voxtype" / "config.toml"
        if voxtype_config.exists():
            config_text = voxtype_config.read_text()
            config_text = re.sub(
                r'^model\s*=\s*"[^"]*"',
                f'model = "{model_name}"',
                config_text,
                flags=re.MULTILINE,
            )
            voxtype_config.write_text(config_text)
            ok(f"config.toml updated: model = \"{model_name}\"")

    # Enable systemd service
    result = run(
        ["systemctl", "--user", "enable", "--now", "voxtype"],
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        ok("systemctl --user enable --now voxtype")
    else:
        warn("Could not automatically enable voxtype service")
        info("Start manually: systemctl --user enable --now voxtype")

    print(f"\n  {CYAN}Voxtype settings:{RESET}")
    info("Hotkey: ScrollLock (push-to-talk)")
    info("Models stored in: ~/.local/share/voxtype/models/")
    info("Config: ~/.config/voxtype/config.toml")


# ── Step 8: Setup SSH for GitHub ────────────────────────────────────────────────────
def step_setup_ssh() -> None:
    header("Step 8: SSH for GitHub")

    ssh_key = HOME / ".ssh" / "id_ed25519"
    pub_key = HOME / ".ssh" / "id_ed25519.pub"

    if ssh_key.exists():
        ok("SSH key already exists: ~/.ssh/id_ed25519")
    else:
        email = ask("Enter your GitHub email for the SSH key")
        if not email:
            warn("No email entered. Skipping SSH key generation.")
            return

        (HOME / ".ssh").mkdir(mode=0o700, exist_ok=True)
        run([
            "ssh-keygen", "-t", "ed25519",
            "-C", email,
            "-f", str(ssh_key),
            "-N", "",
        ])
        ok("SSH key generated")

    # Show public key
    if pub_key.exists():
        pub_key_content = pub_key.read_text().strip()
        print(f"\n  {YELLOW}Your public SSH key:{RESET}")
        print(f"\n  {CYAN}{pub_key_content}{RESET}\n")
        print(f"  {YELLOW}Add it to GitHub:{RESET}")
        print(f"  {CYAN}https://github.com/settings/keys{RESET}\n")

        input(f"  {YELLOW}Press Enter after adding the key to GitHub...{RESET} ")

        # Test connection
        result = run(
            ["ssh", "-T", "-o", "StrictHostKeyChecking=accept-new", "git@github.com"],
            check=False,
            capture_output=True,
            text=True,
        )
        # ssh -T returns code 1 but with a success message
        if "successfully authenticated" in result.stderr:
            ok("SSH connection to GitHub works!")
        else:
            warn("Could not verify SSH connection")
            info("Check manually: ssh -T git@github.com")


# ── Step 9: Setup Zsh ───────────────────────────────────────────────────────────────
def step_setup_zsh() -> None:
    header("Step 9: Setup Zsh")

    upgrade_zsh = INSTALL_DIR / "upgrade_zsh.py"
    if not upgrade_zsh.exists():
        warn("upgrade_zsh.py not found in repository")
        return

    info("Running upgrade_zsh.py to set up Oh My Zsh and plugins...")
    result = run(["python3", str(upgrade_zsh)], check=False)
    if result.returncode == 0:
        ok("Zsh configured")
    else:
        warn("upgrade_zsh.py finished with an error. Check zsh manually.")


# ── Step 11: Finish ─────────────────────────────────────────────────────────────────
def step_finish() -> None:
    header("Installation complete!")

    print(f"""
{GREEN}{BOLD}╔══════════════════════════════════════════════════╗
║         Dotfiles successfully installed!          ║
╚══════════════════════════════════════════════════╝{RESET}

{CYAN}What was installed:{RESET}
  ✓ Hyprland, Waybar, Rofi, Alacritty, Dunst
  ✓ Configs in ~/.config/
  ✓ Wallpapers in ~/Pictures/Wallpapers/
  ✓ Voxtype (voice input)
  ✓ Zsh + Oh My Zsh

{YELLOW}What to do manually:{RESET}
  • Enable SDDM: sudo systemctl enable sddm
  • Reboot or launch Hyprland: Hyprland
  • Configure monitors in ~/.config/hypr/config/system/monitors.conf
  • Configure keybindings in ~/.config/hypr/config/binds/main.conf

{CYAN}Wallpaper switching:{RESET}
  • Random: Super+W (configured in Hyprland binds)
  • Directory: ~/Pictures/Wallpapers/

{CYAN}Voice input:{RESET}
  • Hold ScrollLock to record voice
  • Text will be typed at the cursor position
""")


# ── Entry point ─────────────────────────────────────────────────────────────────────
def main() -> None:
    banner()

    print(f"  {YELLOW}This will install the dotfiles rice from https://github.com/redmoondz/dotfiles{RESET}")
    confirm = ask("Continue installation? [Y/n]", "Y").lower()
    if confirm not in ("y", "yes", ""):
        print("  Installation cancelled.")
        sys.exit(0)

    try:
        step_check()          # Step 0
        step_install_yay()     # Step 1
        install_type = step_choose_install_type()  # Step 2
        step_clone_repo()      # Step 3
        step_install_packages(install_type)  # Step 4
        step_copy_configs()    # Step 5
        step_copy_wallpapers() # Step 6
        step_setup_voxtype()   # Step 7
        step_setup_ssh()       # Step 8
        step_setup_zsh()       # Step 9
        step_finish()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Installation interrupted by user.{RESET}\n")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        error(f"Command failed: {e.cmd}")
        error(f"Exit code: {e.returncode}")
        sys.exit(1)
    finally:
        # Clean up temporary files
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
