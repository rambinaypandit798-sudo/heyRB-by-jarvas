# Roo Code Rule 04: Clean API Integration & Prefix Flexibility

1. **Bypass Rigid Prefix Restrictions**:
   - Strictly prohibit enforcing hardcoded API key prefixes like `sk-` or `sk_`.
   - Google Gemini API keys follow `AIzaSy...` formatting; Supabase keys can be `sb_publishable_` or legacy JWTs; and environment keys may be injected dynamically.
   - All API client wrappers and middleware must accept, trim, and pass keys without throwing prefix mismatch errors.

2. **Upstream Error Handling**:
   - Direct Google Gemini API requests (`generativelanguage.googleapis.com`) must gracefully handle rate limits (429 with backoff), streaming responses (SSE), and multimodal payloads without terminating agent sessions.
