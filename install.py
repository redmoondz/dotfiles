#!/usr/bin/env python3
"""
install.py — установщик dotfiles redmoondz одной командой.

Запуск:
    curl -sL https://raw.githubusercontent.com/redmoondz/dotfiles/main/install.py \
         -o /tmp/install.py && python3 /tmp/install.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# ── Константы ─────────────────────────────────────────────────────────────────
REPO_URL = "https://github.com/redmoondz/dotfiles.git"
REPO_BRANCH = "main"
INSTALL_DIR = Path(tempfile.mkdtemp()) / "dotfiles"

HOME = Path.home()
CONFIG_DIR = HOME / ".config"
PICTURES_DIR = HOME / "Pictures" / "Wallpapers"

VOXTYPE_MODELS_DIR = HOME / ".local" / "share" / "voxtype" / "models"
VOXTYPE_MODELS = {
    "large-v3-turbo": {
        "file": "ggml-large-v3-turbo.bin",
        "size": "~1.6 GB",
        "desc": "Многоязычная (EN+RU), высокое качество — как в текущей конфигурации",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin",
    },
    "base.en": {
        "file": "ggml-base.en.bin",
        "size": "~141 MB",
        "desc": "Только английский, быстрая загрузка",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
    },
}

# ── Цвета ─────────────────────────────────────────────────────────────────────
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"


# ── Вспомогательные функции ───────────────────────────────────────────────────
def banner() -> None:
    print(f"""
{GREEN}{BOLD}
  ██████╗  ██████╗ ████████╗███████╗██╗██╗     ███████╗███████╗
  ██╔══██╗██╔═══██╗╚══██╔══╝██╔════╝██║██║     ██╔════╝██╔════╝
  ██║  ██║██║   ██║   ██║   █████╗  ██║██║     █████╗  ███████╗
  ██║  ██║██║   ██║   ██║   ██╔══╝  ██║██║     ██╔══╝  ╚════██║
  ██████╔╝╚██████╔╝   ██║   ██║     ██║███████╗███████╗███████║
  ╚═════╝  ╚═════╝    ╚═╝   ╚═╝     ╚═╝╚══════╝╚══════╝╚══════╝
{RESET}
  {CYAN}Hyprland rice installer by redmoondz{RESET}
  {CYAN}https://github.com/redmoondz/dotfiles{RESET}
