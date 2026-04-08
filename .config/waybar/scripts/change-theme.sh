#!/bin/bash
# Waybar theme switcher — copies a preset to themes/palette.css and restarts waybar
# Usage: change-theme.sh [theme-name]

THEMES_DIR="$HOME/.config/waybar/themes"
PALETTE="$THEMES_DIR/palette.css"

list_themes() {
    for theme in "$THEMES_DIR"/*.css; do
        local name
        name="$(basename "$theme" .css)"
        if [[ "$name" != "palette" ]]; then
            echo "$name"
        fi
    done
}

set_theme() {
    local theme_path="$THEMES_DIR/$1.css"

    if [[ ! -f "$theme_path" ]]; then
        echo "Theme '$1' not found. Available:"
        list_themes
        return 1
    fi

    cp "$theme_path" "$PALETTE"

    local rofi_theme="$HOME/.config/rofi/colors/$1.rasi"
    local rofi_palette="$HOME/.config/rofi/colors/palette.rasi"
    if [[ -f "$rofi_theme" ]]; then
        cp "$rofi_theme" "$rofi_palette"
    fi

    local alacritty_theme="$HOME/.config/alacritty/themes/$1.toml"
    local alacritty_palette="$HOME/.config/alacritty/palette.toml"
    if [[ -f "$alacritty_theme" ]]; then
        cp "$alacritty_theme" "$alacritty_palette"
    fi

    if pgrep -x "waybar" > /dev/null; then
        pkill waybar
        sleep 0.5
        waybar &
    fi
}

if [[ $# -eq 0 ]]; then
    echo "Usage: $(basename "$0") <theme-name>"
    echo ""
    echo "Available themes:"
    list_themes
    exit 0
fi

set_theme "$1"
