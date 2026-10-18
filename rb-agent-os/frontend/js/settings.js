/**
 * Settings and Secondary Screens Controller for RB Agent OS.
 * Manages operator preferences, memories, device status, and sync.
 */

class SettingsController {
  constructor() {
    this.drawer = document.getElementById("settings-drawer");
    this.activeTab = "preferences";
    this.init();
  }

  init() {
    // Hamburger menu toggle
    const menuBtn = document.getElementById("btn-menu");
    if (menuBtn) {
      menuBtn.addEventListener("click", () => this.openDrawer());
    }

    const closeBtn = document.getElementById("btn-close-drawer");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => this.closeDrawer());
    }

    // Close on backdrop click
    if (this.drawer) {
      this.drawer.addEventListener("click", (e) => {
        if (e.target === this.drawer) this.closeDrawer();
      });
    }

    // Wire tabs
    const tabs = document.querySelectorAll(".drawer-tab");
    tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        this.switchTab(tab.dataset.tab);
      });
    });

    this.loadSettings();
  }

  openDrawer() {
    if (this.drawer) {
      this.drawer.classList.add("open");
      this.refreshActiveTab();
    }
  }

  closeDrawer() {
    if (this.drawer) {
      this.drawer.classList.remove("open");
    }
  }

  switchTab(tabName) {
    this.activeTab = tabName;
    const body = document.getElementById("drawer-body-content");
    if (!body) return;

    if (tabName === "preferences") {
      this.renderPreferencesTab(body);
    } else if (tabName === "history") {
      this.renderHistoryTab(body);
    } else if (tabName === "device") {
      this.renderDeviceTab(body);
    } else if (tabName === "memory") {
      this.renderMemoryTab(body);
    } else if (tabName === "learning") {
      this.renderLearningTab(body);
    } else if (tabName === "sync") {
      this.renderSyncTab(body);
    }
  }

  refreshActiveTab() {
    this.switchTab(this.activeTab);
  }

  async loadSettings() {
    try {
      const res = await fetch("/api/settings");
      if (!res.ok) return;
      const data = await res.json();
      this.settingsData = data;

      // Update UI Header Greeting
      const greetingEl = document.getElementById("greeting-text");
      if (greetingEl && data.preferences.greeting) {
        greetingEl.textContent = data.preferences.greeting;
      }

      // Update Active Model Pill
      const modelBadge = document.getElementById("active-model-name");
      if (modelBadge && data.preferences.active_model) {
        modelBadge.textContent = data.preferences.active_model;
      }
    } catch (e) {}
  }

  renderPreferencesTab(container) {
    const p = this.settingsData?.preferences || {};
    container.innerHTML = `
      <div class="settings-card">
        <h3>Operator Profile</h3>
        <div class="form-group">
          <label class="form-label">Operator Name</label>
          <input type="text" id="pref-user-name" class="form-input" value="${p.user_name || 'Ram Binay'}">
        </div>
        <div class="form-group">
          <label class="form-label">Home Greeting</label>
          <input type="text" id="pref-greeting" class="form-input" value="${p.greeting || 'नमस्ते, Ram Binay, आज आपका क्या प्लान है?'}">
        </div>
        <div class="form-group">
          <label class="form-label">Primary Language</label>
          <select id="pref-lang" class="form-select">
            <option value="hi" ${p.language === 'hi' ? 'selected' : ''}>Hindi (हिन्दी)</option>
            <option value="en" ${p.language === 'en' ? 'selected' : ''}>English</option>
            <option value="hinglish" ${p.language === 'hinglish' ? 'selected' : ''}>Hinglish</option>
          </select>
        </div>
        <button class="btn-primary" onclick="window.settingsController.savePreferences()">Save Profile</button>
      </div>

      <div class="settings-card">
        <h3>AI Provider Configuration</h3>
        <div class="form-group">
          <label class="form-label">Active Provider</label>
          <select id="pref-provider" class="form-select" onchange="window.settingsController.onProviderChange(this.value)">
            <option value="gemini" ${p.active_provider === 'gemini' ? 'selected' : ''}>Google Gemini</option>
            <option value="openai" ${p.active_provider === 'openai' ? 'selected' : ''}>OpenAI</option>
            <option value="anthropic" ${p.active_provider === 'anthropic' ? 'selected' : ''}>Anthropic Claude</option>
            <option value="local" ${p.active_provider === 'local' ? 'selected' : ''}>Local Fallback (Offline)</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">Model Name</label>
          <input type="text" id="pref-model" class="form-input" value="${p.active_model || 'gemini-1.5-flash'}">
        </div>
        <button class="btn-primary" onclick="window.settingsController.saveModelConfig()">Apply Model</button>
      </div>
    `;
  }

  async savePreferences() {
    const name = document.getElementById("pref-user-name")?.value;
    const greeting = document.getElementById("pref-greeting")?.value;
    const lang = document.getElementById("pref-lang")?.value;

    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: "user_name", value: name })
    });
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: "greeting", value: greeting })
    });
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: "language", value: lang })
    });

    alert("Preferences saved successfully!");
    this.loadSettings();
  }

  async saveModelConfig() {
    const prov = document.getElementById("pref-provider")?.value;
    const model = document.getElementById("pref-model")?.value;

    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: "active_provider", value: prov })
    });
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: "active_model", value: model })
    });

    alert("Provider settings updated!");
    this.loadSettings();
  }

  onProviderChange(prov) {
    const modelInput = document.getElementById("pref-model");
    if (!modelInput) return;
    if (prov === "gemini") modelInput.value = "gemini-1.5-flash";
    else if (prov === "openai") modelInput.value = "gpt-4o-mini";
    else if (prov === "anthropic") modelInput.value = "claude-3-5-sonnet-20241022";
    else if (prov === "local") modelInput.value = "rb-local-engine";
  }

  async renderHistoryTab(container) {
    container.innerHTML = `<div style="text-align:center; padding: 20px;">Loading conversations...</div>`;
    try {
      const res = await fetch("/api/conversations");
      const list = await res.json();
      if (!list.length) {
        container.innerHTML = `<div class="settings-card"><p>No conversation history yet.</p></div>`;
        return;
      }
      let html = `<div class="settings-card"><h3>Saved Conversations</h3>`;
      list.forEach(c => {
        html += `
          <div style="padding: 10px 0; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
            <div style="cursor: pointer;" onclick="window.settingsController.selectConversation('${c.id}')">
              <strong>${c.title}</strong>
              <div style="font-size: 0.72rem; color: #94a3b8;">${new Date(c.updated_at).toLocaleString()}</div>
            </div>
            <button class="feedback-btn" onclick="window.settingsController.deleteConversation('${c.id}')" title="Delete">🗑️</button>
          </div>
        `;
      });
      html += `</div>`;
      container.innerHTML = html;
    } catch (e) {
      container.innerHTML = `<div class="settings-card"><p>Error loading history: ${e.message}</p></div>`;
    }
  }

  selectConversation(id) {
    window.chatController.conversationId = id;
    localStorage.setItem("rb_active_conversation_id", id);
    window.chatController.loadConversation(id);
    this.closeDrawer();
  }

  async deleteConversation(id) {
    if (!confirm("Delete this conversation?")) return;
    await fetch(`/api/conversations/${id}`, { method: "DELETE" });
    if (window.chatController.conversationId === id) {
      window.chatController.conversationId = null;
      localStorage.removeItem("rb_active_conversation_id");
      document.getElementById("conversation-stream").innerHTML = "";
    }
    this.renderHistoryTab(document.getElementById("drawer-body-content"));
  }

  renderDeviceTab(container) {
    const dev = this.settingsData?.device_integration || {};
    container.innerHTML = `
      <div class="settings-card">
        <h3>Android & Termux Integration</h3>
        <p style="font-size: 0.8rem; margin-bottom: 12px; color: #64748b;">
          Direct device interaction layer via Termux:API and Android activities.
        </p>
        <div style="font-size: 0.82rem; line-height: 1.8;">
          <div>Termux:API Installed: <strong>${dev.termux_api_installed ? '✓ Yes' : '✗ No (pkg install termux-api)'}</strong></div>
          <div>Battery Monitoring: <strong>${dev.termux_battery_available ? '✓ Ready' : '✗ Unavailable'}</strong></div>
          <div>Screen Toast: <strong>${dev.termux_toast_available ? '✓ Ready' : '✗ Unavailable'}</strong></div>
          <div>Activity Manager: <strong>${dev.android_activity_manager_available ? '✓ Ready' : '✗ Unavailable'}</strong></div>
          <div>Integration Mode: <strong>${dev.companion_mode || 'PWA Bridge'}</strong></div>
        </div>
      </div>
      <div class="settings-card">
        <h3>Quick Hardware Tests</h3>
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;">
          <button class="btn-primary" style="flex: 1;" onclick="window.settingsController.testBattery()">Test Battery</button>
          <button class="btn-primary" style="flex: 1;" onclick="window.settingsController.testVibrate()">Test Vibrate</button>
        </div>
      </div>
    `;
  }

  async testBattery() {
    window.chatController.sendMessage("Check battery status", false);
    this.closeDrawer();
  }

  async testVibrate() {
    window.chatController.sendMessage("Vibrate device 300ms", false);
    this.closeDrawer();
  }

  async renderMemoryTab(container) {
    container.innerHTML = `<div style="text-align:center; padding: 20px;">Loading memories...</div>`;
    try {
      const res = await fetch("/api/memories");
      const memories = await res.json();
      let html = `
        <div class="settings-card">
          <h3>Stored Memories</h3>
          <p style="font-size: 0.78rem; color: #64748b; margin-bottom: 10px;">Persistent knowledge approved by operator.</p>
          <div style="max-height: 200px; overflow-y: auto;">
      `;
      if (!memories.length) {
        html += `<p style="font-size: 0.8rem; color: #94a3b8;">No stored memories yet.</p>`;
      } else {
        memories.forEach(m => {
          html += `
            <div style="padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 0.82rem; display: flex; justify-content: space-between;">
              <div>
                <span>${m.content}</span>
                <div style="font-size: 0.68rem; color: #94a3b8;">[${m.category}] • ${new Date(m.created_at).toLocaleDateString()}</div>
              </div>
              <button class="feedback-btn" onclick="window.settingsController.deleteMemory('${m.id}')">🗑️</button>
            </div>
          `;
        });
      }
      html += `
          </div>
          <button class="btn-primary" style="margin-top: 12px; background: #ef4444;" onclick="window.settingsController.clearMemories()">Clear All Memories</button>
        </div>
      `;
      container.innerHTML = html;
    } catch (e) {
      container.innerHTML = `<p>Error: ${e.message}</p>`;
    }
  }

  async deleteMemory(id) {
    await fetch(`/api/memories/${id}`, { method: "DELETE" });
    this.renderMemoryTab(document.getElementById("drawer-body-content"));
  }

  async clearMemories() {
    if (!confirm("Clear all memories?")) return;
    await fetch("/api/memories", { method: "DELETE" });
    this.renderMemoryTab(document.getElementById("drawer-body-content"));
  }

  async renderLearningTab(container) {
    container.innerHTML = `<div style="text-align:center; padding: 20px;">Loading learning metrics...</div>`;
    try {
      const res = await fetch("/api/learning/stats");
      const stats = await res.json();
      container.innerHTML = `
        <div class="settings-card">
          <h3>Self-Learning Analytics</h3>
          <div style="font-size: 0.85rem; line-height: 1.8;">
            <div>Satisfaction Rate: <strong>${stats.satisfaction_rate}%</strong></div>
            <div>Positive Feedbacks: <strong>${stats.positive_feedback}</strong></div>
            <div>Negative Corrections: <strong>${stats.negative_feedback}</strong></div>
            <div>Total Completed Tasks: <strong>${stats.completed_tasks}</strong></div>
            <div>Active Memories: <strong>${stats.active_memories}</strong></div>
          </div>
        </div>
        <div class="settings-card">
          <h3>Multi-Model Benchmark Runner</h3>
          <p style="font-size: 0.78rem; color: #64748b; margin-bottom: 10px;">Run benchmark evaluation cases against active provider.</p>
          <button class="btn-primary" onclick="window.settingsController.runBenchmarks()">Run Benchmark Suite</button>
          <div id="benchmark-results" style="margin-top: 10px; font-size: 0.8rem;"></div>
        </div>
      `;
    } catch (e) {
      container.innerHTML = `<p>Error: ${e.message}</p>`;
    }
  }

  async runBenchmarks() {
    const el = document.getElementById("benchmark-results");
    if (el) el.innerHTML = "Running cross-model benchmarks...";
    try {
      const res = await fetch("/api/benchmark/run", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      const data = await res.json();
      if (el) {
        el.innerHTML = `<strong>Completed:</strong> ${data.results.length} tests evaluated. Scores logged to database.`;
      }
    } catch (e) {
      if (el) el.innerHTML = "Benchmark error: " + e.message;
    }
  }

  renderSyncTab(container) {
    const s = this.settingsData?.sync_status || {};
    container.innerHTML = `
      <div class="settings-card">
        <h3>Supabase Cloud Synchronization</h3>
        <p style="font-size: 0.78rem; color: #64748b; margin-bottom: 10px;">
          Configured URL: <code>${s.supabase_url}</code>
        </p>
        <div style="font-size: 0.82rem; line-height: 1.8;">
          <div>Sync Enabled: <strong>${s.enabled ? 'Yes' : 'No (Offline Mode)'}</strong></div>
          <div>Anon Key Configured: <strong>${s.has_credentials ? 'Yes' : 'No'}</strong></div>
          <div>Pending Queue: <strong>${s.pending_count}</strong></div>
          <div>Synced Records: <strong>${s.synced_count}</strong></div>
        </div>
        <button class="btn-primary" style="margin-top: 12px;" onclick="window.settingsController.triggerSync()">Process Sync Queue Now</button>
      </div>
    `;
  }

  async triggerSync() {
    const res = await fetch("/api/sync/process", { method: "POST" });
    const data = await res.json();
    alert(`Sync Result: ${data.message || data.status}`);
    this.refreshActiveTab();
  }
}

window.settingsController = new SettingsController();