""")


def info(msg: str) -> None:
    print(f"  {CYAN}→{RESET} {msg}")


def ok(msg: str) -> None:
    print(f"  {GREEN}✓{RESET} {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}⚠{RESET} {msg}")


def error(msg: str) -> None:
    print(f"  {RED}✗{RESET} {msg}", file=sys.stderr)


def header(title: str) -> None:
    print(f"\n{BOLD}{CYAN}━━━ {title} ━━━{RESET}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {YELLOW}?{RESET} {prompt}{suffix}: ").strip()
        return answer if answer else default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def choose(prompt: str, options: list[tuple[str, str]]) -> int:
    """Показать меню выбора, вернуть индекс выбранного (0-based)."""
    print(f"\n  {YELLOW}?{RESET} {prompt}\n")
    for i, (label, desc) in enumerate(options, 1):
        print(f"    {CYAN}[{i}]{RESET} {label}")
        if desc:
            print(f"        {desc}")
    while True:
        try:
            answer = input(f"\n  Выбор [1-{len(options)}]: ").strip()
            idx = int(answer) - 1
            if 0 <= idx < len(options):
                return idx
        except (ValueError, EOFError, KeyboardInterrupt):
            pass
        print(f"  {RED}Введите число от 1 до {len(options)}{RESET}")


def run(cmd: list[str], check: bool = True, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, **kwargs)


def run_sudo(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return run(["sudo"] + cmd, check=check)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


# ── Шаг 0: Проверки ───────────────────────────────────────────────────────────
def step_check() -> None:
    header("Шаг 0: Проверки окружения")

    # Arch Linux
    if not Path("/etc/arch-release").exists():
        error("Это не Arch Linux. Установщик поддерживает только Arch Linux.")
        sys.exit(1)
    ok("Arch Linux обнаружен")

    # Python версия
    if sys.version_info < (3, 8):
        error(f"Требуется Python 3.8+, обнаружен {sys.version}")
        sys.exit(1)
    ok(f"Python {sys.version_info.major}.{sys.version_info.minor}")

    # Права (не root)
    if os.geteuid() == 0:
        error("Не запускайте установщик от имени root. Используйте обычного пользователя.")
        sys.exit(1)
    ok(f"Пользователь: {os.environ.get('USER', 'unknown')}")


# ── Шаг 1: Установка yay ──────────────────────────────────────────────────────
def step_install_yay() -> None:
    header("Шаг 1: AUR helper (yay)")

    if command_exists("yay"):
        ok("yay уже установлен")
        return

    info("Устанавливаю yay...")
    run_sudo(["pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"])

    yay_dir = Path(tempfile.mkdtemp()) / "yay-install"
    run(["git", "clone", "https://aur.archlinux.org/yay.git", str(yay_dir)])
    run(["makepkg", "-si", "--noconfirm"], cwd=yay_dir)
    ok("yay установлен")


# ── Шаг 2: Выбор типа установки ──────────────────────────────────────────────
def step_choose_install_type() -> str:
    header("Шаг 2: Тип установки")

    choice = choose(
        "Выберите набор пакетов для установки:",
        [
            ("Minimal", "Только пакеты для rice (~35 пакетов: Hyprland, Waybar, Rofi и т.д.)"),
            ("Full", "Все пакеты с исходной системы (~230+ пакетов)"),
        ],
    )
    install_type = "minimal" if choice == 0 else "full"
    ok(f"Выбрано: {install_type}")
    return install_type


# ── Шаг 3-4: Установка пакетов ────────────────────────────────────────────────
def step_install_packages(install_type: str) -> None:
    header(f"Шаг 3-4: Установка пакетов ({install_type})")

    pacman_file = INSTALL_DIR / "packages" / f"{install_type}_pacman.txt"
    aur_file = INSTALL_DIR / "packages" / f"{install_type}_aur.txt"

    # Pacman пакеты
    if pacman_file.exists():
        packages = [p.strip() for p in pacman_file.read_text().splitlines() if p.strip()]
        info(f"Устанавливаю {len(packages)} пакетов через pacman...")
        run_sudo(["pacman", "-S", "--needed", "--noconfirm"] + packages)
        ok(f"{len(packages)} pacman пакетов установлено")
    else:
        warn(f"Файл пакетов не найден: {pacman_file}")

    # AUR пакеты
    if aur_file.exists():
        aur_packages = [p.strip() for p in aur_file.read_text().splitlines() if p.strip()]
        info(f"Устанавливаю {len(aur_packages)} AUR пакетов через yay...")
        run(["yay", "-S", "--needed", "--noconfirm"] + aur_packages)
        ok(f"{len(aur_packages)} AUR пакетов установлено")
    else:
        warn(f"AUR файл не найден: {aur_file}")


# ── Шаг 5: Клонирование репозитория ──────────────────────────────────────────
def step_clone_repo() -> None:
    header("Шаг 5: Клонирование репозитория")

    info(f"Клонирую {REPO_URL} (ветка {REPO_BRANCH})...")
    run(["git", "clone", "--branch", REPO_BRANCH, REPO_URL, str(INSTALL_DIR)])
    ok(f"Репозиторий скачан в {INSTALL_DIR}")


# ── Шаг 6: Копирование конфигов ───────────────────────────────────────────────
def step_copy_configs() -> None:
    header("Шаг 6: Копирование конфигов")

    # .config директории
    src_config = INSTALL_DIR / ".config"
    if src_config.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        for item in src_config.iterdir():
            dst = CONFIG_DIR / item.name
            if dst.exists():
                if dst.is_dir():
                    shutil.rmtree(dst)
                else:
                    dst.unlink()
            shutil.copytree(item, dst) if item.is_dir() else shutil.copy2(item, dst)
        ok(".config/ скопирован")

    # Файлы из корня репозитория
    for name in [".zshrc", ".bashrc", ".dir_colors", ".inputrc"]:
        src = INSTALL_DIR / name
        if src.exists():
            shutil.copy2(src, HOME / name)
            ok(name)


# ── Шаг 7: Копирование обоев ──────────────────────────────────────────────────
def step_copy_wallpapers() -> None:
    header("Шаг 7: Обои")

    src_wallpapers = INSTALL_DIR / "Pictures" / "Wallpapers"
    if not src_wallpapers.exists():
        warn("Каталог обоев не найден в репозитории")
        return

    PICTURES_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for wp in src_wallpapers.iterdir():
        if wp.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            shutil.copy2(wp, PICTURES_DIR / wp.name)
            count += 1
    ok(f"{count} обоев скопировано → ~/Pictures/Wallpapers/")


# ── Шаг 8: Настройка Voxtype ──────────────────────────────────────────────────
def step_setup_voxtype() -> None:
    header("Шаг 8: Voxtype (голосовой ввод)")

    if not command_exists("voxtype"):
        warn("voxtype не установлен. Пропускаю настройку.")
        info("Установите вручную: yay -S voxtype")
        return

    ok("voxtype установлен")
    VOXTYPE_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # Проверить уже загруженные модели
    existing_models = list(VOXTYPE_MODELS_DIR.glob("ggml-*.bin"))
    if existing_models:
        ok(f"Найдено моделей: {len(existing_models)}")
        for m in existing_models:
            info(f"  {m.name} ({m.stat().st_size // (1024*1024)} MB)")
        download = ask("Скачать дополнительную модель? [y/N]", "N").lower() == "y"
    else:
        info("Модели Whisper не найдены")
        download = True

    if download:
        model_choices = list(VOXTYPE_MODELS.items())
        idx = choose(
            "Выберите модель для скачивания:",
            [(name, f"{info_['size']} — {info_['desc']}") for name, info_ in model_choices],
        )
        model_name, model_info = model_choices[idx]
        model_path = VOXTYPE_MODELS_DIR / model_info["file"]

        if model_path.exists():
            ok(f"Модель уже скачана: {model_info['file']}")
        else:
            print(f"\n  {YELLOW}Скачивание {model_info['file']} ({model_info['size']})...{RESET}")
            print(f"  URL: {model_info['url']}\n")

            try:
                # Скачивание с прогрессом
                def show_progress(count, block_size, total_size):
                    if total_size > 0:
                        percent = min(count * block_size * 100 // total_size, 100)
                        mb_done = count * block_size // (1024 * 1024)
                        mb_total = total_size // (1024 * 1024)
                        print(f"\r  Скачано: {mb_done}/{mb_total} MB ({percent}%)   ", end="", flush=True)

                urllib.request.urlretrieve(model_info["url"], model_path, show_progress)
                print()
                ok(f"Модель скачана: {model_info['file']}")
            except Exception as e:
                error(f"Ошибка скачивания: {e}")
                info(f"Скачайте вручную:\n    wget -O {model_path} {model_info['url']}")

    # Активировать systemd сервис
    result = run(
        ["systemctl", "--user", "enable", "--now", "voxtype"],
        check=False,
        capture_output=True,
    )
    if result.returncode == 0:
        ok("systemctl --user enable --now voxtype")
    else:
        warn("Не удалось автоматически включить voxtype сервис")
        info("Запустите вручную: systemctl --user enable --now voxtype")

    print(f"\n  {CYAN}Voxtype настройки:{RESET}")
    info("Хоткей: ScrollLock (push-to-talk)")
    info("Модели хранятся в: ~/.local/share/voxtype/models/")
    info("Конфиг: ~/.config/voxtype/config.toml")


# ── Шаг 9: Настройка SSH для GitHub ──────────────────────────────────────────
def step_setup_ssh() -> None:
    header("Шаг 9: SSH для GitHub")

    ssh_key = HOME / ".ssh" / "id_ed25519"
    pub_key = HOME / ".ssh" / "id_ed25519.pub"

    if ssh_key.exists():
        ok("SSH ключ уже существует: ~/.ssh/id_ed25519")
    else:
        email = ask("Введите ваш GitHub email для SSH ключа")
        if not email:
            warn("Email не введён. Пропускаю генерацию SSH ключа.")
            return

        (HOME / ".ssh").mkdir(mode=0o700, exist_ok=True)
        run([
            "ssh-keygen", "-t", "ed25519",
            "-C", email,
            "-f", str(ssh_key),
            "-N", "",
        ])
        ok("SSH ключ сгенерирован")

    # Показать публичный ключ
    if pub_key.exists():
        pub_key_content = pub_key.read_text().strip()
        print(f"\n  {YELLOW}Ваш публичный SSH ключ:{RESET}")
        print(f"\n  {CYAN}{pub_key_content}{RESET}\n")
        print(f"  {YELLOW}Добавьте его на GitHub:{RESET}")
        print(f"  {CYAN}https://github.com/settings/keys{RESET}\n")

        input(f"  {YELLOW}Нажмите Enter после добавления ключа на GitHub...{RESET} ")

        # Тест соединения
        result = run(
            ["ssh", "-T", "-o", "StrictHostKeyChecking=accept-new", "git@github.com"],
            check=False,
            capture_output=True,
            text=True,
        )
        # ssh -T возвращает код 1 но с успешным сообщением
        if "successfully authenticated" in result.stderr:
            ok("SSH соединение с GitHub работает!")
        else:
            warn("Не удалось проверить SSH соединение")
            info("Проверьте вручную: ssh -T git@github.com")


# ── Шаг 10: Настройка Zsh ────────────────────────────────────────────────────
def step_setup_zsh() -> None:
    header("Шаг 10: Настройка Zsh")

    upgrade_zsh = INSTALL_DIR / "upgrade_zsh.py"
    if not upgrade_zsh.exists():
        warn("upgrade_zsh.py не найден в репозитории")
        return

    info("Запускаю upgrade_zsh.py для настройки Oh My Zsh и плагинов...")
    result = run(["python3", str(upgrade_zsh)], check=False)
    if result.returncode == 0:
        ok("Zsh настроен")
    else:
        warn("upgrade_zsh.py завершился с ошибкой. Проверьте zsh вручную.")


# ── Шаг 11: Завершение ────────────────────────────────────────────────────────
def step_finish() -> None:
    header("Установка завершена!")

    print(f"""
{GREEN}{BOLD}╔══════════════════════════════════════════════════╗
║         Dotfiles успешно установлены!            ║
╚══════════════════════════════════════════════════╝{RESET}

