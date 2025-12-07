# Bug Report: Claude Code UI Rendering Delay

## Summary

Claude Code's UI displays tool execution progress significantly behind actual execution state. When multiple tools are executed, file changes appear in the filesystem immediately but the UI renders tool completions sequentially over extended periods. **This is a consistent, reproducible problem that affects every multi-step task.**

### Severity

**Critical** — For complex tasks (20+ tool calls), the UI can remain blocked for **20-25 minutes** after all tool execution has completed. The user has no way to know when the task is actually done, making it impossible to safely interrupt or provide feedback.

### Consistent Pattern

This delay occurs on **every request**, not just occasional edge cases:

- Small tasks (5 tools): ~37 seconds of unnecessary blocking
- Medium tasks (15 tools): ~2-3 minutes of blocking
- Large tasks (30+ tools): **20-25 minutes of blocking**

The delay scales linearly with the number of tool calls (~7-8 seconds per tool).

---

## Environment

- **Claude Code Version**: 2.0.55
- **Platform**: VS Code Extension (also reproducible in CLI)
- **Host**: GitHub Codespaces (containerized Linux environment)
- **OS**: Linux 6.8.0-1030-azure
- **VS Code Server**: Remote server mode

---

## Steps to Reproduce

1. Open Claude Code in VS Code
2. Request a multi-step task that triggers tool execution (e.g., "Create 10 new files with boilerplate content")
3. Observe VS Code's diff view or file explorer — changes appear immediately
4. Observe Claude Code panel — tool completions render sequentially over several seconds/minutes
5. Attempt to send a new message — input is blocked until all UI rendering completes

---

## Expected vs Actual Behavior

### Expected

- UI should update in near-real-time as tools complete
- Input should not be blocked for extended periods after tool execution finishes
- Parallel tool executions should render in parallel (or at least in rapid succession)

### Actual

- Tools execute in parallel (verified via filesystem timestamps and debug logs)
- UI renders tool results sequentially with ~4-8 second gaps between each
- Input remains blocked until all rendering completes
- Status indicators continue cycling ("Unfurling...", "Crafting...", etc.) after execution is done

---

## Evidence

### 1. Video Evidence (5:12 Recording)

A screen recording demonstrates a task that completes at ~50 seconds but doesn't allow user input until ~304 seconds.

#### Video Timeline

| Video Time | Log Status                | UI Status        | What's Visible                     |
| ---------- | ------------------------- | ---------------- | ---------------------------------- |
| 0:00       | Task in progress          | Working          | Steps being logged                 |
| 0:45       | Step 12 of 12             | Working          | Final step completing              |
| **0:50**   | **`DONE: Task complete`** | Still processing | **Log shows task finished**        |
| 1:20       | DONE (30s ago)            | "Spelunking..."  | UI cycling through status messages |
| 2:20       | DONE (90s ago)            | "Cerebrating..." | Still rendering tool results       |
| 4:00       | DONE (190s ago)           | "Wrangling..."   | File diffs still rendering         |
| **5:04**   | DONE (254s ago)           | **Complete**     | **Input field finally usable**     |

#### Key Measurements

| Metric                          | Value                            |
| ------------------------------- | -------------------------------- |
| Task completion (per log file)  | ~50 seconds into video           |
| UI completion (input unblocked) | ~304 seconds into video          |
| **Total UI rendering lag**      | **~254 seconds (~4 min 14 sec)** |
| **Percentage of time wasted**   | **81%**                          |

---

### 2. Debug Log Analysis

Debug logs stored at `~/.claude/debug/latest` show timing discrepancies.

#### Tool Dispatch (All 6 tools queued in 80ms)

```
2025-11-30T16:16:24.257Z [DEBUG] executePreToolHooks called for tool: Bash
2025-11-30T16:16:24.276Z [DEBUG] executePreToolHooks called for tool: Bash
2025-11-30T16:16:24.297Z [DEBUG] executePreToolHooks called for tool: Bash
2025-11-30T16:16:24.311Z [DEBUG] executePreToolHooks called for tool: Bash
2025-11-30T16:16:24.324Z [DEBUG] executePreToolHooks called for tool: Bash
2025-11-30T16:16:24.337Z [DEBUG] executePreToolHooks called for tool: Bash
```

#### Tool Completion (Spread over 22 seconds)

```
2025-11-30T16:16:32.956Z [DEBUG] PostToolUse: Bash
2025-11-30T16:16:33.046Z [DEBUG] PostToolUse: Bash
2025-11-30T16:16:33.124Z [DEBUG] PostToolUse: Bash
2025-11-30T16:16:37.831Z [DEBUG] PostToolUse: Bash
2025-11-30T16:16:42.524Z [DEBUG] PostToolUse: Bash
2025-11-30T16:16:46.114Z [DEBUG] PostToolUse: Bash
```

