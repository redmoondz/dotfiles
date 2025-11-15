#!/bin/bash
WALLPAPER_DIR="$HOME/Pictures/Wallpaper"
LAST_WALLPAPER="$HOME/.config/hypr/scripts/.last_wallpaper"
HYPRPAPER_CONF="$HOME/.config/hypr/hyprpaper.conf"

# Create wallpaper dir if not exists
mkdir -p "$WALLPAPER_DIR"

# Get all image files
mapfile -t files < <(find "$WALLPAPER_DIR" -type f \( -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" -o -iname "*.bmp" -o -iname "*.webp" \))

if [ ${#files[@]} -eq 0 ]; then
    notify-send "No wallpapers found in $WALLPAPER_DIR"
    exit 1
fi

# Read last wallpaper
if [ -f "$LAST_WALLPAPER" ]; then
    last=$(cat "$LAST_WALLPAPER")
else
    last=""
fi

# Filter out last wallpaper
filtered=()
for f in "${files[@]}"; do
    if [[ "$f" != "$last" ]]; then
        filtered+=("$f")
    fi
done

# If only one wallpaper, use it
if [ ${#filtered[@]} -eq 0 ]; then
    filtered=("${files[@]}")
fi

# Pick random wallpaper
RANDOM_INDEX=$((RANDOM % ${#filtered[@]}))
new_wallpaper="${filtered[$RANDOM_INDEX]}"

# Set wallpaper (using hyprpaper and hyprland)
hyprctl hyprpaper preload "$new_wallpaper"
hyprctl hyprpaper wallpaper ",$new_wallpaper"

# Save last wallpaper
echo "$new_wallpaper" > "$LAST_WALLPAPER"

# Update hyprpaper.conf to persist the choice after reboot
sed -i "s|^preload = .*|preload = $new_wallpaper|" "$HYPRPAPER_CONF"
sed -i "s|^wallpaper = ,.*|wallpaper = ,$new_wallpaper|" "$HYPRPAPER_CONF"

# Send notification
wallpaper_name=$(basename "$new_wallpaper")
notify-send "Wallpaper Changed" "Set to: $wallpaper_name" -i "$new_wallpaper"
