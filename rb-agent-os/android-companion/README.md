# RB Agent OS — Android Companion Module

**Operator & Project Owner:** Ram Binay Kumar Pandit  
**Target Platform:** Android 8.0+ (API 26+)  
**Role:** Native foreground bridge for 24/7 background wake-word listening ("Hey RB") and device hardware interactions.

---

## 1. Architecture Overview

When running as a Progressive Web App (PWA) in a mobile browser, Android restricts continuous background audio recording to prevent battery drain and preserve user privacy.

The **Android Companion** bridges this gap:
1. **Foreground Service:** Runs with a visible persistent notification (`FOREGROUND_SERVICE_MICROPHONE`).
2. **Local Loopback Bridge:** Dispatches recognized speech directly to Termux localhost server:
   ```
   http://127.0.0.1:8765/api/voice/process
   ```
3. **Intent Dispatcher:** Receives commands from Termux backend to launch native Android activities, share sheets, and URI schemes (`tel:`, `sms:`, `geo:`).

---

## 2. Prerequisites & Building

- Android Studio or Gradle command-line (`gradlew assembleDebug`).
- Termux with RB Agent OS server running on port `8765`.
- Termux:API app installed for Termux-native sensor queries.

---

## 3. Supported Device Automations

| Action | Transport | Permission Required |
| :--- | :--- | :--- |
| Screen Toast | Termux:API | Standard |
| Device Vibration | Termux:API / Companion | `android.permission.VIBRATE` |
| Battery Status | Termux:API | `android.permission.BATTERY_STATS` |
| Wake-Word "Hey RB" | Companion Foreground Service | `RECORD_AUDIO`, `FOREGROUND_SERVICE` |
| Deep Links / URL launch | `am start` / Intent | Standard |

---

## 4. Privacy & Disclosure

- Audio is processed locally on-device.
- No continuous audio streams are uploaded externally without operator request.
- The companion app displays an active foreground notification while listening.
