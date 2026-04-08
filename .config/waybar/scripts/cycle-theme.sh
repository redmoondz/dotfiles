#!/bin/bash
# Cycle through waybar theme presets

THEMES_DIR="$HOME/.config/waybar/themes"
SCRIPT="$HOME/.config/waybar/scripts/change-theme.sh"
STATE_FILE="$HOME/.cache/waybar_theme_index"

mapfile -t themes < <(
    for f in "$THEMES_DIR"/*.css; do
        name="$(basename "$f" .css)"
        if [[ "$name" != "palette" ]]; then
            echo "$name"
        fi
    done | sort
)

idx=0
[[ -f "$STATE_FILE" ]] && idx=$(cat "$STATE_FILE")

idx=$(( (idx + 1) % ${#themes[@]} ))
printf "%d" "$idx" > "$STATE_FILE"

"$SCRIPT" "${themes[$idx]}"
