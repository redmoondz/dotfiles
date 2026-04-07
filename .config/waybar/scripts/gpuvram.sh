#!/bin/bash
# gpuvram.sh - Show GPU load and VRAM usage for Waybar (NVIDIA only, extendable)

STATE_FILE="/tmp/gpuvram_mode"

if [ "$1" = "--toggle" ]; then
    if [ "$(cat "$STATE_FILE" 2>/dev/null)" = "pct" ]; then
        echo "gb" > "$STATE_FILE"
    else
        echo "pct" > "$STATE_FILE"
    fi
    pkill -SIGRTMIN+7 waybar
    exit 0
fi

MODE=$(cat "$STATE_FILE" 2>/dev/null || echo "gb")

# Try NVIDIA first (nvidia-smi required)
if command -v nvidia-smi &>/dev/null; then
    DATA=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$DATA" ]; then
        LOAD=$(echo "$DATA" | awk -F', ' '{print $1}')
        VRAM_USED=$(echo "$DATA" | awk -F', ' '{print $2}')
        VRAM_TOTAL=$(echo "$DATA" | awk -F', ' '{print $3}')
        VRAM_GB=$(awk "BEGIN { printf \"%.1f\", ${VRAM_USED}/1024 }")
        VRAM_PCT=$(awk "BEGIN { printf \"%.0f\", ${VRAM_USED}/${VRAM_TOTAL}*100 }")

        if [ "$MODE" = "pct" ]; then
            echo "{\"text\": \"<span foreground='#76B900'>󰾲 ${LOAD}%  ${VRAM_PCT}%</span>\", \"tooltip\": \"GPU ${LOAD}% VRAM ${VRAM_USED}MiB/${VRAM_TOTAL}MiB (${VRAM_PCT}%)\"}"
        else
            echo "{\"text\": \"<span foreground='#76B900'>󰾲 ${LOAD}%  ${VRAM_GB}GB</span>\", \"tooltip\": \"GPU ${LOAD}% VRAM ${VRAM_USED}MiB/${VRAM_TOTAL}MiB\"}"
        fi
        exit 0
    fi
fi

# TODO: Add AMD/Intel support here

echo '{"text": "󰾲 --%  --%", "tooltip": "GPU/VRAM info not available"}'
exit 1
