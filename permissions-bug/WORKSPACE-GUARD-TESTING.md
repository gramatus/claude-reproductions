# Workspace Guard Hook - Test Results

**Last Updated:** 2025-12-07

## Confirmed Hook Behaviors

| Hook Output                              | Exit | Result                                  |
| ---------------------------------------- | ---- | --------------------------------------- |
| `{"decision": "approve", "reason": "x"}` | 0    | Command runs silently                   |
| `{"decision": "block", "reason": "x"}`   | 0    | Command blocked, reason shown to Claude |
| `{"reason": "x"}` (no decision field)    | 0    | Defers to permission system             |
| stderr message                           | 2    | Command blocked, message shown          |

**Key Finding:** The `defer_to_user()` approach (JSON with reason, no decision) correctly defers to Claude Code's permission system. If the command pattern is in the `ask` list, the user sees a prompt.

## What Appears in Permission Prompts

| Source                           | Shown to User?                 |
| -------------------------------- | ------------------------------ |
| Bash tool `description`          | Yes - appears in prompt        |
| Hook `reason` (defer mode)       | No - not shown                 |
| Hook `reason` (block mode)       | No - shown to Claude, not user |
| Hook `hookSpecificOutput` reason | No - not shown to user         |

## Current Settings

```json
{
  "permissions": {
    "allow": ["Bash(git status:*)", "Bash(pwd)", ...],
    "ask": ["Bash(echo:*)"],
    "deny": ["Bash(curl:*)", "Bash(wget:*)", ...]
  }
}
```

---

## Test Protocol

### Important: Claude Cannot See Permission Prompts

After running a test command, Claude MUST:

1. **STOP** - Do not fill in results
2. **ASK** the user to report what they observed
3. **WAIT** for user response before recording results

Only the user can report:

- Was there a prompt?
- What was the prompt text?
- What options were shown?
- What did they select?

---

## Test Results

| Test | Hook Function        | Hook Output                                | Command          | Prompted?      | Executed? | Notes                                   |
| ---- | -------------------- | ------------------------------------------ | ---------------- | -------------- | --------- | --------------------------------------- |
| 11   | `allow_command()`    | `{"decision": "approve", "reason": "..."}` | `echo "test-11"` | No             | Yes       | Approve bypasses permission system      |
| 12   | `defer_to_user()`    | `{"reason": "..."}` (no decision)          | `echo "test-12"` | **Yes**        | Yes       | Defer works - triggers ask list         |
| 13   | `ask_user()`         | `{"hookSpecificOutput": {...}}`            | `echo "test-13"` | **Yes**        | Yes       | Only Bash desc shown, not hook reason   |
| 14   | `block_for_review()` | `{"decision": "block", "reason": "..."}`   | `echo "test-14"` | No             | No        | Block works - reason shown to Claude    |
| 15   | `block_command()`    | stderr + exit 2                            | `echo "test-15"` | No             | No        | Block works - stderr shown to Claude    |
| 16   | (normal logic)       | block (exit 2)                             | `echo \| curl`   | No             | No        | Hook blocks pipe to denied command      |
| 17   | (normal logic)       | block (exit 2)                             | `echo && curl`   | No             | No        | Hook blocks chain to denied command     |
| 18   | `defer_to_user()`    | `{"reason": "..."}` (no decision)          | `echo \| curl`   | No             | No        | Permission system denied `curl` in pipe |
| 19   | `defer_to_user()`    | `{"reason": "..."}` (no decision)          | `echo && curl`   |                |           | Defer chain - test permission system    |
| 20   | `ask_user()`         | `{"hookSpecificOutput": {...}}`            | `echo "test-20"` | CLI:Yes VSC:No | Yes       | **CLI/VSC differ** - see notes below    |
| 21   | `ask_user()`         | `{"hookSpecificOutput": {...}}`            | `echo "test-21"` | CLI:Yes VSC:No | CLI:Yes VSC:No | **CLI/VSC differ** - deny wins in VSC   |
| 22   | `allow_command()`    | `{"decision": "approve", ...}`             | `echo "test-22"` | No             | Yes       | **Hook wins** - approve overrides deny  |
| 23   | `block_for_review()` | `{"decision": "block", ...}`               | `echo "test-23"` | No             | No        | **Hook wins** - block overrides allow   |
| 24   | `allow_hookspec()`   | `{"hookSpecificOutput": {permissionDecision: "allow"}}` | `echo "test-24"` | No             | Yes       | **Consistent** - hook wins in both envs |
| 25   | `deny_hookspec()`    | `{"hookSpecificOutput": {permissionDecision: "deny"}}`  | `echo "test-25"` | No             | No        | **Consistent** - hook wins in both envs |

