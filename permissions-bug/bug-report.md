# [BUG] VS Code Extension Ignores Hook `permissionDecision: "ask"` - CLI/Extension Behavior Divergence

## Environment

- **Claude Code CLI version**: 2.0.61
- **VS Code Extension version**: 2.0.61
- **Operating System**: Debian 12 in GitHub Codespaces
- **VS Code version**: 1.106.3

## Bug Description

The VS Code extension does not respect `hookSpecificOutput.permissionDecision: "ask"` from PreToolUse hooks. The same hook configuration works correctly in CLI (prompts user for permission) but is silently ignored in the VS Code extension.

This creates a significant behavior divergence between CLI and VS Code extension, making it impossible to implement consistent permission workflows across both interfaces.

## Steps to Reproduce

### 1. Create hook configuration

**`.claude/settings.json`**:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/hook-ask-test.sh \"$CLAUDE_TOOL_INPUT\""
          }
        ]
      }
    ]
  }
}
```

### 2. Create test hook script

**`hook-ask-test.sh`**:

```bash
#!/bin/bash
# Returns "ask" decision for specific test commands
INPUT="$1"

if echo "$INPUT" | grep -q "hook-ask-test"; then
    echo '{"hookSpecificOutput": {"permissionDecision": "ask"}, "reason": "Testing ask behavior"}'
    exit 0
fi

# Defer to permission system for other commands
echo '{"reason": "No hook match"}'
exit 0
```

### 3. Test in CLI

```bash
claude
> run: echo "hook-ask-test"
```

**Expected & Actual (CLI)**: User is prompted for permission. Hook "ask" decision is respected.

### 4. Test in VS Code Extension

Open Claude Code panel in VS Code, send same prompt:

```
run: echo "hook-ask-test"
```

**Expected**: User is prompted for permission (same as CLI)
**Actual**: Command executes based on permission rules, hook "ask" decision is ignored

## Test Matrix Results

| Hook Output Format                                        | Exit Code | CLI Behavior     | VS Code Behavior | Consistent? |
| --------------------------------------------------------- | --------- | ---------------- | ---------------- | ----------- |
| `{"decision": "approve"}`                                 | 0         | Runs silently    | Runs silently    | ✓           |
| `{"decision": "block", "reason": "x"}`                    | 0         | Blocked          | Blocked          | ✓           |
| `{"hookSpecificOutput": {permissionDecision: "allow"}}`   | 0         | Runs silently    | Runs silently    | ✓           |
| `{"hookSpecificOutput": {permissionDecision: "deny"}}`    | 0         | Blocked          | Blocked          | ✓           |
| **`{"hookSpecificOutput": {permissionDecision: "ask"}}`** | 0         | **Prompts user** | **Ignored**      | ✗           |
| stderr message                                            | 2         | Blocked          | Blocked          | ✓           |

## Impact

1. **Security workflows broken**: Cannot implement "ask before executing" policies that work consistently across interfaces
2. **Permission escalation**: Commands that should require user confirmation in VS Code execute without prompting
3. **Documentation mismatch**: Hook documentation implies consistent behavior across interfaces
4. **Unpredictable UX**: Users get different permission experiences depending on interface choice

## Workaround

Use `{"decision": "block"}` instead of "ask" for critical security controls. This works in both environments but removes the ability to let users approve case-by-case.

## Additional Context

### Attempted Fixes (None Worked)

1. **`claudeCode.claudeProcessWrapper`** pointed to system CLI binary (`/home/node/.local/bin/claude`) - no effect
2. Various hook output format variations - "ask" specifically is ignored regardless of format

### Related Issues

- #12604 - Extension ignores permission settings
- #13028 - Permissions in settings.local.json not respected
- #10801 - No way to bypass MCP tool approval prompts
- #8727 - Doesn't support custom API endpoints from settings.json

### Root Cause Hypothesis

The VS Code extension appears to have a separate permission handling implementation that:

1. Correctly processes "allow"/"approve" and "deny"/"block" decisions from hooks
2. Does not implement the "ask" code path that exists in CLI
3. Falls back to the standard permission system when encountering "ask"

## Expected Resolution

VS Code extension should implement the same "ask" behavior as CLI:

1. When hook returns `permissionDecision: "ask"`, show permission prompt to user
2. User can approve or deny the specific tool invocation
3. Behavior should be identical to CLI experience

## Reproduction Repository

The bug should be easily reproducible in https://github.com/gramatus/claude-reproductions.
