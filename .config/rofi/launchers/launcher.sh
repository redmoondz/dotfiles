#!/usr/bin/env bash
# Smart Rofi Launcher — apps + calculator + URL opener
# Original launcher backed up as launcher.sh.bak

dir="$HOME/.config/rofi"
theme='style-1'
history_file="$HOME/.cache/rofi-launch-history"
mkdir -p "$(dirname "$history_file")"
touch "$history_file"

# ─── App list generation ───────────────────────────────────────────────
# Generates tab-separated: name\ticon\tdesktop-path
list_apps_raw() {
    local dirs=(
        /usr/share/applications
        /usr/local/share/applications
        "$HOME/.local/share/applications"
        /var/lib/flatpak/exports/share/applications
        "$HOME/.local/share/flatpak/exports/share/applications"
    )
    local -A seen

    for d in "${dirs[@]}"; do
        [[ -d "$d" ]] || continue
        for f in "$d"/*.desktop; do
            [[ -f "$f" ]] || continue

            # Skip NoDisplay/Hidden entries
            grep -qiE '^(NoDisplay|Hidden)\s*=\s*true' "$f" && continue

            local name icon
            name=$(grep -m1 '^Name=' "$f" | cut -d= -f2-)
            icon=$(grep -m1 '^Icon=' "$f" | cut -d= -f2-)

            [[ -z "$name" ]] && continue

            # Deduplicate by name
            [[ -n "${seen[$name]+x}" ]] && continue
            seen[$name]=1

            printf '%s\t%s\t%s\n' "$name" "$icon" "$f"
        done
    done | sort -t $'\t' -k1,1 -f
}

# ─── Detection helpers ─────────────────────────────────────────────────

is_math() {
    local input="$1"
    # Store regex in variables to avoid bash parsing issues
    local re_start='^[[:space:]]*([-]?[0-9(]|sqrt|sin|cos|tan|log|ln|exp|abs|ceil|floor)'
    local re_ops='[+*/^%]'
    local re_minus='[0-9]-[0-9]'
    local re_funcs='(sqrt|sin|cos|tan|log|ln|exp|abs|ceil|floor)[(]'
    # Must start with a digit, open paren, or math function name
    [[ "$input" =~ $re_start ]] || return 1
    # Must contain at least one operator or math function call
    [[ "$input" =~ $re_ops ]] || [[ "$input" =~ $re_minus ]] || \
    [[ "$input" =~ $re_funcs ]] || return 1
    return 0
}

is_url() {
    local input="$1"
    local re_proto='^https?://'
    local re_www='^www[.]'
    local re_tld='^[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?[.](com|org|net|io|dev|ru|edu|gov|info|me|co|uk|de|pro|app|tech|xyz|su|by|ua|kz)(/.*)?$'
    # Explicit protocol
    [[ "$input" =~ $re_proto ]] && return 0
    # www. prefix
    [[ "$input" =~ $re_www ]] && return 0
    # domain.tld or domain.tld/path — common TLDs
    [[ "$input" =~ $re_tld ]] && return 0
    return 1
}

# ─── Handlers ──────────────────────────────────────────────────────────

handle_calc() {
    local expr="$1"
    local result

    if command -v qalc &>/dev/null; then
        result=$(qalc -t "$expr" 2>/dev/null)
    elif command -v python3 &>/dev/null; then
        # Only allow safe math characters before sending to eval
        local safe_chars='^[0-9 +*/().^%,a-z-]*$'
        if [[ ! "$expr" =~ $safe_chars ]]; then
            notify-send "⚠️ Calculator" "Invalid characters in expression"
            return 1
        fi
        result=$(python3 -c "
from math import *
try:
    r = eval('$expr', {'__builtins__': {}}, {k: v for k, v in vars(__import__('math')).items() if not k.startswith('_')})
    print(r)
except:
    print('error')
" 2>/dev/null)
    else
        notify-send "⚠️ Calculator" "qalc not installed. Install: sudo pacman -S libqalculate"
        return 1
    fi

    if [[ -n "$result" && "$result" != "error" ]]; then
        echo -n "$result" | wl-copy
        notify-send "🔢 $expr = $result" "Copied to clipboard"
    else
        notify-send "⚠️ Calculator" "Could not evaluate: $expr"
    fi
}

handle_url() {
    local url="$1"
    local re_proto='^https?://'
    # Prepend https:// if no protocol
    if [[ ! "$url" =~ $re_proto ]]; then
        url="https://$url"
    fi
    xdg-open "$url" &>/dev/null &
    disown
}

handle_app() {
    local desktop_file="$1"
    local app_name="$2"
    if [[ -f "$desktop_file" ]]; then
        # Record launch in history
        if [[ -n "$app_name" ]]; then
            # Remove old entry for this app, append new one with current timestamp
            grep -vP "^[0-9]+\\t${app_name}$" "$history_file" > "${history_file}.tmp" 2>/dev/null || true
            printf '%s\t%s\n' "$(date +%s)" "$app_name" >> "${history_file}.tmp"
            mv "${history_file}.tmp" "$history_file"
        fi
        gtk-launch "$(basename "$desktop_file")" &>/dev/null &
        disown
    fi
}

# ─── Main ──────────────────────────────────────────────────────────────

# Cache app list once (name\ticon\tdesktop-path)
tmp_list=$(mktemp /tmp/rofi-apps.XXXXXX)
trap "rm -f '$tmp_list'" EXIT
list_apps_raw > "$tmp_list"

# Sort by launch history (MRU first), then alphabetically
tmp_sorted=$(mktemp /tmp/rofi-sorted.XXXXXX)
trap "rm -f '$tmp_list' '$tmp_sorted'" EXIT
awk -F'\t' '
    NR==FNR { hist[$2] = $1; next }
    {
        ts = (($1 in hist) ? hist[$1] : 0)
        printf "%s\t%s\t%s\t%s\n", ts, $1, $2, $3
    }
' "$history_file" "$tmp_list" | sort -t $'\t' -k1,1 -rn | cut -f2- > "$tmp_sorted"

# Pipe to rofi: convert to rofi dmenu format with icons
chosen=$(awk -F'\t' '{printf "%s\0icon\x1f%s\n", $1, $2}' "$tmp_sorted" | rofi \
    -dmenu \
    -i \
    -p "" \
    -show-icons \
    -matching fuzzy \
    -theme "${dir}/${theme}.rasi" \
)

# Nothing selected (Escape)
[[ -z "$chosen" ]] && exit 0

# Look up .desktop file by selected app name (case-insensitive)
desktop_file=$(awk -F'\t' -v name="$chosen" '{if (tolower($1) == tolower(name)) {print $3; exit}}' "$tmp_list")

if [[ -n "$desktop_file" && -f "$desktop_file" ]]; then
    handle_app "$desktop_file" "$chosen"
    exit 0
fi

# Not an app — try calc or URL on the raw input
input="$chosen"

# 1. Check if it's a math expression
if is_math "$input"; then
    handle_calc "$input"
    exit 0
fi

# 2. Check if it's a URL
if is_url "$input"; then
    handle_url "$input"
    exit 0
fi
