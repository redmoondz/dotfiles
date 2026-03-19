#!/bin/bash
# Script to cycle through Waybar themes

THEMES_DIR="$HOME/.config/waybar/themes"
SCRIPT="$HOME/.config/waybar/scripts/change-theme.sh"


# Получить имена тем без расширения .css
mapfile -t themes < <(for f in "$THEMES_DIR"/*.css; do bn="$(basename "$f" .css)"; if [[ "$bn" != "theme" ]]; then echo "$bn"; fi; done | sort)

# File to store the current theme index
STATE_FILE="$HOME/.cache/waybar_theme_index"

# Read the current index or start at 0
if [[ -f "$STATE_FILE" ]]; then
    idx=$(cat "$STATE_FILE")
else
    idx=0
fi

# Increment index and wrap around
idx=$(( (idx + 1) % ${#themes[@]} ))

# Save new index
printf "%d" "$idx" > "$STATE_FILE"

# Change theme
"$SCRIPT" "${themes[$idx]}"
