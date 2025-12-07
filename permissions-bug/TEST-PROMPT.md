# Test Prompt for Bug Reproduction

Copy and paste this prompt into Claude Code to reproduce the bug:

---

## For VS Code Extension

```
run: echo "test-20"
```

**What you should observe:**
- The command runs immediately without prompting you
- Output: `test-20`

**What SHOULD happen (per CLI behavior):**
- You should see a permission prompt asking "Do you want to proceed?"
- The prompt should show the hook's reason: "TEST-20: Hook asking, echo is in allow list"

---

## For CLI (To Compare)

The devcontainer automatically installs Claude CLI. Open terminal and run:

```bash
claude
```

Then send:

```
run: echo "test-20"
```

**What you'll observe:**
- Permission prompt appears with the message from the hook
- You can choose to approve or deny
- This is the CORRECT behavior that VS Code should match

**Note**: On first run, you may need to authenticate with `claude auth`

---

## Additional Tests (Optional)

After testing the basic case above, you can test these variations (each requires a new Claude Code session):

### Test 21: Hook "ask" + Permission "deny"

**Setup**: First move `Bash(echo:*)` from `allow` to `deny` in [.claude/settings.json](../.claude/settings.json#L62)

```
run: echo "test-21"
```

**Expected in CLI**: Prompts user (hook wins)
**Actual in VS Code**: Denied without prompt (permission system wins)

### Test 24: Hook "allow" format (should work)

**Setup**: Ensure `Bash(echo:*)` is in `deny` list

```
run: echo "test-24"
```

**Expected**: Runs in BOTH CLI and VS Code (hook overrides deny)
**Actual**: Works consistently ✓

### Test 25: Hook "deny" format (should work)

**Setup**: Move `Bash(echo:*)` back to `allow` list

```
run: echo "test-25"
```

**Expected**: Blocked in BOTH CLI and VS Code (hook overrides allow)
**Actual**: Works consistently ✓

---

## Quick Verification

If you see `test-20` output immediately without a prompt in VS Code, the bug is confirmed.

The hook is configured at [.claude/hooks/workspace-guard.py:403](../.claude/hooks/workspace-guard.py#L403) to return `permissionDecision: "ask"` for any command containing `test-20`.

See [REPRODUCE.md](REPRODUCE.md) for detailed analysis and [bug-report.md](bug-report.md) for the full bug report.
