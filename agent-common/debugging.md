# Debugging Protocol

When a fix doesn't work, **do not** try another variation of the same approach. Instead, escalate your diagnostic depth.

## The Debugging Ladder (climb it, don't loop)

### Level 1: Verify assumptions

- Before fixing anything, verify the problem actually exists where you think it does
- Add logging at the entry and exit points of the suspected code path
- Confirm the code is even being executed

### Level 2: Make the invisible visible

- Ensure logs are actually reaching output (test frameworks like Jest, and tools like Backstage, often swallow console output)
- Use `--verbose` flags, configure test reporters, or write to stderr/files if needed
- When mocking: log the actual response received by the code under test - silent failures in mock consumers are common

### Level 3: Trace the actual data flow

- Log inputs, outputs, and intermediate state at each transformation step
- Don't assume what an API returns - log and verify the actual response structure
- Check for silent type coercion, undefined values being swallowed, or error handlers eating exceptions

### Level 4: Question the boundaries

- If your code looks correct, the bug may be in dependencies
- **Add logging inside node_modules** when necessary - this is faster than guessing
- Check if library versions match documentation you're referencing
- Verify environment variables and configuration are what you expect at runtime

## Rules

1. **Two strikes rule**: If you try two similar fixes and both fail, stop and add more logging before trying a third
2. **State your hypothesis**: Before each fix, explicitly write what you believe the root cause is and what evidence would confirm or refute it
3. **Preserve diagnostic code**: Don't remove logging until the bug is confirmed fixed; comment it out if it's noisy
4. **Admit uncertainty**: Say "I'm not sure what's causing this yet" rather than guessing repeatedly

---

## Reasoning Discipline

When facing a decision between approaches:

1. First, list the options without evaluating them
2. Define your evaluation criteria explicitly
3. Evaluate each option against the criteria once
4. Make a decision and commit to it

Do not revisit a decision unless genuinely new information emerges. If uncertain, state "I'm uncertain between X and Y because [tradeoff]" rather than oscillating between options.

---

## Session Management & Context Hygiene

Long debugging sessions accumulate noise: failed attempts, abandoned hypotheses, contradictory observations. This degrades reasoning quality. Use the following mechanisms to manage this.

### User-Triggered Reset

When the user says any of the following (or similar variations), immediately generate a handoff document:

- "handoff", "session handoff", "debug handoff"
- "fresh start", "let's reset", "start fresh"
- "summarize for new session"
- "context is getting noisy"
- "write a summary so we can continue in a new chat"

### Self-Triggered Reset

Proactively suggest a session reset when you notice:

- You've attempted 5+ fixes without clear progress
- You're revisiting hypotheses you already explored
- Your reasoning is oscillating between the same options
- The conversation has exceeded ~50 back-and-forth exchanges on the same problem
- You catch yourself uncertain about what has already been tried

When this happens, say something like: "This session has accumulated a lot of context and I think we'd benefit from a fresh start. Want me to write a handoff document so we can continue in a new session without losing what we've learned?"

### Handoff Document Format

Write the handoff to `DEBUG-HANDOFF.md` (or a name the user specifies) with this structure:

```markdown
## Debug Handoff: [Brief Problem Description]

Generated: [timestamp]

### Problem Statement

What we're trying to fix, with exact reproduction steps.

### Confirmed Facts

Things verified with logging or direct evidence. Not assumptions.

- [fact]: [evidence that confirmed it]

### Ruled Out

Approaches tried and _why_ they failed. This prevents the next session from repeating them.

- [approach]: [why it didn't work, with evidence]

### Current Hypotheses

What we still think might be wrong, ranked by likelihood.

1. [hypothesis]: [supporting observations]

### Unexplored Avenues

Ideas we haven't tried yet.

- [idea]: [why it might help]

### Relevant Code Locations

Files and line numbers confirmed to be involved.

- `path/to/file.ts:123` - [what happens here]

### Session Notes

Any other context that would help the next session.
```

The emphasis on evidence ("confirmed", "ruled out with evidence") is critical. Without this, fresh sessions often repeat the same mistakes.

---

## Test Failure Analysis

When analyzing test failures, follow this systematic approach:

1. **Analyze each failure individually**:

   - Read the error message and stack trace carefully
   - Identify what the test expects vs. what it receives
   - Examine both the test code and the implementation code
   - Determine the root cause: is the test incorrect or is the code incorrect?

2. **Provide structured analysis**:

   - List each test failure separately
   - For each failure, state:
     - **Issue**: What is failing and why
     - **Root cause**: Whether the test is incorrect or the code is incorrect
     - **Reasoning**: Why you believe the test or code is wrong (cite constants, config paths, actual behavior, etc.)
   - **Fix**: What needs to be changed

3. **Separate fixes by category**:

   - **Test Fixes**: List all fixes for incorrect tests (when implementation is correct)
   - **Code Fixes**: List all fixes for incorrect code (when test expectations are correct)
   - Keep these in separate, clearly labeled sections

4. **Verification principles**:

   - Check against defined constants (e.g., `PROVIDER_NAME`, `PROCESSOR_NAME`)
   - Verify config paths match actual configuration structure
   - Ensure tests match the actual implementation behavior
   - Consider whether changing the test or the code makes more sense architecturally

5. **Common test issues to check**:
   - Tests using hardcoded strings instead of constants
   - Tests expecting wrong config paths
   - Tests with incorrect type assertions
   - Tests missing required config values
   - Tests with incorrect mock call counts
   - Tests checking for substrings that match comments instead of actual keys

**Example structure for reporting:**

```
## Test Failure Analysis

### Failure 1: ProcessorNameTest
- **Issue**: Test expects 'EntityMergingProcessor' but receives 'GithubVendingStitchingProcessor'
- **Root Cause**: Test is incorrect
- **Reasoning**: The constant ENTITY_MERGING_PROCESSOR_NAME is defined as 'GithubVendingStitchingProcessor' in constants.ts
- **Category**: Test Fix

### Failure 2: ConfigValidation
- **Issue**: Missing required config value 'auth.environment'
- **Root Cause**: Test is incorrect
- **Reasoning**: App.tsx reads this config but test doesn't provide it
- **Category**: Test Fix
```
