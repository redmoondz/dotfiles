# Completions for waybar-theme command
# Copy this file to ~/.config/fish/completions/waybar-theme.fish

function __waybar_theme_complete
    set themes_dir "$HOME/.config/waybar/themes"
    for theme in $themes_dir/*.css
        if test -f $theme; and test (basename $theme) != "theme.css"
            basename $theme .css
        end
    end
end

complete -c waybar-theme -f -a "(__waybar_theme_complete)" -d "Available waybar themes"
