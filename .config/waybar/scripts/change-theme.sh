#!/bin/bash

# Waybar Theme Changer Script
# Usage: change-theme.sh [theme-name]

WAYBAR_CONFIG_DIR="$HOME/.config/waybar"
THEMES_DIR="$WAYBAR_CONFIG_DIR/themes"
THEME_FILE="$THEMES_DIR/theme.css"

# Function to list available themes
list_themes() {
    echo "Доступные темы:"
    echo "==============="
    for theme in "$THEMES_DIR"/*.css; do
        if [[ -f "$theme" && "$(basename "$theme")" != "theme.css" ]]; then
            basename "$theme" .css
        fi
    done
}

# Function to set theme
set_theme() {
    local theme_name="$1"
    local theme_path="$THEMES_DIR/$theme_name.css"
    
    if [[ ! -f "$theme_path" ]]; then
        echo "❌ Тема '$theme_name' не найдена!"
        echo ""
        list_themes
        return 1
    fi
    
    # Copy the selected theme to theme.css
    cp "$theme_path" "$THEME_FILE"
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Тема '$theme_name' успешно применена!"
        
        # Restart waybar if it's running
        if pgrep -x "waybar" > /dev/null; then
            echo "🔄 Перезапуск Waybar..."
            pkill waybar
            sleep 1
            waybar &
            echo "✨ Waybar перезапущен с новой темой!"
        else
            echo "ℹ️  Waybar не запущен. Запустите его для применения темы."
        fi
    else
        echo "❌ Ошибка при применении темы!"
        return 1
    fi
}

# Main script logic
if [[ $# -eq 0 ]]; then
    echo "🎨 Скрипт смены тем Waybar"
    echo "=========================="
    echo ""
    echo "Использование: $(basename "$0") [имя-темы]"
    echo ""
    list_themes
    exit 0
fi

theme_name="$1"
set_theme "$theme_name"
