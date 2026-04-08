#!/bin/bash
# wallpaper-colors.sh — extract accent colors from wallpaper → themes/palette.css
#
# Usage: wallpaper-colors.sh [wallpaper_path]
#   wallpaper_path defaults to reading from ~/.config/hypr/current_wallpaper
#
# Possible backends (pick one):
#   matugen  — Material You palette (rust)
#   pywal    — 16-color palette (python), `wal -i <image>`
#   colorthief — dominant N colors (python)
#
# Output: overwrites ~/.config/waybar/themes/palette.css with new --color-* values,
#         then restarts waybar.

PALETTE="$HOME/.config/waybar/themes/palette.css"
WALLPAPER="${1:-$(cat ~/.config/hypr/current_wallpaper 2>/dev/null)}"

if [[ -z "$WALLPAPER" || ! -f "$WALLPAPER" ]]; then
    echo "Error: wallpaper not found: '$WALLPAPER'" >&2
    exit 1
fi

# TODO: implement color extraction and write to $PALETTE
echo "Not implemented yet" >&2
exit 1
