/**
 * Central Planetary Reactor Controller for RB Agent OS.
 * Manages real visual states without mock simulations:
 * - idle
 * - listening
 * - thinking
 * - executing
 * - speaking
 * - success
 * - error
 */

class ReactorController {
  constructor(containerId = "reactor-container", statusTextId = "reactor-status-text") {
    this.container = document.getElementById(containerId);
    this.statusText = document.getElementById(statusTextId);
    this.currentState = "idle";
    this.resetTimer = null;
  }

  setState(state, statusMessage = null, autoResetMs = 0) {
    if (!this.container) return;

    // Clear previous state classes
    this.container.classList.remove(
      "state-listening",
      "state-thinking",
      "state-executing",
      "state-speaking",
      "state-success",
      "state-error"
    );

    if (this.resetTimer) {
      clearTimeout(this.resetTimer);
      this.resetTimer = null;
    }

    this.currentState = state;

    if (state !== "idle") {
      this.container.classList.add(`state-${state}`);
    }

    // Update status text if provided or use default descriptive text
    if (this.statusText) {
      if (statusMessage) {
        this.statusText.textContent = statusMessage;
      } else {
        const defaults = {
          idle: "RB Agent Core Online",
          listening: "Listening for speech...",
          thinking: "Reasoning and analyzing...",
          executing: "Executing verified action...",
          speaking: "Speaking response...",
          success: "Action verified successfully",
          error: "Action restricted or failed"
        };
        this.statusText.textContent = defaults[state] || "Ready";
      }
    }

    // Auto-reset back to idle after temporary confirmation states
    if (autoResetMs > 0) {
      this.resetTimer = setTimeout(() => {
        this.setState("idle");
      }, autoResetMs);
    }
  }

  getState() {
    return this.currentState;
  }
}

// Global instance
window.reactor = new ReactorController();