---

## Test Commands

Each test requires a **new session** (hook config is cached at session start).

```bash
# Test 11: approve decision (should run silently)
echo "test-11"

# Test 12: defer with reason (should prompt if in ask list)
echo "test-12"

# Test 13: hookSpecificOutput format
# IMPORTANT: Use description "FROM-BASH-DESC" to distinguish from hook output
# Hook should output reason "FROM-HOOK-OUTPUT" in hookSpecificOutput
# Check which text(s) appear in the prompt
echo "test-13"

# Test 14: block decision
echo "test-14"

# Test 15: exit 2 with stderr
echo "test-15"

# Test 16: pipe to denied command (normal logic - should block)
echo "x" | curl localhost

# Test 17: chain to denied command (normal logic - should block)
echo "x" && curl localhost

# Test 18: pipe to denied command (defer to permission system)
echo "test-18" | curl localhost

# Test 19: chain to denied command (defer to permission system)
echo "test-19" && curl localhost

# Test 20: Hook ask + echo in ALLOW list (requires settings change)
echo "test-20"

# Test 21: Hook ask + echo in DENY list (requires settings change)
echo "test-21"

# Test 22: Hook approve + echo in DENY list (requires settings change)
echo "test-22"

# Test 23: Hook block + echo in ALLOW list (requires settings change)
echo "test-23"

# Test 24: hookSpecificOutput allow + echo in DENY list (requires settings change)
echo "test-24"

# Test 25: hookSpecificOutput deny + echo in ALLOW list (requires settings change)
echo "test-25"
```

---

## Hook Functions Reference

```python
allow_command(reason)      # {"decision": "approve", "reason": "..."} - runs silently
defer_to_user(reason)      # {"reason": "..."} - defers to permission system
ask_user(reason)           # {"hookSpecificOutput": {permissionDecision: "ask"}} - prompts in CLI only
block_for_review(reason)   # {"decision": "block", "reason": "..."} - blocks, reason to Claude
block_command(issues)      # exit 2 + stderr - blocks, message shown
allow_hookspec(reason)     # {"hookSpecificOutput": {permissionDecision: "allow"}} - test format
deny_hookspec(reason)      # {"hookSpecificOutput": {permissionDecision: "deny"}} - test format
```

---

## Test 18 Analysis

**Key Finding:** When hook defers (`{"reason": "..."}` with no decision), Claude Code's permission system:

1. Parses the full command including pipes
2. Identifies `curl localhost` as a subcommand
3. Applies the deny rule for `curl`
4. Error message: "Permission to use Bash with command curl localhost has been denied"

This confirms the permission system is smarter than prefix-matching when evaluating commands.

---

## Investigation Plan: Hook Defer Behavior

### Goals

1. Make redirects trigger ask prompts
2. Allow normal echo commands (no pipes/chains) silently
3. Everything else follows normal permission system

### Open Questions

| #   | Question                                       | Test Approach                                           |
| --- | ---------------------------------------------- | ------------------------------------------------------- |
| Q1  | Does `ask_user()` actually ask, or just defer? | Compare Test 13 behavior with echo in ask vs allow list |
| Q2  | CLI vs VS Code extension differences?          | Run same test in both environments                      |
| Q3  | Hook "ask" + echo in allow list → ?            | Test 20: Set echo in allow, hook returns ask            |
| Q4  | Hook "ask" + echo in deny list → ?             | Test 21: Set echo in deny, hook returns ask             |
| Q5  | Hook "allow" + echo in deny list → ?           | Test 22: Set echo in deny, hook returns approve         |
| Q6  | Hook "deny" + echo in allow list → ?           | Test 23: Set echo in allow, hook returns block          |

### Proposed Tests

#### Test 20: Hook Ask + Permission Allow

**Setup:**

- Move `Bash(echo:*)` from `ask` to `allow` list
- Hook returns `ask_user("reason")` for `test-20`

**Command:** `echo "test-20"`

**Question:** Does hook's "ask" override the allow list?

---

#### Test 21: Hook Ask + Permission Deny

**Setup:**

- Move `Bash(echo:*)` to `deny` list
- Hook returns `ask_user("reason")` for `test-21`

**Command:** `echo "test-21"`

**Question:** Does hook's "ask" override the deny list?

---

#### Test 22: Hook Allow + Permission Deny

