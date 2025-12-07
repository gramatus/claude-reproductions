# Task Completion Logging

How to log task progress during multi-step work so users can monitor completion.

## Purpose

Due to a known UI rendering delay bug in Claude Code, the UI can remain blocked for 20+ minutes after all work is actually complete. This logging mechanism lets the user know when they can safely interrupt.

**MANDATORY**: This logging is required, not optional. The user depends on this to know progress.

---

## When to Log

| Event | Action |
|-------|--------|
| Mark a todo as `completed` | Log step to file (silent) |
| Return control to user | Log to file AND signal (triggers popup) |

**Trigger rule**: If you use TodoWrite to mark status = "completed", you MUST also log it.

---

## How to Log

```bash
# For todo step completions - immediately after marking completed (silent, no popup):
echo "[$(date +%H:%M:%S)] STEP: <todo item description> (X of Y)" >> .cache/claude-status.txt

# For final completion - log to file, then signal to trigger popup:
echo "[$(date +%H:%M:%S)] DONE: <brief description>" >> .cache/claude-status.txt
/signal-task-completed <brief description>
```

---

## Example Session

```bash
# Step completions (silent logging)
echo "[14:32:15] STEP: Add Kind filter to TechDocs (1 of 4)" >> .cache/claude-status.txt
echo "[14:35:42] STEP: Standardize Norwegian labels (2 of 4)" >> .cache/claude-status.txt
echo "[14:38:19] STEP: Add visibility conditions (3 of 4)" >> .cache/claude-status.txt
echo "[14:41:55] STEP: Create reusable EntityFilterSidebar (4 of 4)" >> .cache/claude-status.txt

# Final completion (log + popup signal)
echo "[14:42:03] DONE: Filter sidebar consolidation" >> .cache/claude-status.txt
/signal-task-completed Filter sidebar consolidation
```

---

## User Monitoring

Users can monitor progress with:

```bash
watch -n 1 cat .cache/claude-status.txt
```

---

## Why the Final Signal Matters

The `/signal-task-completed` command triggers an ask popup. This interrupts the session when actual work is done, even if Claude gets stuck on something afterwards. Users can safely stop the task when they see the popup.
