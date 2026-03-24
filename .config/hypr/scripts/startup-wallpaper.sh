#!/bin/bash
# Startup wallpaper script - loads last wallpaper on boot

WALLPAPER_DIR="$HOME/Pictures/Wallpaper"
LAST_WALLPAPER="$HOME/.config/hypr/scripts/.last_wallpaper"
HYPRPAPER_CONF="$HOME/.config/hypr/hyprpaper.conf"

# Wait for hyprpaper to start
sleep 2

# Check if last wallpaper file exists and contains a valid path
if [ -f "$LAST_WALLPAPER" ] && [ -s "$LAST_WALLPAPER" ]; then
    last_wallpaper=$(cat "$LAST_WALLPAPER")
    
    # Check if the wallpaper file still exists
    if [ -f "$last_wallpaper" ]; then
        # Set the last used wallpaper
        hyprctl hyprpaper preload "$last_wallpaper"
        hyprctl hyprpaper wallpaper ",$last_wallpaper"
        
        # Update hyprpaper.conf to persist the choice
        sed -i "s|^preload = .*|preload = $last_wallpaper|" "$HYPRPAPER_CONF"
        sed -i "s|^wallpaper = ,.*|wallpaper = ,$last_wallpaper|" "$HYPRPAPER_CONF"
        
        exit 0
    fi
fi

# If no last wallpaper or file doesn't exist, set a random one
if [ -x "$HOME/.config/hypr/scripts/random_wallpaper.sh" ]; then
    "$HOME/.config/hypr/scripts/random_wallpaper.sh"
fi
