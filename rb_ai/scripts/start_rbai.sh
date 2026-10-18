#!/data/data/com.termux/files/usr/bin/bash
# RB.AI Daemon Starter with Termux Wake-Lock

# Acquire wake lock so Termux does not sleep in background
if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
    echo "🔒 Termux wake-lock acquired."
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting RB.AI Server on 127.0.0.1:8765..."
python3 cli.py --server
