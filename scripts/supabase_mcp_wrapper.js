#!/usr/bin/env node
/**
 * Supabase MCP Server Wrapper
 * Automatically resolves environment variables from .env if needed
 * and launches @supabase/mcp-server-supabase cleanly.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// Attempt to load .env from workspace or subprojects if not in process.env
const envPaths = [
  path.join(process.cwd(), '.env'),
  path.join(__dirname, '..', '.env'),
  path.join(__dirname, '..', 'rb-agent-source', '.env'),
  path.join(__dirname, '..', 'rb_ai', '.env'),
  path.join(__dirname, '..', 'rb-agent-os', '.env')
];

for (const ep of envPaths) {
  if (fs.existsSync(ep)) {
    try {
      const content = fs.readFileSync(ep, 'utf8');
      for (const line of content.split('\n')) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        const [k, ...vParts] = trimmed.split('=');
        const key = k.trim();
        const val = vParts.join('=').trim().replace(/^["']|["']$/g, '');
        if (!process.env[key] && val) {
          process.env[key] = val;
        }
      }
    } catch (e) {}
  }
}

const token = process.env.SUPABASE_ACCESS_TOKEN ||
              process.env.SUPABASE_SERVICE_KEY ||
              process.env.SUPABASE_KEY ||
              process.env.SUPABASE_PUBLISHABLE_KEY ||
              process.env.SUPABASE_ANON_KEY ||
              'bypass-local-token';

const projectRef = process.env.SUPABASE_PROJECT_ID ||
                   process.env.VITE_SUPABASE_PROJECT_ID;

const args = [];
if (token) {
  args.push('--access-token', token);
}
if (projectRef) {
  args.push('--project-ref', projectRef);
}
if (process.env.SUPABASE_URL) {
  args.push('--api-url', process.env.SUPABASE_URL);
}

const mcpBin = '/data/data/com.termux/files/usr/bin/mcp-server-supabase';
const child = spawn(mcpBin, args, {
  stdio: 'inherit',
  env: {
    ...process.env,
    SUPABASE_ACCESS_TOKEN: token
  }
});

child.on('exit', (code) => {
  process.exit(code || 0);
});