{CYAN}Что установлено:{RESET}
  ✓ Hyprland, Waybar, Rofi, Alacritty, Dunst
  ✓ Конфиги в ~/.config/
  ✓ Обои в ~/Pictures/Wallpapers/
  ✓ Voxtype (голосовой ввод)
  ✓ Zsh + Oh My Zsh

{YELLOW}Что сделать вручную:{RESET}
  • Включить SDDM: sudo systemctl enable sddm
  • Перезагрузиться или запустить Hyprland: Hyprland
  • Настроить мониторы в ~/.config/hypr/config/system/monitors.conf
  • Настроить клавиши в ~/.config/hypr/config/binds/main.conf

{CYAN}Обои меняются:{RESET}
  • Случайные: Super+W (настроено в Hyprland binds)
  • Директория: ~/Pictures/Wallpapers/

{CYAN}Голосовой ввод:{RESET}
  • Зажмите ScrollLock для записи голоса
  • Текст вставится в активное поле
""")


# ── Точка входа ───────────────────────────────────────────────────────────────
def main() -> None:
    banner()

    print(f"  {YELLOW}Это установит dotfiles rice из https://github.com/redmoondz/dotfiles{RESET}")
    confirm = ask("Продолжить установку? [Y/n]", "Y").lower()
    if confirm not in ("y", "yes", ""):
        print("  Установка отменена.")
        sys.exit(0)

    try:
        step_check()
        step_install_yay()
        install_type = step_choose_install_type()
        step_clone_repo()
        step_install_packages(install_type)
        step_copy_configs()
        step_copy_wallpapers()
        step_setup_voxtype()
        step_setup_ssh()
        step_setup_zsh()
        step_finish()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Установка прервана пользователем.{RESET}\n")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        error(f"Команда завершилась с ошибкой: {e.cmd}")
        error(f"Код: {e.returncode}")
        sys.exit(1)
    finally:
        # Очистка временных файлов
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
