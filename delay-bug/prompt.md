# Claude Code Self-Diagnosis: UI Rendering Delay Investigation

## Your Mission

You are investigating a significant UX issue in Claude Code itself. The symptom: your UI shows tool execution progress **minutes behind** actual filesystem state. Users see completed file changes in VS Code's diff view while your panel still claims to be on earlier steps. Users are blocked from interacting until your UI catches up.

This is not theoretical — it has been documented with screenshots showing todo lists claiming "Phase 1.4" while diffs show "Phase 2" work already complete.

## Phase 1: Locate and Examine Logs

### 1.1 Find Claude Code's log locations

```bash
# Check common locations
ls -la ~/.claude/ 2>/dev/null
ls -la ~/.claude/logs/ 2>/dev/null
find ~/.claude -name "*.log" -o -name "*.jsonl" 2>/dev/null

# VS Code extension logs (Codespaces path)
ls -la ~/.vscode-server/data/logs/ 2>/dev/null
find ~/.vscode-server -name "*claude*" -type f 2>/dev/null

# Check for temp files
ls -la /tmp/*claude* 2>/dev/null

# Extension storage
ls -la ~/.vscode-server/extensions/*claude* 2>/dev/null
```

### 1.2 Check VS Code Output Channels

In VS Code, open Output panel (Ctrl+Shift+U) and look for:

- "Claude" or "Claude Code" channel
- "Extension Host" channel (filter for claude)

Report what log sources you find.

### 1.3 Examine recent log entries

For any logs found, examine the most recent entries:

```bash
# Tail recent logs (adjust path based on what you find)
tail -100 ~/.claude/logs/*.log 2>/dev/null
```

Look for:

- Timestamps around tool executions
- Any "batch" or "queue" terminology
- Latency measurements
- IPC or WebSocket references

## Phase 2: Architecture Discovery

### 2.1 Understand your own process model

```bash
# What Claude-related processes are running?
ps aux | grep -i claude

# Check for node processes (extension host)
ps aux | grep -E "(node|extensionHost)" | head -20

# Network connections (API calls, websockets)
netstat -an | grep ESTABLISHED | head -20
# or
ss -tunapl | head -20
```

### 2.2 Find configuration files

```bash
# Claude Code settings
find ~ -name "*claude*" -name "*.json" 2>/dev/null
cat ~/.claude/settings.json 2>/dev/null
cat ~/.claude/settings.local.json 2>/dev/null

# Check for any queue/batch configuration
grep -r "batch\|queue\|parallel\|concurrent" ~/.claude/ 2>/dev/null
```

### 2.3 Extension manifest

```bash
# Find and examine the extension's package.json
find ~/.vscode-server/extensions -name "package.json" -path "*claude*" -exec cat {} \; 2>/dev/null
```

## Phase 3: Controlled Timing Test (CRITICAL)

This is the most important test. It captures the **actual lag** between filesystem changes and UI completion.

### 3.1 Setup test file

```bash
# Create a test file with 5 lines
echo -e "line1\nline2\nline3\nline4\nline5" > /tmp/timing_test.txt

# Record start time
echo "=== TEST START ===" && date +%Y-%m-%dT%H:%M:%S.%3NZ && stat /tmp/timing_test.txt | grep Modify
```

### 3.2 Make sequential edits with timestamp capture

Make 5 Edit operations to the test file. **CRITICAL**: After EACH edit, immediately run a Bash command to capture timestamps:

```bash
echo "After Edit N:" && date +%Y-%m-%dT%H:%M:%S.%3NZ && stat /tmp/timing_test.txt | grep Modify
```

Example edit sequence:
1. Edit: Replace "line1" with "EDIT1: Modified at checkpoint 1"
2. Bash: Capture timestamp
3. Edit: Replace "line2" with "EDIT2: Modified at checkpoint 2"
4. Bash: Capture timestamp
5. ... repeat for all 5 lines

### 3.3 Record data in table format

| Edit | File Modified (stat) | Next Tool Ran | Lag |
|------|---------------------|---------------|-----|
| Edit 1 | | | |
| Edit 2 | | | |
| Edit 3 | | | |
| Edit 4 | | | |
| Edit 5 | | | |

### 3.4 Measure end-to-end lag

After the final edit and summary, ask the user:

> "What time does your clock show right now?"

Compare this to:
- The filesystem modification time of the last edit
- The timestamp of the "TEST COMPLETE" message

**Expected finding**: ~70+ seconds between last filesystem write and user input unblocked.

### 3.5 Watch file changes in real-time (optional)

Open a second terminal and run before starting the task:

```bash
# Watch for file modifications (run this BEFORE the task)
inotifywait -m -e modify,create,delete /tmp/ 2>/dev/null || \
  watch -n 0.5 "ls -la /tmp/timing_test.txt; cat /tmp/timing_test.txt"
```

This will show exactly when file changes occur vs when UI reports them.

## Phase 4: Analyze Findings

After gathering data, analyze:

### 4.1 Timing gaps

- What is the delta between file modification timestamps and UI completion?
- Are there patterns (first tool fast, subsequent tools delayed)?
- Does the gap scale with number of tools or file size?

### 4.2 Log patterns

- Do logs show batched tool submissions?
- Is there evidence of a rendering queue?
- Are there any error or warning messages?

### 4.3 Process behavior

- Is there a separate process for execution vs display?
- Any evidence of IPC overhead?

## Phase 5: Report Template

Compile your findings:

```markdown
## Investigation Results

### Log Sources Found

- [list locations and what they contain]

### Timing Measurements

- File modification timestamp: [X]
- UI completion timestamp: [Y]
- Delta: [Z seconds]

### Architecture Observations

- [describe what you learned about process model]

### Root Cause Hypothesis

Based on evidence, the delay appears to be caused by:
[your analysis]

### Potential Mitigations

- [suggestions based on what you found]
```

