# Claude Code UI Rendering Delay: Diagnostic Report

## Issue Summary

Claude Code's UI displays tool execution progress significantly behind actual execution state. File changes appear in the filesystem (visible via diff view) minutes before the Claude Code panel shows corresponding tool completions. Users are blocked from sending new messages until UI rendering catches up, even though all work has completed.

## Observed Behavior

### Symptoms

1. **Diff view shows completed work** while Claude Code panel still shows earlier steps in progress
2. **Todo list checkboxes lag behind** — e.g., UI shows "Phase 1.4" as current while filesystem contains changes from Phase 2+
3. **Status indicators continue cycling** ("Unfurling...", "Crafting...", "Scheming...", "Whirring...") after all tool execution has completed
4. **Input blocked for 3-5 minutes** after complex operations, waiting for UI to catch up
5. **Minimal text output** — delays are not caused by streaming prose; tool calls have brief descriptions

### Evidence Pattern

- User initiates multi-step task (e.g., 6-phase todo list with grep/read/edit operations)
- Tool execution happens rapidly (file changes visible immediately in diff view)
- UI renders tool results sequentially over several minutes
- "% used" context indicator increases incrementally as UI catches up
- User cannot interact until UI completes rendering

### Logical Proof That This Is Display Lag (Not Thinking Time)

If tool execution were truly sequential and dependent:

- Grep result → informs what lines to read
- Read result → informs what edit to make
- Edit → depends on both previous results

Then edits **cannot exist before reads complete**, because Claude wouldn't know what to edit. Yet the filesystem shows completed edits while UI claims to still be on earlier read operations. Therefore: execution is batched/parallel, but display is sequential.

## Environment Details

- **Platform**: VS Code Extension (Claude Code)
- **Host**: GitHub Codespaces (containerized Linux environment)
- **File sizes**: Large files (3700+ lines observed in BackstageMockup4.html)
- **Operation types**: Grep, Read (line ranges), Edit (multi-line changes)
- **"Edit automatically" mode**: Enabled

## Quantified Impact

- **Per-tool lag**: ~7-8 seconds between filesystem write and UI proceeding to next action
- **Cumulative delay**: 5 edits = ~37s lag; 14 edits = ~2+ minutes; 20+ tools = 3-5 minutes
- **End-to-end lag**: ~70+ seconds from last edit to user input unblocked
- **Context usage**: Observed at 52%, 58%, 65%, 68%, 69%, 70% during delay periods
- **Productivity loss**: Significant for iterative development workflows

## Hypotheses to Investigate

### H1: Batched Tool Execution with Sequential Rendering

Claude returns multiple tool calls in a single API response. Tools execute near-simultaneously, but the extension renders results one-by-one with artificial pacing or processing overhead.

### H2: WebSocket/IPC Bottleneck

Communication between the execution layer and VS Code extension has bandwidth or message-ordering constraints causing display queue buildup.

### H3: Diff Rendering Overhead

Each tool result triggers VS Code diff computation. Large files or many changes may cause rendering backlog.

### H4: Context Window Processing

The "Inferring..." phase or context serialization between tool calls adds latency not visible in the UI state.

### H5: Extension Event Loop Blocking

The VS Code extension's main thread is blocked by synchronous operations while processing tool results.

## Debug Log Analysis

### Log Location

Debug logs are stored at `~/.claude/debug/`:

```bash
ls -la ~/.claude/debug/
# latest -> symlink to current session (may not update immediately)
# *.txt -> individual session logs by UUID
```

**Note**: The `latest` symlink may point to an older session. Check modification times to find the current session's log file.

### Key Events to Filter

```bash
# View tool timing events from most recent log
cat ~/.claude/debug/*.txt | grep -E "(PreToolUse|PostToolUse|Stream started|executePreToolHooks)" | tail -100

# Watch live during a task
tail -f ~/.claude/debug/*.txt | grep -E "(PreToolUse|PostToolUse|Stream started)"

# Find the current session's log (most recently modified)
ls -lt ~/.claude/debug/*.txt | head -1
```

