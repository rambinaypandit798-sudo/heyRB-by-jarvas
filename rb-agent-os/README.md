# RB Agent OS — Autonomous Mobile-First Personal AI Assistant

**Project Owner:** Ram Binay Kumar Pandit  
**Application Name:** RB Agent OS  
**Platform:** Android-first Progressive Web App (PWA) with optional Native Android Companion  
**Backend:** Python FastAPI (Asynchronous)  
**Local Runtime:** Termux on Android, Port `8765`  
**Database:** SQLite (`rb_agent.db`) with 18 structured relational tables  
**Optional Cloud:** Supabase (`https://sjkpzpglpfgjhuzjkseb.supabase.co`)  
**Primary Languages:** Hindi, English, Hinglish  

---

## 1. Project Overview

**RB Agent OS** is a personal AI assistant centered on a futuristic rotating planetary reactor. Designed from the ground up for Android mobile devices and Termux, it combines conversational intelligence, two-way voice interaction, autonomous intent routing, authorized Android hardware automation, safe code execution, persistent memory, and self-learning capabilities.

### Key Features
- **Central Planetary Reactor:** Continuously rotating holographic spherical energy core with real application states (`idle`, `listening`, `thinking`, `executing`, `speaking`, `success`, `error`).
- **Autonomous Intent Routing:** Understands natural Hindi, English, and Hinglish. Automatically selects internal tools and workflows without requiring manual agent toggles.
- **Controlled Python Code Execution:** Runs scripts inside an isolated workspace with timeouts, output limits, and strict argument arrays.
- **Android & Termux Integration:** Real device actions via Termux:API (`battery status`, `screen toast`, `vibration`, `intents/deep links`).
- **Persistent Local Memory & Database:** 18 SQLite tables storing conversations, memories, tasks, logs, tools, skills, feedback, and benchmarks.
- **Multi-Model Support:** Google Gemini (`gemini-1.5-flash`), OpenAI, Anthropic Claude, and a built-in local offline engine.
- **Offline & PWA Ready:** Manifest, Service Worker, and offline conversational fallback.
- **Native Android Companion Module:** Source code and manifest for persistent background wake-word listening ("Hey RB") and local loopback relay.

---

## 2. Directory Structure

```
rb-agent-os/
├── cli.py                     # CLI Launcher & Diagnostics runner
├── requirements.txt           # Pure-Python dependencies verified for Termux
├── .env.example               # Configuration template with placeholders
├── .env                       # Active runtime configuration
├── rb_agent.db                # SQLite database (18 tables)
├── workspace/                 # Designated isolated workspace directory
├── app/
│   ├── config.py              # Environment configuration & settings
│   ├── main.py                # FastAPI server, static mounts & health check
│   ├── api/                   # REST API routes
│   │   ├── chat.py            # Conversational endpoints & history
│   │   ├── voice.py           # Speech processing & wake-word status
│   │   ├── tasks.py           # Task lifecycle, approvals & cancellation
│   │   ├── memory.py          # Persistent memory CRUD & export
│   │   ├── tools.py           # Tool registry discovery & direct execution
│   │   └── settings.py        # Operator profile, learning stats & sync
│   ├── core/                  # Engine internals
│   │   ├── router.py          # Autonomous intent classifier & language detector
│   │   ├── planner.py         # Multi-step task planner
│   │   ├── orchestrator.py    # Real-time task lifecycle & verification coordinator
│   │   ├── permissions.py     # Path traversal & command injection security
│   │   └── verifier.py        # External action result verifier
│   ├── models/                # Model adapters
│   │   ├── adapter.py         # Abstract base adapter & response schema
│   │   ├── gemini.py          # Google Gemini 1.5 Flash adapter
│   │   ├── openai_adapter.py  # OpenAI GPT-4o-mini adapter
│   │   ├── anthropic_adapter.py # Anthropic Claude adapter
│   │   └── local_fallback.py  # Local offline rule-based & memory engine
│   ├── tools/                 # Tool implementations
│   │   ├── registry.py        # Central tool registry with execution logs
│   │   ├── code_executor.py   # Isolated Python subprocess runner
│   │   ├── file_ops.py        # Workspace file read/write/list/delete
│   │   ├── web_search.py      # Online research & factual search
│   │   └── android_tools.py   # Termux:API & Android intent tools
│   ├── learning/              # Self-learning engine
│   │   ├── engine.py          # Feedback collector & learning analytics
│   │   ├── evaluator.py       # Cross-model benchmark evaluation runner
│   │   └── skills.py          # Versioned skill registry
│   ├── memory/
│   │   └── manager.py         # Persistent memory storage & search
│   ├── integrations/
│   │   └── supabase_sync.py   # Retry-safe Supabase offline queue sync
│   └── database/
│       ├── db.py              # SQLite thread-safe connection manager
│       ├── schema.py          # SQL schema & default seeds
│       └── models.py          # Pydantic data schemas
├── frontend/                  # Mobile-first PWA interface
│   ├── index.html             # Single-page interface with Planetary Reactor
│   ├── manifest.json          # Web App Manifest
│   ├── service-worker.js      # Offline cache worker
│   ├── css/
│   │   ├── style.css          # Theme, message bubbles & drawer styles
│   │   └── reactor.css        # Holographic planetary energy core animations
│   └── js/
│       ├── app.js             # Bootstrap & event wiring
│       ├── reactor.js         # Dynamic visual state controller
│       ├── voice.js           # Web Speech Recognition & Speech Synthesis
│       ├── chat.js            # Message flow, task approval & feedback
│       ├── settings.js        # Secondary screens controller
│       └── pwa.js             # PWA installer & network status monitor
├── android-companion/         # Native companion Android application
│   ├── README.md
│   ├── AndroidManifest.xml
│   └── src/com/rbagent/os/
│       ├── ForegroundVoiceService.java
│       └── MainActivity.java
└── tests/                     # Automated test suite (24 unit tests)
    ├── test_database.py
    ├── test_security.py
    ├── test_tools.py
    ├── test_router.py
    └── test_api.py
```

---

## 3. Installation & Setup in Termux

### Step 1: Install System Dependencies
```bash
pkg update && pkg install -y python git termux-api
```

### Step 2: Install Python Packages
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy and adjust `.env` as needed:
```bash
cp .env.example .env
```
To use Google Gemini, add your API key in `.env`:
```ini
ACTIVE_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```
*(If no API key is provided, RB Agent OS automatically uses its built-in Local Offline Engine).*

---

## 4. Running the Application

### Launch Server
```bash
python3 cli.py --server
```
Default URL: `http://127.0.0.1:8765`

### Run System Diagnostics
```bash
python3 cli.py --status
```

---

## 5. Running Automated Tests

Run the full test suite covering database persistence, security permissions, code execution, intent routing, and API endpoints:
```bash
python3 -m unittest discover -s tests -v
```

---

## 6. Security Principles

1. **Path Traversal Protection:** All file operations are strictly verified against `workspace/`. Attempts to access parent paths (`../`) or absolute paths outside the approved directory raise `SecurityViolationError` and are recorded in `audit_logs`.
2. **Command Injection Prevention:** Code execution uses argument lists (`[sys.executable, script_path]`) rather than string-interpolated shells. Shell metacharacters are rejected.
3. **Action Confirmation:** Sensitive operations (`write_file`, `delete_file`, `android_open_intent`) enter `awaiting_approval` state until the operator explicitly clicks Approve or confirms.
4. **Verification Assurance:** The system never fabricates success. Returned output is verified directly against exit codes, stdout/stderr, and filesystem state.
