# Quick Reproduction Guide

This bug demonstrates that VS Code Extension ignores `hookSpecificOutput.permissionDecision: "ask"` from PreToolUse hooks, while the CLI respects it.

## Setup (Already Complete)

The repo is already configured with:
- Hook: [.claude/hooks/workspace-guard.py](../.claude/hooks/workspace-guard.py)
- Settings: [.claude/settings.json](../.claude/settings.json)
- Permission rules: `Bash(echo:*)` is in the `allow` list

## One-Command Reproduction

### In VS Code Extension (Current Environment)

Open Claude Code panel and run:

```
run: echo "test-20"
```

**Expected**: User prompted for permission (hook returns "ask")
**Actual**: Command runs silently (hook's "ask" is ignored)

### In CLI (For Comparison)

The devcontainer includes Claude CLI automatically. Open a terminal and run:

```bash
claude
> run: echo "test-20"
```

**Result**: User IS prompted with "TEST-20: Hook asking, echo is in allow list"

**Note**: On first run, authenticate with `claude auth`

## What's Happening

1. The hook ([workspace-guard.py:403](../.claude/hooks/workspace-guard.py#L403)) detects `test-20` and returns:
   ```json
   {
     "hookSpecificOutput": {
       "permissionDecision": "ask",
       "permissionDecisionReason": "TEST-20: Hook asking, echo is in allow list"
     }
   }
   ```

2. **CLI behavior**: Shows permission prompt with hook's reason
3. **VS Code behavior**: Ignores the "ask", falls back to permission list (which has `Bash(echo:*)` in allow), runs silently

## Test Matrix

| Hook Decision | Permission List | CLI Behavior | VS Code Behavior | Consistent? |
|--------------|----------------|--------------|------------------|-------------|
| `"ask"`      | allow          | **Prompts**  | **Runs silently** | ✗          |
| `"ask"`      | deny           | **Prompts**  | **Denied**       | ✗          |
| `"allow"`    | deny           | Runs         | Runs             | ✓          |
| `"deny"`     | allow          | Blocked      | Blocked          | ✓          |
| `"approve"`  | deny           | Runs         | Runs             | ✓          |
| `"block"`    | allow          | Blocked      | Blocked          | ✓          |

## Other Test Commands

All require new session (hooks cached at startup):

```bash
# Test 21: Hook ask + permission deny
echo "test-21"

# Test 24: hookSpecificOutput allow (works in both)
echo "test-24"

# Test 25: hookSpecificOutput deny (works in both)
echo "test-25"
```

See [WORKSPACE-GUARD-TESTING.md](WORKSPACE-GUARD-TESTING.md) for full test results and analysis.

## Root Cause

The VS Code extension has a separate permission handling implementation that:
- Correctly processes `"allow"`/`"approve"` and `"deny"`/`"block"` decisions
- **Does not implement** the `"ask"` code path that exists in CLI
- Falls back to standard permission system when encountering `"ask"`

This creates a security gap: hooks cannot enforce "ask before executing" policies in VS Code.

## Attempted Workarounds (Failed)

1. ✗ Setting `"claudeCode.claudeProcessWrapper": "/home/node/.local/bin/claude"` - no effect
2. ✗ Various hook output format variations - "ask" specifically is ignored

## Expected Fix

VS Code extension should match CLI behavior:
- When hook returns `permissionDecision: "ask"`, show permission prompt
- User can approve/deny the specific tool invocation
- Behavior identical to CLI
