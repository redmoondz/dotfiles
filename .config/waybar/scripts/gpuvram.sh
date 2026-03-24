#!/bin/bash
# gpuvram.sh - Show GPU load and VRAM usage for Waybar (NVIDIA only, extendable)

# Try NVIDIA first (nvidia-smi required)
if command -v nvidia-smi &>/dev/null; then
    LOAD=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n1)
    VRAM_USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -n1)
    VRAM_GB=$(awk "BEGIN { printf \"%.1f\", ${VRAM_USED}/1024 }")
    echo "{\"text\": \"<span foreground='#76B900'> ${LOAD}%  ${VRAM_GB}GB</span>\", \"tooltip\": \"GPU ${LOAD}% VRAM ${VRAM_USED}MiB\"}"
    exit 0
fi

# TODO: Add AMD/Intel support here

echo '{"text": " --%  --%", "tooltip": "GPU/VRAM info not available"}'
exit 1