## Important Notes

1. **You are investigating yourself** — this is meta, but useful
2. **Be honest about limitations** — if you can't access certain logs, say so
3. **Timestamps are crucial** — record them precisely
4. **Don't assume** — verify with evidence

## Success Criteria

This investigation succeeds if you can answer:

1. Where does the delay occur? (execution layer, IPC, rendering, or input blocking)
2. Is batching happening? (multiple tools executed before UI updates)
3. What is the actual magnitude of the delay?
4. Are there configuration options that might help?

### Key Metrics to Capture

| Metric | How to Measure | Expected Value (Bug Present) |
|--------|----------------|------------------------------|
| Per-tool lag | stat time vs next tool timestamp | ~7-8 seconds |
| Cumulative lag | Sum of per-tool lags | ~37 seconds for 5 edits |
| End-to-end lag | Last edit stat time vs user input time | ~70+ seconds |
| PostToolUse spread | Debug log timestamps | Tools spread over 20+ seconds |

---

## Phase 6: Post-Task Debug Log Analysis

After completing a complex task, ask Claude Code to analyze the debug logs to understand timing behavior.

### 6.1 Identify Current Session Log

The `latest` symlink may not update immediately. Find the actual current session:

```bash
# List logs by modification time
ls -lt ~/.claude/debug/*.txt | head -5

# Get the most recently modified log file
CURRENT_LOG=$(ls -t ~/.claude/debug/*.txt | head -1)
echo "Current session log: $CURRENT_LOG"
```

### 6.2 Extract Tool Timing Events

```bash
# Extract timing events from current session
cat "$CURRENT_LOG" | grep -E "(PreToolUse|PostToolUse|Stream started|executePreToolHooks)" | tail -100

# Count tool executions
cat "$CURRENT_LOG" | grep "PostToolUse" | wc -l
```

### 6.3 Analysis Prompt for Claude Code

Copy this prompt to ask Claude Code to analyze the logs:

```
Analyze the debug log timing for this session. Run:

cat ~/.claude/debug/*.txt | grep -E "(PreToolUse|PostToolUse|Stream started)" | tail -100

Then for each tool execution:
1. Calculate PreToolHooks → PostToolUse delta (should be <100ms for normal execution)
2. Calculate PostToolUse → "Stream started" delta (this is API streaming overhead)
3. Identify any parallel tool dispatches (multiple PreToolHooks within 100ms of each other)
4. Flag any gaps >5 seconds between consecutive PostToolUse events

Summarize:
- Total tools executed
- Average PostToolUse gap
- Whether parallel dispatch occurred
- Any anomalies suggesting UI rendering lag
```

### 6.4 Comparison Template

For comparing CLI vs VS Code Extension:

```bash
# After running same task in both environments:

echo "=== VS Code Extension Session ==="
cat ~/.claude/debug/[VSCODE-SESSION-ID].txt | grep "PostToolUse" | head -20

echo "=== CLI Session ==="
cat ~/.claude/debug/[CLI-SESSION-ID].txt | grep "PostToolUse" | head -20
```

### 6.5 Quick Health Check

Run this after any complex task to check for timing issues:

```bash
# Quick timing health check
echo "=== Recent Tool Timing ==="
LATEST=$(ls -t ~/.claude/debug/*.txt | head -1)
cat "$LATEST" | grep -E "PostToolUse" | tail -10 | while read line; do
  echo "$line" | cut -d'Z' -f1 | cut -d'T' -f2
done

echo ""
echo "=== Parallel Dispatch Check ==="
cat "$LATEST" | grep "executePreToolHooks" | tail -20
```

---

## Automated Logging Request

To have Claude Code automatically log timing during a complex task, start your session with:

```
For this task, please periodically run:
  cat ~/.claude/debug/*.txt | grep -E "(PostToolUse|Stream started)" | tail -20
to capture timing data. At the end, analyze the timing patterns and report any anomalies.
```

Good luck investigating yourself!

---

## Phase 8: Timing Tests During Real Tasks

When performing a real multi-step task (not a dedicated timing test), incorporate timing capture to collect data while doing useful work.

### 8.1 Before starting the task

```bash
echo "=== TASK START ===" && date +%Y-%m-%dT%H:%M:%S.%3NZ
```

### 8.2 During the task

For tasks involving multiple Edit operations, periodically run:

```bash
echo "=== CHECKPOINT ===" && date +%Y-%m-%dT%H:%M:%S.%3NZ && ls -lt /path/to/modified/file | head -1
```

### 8.3 After task completion

1. Note the time when you can send a new message
2. Run debug log analysis:

```bash
LATEST=$(ls -t ~/.claude/debug/*.txt | head -1)
echo "=== PostToolUse Timeline ===" && grep "PostToolUse" "$LATEST" | tail -20
echo "" && echo "=== Edit timestamps ===" && grep "PostToolUse.*Edit" "$LATEST" | tail -10
```

3. Compare:
   - First Edit PostToolUse timestamp
   - Last Edit PostToolUse timestamp
   - Time when you could send next message

### 8.4 Report template for real tasks

After completing a real task, document:

```markdown
## Timing Data from [Task Name]

**Task**: [Brief description]
**Files modified**: [count]
**Edit operations**: [count]

### Timeline

| Event | Timestamp |
|-------|-----------|
| Task started | |
| First Edit (PostToolUse) | |
| Last Edit (PostToolUse) | |
| User could input | |

### Lag Calculation

- First to last Edit: [X] seconds
- Last Edit to user input: [Y] seconds
- Per-edit average lag: [Z] seconds
```

---

_Prompt last updated: 2025-12-01_
