# Waybar Theme Changer

Скрипт для быстрой смены тем Waybar из терминала с поддержкой автодополнения в Fish shell.

## Установка

Скрипт уже установлен и настроен. Для применения изменений перезагрузите Fish shell:

```bash
source ~/.config/fish/config.fish
```

## Использование

### Доступные команды:

1. **Показать все доступные темы:**
   ```bash
   waybar-theme
   # или короткий алиас:
   wbt
   ```

2. **Применить конкретную тему:**
   ```bash
   waybar-theme Catppuccin-Mocha
   # или с коротким алиасом:
   wbt Tokyo-Night
   ```

3. **Автодополнение:** Нажмите Tab после ввода команды для показа доступных тем

### Доступные темы:
- Catppuccin-Latte
- Catppuccin-Mocha  
- Cyberpunk-Edge
- Decay-Green
- Frosted-Glass
- Graphite-Mono
- Gruvbox-Retro
- Material-Sakura
- Rose-Pine
- Tokyo-Night
- Wall-Dcol

## Особенности

- ✅ Автоматическое применение темы
- ✅ Перезапуск Waybar если он запущен
- ✅ Автодополнение в Fish shell
- ✅ Проверка существования темы
- ✅ Удобные сообщения с эмодзи
- ✅ Короткий алиас `wbt`

## Файлы

- `/home/redmoon/.config/waybar/scripts/waybar-theme.fish` - основной скрипт
- `/home/redmoon/.config/waybar/scripts/change-theme.sh` - альтернативная bash версия
- `~/.config/fish/completions/waybar-theme.fish` - автодополнение
- `~/.config/fish/config.fish` - содержит алиасы

## Примеры использования

```bash
# Показать все темы
wbt

# Применить тему Catppuccin
wbt Catppuccin-Mocha

# Применить тему с автодополнением (нажмите Tab)
wbt <Tab>
```

Скрипт автоматически перезапустит Waybar если он запущен, или предложит запустить его вручную если он не активен.
