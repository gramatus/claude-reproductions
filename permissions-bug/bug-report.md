# [BUG] VS Code Extension Ignores Hook `permissionDecision: "ask"`

Copy-paste content for the GitHub issue template fields:

---

## What's Wrong?

The VS Code extension ignores `hookSpecificOutput.permissionDecision: "ask"` from PreToolUse hooks. The CLI correctly prompts the user for permission, but VS Code silently falls back to permission rules.

This creates a security gap: hooks cannot enforce "ask before executing" policies in VS Code, only in CLI.

Hook decisions `"allow"`, `"deny"`, `"approve"`, `"block"` all work consistently in both interfaces—only `"ask"` is broken.

---

## What Should Happen?

When a hook returns `permissionDecision: "ask"`, VS Code should show a permission prompt (same as CLI does).

---

## Steps to Reproduce

1. Fork and open in GitHub Codespaces: https://github.com/gramatus/claude-reproductions
2. In Claude Code (VS Code extension), run: `run: echo "test-20"`
3. Observe: command runs silently without prompting
4. Compare with CLI: open terminal, run `claude`, then `run: echo "test-20"`
5. Observe: CLI correctly shows permission prompt

See full test matrix: https://github.com/gramatus/claude-reproductions/blob/main/permissions-bug/REPRODUCE.md

---

## Is this a regression?

I don't know

---

## Claude Code Version

2.0.61

---

## Platform

Anthropic API

---

## Operating System

Ubuntu/Debian Linux

---

## Terminal/Shell

VS Code integrated terminal

---

## Additional Information

**Workaround**: Use `{"decision": "block"}` instead of `"ask"`. Works in both environments but removes case-by-case approval.

**Related issues**:
- #12604 - Extension ignores permission settings
- #13028 - Permissions in settings.local.json not respected

**Full reproduction repo**: https://github.com/gramatus/claude-reproductions/tree/main/permissions-bug
