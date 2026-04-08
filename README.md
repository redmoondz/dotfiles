# dotfiles

[![Hyprland](https://img.shields.io/badge/Hyprland-abd6fd?style=for-the-badge "Hyprland - A dynamic tiling Wayland compositor based on wlroots that doesn't sacrifice on its looks")](https://hyprland.org/)
[![Waybar](https://img.shields.io/badge/Waybar-cdd6f4?style=for-the-badge "Waybar - Highly customizable Wayland bar for Sway and Wlroots based compositors")](https://github.com/Alexays/Waybar)
[![Hyprlock](https://img.shields.io/badge/Hyprlock-89dceb?style=for-the-badge "Hyprlock - Hyprland's GPU-accelerated screen locking utility")](https://github.com/hyprwm/hyprlock)
[![Alacritty](https://img.shields.io/badge/Alacritty-cba6f7?style=for-the-badge "Alacritty - A fast, cross-platform, OpenGL terminal emulator")](https://github.com/alacritty/alacritty)
[![Rofi](https://img.shields.io/badge/Rofi-fab387?style=for-the-badge "Rofi- A window switcher, application launcher and dmenu replacement")](https://github.com/lbonn/rofi)
[![Cliphist](https://img.shields.io/badge/Cliphist-cdd6f4?style=for-the-badge "Cliphist - Wayland clipboard manager")](https://github.com/sentriz/cliphist)
[![Zathura](https://img.shields.io/badge/Zathura-94e2d5?style=for-the-badge "Zathura is a highly customizable and functional document viewer")](https://github.com/pwmt/zathura)
[![Swaylock](https://img.shields.io/badge/Swaylock-f9e2af?style=for-the-badge "Swaylock - Screen locking utility for Wayland compositors")](https://github.com/mortie/swaylock-effects)
[![Dunst](https://img.shields.io/badge/Dunst-fab387?style=for-the-badge "Dunst - Lightweight and customizable notification daemon")](https://github.com/dunst-project/dunst)
[![Voxtype](https://img.shields.io/badge/Voxtype-cba6f7?style=for-the-badge "Voxtype - Push-to-talk voice typing")](https://voxtype.io/)

## Installation

### One-command install

```bash
curl -sL https://raw.githubusercontent.com/redmoondz/dotfiles/main/install.py \
     -o /tmp/install.py && python3 /tmp/install.py
```

The installer will:
1. Install `yay` (AUR helper) if needed
2. Let you choose **Minimal** (~35 packages) or **Full** install
3. Install all packages with `--noconfirm`
4. Copy configs to `~/.config/`
5. Copy wallpapers to `~/Pictures/Wallpapers/`
6. Set up **Voxtype** voice typing (with model download)
7. Configure **SSH** for GitHub (semi-automatic)
8. Set up **Zsh** with Oh My Zsh and plugins

### Advanced installation (manual)

<details>
<summary>Manual step-by-step</summary>

Clone the repository:
```bash
git clone https://github.com/redmoondz/dotfiles.git ~/dotfiles
```

Install required packages:
```bash
sudo pacman -S --needed hyprland hyprpaper hypridle hyprlock waybar konsole alacritty \
    dunst libnotify fastfetch pamixer bash-completion cliphist slurp grim \
    ttf-firacode-nerd ttf-jetbrains-mono-nerd noto-fonts-emoji \
    github-cli libmtp gvfs-mtp android-tools ntfs-3g git curl base-devel zsh

yay -S --needed swaylock-effects-git rofi-lbonn-wayland-git rofi-emoji-git \
    brillo hyprpicker-git voxtype
```

Copy configs:
```bash
cp -r ~/dotfiles/.config/* ~/.config/
cp ~/dotfiles/.zshrc ~/
mkdir -p ~/Pictures/Wallpapers
cp ~/dotfiles/Pictures/Wallpapers/*.jpg ~/Pictures/Wallpapers/
```

Checkout the `main` branch and adjust Hyprland keybindings in `.config/hypr/config/binds/`.

</details>

## Voice typing (Voxtype)

Push-to-talk voice input using local Whisper AI — works offline.

- **Hotkey:** `ScrollLock` (hold to record, release to transcribe)
- **Languages:** English + Russian (large-v3-turbo model)
- **Output:** Types text directly at cursor position
- **Config:** `~/.config/voxtype/config.toml`

The `install.py` script handles model download and service setup automatically.

Manual service control:
```bash
systemctl --user enable --now voxtype   # start and enable on login
systemctl --user status voxtype         # check status
```

## Syncing configs (for development)

To update the repository with your latest system configs:

```bash
python3 sync_configs.py              # sync and push to GitHub
python3 sync_configs.py --dry-run    # preview what will be synced
python3 sync_configs.py --no-push    # sync without pushing
```

## Preview
[preview](https://github.com/sameemul-haque/dotfiles/assets/110324374/3f3ad231-ba5c-42fc-9d01-6466e4550158 "dotfiles preview")

<!-- ![preview1-old-neofetch](https://github.com/sameemul-haque/dotfiles/assets/110324374/0250fcdc-dd46-4e53-9855-6630b02950fe) -->

| ![waybar.jpg](./assets/waybar.jpg) |
| :-------------------------------: |
| _waybar.jpg_ |

| ![waybar-nvim-rofi-alacritty.jpg](./assets/waybar-nvim-rofi-alacritty.jpg) |
| :-----------------------------------------------: |
| _waybar nvim rofi alacritty.jpg_ |

| ![floating-spotify-alacritty.jpg](./assets/floating-spotify-alacritty.jpg) |
| :------------------------------------------: |
| _Floating spotify alacritty.jpg_ |



## Dotfiles are available for the following:
| HYPRLAND | WAYBAR | ROFI | DUNST | HYPRLOCK | SWAYLOCK | ZATHURA | ALACRITTY | KONSOLE | NEOVIM | FASTFETCH | VOXTYPE |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Star History
<picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=redmoondz/dotfiles&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=redmoondz/dotfiles&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=redmoondz/dotfiles&type=Date" />
</picture>
