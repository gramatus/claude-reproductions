# Reproducing the UI Rendering Delay Bug

## Quick Summary

This bug causes Claude Code's UI to take ~7-8 seconds per tool call to display results, even though tools execute instantly. A complex task with 30+ tools = **20-25 minutes** of unnecessary waiting.

---

## Reproduction Method

This repo contains the "before" state of a real refactoring task that originally triggered the bug. The task involves:

- Creating 6 new files
- Creating 5 symlinks
- Modifying 5 existing files
- ~30+ tool operations total

### Setup

1. Create the log file:

   ```bash
   mkdir -p .cache && touch .cache/claude-status.txt
   ```

2. Open `.cache/claude-status.txt` in VS Code and keep it visible alongside the Claude Code panel

### Run the Test Prompt

Copy and paste this prompt into Claude Code:

```
Implement the plan in delay-bug/abundant-giggling-pelican.md

The "before" state files are in agent-common/ and the plan describes refactoring them into slash commands.

IMPORTANT: After completing EACH major step (creating a file, modifying a file, creating symlinks), log progress:
echo "[$(date +%H:%M:%S)] STEP: <description>" >> .cache/claude-status.txt

After ALL work is complete, log:
echo "[$(date +%H:%M:%S)] DONE: Plan implemented" >> .cache/claude-status.txt

Then tell me the current time.
```

### What to Observe

1. **In the log file**: Steps appear rapidly as tools actually execute
2. **In Claude Code UI**: Tool completions render one-by-one over many minutes
3. **Input blocked**: You can't type until all tool results are displayed

### Expected Timing (if bug is present)

| Event                       | Time                    |
| --------------------------- | ----------------------- |
| First step logged           | T+0s                    |
| "DONE" logged               | T+2-5 min (actual work) |
| UI shows all tools complete | T+20-30 min             |
| Can send next message       | T+20-30 min             |

**Bug confirmed if**: Log file shows "DONE" 15+ minutes before you can interact with Claude Code.

---

## Why This Task Reproduces the Bug

The original bug was discovered during exactly this type of refactoring task. The key factors:

1. **Many sequential tool calls**: Each file read, grep, edit, and write is a separate tool
2. **Complex reasoning**: The model thinks between operations, which seems to contribute to the delay
3. **Real work**: Unlike synthetic tests, this involves actual code analysis and transformation

The video evidence (`output_h265_crf26_8fps.mp4`) and screenshots in this folder were captured during this exact task.

---

## After the Test

### Verify in Debug Logs

```bash
LATEST=$(ls -t ~/.claude/debug/*.txt 2>/dev/null | head -1)

echo "=== PostToolUse Timeline ==="
grep "PostToolUse" "$LATEST" | tail -30

echo ""
echo "=== Time spread ==="
grep "PostToolUse" "$LATEST" | head -1
grep "PostToolUse" "$LATEST" | tail -1
```

**Bug confirmed if**: PostToolUse events span 15+ minutes for work that completed in 2-5 minutes.

### Cleanup

To reset for another test:

```bash
git checkout -- agent-common/
rm -rf .claude/commands/pr-review.md .claude/commands/pr-summary.md .claude/commands/commit.md .claude/commands/handoff.md .claude/commands/save.md
rm -f .cache/claude-status.txt
```

---

## Evidence from Original Bug Discovery

The frames and video in this folder show the original occurrence:

| File                                            | What it shows                                            |
| ----------------------------------------------- | -------------------------------------------------------- |
| `frame_050s_task_complete_ui_still_working.jpg` | Log shows "DONE" but UI still processing                 |
| `frame_140s_90sec_after_done.jpg`               | 90 seconds after completion, UI still catching up        |
| `frame_292s_summary_starting.jpg`               | ~4 min after done, UI starting to show summary           |
| `frame_304s_ui_finally_complete.jpg`            | UI finally finished, 254 seconds after actual completion |
| `output_h265_crf26_8fps.mp4`                    | Full 5:12 video showing the entire delay                 |

---

## Key Insight

The bug is **not** about tool execution time. Tools run fast. The bug is in the **UI rendering pipeline** - each tool result takes ~7-8 seconds to display, regardless of how quickly it executed.

Simple file creation tests may not trigger the bug because they lack the thinking/reasoning steps that seem to contribute to the delay. This real refactoring task reliably reproduces it.
