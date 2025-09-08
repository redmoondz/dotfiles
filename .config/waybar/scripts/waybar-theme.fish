#!/usr/bin/env fish

# Waybar Theme Changer for Fish Shell
# Usage: waybar-theme [theme-name]

set WAYBAR_CONFIG_DIR "$HOME/.config/waybar"
set THEMES_DIR "$WAYBAR_CONFIG_DIR/themes"
set THEME_FILE "$THEMES_DIR/theme.css"

function list_themes
    echo "Доступные темы:"
    echo "==============="
    for theme in $THEMES_DIR/*.css
        if test -f $theme; and test (basename $theme) != "theme.css"
            basename $theme .css
        end
    end
end

function set_theme
    set theme_name $argv[1]
    set theme_path "$THEMES_DIR/$theme_name.css"
    
    if not test -f $theme_path
        echo "❌ Тема '$theme_name' не найдена!"
        echo ""
        list_themes
        return 1
    end
    
    # Copy the selected theme to theme.css
    cp $theme_path $THEME_FILE
    
    if test $status -eq 0
        echo "✅ Тема '$theme_name' успешно применена!"
        
        # Restart waybar if it's running
        if pgrep -x "waybar" > /dev/null
            echo "🔄 Перезапуск Waybar..."
            pkill waybar
            sleep 1
            waybar &
            echo "✨ Waybar перезапущен с новой темой!"
        else
            echo "ℹ️  Waybar не запущен. Запустите его для применения темы."
        end
    else
        echo "❌ Ошибка при применении темы!"
        return 1
    end
end

# Main script logic
if test (count $argv) -eq 0
    echo "🎨 Скрипт смены тем Waybar"
    echo "=========================="
    echo ""
    echo "Использование: waybar-theme [имя-темы]"
    echo ""
    list_themes
    exit 0
end

set theme_name $argv[1]
set_theme $theme_name
