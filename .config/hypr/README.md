# Hyprland Configuration Structure

This configuration follows best practices for modular Hyprland ricing setups.

## 📁 Directory Structure

```
~/.config/hypr/
├── hyprland.conf           # Main entry point (sources all other configs)
├── hyprland.conf.backup    # Backup of original configuration
├── config/                 # Configuration files (flat structure)
│   ├── binds.conf          # Keybinds
│   ├── input.conf          # Input device settings
│   ├── layouts.conf        # Layout settings
│   ├── rules.conf          # Window/workspace rules
│   ├── system.conf         # System-level config
│   └── visual.conf         # Visual appearance
├── scripts/                # Utility scripts
│   ├── .last_wallpaper     # Last wallpaper used (state file)
│   ├── 80hz.sh             # 80Hz refresh script
│   ├── nogaps.sh           # Toggle gaps script
│   ├── random_wallpaper.sh # Random wallpaper selector
│   ├── reload.sh           # Reload Hyprland configuration
│   └── startup-wallpaper.sh# Set wallpaper on startup
├── hypridle.conf           # Idle management configuration
├── hyprlock.conf           # Lock screen configuration
└── hyprpaper.conf          # Wallpaper configuration
```

## 🎯 Benefits of This Structure

### **Modularity**
- Each file focuses on a single aspect of configuration
- Easy to share specific parts with others
- Simplified troubleshooting and maintenance

### **Organization**
- Flat config structure for simplicity
- Clear naming conventions
- Self-documenting structure

### **Maintainability**
- Changes isolated to relevant files
- Easier to track modifications
- Better version control support

### **Extensibility**
- Easy to add new configuration files
- Simple to override specific settings

## 🚀 Usage

The main `hyprland.conf` file serves as the entry point and sources all other configuration files. You can:

1. **Edit specific aspects**: Modify only the relevant configuration file
2. **Override settings**: Create additional files and source them last
3. **Environment-specific configs**: Create variants for different setups
4. **Share configurations**: Share individual files or entire categories

## 🔧 Customization

### Adding New Keybinds
Add them to `config/binds.conf`.

### Modifying Appearance
Edit `config/visual.conf` for visual settings.

### Window Rules
Add rules to `config/rules.conf`.

## 📋 Migration Notes

Your original configuration has been backed up as `hyprland.conf.backup`. The new structure maintains all your existing settings while organizing them logically.

## 🔗 References

- [Hyprland Wiki](https://wiki.hyprland.org/)
- [Configuration Guide](https://wiki.hyprland.org/Configuring/)
- [Example Configurations](https://wiki.hyprland.org/Configuring/Example-configurations/)
