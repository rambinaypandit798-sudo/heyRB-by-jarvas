"""
SQLite schema definition and seed initialization for RB Agent OS.
All 18 tables according to the Master Specification.
"""

SCHEMA_SQL = """
-- 1. Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

-- 2. Messages
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    status TEXT DEFAULT 'completed' CHECK(status IN ('pending', 'streaming', 'completed', 'failed', 'cancelled')),
    latency_ms INTEGER DEFAULT 0,
    token_usage INTEGER DEFAULT 0,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- 3. User Preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Memories
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    category TEXT DEFAULT 'general',
    content TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'user_chat',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    conversation_id TEXT,
    title TEXT NOT NULL,
    intent TEXT NOT NULL,
    status TEXT DEFAULT 'received' CHECK(status IN ('received', 'classified', 'planned', 'awaiting_approval', 'running', 'verifying', 'completed', 'failed', 'cancelled')),
    input_prompt TEXT NOT NULL,
    result TEXT,
    error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Task Steps
CREATE TABLE IF NOT EXISTS task_steps (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    description TEXT NOT NULL,
    tool_name TEXT,
    input_data TEXT,
    output_data TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'verifying', 'completed', 'failed', 'skipped')),
    execution_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- 7. Execution Logs
CREATE TABLE IF NOT EXISTS execution_logs (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    step_id TEXT,
    level TEXT DEFAULT 'INFO',
    message TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Tool Registry
CREATE TABLE IF NOT EXISTS tool_registry (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    is_enabled INTEGER DEFAULT 1,
    requires_confirmation INTEGER DEFAULT 0,
    parameters_schema TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Skill Registry
CREATE TABLE IF NOT EXISTS skill_registry (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    code TEXT NOT NULL,
    language TEXT DEFAULT 'python',
    is_active INTEGER DEFAULT 1,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Skill Versions
CREATE TABLE IF NOT EXISTS skill_versions (
    id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    code TEXT NOT NULL,
    change_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(skill_id) REFERENCES skill_registry(id) ON DELETE CASCADE
);

-- 11. Learning Feedback
CREATE TABLE IF NOT EXISTS learning_feedback (
    id TEXT PRIMARY KEY,
    message_id TEXT,
    task_id TEXT,
    rating INTEGER CHECK(rating IN (-1, 1)),
    feedback_text TEXT,
    applied INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Model Providers
CREATE TABLE IF NOT EXISTS model_providers (
    id TEXT PRIMARY KEY,
    provider_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    api_endpoint TEXT,
    is_active INTEGER DEFAULT 1,
    max_tokens INTEGER DEFAULT 4096,
    cost_per_1k REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Model Evaluations
CREATE TABLE IF NOT EXISTS model_evaluations (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    benchmark_id TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    latency_ms INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Benchmark Cases
CREATE TABLE IF NOT EXISTS benchmark_cases (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    expected_output TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Training Datasets
CREATE TABLE IF NOT EXISTS training_datasets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    sample_count INTEGER DEFAULT 0,
    file_path TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. Training Jobs
CREATE TABLE IF NOT EXISTS training_jobs (
    id TEXT PRIMARY KEY,
    dataset_id TEXT,
    provider_name TEXT NOT NULL,
    model_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    loss REAL,
    cost REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 17. Sync Queue
CREATE TABLE IF NOT EXISTS sync_queue (
    id TEXT PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('INSERT', 'UPDATE', 'DELETE')),
    payload TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'syncing', 'synced', 'failed')),
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 18. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_task_steps_task ON task_steps(task_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_task ON execution_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
"""

DEFAULT_PREFERENCES = [
    ("user_name", "Ram Binay"),
    ("project_owner", "Ram Binay Kumar Pandit"),
    ("greeting", "नमस्ते, Ram Binay, आज आपका क्या प्लान है?"),
    ("theme", "light_futuristic"),
    ("language", "hi"),
    ("wake_word_enabled", "true"),
    ("voice_auto_speak", "true"),
    ("active_provider", "gemini"),
    ("active_model", "gemini-1.5-flash"),
    ("require_action_confirmation", "true"),
    ("supabase_sync_enabled", "false")
]

DEFAULT_TOOLS = [
    ("tool_run_python", "run_python", "Execute isolated Python script in workspace with timeouts and security checks", "code", 1, 0, '{"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}'),
    ("tool_read_file", "read_file", "Read file contents from approved workspace directory", "filesystem", 1, 0, '{"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}'),
    ("tool_write_file", "write_file", "Write contents to a file in approved workspace directory", "filesystem", 1, 1, '{"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}'),
    ("tool_list_files", "list_files", "List files in approved workspace directory", "filesystem", 1, 0, '{"type": "object", "properties": {"path": {"type": "string"}}}'),
    ("tool_web_search", "web_search", "Query web search for external information and documentation", "research", 1, 0, '{"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}'),
    ("tool_termux_toast", "termux_toast", "Display a toast notification on Android screen via Termux:API", "android", 1, 0, '{"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}'),
    ("tool_termux_vibrate", "termux_vibrate", "Vibrate the Android device for tactile haptic feedback", "android", 1, 0, '{"type": "object", "properties": {"duration_ms": {"type": "integer"}}}'),
    ("tool_termux_battery", "termux_battery_status", "Read real Android battery level and charging state", "android", 1, 0, '{"type": "object", "properties": {}}'),
    ("tool_android_intent", "android_open_intent", "Open external Android app or URL via URI deep link", "android", 1, 1, '{"type": "object", "properties": {"uri": {"type": "string"}}, "required": ["uri"]}')
]

DEFAULT_PROVIDERS = [
    ("prov_gemini", "gemini", "gemini-1.5-flash", "https://generativelanguage.googleapis.com", 1, 8192, 0.0),
    ("prov_gemini_pro", "gemini", "gemini-1.5-pro", "https://generativelanguage.googleapis.com", 1, 8192, 0.0),
    ("prov_openai_mini", "openai", "gpt-4o-mini", "https://api.openai.com/v1", 0, 4096, 0.00015),
    ("prov_anthropic_sonnet", "anthropic", "claude-3-5-sonnet-20241022", "https://api.anthropic.com/v1", 0, 8192, 0.003),
    ("prov_ollama_local", "ollama", "llama3.2", "http://127.0.0.1:11434", 0, 4096, 0.0)
]

DEFAULT_BENCHMARKS = [
    ("bench_1", "What is the capital of India?", "New Delhi", "general", 1),
    ("bench_2", "Write a Python function to check palindrome", "def is_palindrome(s): return s == s[::-1]", "code", 1),
    ("bench_3", "Battery status check", "battery percentage", "android", 1)
]
