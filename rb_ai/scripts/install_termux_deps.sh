#!/data/data/com.termux/files/usr/bin/bash
# RB.AI - Termux Dependency Installer

echo "=== [RB.AI] Installing System Dependencies ==="
pkg update -y
pkg install -y termux-api python curl git jq

echo "=== [RB.AI] Setting up Python dependencies ==="
python3 -m pip install --upgrade pip

echo "=== [RB.AI] Note on Termux:API ==="
echo "Ensure you have installed the 'Termux:API' Companion App from F-Droid or GitHub"
echo "and granted all requested permissions (Microphone, Camera, Notifications)."

echo "=== [RB.AI] Setup Complete! ==="
