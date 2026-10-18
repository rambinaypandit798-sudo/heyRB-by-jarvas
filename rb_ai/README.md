<div align="center">

# ⚡ RB.AI — Autonomous Operating System Agent
### *Next-Generation Multimodal Voice AI, Hardware Automation & 5-Subagent Matrix for Android & Termux*

[![Flutter](https://img.shields.io/badge/Flutter-3.24.x-02569B?logo=flutter&logoColor=white)](https://flutter.dev)
[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Multimodal%20AI-8E75B2?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Android / Termux](https://img.shields.io/badge/Android-Termux%20API-3DDC84?logo=android&logoColor=white)](https://termux.dev)
[![SQLite](https://img.shields.io/badge/Database-SQLite3%20Persistent-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![CI/CD](https://img.shields.io/badge/GitHub%20Actions-Automated%20APK%20Build-2088FF?logo=github-actions&logoColor=white)](.github/workflows/build_apk.yml)
[![Telegram](https://img.shields.io/badge/Telegram-Bot%20Webhook-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-URL%20Automation-25D366?logo=whatsapp&logoColor=white)](https://whatsapp.com)

<p align="center">
  <b>Developed for: Ram Binay kumar Pandit</b><br>
  <i>Engineered with Zero Dummy Code Policy — 100% Production-Grade Working Logic</i>
</p>

---

</div>

## 🌌 Overview

**RB.AI (Robotic Brain / Rapid Butler)** is an elite, autonomous on-device operating system agent engineered natively for **Android** through a symbiotic blend of **Termux Linux Userland**, **Python 3 async core**, and a futuristic **Flutter / Dart UI**.

Unlike ordinary conversational chatbots, RB Agent exercises **direct hardware-level command** over the host device: toggling flashlights, vibrating on haptic cues, reading battery telemetry, snapping camera frames, monitoring telephony state for incoming calls, executing sandboxed bash scripts, and persisting user memory indefinitely via an embedded SQLite database.

---

## 📸 Key Architecture & UI Breakthroughs

```
                                  +---------------------------------------+
                                  |   Ram Binay kumar Pandit (Master)     |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |    JARVIS Arc Reactor Central HUD     |
                                  |   (Continuous Dual Rotating Rings)    |
                                  +-------------------+-------------------+
                                                      |
                         +----------------------------+----------------------------+
                         |                                                         |
                         v                                                         v
    +-----------------------------------------+               +-----------------------------------------+
    |         Flutter Client (v3.24)          |               |       Mobile Web App PWA (Termux)       |
    |  - Dynamic "नमस्ते, [User]" Greeting     |               |  - Instant On-Device Browser Testing    |
    |  - Strict Turn-Taking Speech Engine     |               |  - Live Subtitles & Captions Bar        |
    |  - Sidebar Drawer (No Bottom Bar)       |               |  - Full Hardware Trigger Chips          |
    +--------------------+--------------------+               +--------------------+--------------------+
                         |                                                         |
                         +----------------------------+----------------------------+
                                                      |
                                        REST & WS Gateway (Port 8765)
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |          RB.AI Core Gateway           |
                                  |          (core/server.py)             |
                                  +-------------------+-------------------+
                                                      |
         +--------------------+-----------------------+-----------------------+--------------------+
         |                    |                       |                       |                    |
         v                    v                       v                       v                    v
+------------------+ +------------------+   +-------------------+   +------------------+ +------------------+
| 1. Research &    | | 2. Memory &      |   | 3. Preview / View |   | 4. Automation    | | 5. Coding &      |
|    Web Agent     | |    Notes Agent   |   |    Agent          |   |    Agent         | |    GitHub Agent  |
| - Live DDG HTTP  | | - NLP 'यह चीज़   |   | - Live URL Fetch  |   | - Phone Tasks    | | - Termux Shell   |
|   Search API     | |   सेव कर लो'     |   | - Markdown Render |   | - Call Announce  | | - GitHub REST v3 |
| - Gemini Models  | | - SQLite DB Store|   | - Error Recovery  |   | - Haptics/Torch  | | - Repo Sync      |
+------------------+ +------------------+   +-------------------+   +------------------+ +------------------+
```

---

## 🌟 Distinctive Production Features

### 1. 👤 Dynamic User Identity Engine (Zero Hardcoded Strings)
- Greets the master dynamically on launch and visual banners:
  > **`नमस्ते, Ram Binay kumar Pandit आज आपका क्या प्लान है`**
- Dynamically synchronized across `SharedPreferences`, Python SQLite database (`user_settings`), and UI banners.
- Real-time profile updates with instant reactive recalculation of avatars, greetings, and system prompt contexts.

### 2. ⚛️ JARVIS Arc Reactor HUD Button
- **Continuous Circular Rotation:** Dual counter-rotating outer rings drawn mathematically via Flutter's `CustomPainter` with smooth trigonometric LED tech lines.
- **Glowing Core Reactor:** Features cyan/blue neon haptic visualizer displaying **"RB Agent"** with subtitle *"tap to open agents"*.
- **Targeted Dark Workspace Modal:** Tapping the reactor transitions from the clean light theme into a dark cyberpunk modal (`#070B12`) housing the 5 Sub-Agents orchestration matrix.

### 3. 🌐 Custom 5 Sub-Agents Matrix (100% Real Working Logic)
| Sub-Agent | Color Theme | Working Implementation |
|---|---|---|
| **1. Research & Web Agent** | Cyan (`#00E5FF`) | Live HTTP search engine using DuckDuckGo Instant Answer / HTML APIs to pull real-time data, Gemini release models, and web intelligence without API keys. |
| **2. Memory & Notes Agent** | Emerald (`#10B981`) | Native Natural Language Processing (NLP) detecting Hindi commands (*"यह चीज़ सेव कर लो"*, *"याद रखना"*, *"नोट कर लो"*) and English triggers (*"remember this"*, *"save note"*), auto-extracting titles and storing them into SQLite. |
| **3. Preview / View Agent** | Amber (`#F59E0B`) | Live web scraping and Markdown rendering engine that fetches HTTP headers, inspects DOM metadata, and renders code blocks. |
| **4. Automation Agent** | Purple (`#8B5CF6`) | Low-level hardware controller triggering Android torch, vibration, battery telemetry, clipboard synchronization, and telephony announcements. |
| **5. Coding & GitHub Agent** | Neon Pink (`#EC4899`) | Termux sandbox bash/python script executor + GitHub REST API v3 OAuth integration to list, inspect, and sync user repositories. |

### 4. 🎙️ Live Voice Mode & Strict Turn-Taking Protocol
- **Auto-Speak Greeting:** RB Agent autonomously vocalizes a welcome greeting upon initial load.
- **Strict Turn-Taking:** When the agent finishes speaking, it stops completely and transitions into a pure listening state. It **never** babbles or proactively interrupts until the human speaker pauses.
- **Live Scrolling Subtitles:** Real-time captioning ticker at the bottom of the screen displaying phonetically cleaned text.
- **TTS Pause & Resume Fix:** Progress listener records byte and word offsets, allowing playback to pause and resume accurately mid-sentence.
- **"Hey RB" Wake-Phrase:** Continuous low-power microphone streaming buffer that triggers immediate command processing on hearing *"Hey RB"*.

### 5. 📞 Telephony State & Call Announcements
- Built-in telephony state hooks that detect incoming calls and announce the caller aloud through device speakers:
  > *`"Ram Binay kumar Pandit, Ankit का फोन आया है"`*
- Simultaneous high-priority Android notification dispatched to the status bar.

### 6. 🤖 Omnichannel Integrations (Telegram & WhatsApp)
- **Telegram Bot Webhook / Long-Polling:** Built-in background daemon (`core/telegram_bot.py`) responding to `/start`, `/status`, `/torch`, `/note <text>`, and `/exec <cmd>`.
- **WhatsApp Bridge:** Generates and launches direct `https://wa.me/{phone}?text={encoded}` intents for automated message dispatching.

---

## 📁 Repository Directory Structure

```
rb_ai/
├── MASTER_PROMPT.md                  # Absolute production-ready master prompt blueprint
├── README.md                         # Project documentation and guide
├── .gitignore                        # Git exclusion rules
├── cli.py                            # Interactive CLI & daemon runner
├── requirements.txt                  # Python dependencies
├── core/
│   ├── assistant.py                  # Central assistant orchestrator
│   ├── audio_engine.py               # "Hey RB" Wake-phrase detector & STT/TTS loop
│   ├── automation.py                 # Termux:API hardware bridge + Call Announcements
│   ├── config.py                     # Environment & runtime configuration manager
│   ├── database.py                   # SQLite3 persistent storage (User, Notes, Chats)
│   ├── gemini_engine.py              # Gemini multimodal API with native function calling
│   ├── master_prompt.py              # System prompt injector & dynamic device context
│   ├── server.py                     # HTTP REST & WebSocket API gateway (port 8765)
│   ├── sub_agents.py                 # 5 Sub-Agents operational implementation
│   ├── telegram_bot.py               # Telegram bot long-polling & webhook server
│   ├── web_ui.py                     # Responsive standalone PWA for on-device testing
│   └── whatsapp_bridge.py            # WhatsApp automation bridge
├── scripts/
│   ├── install_termux_deps.sh        # One-click Termux setup script
│   └── start_rbai.sh                 # Background server launcher with wake-lock
└── flutter_client/
    ├── pubspec.yaml                  # Flutter 3.24 dependencies
    └── lib/
        ├── main.dart                 # Flutter entry point with clean light theme
        ├── models/
        │   └── message.dart          # Chat message data model
        ├── screens/
        │   └── home_screen.dart      # Dynamic greeting, Arc Reactor HUD & chat feed
        ├── services/
        │   └── rbai_service.dart     # Service coordinating voice, turn-taking & backend
        └── widgets/
            ├── chat_view.dart        # Chat view with RB Agent tags
            ├── hud_reactor_button.dart    # Rotating JARVIS Arc Reactor HUD button
            ├── sidebar_drawer.dart   # Full sidebar drawer (Bottom bar removed)
            └── sub_agents_workspace.dart  # 5 Sub-Agents dark workspace screen
```

---

## 🚀 Quick Start Guide

### Step 1: Install Termux Dependencies
Run in Termux on your Android phone:
```bash
pkg update && pkg install -y python git termux-api
cd ~
git clone https://github.com/rambinaypandit798-sudo/RB-ai-assistant.git rb_ai
cd rb_ai
pip install -r requirements.txt
```

### Step 2: Configure Gemini API Key
```bash
cp .env.example .env
nano .env # Insert your GEMINI_API_KEY=AIzaSy...
```

### Step 3: Launch RB.AI Server & Web PWA
```bash
python3 cli.py --server
# Or run with background Termux wake-lock:
./scripts/start_rbai.sh
```
Open **`http://localhost:8765/app`** in Chrome/Firefox on your Android device to experience the Arc Reactor HUD, dynamic greeting banner, and sub-agents immediately.

---

## 📱 Building the Android Release APK (GitHub Actions)

This repository includes a fully automated **GitHub Actions CI/CD Pipeline** (`.github/workflows/build_apk.yml`) that compiles the Flutter application into a release APK on every git push.

### Download Compiled Release APK:
1. Navigate to the **[Actions Tab](https://github.com/rambinaypandit798-sudo/RB-ai-assistant/actions)** of your GitHub repository.
2. Click on the latest workflow run (e.g., *"Build RB.AI Release APK"*).
3. Scroll to the **Artifacts** section at the bottom.
4. Download **`RB.AI-release-apk`** and install `app-release.apk` directly onto your Android device!

### Local Build (Alternative):
If you have Flutter installed locally on your PC/Mac:
```bash
cd flutter_client
flutter pub get
flutter build apk --release --no-tree-shake-icons
```
Output: `flutter_client/build/app/outputs/flutter-apk/app-release.apk`

---

## 🔒 Security & Privacy Policy

- **Zero Hardcoded Secrets:** All API keys, credentials, and tokens are stored in `.env` or encrypted in `~/.git-credentials` and SQLite.
- **Sandbox Safety:** The automation engine checks all shell commands against hazardous recursive patterns (`rm -rf /`, `:(){ :|:& };:`) before execution.
- **Privacy-First Telemetry:** All chat history, personal notes, and voice parameters remain strictly stored on your local phone SQLite database (`~/rb_ai/data/rb_agent.db`).

---

## 👨‍💻 Author & Engineering Credits

- **Master & Lead Visionary:** [Ram Binay kumar Pandit](https://github.com/rambinaypandit798-sudo)
- **Repository:** [`rambinaypandit798-sudo/RB-ai-assistant`](https://github.com/rambinaypandit798-sudo/RB-ai-assistant)
- **License:** Open Source under [MIT License](LICENSE)

<div align="center">
  <sub>Built with passion, precision, and zero compromises for autonomous on-device computing.</sub>
</div>