**Setup:**

- `Bash(echo:*)` in `deny` list
- Hook returns `allow_command("reason")` for `test-22`

**Command:** `echo "test-22"`

**Question:** Does hook's "approve" override the deny list?

---

#### Test 23: Hook Deny + Permission Allow

**Setup:**

- `Bash(echo:*)` in `allow` list
- Hook returns `block_for_review("reason")` for `test-23`

**Command:** `echo "test-23"`

**Question:** Does hook's "block" override the allow list?

---

#### Test 24: hookSpecificOutput Allow + Permission Deny

**Setup:**

- `Bash(echo:*)` in `deny` list
- Hook returns `allow_hookspec("reason")` for `test-24`

**Command:** `echo "test-24"`

**Question:** Does hookSpecificOutput's "allow" work like `{"decision": "approve"}`?

---

#### Test 25: hookSpecificOutput Deny + Permission Allow

**Setup:**

- `Bash(echo:*)` in `allow` list
- Hook returns `deny_hookspec("reason")` for `test-25`

**Command:** `echo "test-25"`

**Question:** Does hookSpecificOutput's "deny" work like `{"decision": "block"}`?

---

### Test Matrix

| Test | Hook Format         | Hook Decision | Permission List | Expected | Actual                     |
| ---- | ------------------- | ------------- | --------------- | -------- | -------------------------- |
| 20   | hookSpecificOutput  | ask           | allow           | ?        | CLI: Hook, VSC: Permission |
| 21   | hookSpecificOutput  | ask           | deny            | ?        | CLI: Hook, VSC: Permission |
| 22   | decision            | approve       | deny            | ?        | **Hook** (both envs)       |
| 23   | decision            | block         | allow           | ?        | **Hook** (both envs)       |
| 24   | hookSpecificOutput  | allow         | deny            | ?        | **Hook** (both envs)       |
| 25   | hookSpecificOutput  | deny          | allow           | ?        | **Hook** (both envs)       |

### Hypothesis Based on Existing Evidence

From tests 11-18, we know:

- `approve` → runs silently (Test 11)
- `block` → blocked (Tests 14, 15)
- `defer` + `ask` list → prompts (Test 12)

**Predicted precedence:**

1. Hook `block` always wins (highest priority)
2. Hook `approve` always wins
3. Hook defer/ask → permission system decides
4. Permission system: deny > ask > allow

---

## Test 20 Analysis: CLI vs VS Code Extension

**Finding:** `hookSpecificOutput` format behaves differently across environments.

| Environment       | Hook Output  | Permission | Winner         | Behavior      |
| ----------------- | ------------ | ---------- | -------------- | ------------- |
| CLI               | `ask_user()` | allow      | **Hook**       | Prompted user |
| VS Code Extension | `ask_user()` | allow      | **Permission** | Ran silently  |

**Implication:** The `hookSpecificOutput` format is unreliable for enforcing user confirmation in VS Code extension. For consistent behavior across both environments:

- Use `{"decision": "block", ...}` to always block
- Use `{"decision": "approve", ...}` to always allow
- Use `{"reason": "..."}` (no decision) to defer to permission system

The `hookSpecificOutput` format appears to only work in CLI.

---

## Test 21 Analysis: Hook Ask vs Permission Deny

**Finding:** When hook returns `ask_user()` but command is in deny list:

| Environment       | Hook Output  | Permission | Winner         | Behavior                    |
| ----------------- | ------------ | ---------- | -------------- | --------------------------- |
| CLI               | `ask_user()` | deny       | **Hook**       | Prompted user, ran on "Yes" |
| VS Code Extension | `ask_user()` | deny       | **Permission** | Denied without prompt       |

**Key Insight:** This confirms the CLI/VSCode divergence is consistent:

- **CLI:** Hook's `hookSpecificOutput` triggers a prompt regardless of permission list
- **VSCode:** Permission list is evaluated first; deny blocks before hook can ask

This reinforces that `hookSpecificOutput` should not be relied upon for critical security decisions in VS Code extension environment.

---

## Test 22 Analysis: Hook Approve vs Permission Deny

**Finding:** Hook's `{"decision": "approve", ...}` overrides permission system's deny list.

| Environment       | Hook Output        | Permission | Winner   | Behavior     |
| ----------------- | ------------------ | ---------- | -------- | ------------ |
| CLI               | `allow_command()`  | deny       | **Hook** | Ran silently |
| VS Code Extension | `allow_command()`  | deny       | **Hook** | Ran silently |

