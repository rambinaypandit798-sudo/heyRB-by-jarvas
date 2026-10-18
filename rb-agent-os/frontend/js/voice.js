/**
 * Two-Way Voice Pipeline and Wake-Word Controller for RB Agent OS.
 * Speech recognition -> AI reasoning -> Text-to-Speech -> Reactor speaking sync.
 */

class VoiceController {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.wakeWordEnabled = true;
    this.autoSpeak = true;
    this.selectedVoice = null;
    this.wakeWords = ["hey rb", "rb agent", "namaste rb", "hello rb"];

    this.initRecognition();
    this.initVoices();
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn("SpeechRecognition not supported in this browser.");
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.lang = "hi-IN"; // Supports Hindi & English accents

    this.recognition.onstart = () => {
      this.isListening = true;
      const micBtn = document.getElementById("btn-mic");
      if (micBtn) micBtn.classList.add("recording");
      window.reactor.setState("listening", "Listening...");
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      console.log("[Voice Transcript]:", transcript);
      
      // Check for wake word or direct input
      this.handleVoiceInput(transcript);
    };

    this.recognition.onerror = (event) => {
      console.warn("[Voice Error]:", event.error);
      this.stopListening();
      window.reactor.setState("idle");
    };

    this.recognition.onend = () => {
      this.stopListening();
      if (window.reactor.getState() === "listening") {
        window.reactor.setState("idle");
      }
    };
  }

  initVoices() {
    if (!this.synthesis) return;
    const loadVoices = () => {
      const voices = this.synthesis.getVoices();
      // Prefer Hindi or English Indian voice if available
      this.selectedVoice = voices.find(v => v.lang.includes("hi") || v.lang.includes("IN")) || voices[0];
    };
    loadVoices();
    if (this.synthesis.onvoiceschanged !== undefined) {
      this.synthesis.onvoiceschanged = loadVoices;
    }
  }

  startListening() {
    if (!this.recognition) {
      alert("Microphone recognition is not supported in this mobile browser.");
      return;
    }
    try {
      this.recognition.start();
    } catch (e) {
      console.warn("Recognition already started or error:", e);
    }
  }

  stopListening() {
    this.isListening = false;
    const micBtn = document.getElementById("btn-mic");
    if (micBtn) micBtn.classList.remove("recording");
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
  }

  toggleListening() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  handleVoiceInput(transcript) {
    const inputField = document.getElementById("chat-input");
    if (inputField) {
      inputField.value = transcript;
    }
    // Auto-send voice input
    if (window.chatController) {
      window.chatController.sendMessage(transcript, true);
    }
  }

  speak(text) {
    if (!this.synthesis || !this.autoSpeak) return;

    // Clean markdown before speaking
    const cleanText = text
      .replace(/```[\s\S]*?```/g, "Code block omitted from voice.")
      .replace(/[*#_`]/g, "")
      .trim();

    if (!cleanText) return;

    // Cancel ongoing speech
    this.synthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      window.reactor.setState("speaking", "Speaking...");
    };

    utterance.onend = () => {
      window.reactor.setState("idle", "Ready");
    };

    utterance.onerror = () => {
      window.reactor.setState("idle");
    };

    this.synthesis.speak(utterance);
  }

  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
      window.reactor.setState("idle");
    }
  }
}

window.voiceController = new VoiceController();
