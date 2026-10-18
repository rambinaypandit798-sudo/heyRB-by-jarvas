/**
 * Application Bootstrap for RB Agent OS.
 * Wires events, keyboard handlers, and voice button triggers.
 */

document.addEventListener("DOMContentLoaded", () => {
  console.log("[RB Agent OS] Initializing Mobile PWA Interface...");

  // Initialize Chat Controller
  if (window.chatController) {
    window.chatController.init();
  }

  // Wire Microphone Button
  const micBtn = document.getElementById("btn-mic");
  if (micBtn) {
    micBtn.addEventListener("click", () => {
      if (window.voiceController) {
        window.voiceController.toggleListening();
      }
    });
  }

  // Wire Voice Conversation Continuous Mode Button
  const voiceModeBtn = document.getElementById("btn-voice-mode");
  if (voiceModeBtn) {
    voiceModeBtn.addEventListener("click", () => {
      if (window.voiceController) {
        window.voiceController.toggleListening();
      }
    });
  }

  // Wire Reactor Core Click to Voice Trigger
  const reactorCore = document.querySelector(".reactor-core");
  if (reactorCore) {
    reactorCore.addEventListener("click", () => {
      if (window.voiceController) {
        window.voiceController.toggleListening();
      }
    });
  }

  // Wire Model Selector Tag click to open settings
  const modelTag = document.getElementById("active-model-name");
  if (modelTag) {
    modelTag.addEventListener("click", () => {
      if (window.settingsController) {
        window.settingsController.openDrawer();
      }
    });
  }

  // Viewport resize handling for mobile software keyboard
  const dock = document.querySelector(".bottom-dock");
  if (window.visualViewport && dock) {
    window.visualViewport.addEventListener("resize", () => {
      // Adjust scroll to maintain input visibility above virtual keyboard
      window.scrollTo(0, 0);
    });
  }

  console.log("[RB Agent OS] Core Interface Ready.");
});
