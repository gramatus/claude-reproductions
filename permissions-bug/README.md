# Permissions Bug Reproduction

**Bug**: VS Code Extension ignores `hookSpecificOutput.permissionDecision: "ask"` from PreToolUse hooks

## Quick Start

### One-Command Test

In Claude Code (VS Code Extension), run:

```
run: echo "test-20"
```

**Expected**: Permission prompt
**Actual**: Runs silently (bug confirmed)

### Compare with CLI

Open terminal:

```bash
claude
> run: echo "test-20"
```

**Result**: Shows permission prompt ✓ (correct behavior)

## Documentation

- **[TEST-PROMPT.md](TEST-PROMPT.md)** - Copy-paste test commands
- **[REPRODUCE.md](REPRODUCE.md)** - Detailed reproduction guide with test matrix
- **[bug-report.md](bug-report.md)** - Full bug report with analysis
- **[WORKSPACE-GUARD-TESTING.md](WORKSPACE-GUARD-TESTING.md)** - Complete test results

## How It Works

1. Hook detects `test-20` in command
2. Returns `{"hookSpecificOutput": {"permissionDecision": "ask"}}`
3. **CLI**: Shows prompt with hook's reason ✓
4. **VS Code**: Ignores "ask", uses permission list instead ✗

## Environment

The devcontainer includes:
- Claude CLI (auto-installed)
- Python 3.11 (for hooks)
- Claude Code VS Code Extension
- Pre-configured hooks and permissions

See [../.devcontainer/README.md](../.devcontainer/README.md) for setup details.

## Impact

**Security gap**: Hooks cannot enforce "ask before executing" policies in VS Code Extension, only in CLI.

## Test Matrix

| Hook Decision | Permission | CLI          | VS Code      | Consistent? |
|--------------|------------|--------------|--------------|-------------|
| `"ask"`      | allow      | **Prompts**  | Runs silently| ✗          |
| `"ask"`      | deny       | **Prompts**  | Denied       | ✗          |
| `"allow"`    | deny       | Runs         | Runs         | ✓          |
| `"deny"`     | allow      | Blocked      | Blocked      | ✓          |

See [REPRODUCE.md](REPRODUCE.md) for full details and root cause analysis.