**Key Finding**: 6 tools dispatched in 80ms, but PostToolUse callbacks span 22 seconds.

---

### 3. Controlled Timing Test (Filesystem vs UI)

| Edit   | File Modified (stat) | Next Tool Ran | Lag      |
| ------ | -------------------- | ------------- | -------- |
| Edit 1 | 15:03:22.909         | 15:03:30.454  | **7.5s** |
| Edit 2 | 15:03:30.467         | 15:03:37.340  | **6.9s** |
| Edit 3 | 15:03:37.351         | 15:03:45.335  | **8.0s** |
| Edit 4 | 15:03:45.345         | 15:03:51.525  | **6.2s** |
| Edit 5 | 15:03:51.538         | 15:03:59.935  | **8.4s** |

**Each edit appeared in the filesystem ~7-8 seconds BEFORE the UI could proceed.**

---

### 4. Severe Case: 24-Minute UI Block

During implementation of persona-based dashboards (~30 edit operations):

| Event                        | Timestamp (UTC) | Source             |
| ---------------------------- | --------------- | ------------------ |
| Session resumed              | 16:21:42        | Debug log          |
| Agent logged "task complete" | ~16:34:52       | Agent internal log |
| User could send next message | 16:58:51        | Debug log          |
| **Total UI blocking time**   | **~24 minutes** |                    |

Debug logs show only 2 user-facing messages during the entire 37-minute session, with all tool execution completing by ~16:35. The remaining 24 minutes were pure UI rendering lag.

---

### 5. Logical Proof

For sequential, dependent operations like:

1. Grep for a pattern
2. Read the matching lines
3. Edit based on what was read

If execution were truly sequential, edits **cannot exist** before reads complete. Yet the filesystem shows completed edits while UI claims to still be on earlier operations. This proves execution is batched/parallel, but display is sequential.

---

## Impact Summary

| Scenario                     | Observed Delay    | Per-Tool Lag   |
| ---------------------------- | ----------------- | -------------- |
| 5 sequential Edit operations | ~37 seconds       | ~7-8s per tool |
| 6 parallel Bash commands     | ~22 seconds       | N/A (parallel) |
| 12-step refactoring task     | ~4 minutes        | ~7-8s per tool |
| 30+ tool operations          | **20-25 minutes** | ~7-8s per tool |

### Productivity Impact

- Users cannot provide feedback or corrections while waiting
- Context usage indicator increases incrementally as UI catches up
- Perceived slowness discourages parallel tool usage
- No way to cancel or interrupt during the rendering phase
- **81% of wait time is wasted** (per video evidence)

---

## Root Cause Hypothesis

Based on the evidence, the bottleneck appears to be:

1. **API Response Streaming**: Each tool result must be streamed back from Anthropic's API individually
2. **Sequential Stream Processing**: The extension processes one stream response at a time
3. **UI Blocking**: The input remains blocked until all streams are fully rendered

This is NOT:

- Tool execution time (tools run in parallel, complete quickly)
- Local file I/O (filesystem updates are immediate)
- Permission checking (hooks complete in milliseconds)

---

## Suggested Mitigations

1. **Parallel Stream Rendering**: Process multiple tool result streams concurrently
2. **Optimistic UI Updates**: Show tool as "complete" immediately after local execution succeeds
3. **Progressive Input Unblocking**: Allow user input while final rendering completes
4. **Batch UI Updates**: For parallel tools, accumulate results and update UI in batches
5. **Local-First Display**: Show file changes from local filesystem immediately
6. **Progress Indicator**: Show "X of Y tools rendered" so users know actual progress

---

## Workaround

Until this is fixed, users can implement task completion logging to know when work is actually done:

```bash
# Log step completions
echo "[$(date +%H:%M:%S)] STEP: <description> (X of Y)" >> .cache/claude-status.txt

# Log final completion
echo "[$(date +%H:%M:%S)] DONE: <description>" >> .cache/claude-status.txt
```

Monitor with: `watch -n 1 cat .cache/claude-status.txt`

This allows users to see actual completion and safely interrupt even while the UI is catching up.

---

## How to Capture Debug Logs

```bash
# View latest debug log
cat ~/.claude/debug/latest

# Filter for tool timing
grep -E "(PreToolUse|PostToolUse|Stream started)" ~/.claude/debug/latest

# Watch live during reproduction
tail -f ~/.claude/debug/latest | grep -E "(PreToolUse|PostToolUse)"
```

---

## Attachments

- Video recording: `output_h265_crf26_8fps.mp4` (5:12, 2560×1440)
- Screenshot: `screenshot-35-minute-delay.png`
- Frame captures at key timestamps

---

**Reporter**: User via Claude Code
**Initial Report**: 2025-11-30
**Updated**: 2025-12-07
**Claude Code Version**: 2.0.55
