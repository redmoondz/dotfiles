# Hyprland Configuration Structure

This configuration follows best practices for modular Hyprland ricing setups.

## 📁 Directory Structure

```
~/.config/hypr/
├── hyprland.conf              # Main entry point (sources all other configs)
├── hyprland.conf.backup       # Backup of original configuration
├── config/                    # Modular configuration files
│   ├── system/               # System-level configuration
│   │   ├── monitors.conf     # Monitor setup and positioning
│   │   ├── environment.conf  # Environment variables
│   │   └── autostart.conf    # Applications started with Hyprland
│   ├── input/                # Input device configuration
│   │   ├── keyboard.conf     # Keyboard layouts and settings
│   │   └── mouse.conf        # Mouse and touchpad settings
│   ├── visual/               # Visual appearance
│   │   ├── general.conf      # Gaps, borders, layout settings
│   │   ├── decoration.conf   # Rounding, blur, shadows, transparency
│   │   └── animations.conf   # Animation configurations
│   ├── layouts/              # Layout-specific settings
│   │   ├── dwindle.conf      # Dwindle layout configuration
│   │   └── master.conf       # Master layout configuration
│   ├── rules/                # Window and workspace rules
│   │   ├── window.conf       # Window rules for applications
│   │   └── workspace.conf    # Workspace assignment rules
│   └── binds/                # Keybind configurations
│       ├── main.conf         # Core window management binds
│       ├── media.conf        # Volume, brightness, media controls
│       ├── applications.conf # Application launchers
│       ├── workspaces.conf   # Workspace switching and movement
│       └── system.conf       # System commands (lock, logout, etc.)
├── scripts/                  # Utility scripts
│   ├── nogaps.sh            # Toggle gaps script
│   ├── random_wallpaper.sh  # Random wallpaper selector
│   └── reload.sh            # Reload Hyprland configuration
├── hypridle.conf            # Idle management configuration
├── hyprlock.conf            # Lock screen configuration
└── hyprpaper.conf           # Wallpaper configuration
```

## 🎯 Benefits of This Structure

### **Modularity**
- Each file focuses on a single aspect of configuration
- Easy to share specific parts with others
- Simplified troubleshooting and maintenance

### **Organization**
- Logical grouping by functionality
- Clear naming conventions
- Self-documenting structure

### **Maintainability**
- Changes isolated to relevant files
- Easier to track modifications
- Better version control support

### **Extensibility**
- Easy to add new configuration categories
- Simple to override specific settings
- Support for environment-specific configs

## 🚀 Usage

The main `hyprland.conf` file serves as the entry point and sources all other configuration files. You can:

1. **Edit specific aspects**: Modify only the relevant configuration file
2. **Override settings**: Create additional files and source them last
3. **Environment-specific configs**: Create variants for different setups
4. **Share configurations**: Share individual files or entire categories

## 🔧 Customization

### Adding New Keybinds
Add them to the appropriate file in `config/binds/`:
- Window management → `main.conf`
- Applications → `applications.conf`
- Media controls → `media.conf`
- System functions → `system.conf`

### Modifying Appearance
Edit files in `config/visual/`:
- Colors and borders → `general.conf`
- Window effects → `decoration.conf`
- Transitions → `animations.conf`

### Window Rules
Add application-specific rules to `config/rules/window.conf`

## 📋 Migration Notes

Your original configuration has been backed up as `hyprland.conf.backup`. The new structure maintains all your existing settings while organizing them logically.

## 🔗 References

- [Hyprland Wiki](https://wiki.hyprland.org/)
- [Configuration Guide](https://wiki.hyprland.org/Configuring/)
- [Example Configurations](https://wiki.hyprland.org/Configuring/Example-configurations/)
