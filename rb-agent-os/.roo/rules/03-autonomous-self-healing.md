# Roo Code Rule 03: Autonomous Error Self-Healing Loop

1. **Uninterrupted Autonomous Recovery**:
   - If an npm build failure, compile error, test failure, API mismatch, or terminal exception occurs: **DO NOT STOP AND DO NOT ASK THE USER**.
   - Immediately inspect the stack trace and error logs.
   - Locate the exact file, line number, and broken symbol or missing import.
   - Apply the targeted fix directly to the file.
   - Re-run the build, test, or server restart sequence automatically.
   - Verify connectivity and check that the issue is 100% resolved before reporting the final outcome.

2. **Self-Healing Protocol**:
   - Max Self-Healing Iterations: 5 consecutive targeted fixes per failure point.
   - Preserve diff history and log remediation steps to `.ralph/errors.log` or `.planning/debug.log`.
