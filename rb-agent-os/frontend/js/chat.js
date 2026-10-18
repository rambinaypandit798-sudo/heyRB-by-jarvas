/**
 * Live Chat and Message Stream Controller for RB Agent OS.
 * Manages conversational turns, markdown rendering, tool approval, and feedback.
 */

class ChatController {
  constructor() {
    this.conversationId = localStorage.getItem("rb_active_conversation_id") || null;
    this.streamContainer = document.getElementById("conversation-stream");
    this.inputField = document.getElementById("chat-input");
    this.isProcessing = false;
  }

  init() {
    if (this.inputField) {
      this.inputField.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.submitFromInput();
        }
      });
      // Auto-resize textarea
      this.inputField.addEventListener("input", () => {
        this.inputField.style.height = "auto";
        this.inputField.style.height = Math.min(this.inputField.scrollHeight, 100) + "px";
      });
    }

    const sendBtn = document.getElementById("btn-send");
    if (sendBtn) {
      sendBtn.addEventListener("click", () => this.submitFromInput());
    }

    // Load active conversation messages if available
    if (this.conversationId) {
      this.loadConversation(this.conversationId);
    }
  }

  submitFromInput() {
    if (!this.inputField) return;
    const text = this.inputField.value.trim();
    if (!text || this.isProcessing) return;
    this.inputField.value = "";
    this.inputField.style.height = "auto";
    this.sendMessage(text, false);
  }

  async sendMessage(text, isVoice = false) {
    if (this.isProcessing) return;
    this.isProcessing = true;

    // Append User Bubble
    this.appendMessage("user", text);

    // Set Reactor State to Thinking
    window.reactor.setState("thinking", "Analyzing request...");

    try {
      const payload = {
        conversation_id: this.conversationId,
        message: text,
        voice_input: isVoice
      };

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      this.conversationId = data.conversation_id;
      localStorage.setItem("rb_active_conversation_id", this.conversationId);

      // Append Assistant Bubble
      this.appendMessage("assistant", data.response, data.message_id, data.task_id, data.status);

      // Update Reactor State
      const targetState = data.reactor_state || (data.status === "completed" ? "success" : "error");
      window.reactor.setState(targetState, null, 2500);

      // Speak response if voice was used
      if (isVoice && window.voiceController && data.status === "completed") {
        window.voiceController.speak(data.response);
      }
    } catch (e) {
      this.appendMessage("assistant", `⚠️ Connection error: ${e.message}`, null, null, "failed");
      window.reactor.setState("error", "Network or server failure", 3000);
    } finally {
      this.isProcessing = false;
    }
  }

  appendMessage(role, content, messageId = null, taskId = null, status = "completed") {
    if (!this.streamContainer) return;

    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${role}`;

    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Format content with simple markdown formatting (pre/code, bold, list)
    let formattedContent = this.escapeHtml(content)
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>');

    let actionApprovalHtml = "";
    if (status === "awaiting_approval" && taskId) {
      actionApprovalHtml = `
        <div style="margin-top: 10px; display: flex; gap: 8px;">
          <button class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="window.chatController.approveTask('${taskId}')">✓ Approve Action</button>
          <button class="btn-primary" style="padding: 6px 12px; font-size: 0.8rem; background: #64748b;" onclick="window.chatController.cancelTask('${taskId}')">✕ Cancel</button>
        </div>
      `;
    }

    bubble.innerHTML = `
      <div class="message-header">
        <span>${role === "user" ? "You" : "RB Agent"}</span>
        <span>${timeStr}</span>
      </div>
      <div class="message-content">${formattedContent}</div>
      ${actionApprovalHtml}
      ${role === "assistant" && messageId ? `
        <div class="message-footer">
          <button class="feedback-btn" title="Helpful" onclick="window.chatController.sendFeedback('${messageId}', 1)">👍</button>
          <button class="feedback-btn" title="Not helpful" onclick="window.chatController.sendFeedback('${messageId}', -1)">👎</button>
          <button class="feedback-btn" title="Copy text" onclick="navigator.clipboard.writeText('${this.escapeHtml(content)}')">📋</button>
        </div>
      ` : ''}
    `;

    this.streamContainer.appendChild(bubble);
    this.streamContainer.scrollTop = this.streamContainer.scrollHeight;
  }

  async approveTask(taskId) {
    try {
      window.reactor.setState("executing", "Executing approved action...");
      const res = await fetch(`/api/tasks/${taskId}/approve`, { method: "POST" });
      const data = await res.json();
      this.appendMessage("assistant", `✅ Action approved and executed: ${JSON.stringify(data.step_result.message || data.step_result)}`);
      window.reactor.setState("success", "Action verified", 2500);
    } catch (e) {
      alert("Failed to approve task: " + e.message);
      window.reactor.setState("error", "Approval error", 3000);
    }
  }

  async cancelTask(taskId) {
    try {
      await fetch(`/api/tasks/${taskId}/cancel`, { method: "POST" });
      this.appendMessage("assistant", "🛑 Task cancelled by operator.");
      window.reactor.setState("idle", "Task cancelled", 2000);
    } catch (e) {
      alert("Failed to cancel task: " + e.message);
    }
  }

  async sendFeedback(messageId, rating) {
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_id: messageId, rating: rating })
      });
      alert(rating === 1 ? "Thank you! Feedback recorded to memory." : "Feedback recorded. We'll adjust behavior.");
    } catch (e) {}
  }

  async loadConversation(convId) {
    try {
      const res = await fetch(`/api/conversations/${convId}/messages`);
      if (!res.ok) return;
      const messages = await res.json();
      this.streamContainer.innerHTML = "";
      messages.forEach(m => {
        this.appendMessage(m.role, m.content, m.id, null, m.status);
      });
    } catch (e) {}
  }

  escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
}

window.chatController = new ChatController();