### Timing Pattern Analysis

Look for these patterns in the log timestamps:

| Pattern | Normal Value | Bug Indicator |
|---------|--------------|---------------|
| PreToolHooks → PostToolUse | <100ms | Normal tool execution |
| PostToolUse → "Stream started" | 2-3s | API response streaming overhead |
| Multiple PreToolHooks within 100ms | N/A | Parallel tool dispatch detected |
| PostToolUse events spread over 20+ seconds | N/A | **Bug: Sequential rendering of parallel calls** |

### Example Log Analysis

```
# Normal sequential execution pattern:
19:30:16.720 executePreToolHooks for Edit
19:30:16.831 PostToolUse Edit          (+111ms - fast)
19:30:19.594 Stream started            (+2.76s - API overhead)
19:30:21.360 executePreToolHooks for Read (next tool starts)

# Problematic parallel dispatch pattern (from bug report):
16:16:24.257 executePreToolHooks for Bash
16:16:24.276 executePreToolHooks for Bash  (+19ms - parallel!)
16:16:24.297 executePreToolHooks for Bash  (+21ms - parallel!)
... 6 tools dispatched in 80ms total ...
16:16:32.956 PostToolUse Bash          (+8.7s later)
16:16:37.831 PostToolUse Bash          (+13.6s from start)
16:16:46.114 PostToolUse Bash          (+21.9s from start - spread over 22s!)
```

### CLI vs VS Code Extension

The CLI may exhibit less latency than the VS Code extension. When comparing:
- Run the same task in both environments
- Capture debug logs from each
- Compare PostToolUse timing spreads

## Files and Logs to Check

Claude Code logs are stored in these locations:

- `~/.claude/debug/` - **Primary debug logs with timestamps**
- `~/.claude/logs/` - Additional logs (if present)
- VS Code Output panel → "Claude" or "Claude Code" channel
- Extension host logs: `~/.vscode-server/data/logs/` (in Codespaces)
- `/tmp/` for any Claude-created temp files

## Timestamps for Correlation

If investigating with logs, look for operations on `BackstageMockup4.html` and `backstagesimulator.html` with multi-phase todo lists involving:

- Grep for components, systems, relations
- Read operations on line ranges 800-900, 1200-1400, 4200-4500
- Edit operations adding 10-40 lines

## Controlled Timing Test Methodology

The most reliable way to measure the lag is to capture filesystem timestamps alongside debug logs.

### Setup

```bash
# Create test file
echo -e "line1\nline2\nline3\nline4\nline5" > /tmp/timing_test.txt

# Record start time
echo "=== TEST START ===" && date +%Y-%m-%dT%H:%M:%S.%3NZ
```

### During Edits

After EACH edit operation, run a Bash command to capture timestamps:

```bash
echo "After Edit N:" && date +%Y-%m-%dT%H:%M:%S.%3NZ && stat /tmp/timing_test.txt | grep Modify
```

This captures:
- **Wall-clock time**: When Claude Code proceeded to the next action
- **Filesystem time**: When the edit actually wrote to disk

The **difference** between these is the UI lag per tool.

### Data Collection Table

| Edit | File Modified (stat) | Next Tool Ran | Lag |
|------|---------------------|---------------|-----|
| Edit 1 | | | |
| Edit 2 | | | |
| Edit 3 | | | |
| Edit 4 | | | |
| Edit 5 | | | |

### End-to-End Measurement

After the final edit, ask the user to note the wall-clock time when they can send a new message. Compare to:
- Filesystem modification time of last edit
- Debug log PostToolUse timestamp

### Expected Values (Bug Present)

| Metric | Value |
|--------|-------|
| Per-tool lag (stat → next tool) | ~7-8 seconds |
| Cumulative lag (5 edits) | ~37 seconds |
| End-to-end lag (last edit → user input) | ~70+ seconds |

---

_Report generated for self-diagnosis by Claude Code_
_Updated: 2025-12-01_
