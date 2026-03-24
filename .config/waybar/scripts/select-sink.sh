#!/usr/bin/env bash

# Build associative array: description -> sink name
declare -A sink_map
current_name=""

while IFS= read -r line; do
    if [[ "$line" =~ ^Sink\ #[0-9]+ ]]; then
        current_name=""
    elif [[ "$line" =~ ^[[:space:]]+Name:[[:space:]](.+)$ ]]; then
        current_name="${BASH_REMATCH[1]}"
    elif [[ "$line" =~ ^[[:space:]]+device\.description[[:space:]]*=[[:space:]]*\"(.+)\"$ ]]; then
        sink_map["${BASH_REMATCH[1]}"]="$current_name"
    fi
done < <(pactl list sinks)

# Show dropdown at top-right, just below the waybar (24px height + 5px margin-top = 29px)
chosen=$(printf '%s\n' "${!sink_map[@]}" | rofi -dmenu \
    -location 3 \
    -yoffset 29 \
    -xoffset -320 \
    -theme-str 'window { width: 220px; background-color: #262626; border: 1px; border-color: #a6a6a6; border-radius: 7px; } inputbar { enabled: false; } listview { lines: 8; scrollbar: false; padding: 4px; } element { padding: 5px 10px; background-color: transparent; text-color: #d9d9d9; border-radius: 5px; } element selected.normal { background-color: #a6a6a6; text-color: #262626; } element normal.normal { background-color: transparent; text-color: #d9d9d9; } element alternate.normal { background-color: transparent; text-color: #d9d9d9; }' \
    -p "")

[[ -z "$chosen" ]] && exit 0

sink="${sink_map[$chosen]}"
pactl set-default-sink "$sink"

# Move all active audio streams to the new sink
pactl list sink-inputs short | awk '{print $1}' | while read -r id; do
    pactl move-sink-input "$id" "$sink"
done
