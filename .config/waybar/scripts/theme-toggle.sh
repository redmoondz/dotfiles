#!/bin/bash

toggle() {
    current=$(gsettings get org.gnome.desktop.interface color-scheme)
    if [[ "$current" == "'prefer-dark'" ]]; then
        gsettings set org.gnome.desktop.interface color-scheme "default"
    else
        gsettings set org.gnome.desktop.interface color-scheme "prefer-dark"
    fi
    pkill -SIGRTMIN+8 waybar
}

status() {
    current=$(gsettings get org.gnome.desktop.interface color-scheme)
    if [[ "$current" == "'prefer-dark'" ]]; then
        echo '{"text": "󰖙", "tooltip": "Switch to Light Mode", "class": "dark"}'
    else
        echo '{"text": "󰖔", "tooltip": "Switch to Dark Mode", "class": "light"}'
    fi
}

case "$1" in
    --toggle) toggle ;;
    *) status ;;
esac