**Key Insight:** Unlike `hookSpecificOutput` (which differs between CLI/VSC), the `{"decision": "approve"}` format is respected consistently across both environments.

**Security Implication:** Hooks have ultimate authority. A hook returning "approve" can bypass the deny list entirely. This is powerful but requires careful hook implementation - a bug in hook logic could allow denied commands to execute.

---

## Test 24 Analysis: hookSpecificOutput Allow vs Permission Deny

**Finding:** `hookSpecificOutput` with `permissionDecision: "allow"` overrides deny list in **both** environments.

| Environment       | Hook Output        | Permission | Winner   | Behavior     |
| ----------------- | ------------------ | ---------- | -------- | ------------ |
| CLI               | `allow_hookspec()` | deny       | **Hook** | Ran silently |
| VS Code Extension | `allow_hookspec()` | deny       | **Hook** | Ran silently |

**Key Insight:** Unlike `permissionDecision: "ask"` (which behaves inconsistently), `permissionDecision: "allow"` is respected consistently across both environments - matching the behavior of `{"decision": "approve"}`.

**Summary of hookSpecificOutput consistency:**

- `"allow"` - Consistent (hook wins in both)
- `"deny"` - Consistent (hook wins in both)
- `"ask"` - **Inconsistent** (CLI honors hook, VS Code ignores it)

---

## Test 25 Analysis: hookSpecificOutput Deny vs Permission Allow

**Finding:** `hookSpecificOutput` with `permissionDecision: "deny"` blocks command in **both** environments.

| Environment       | Hook Output       | Permission | Winner   | Behavior |
| ----------------- | ----------------- | ---------- | -------- | -------- |
| CLI               | `deny_hookspec()` | allow      | **Hook** | Blocked  |
| VS Code Extension | `deny_hookspec()` | allow      | **Hook** | Blocked  |

**Key Insight:** Unlike `permissionDecision: "ask"` (which only works in CLI), `permissionDecision: "deny"` is respected consistently across both environments.

**Updated hookSpecificOutput behavior matrix:**

| permissionDecision | CLI            | VS Code        | Consistent? |
| ------------------ | -------------- | -------------- | ----------- |
| `"ask"`            | Hook wins      | Permission wins | No          |
| `"deny"`           | Hook wins      | Hook wins       | **Yes**     |
| `"allow"`          | Hook wins      | Hook wins       | **Yes**     |

---

## Known Issues

1. **Pipe/chain bypass** - Hook blocks these (Test 16 confirmed). Tests 18-19 will show if permission system also catches them when hook defers.
2. **CLI/VS Code inconsistency** - `hookSpecificOutput` (ask_user) prompts in CLI but is ignored in VS Code extension (Test 20)

---

## Test 20 Rerun: VS Code Process Wrapper Configuration

**Date:** 2025-12-07

**Change:** Added VS Code setting:
```json
"claudeCode.claudeProcessWrapper": "/home/node/.local/bin/claude"
```

**Purpose:** Test if using the Claude CLI binary directly (instead of the default VS Code extension wrapper) affects hook behavior - specifically whether `hookSpecificOutput` with `permissionDecision: "ask"` will now prompt in VS Code as it does in CLI.

**Test Setup:**
- `Bash(echo:*)` in ALLOW list
- Hook returns `ask_user("TEST-20: ...")` for `test-20` commands

**Command:** `echo "test-20"`

**Expected (if wrapper matters):** User prompted (matching CLI behavior)
**Expected (if wrapper doesn't matter):** Runs silently (same as before)

| Run | Wrapper Config | Prompted? | Executed? | Notes |
| --- | -------------- | --------- | --------- | ----- |
| 1   | (default)      | No        | Yes       | Original test - permission won |
| 2   | `/home/node/.local/bin/claude` | No | Yes | Wrapper doesn't affect behavior |

**Conclusion:** The `claudeProcessWrapper` setting doesn't change hook behavior. The CLI/VS Code divergence for `hookSpecificOutput.permissionDecision: "ask"` is inherent to the VS Code extension's permission handling, not the process wrapper.

**Verified in CLI (same session):** CLI correctly shows prompt with hook reason "TEST-20: Hook asking, echo is in allow list" and "Do you want to proceed?" options. This confirms:
- CLI: `hookSpecificOutput.permissionDecision: "ask"` → **Prompts user**
- VS Code: `hookSpecificOutput.permissionDecision: "ask"` → **Ignored, permission system decides**

This is a fundamental implementation difference, not a configuration issue.
