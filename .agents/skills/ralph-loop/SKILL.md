---
name: ralph-loop
description: Continuous autonomous task execution loop until tasks are 100% complete. Integrates PRD task lists, automated testing, CodeRabbit reviews, and self-healing error recovery.
---

# Ralph Loop Autonomous Task Runner

The Ralph Loop pattern runs an autonomous, persistent execution loop where tasks are selected, implemented, verified with tests and CodeRabbit reviews, and iterated continuously until 100% completed.

## CLI Usage

```bash
# Check Ralph Loop status
ralph-loop check

# View current task list and completion percentage
ralph-loop status

# Run autonomous loop until all tasks are 100% complete
ralph-loop run

# Add a new task to the loop queue
ralph-loop add --title "Implement Feature X" --desc "Add authentication flow"
```

## Workflow Lifecycle

1. **Read Durable State**: Scans `.agents/tasks/prd.json` or `PLAN.md`.
2. **Execute Story**: Implement file modifications with zero conversational filler.
3. **Automated Verification**: Runs unit tests and `coderabbit-review`.
4. **Self-Healing Loop**: If build or syntax fails, inspects stack trace and fixes without user intervention.
5. **Repeat**: Moves to the next task until 100% of tasks pass.
