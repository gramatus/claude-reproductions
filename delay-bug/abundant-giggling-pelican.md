# Plan: Agent Instructions Refactor - Slash Commands & Documentation Cleanup

## Summary

Refactor agent instructions to:
1. Move procedural workflows from reference docs into slash commands
2. Slim down CLAUDE.md by moving task logging to a separate file
3. Make web research guidance tool-agnostic
4. Update all cross-references

---

## Changes Overview

### New Files to Create

| File | Purpose |
|------|---------|
| `.github/agent-common/task-logging.md` | Task completion logging (extracted from CLAUDE.md) |
| `.claude/commands/pr-review.md` | `/pr-review` slash command |
| `.claude/commands/pr-summary.md` | `/pr-summary` slash command |
| `.claude/commands/commit.md` | `/commit` slash command |
| `.claude/commands/handoff.md` | `/handoff` slash command |
| `.claude/commands/save.md` | `/save` slash command |

### Symlinks to Create

```bash
ln -sf ../../.claude/commands/pr-review.md .github/prompts/pr-review.prompt.md
ln -sf ../../.claude/commands/pr-summary.md .github/prompts/pr-summary.prompt.md
ln -sf ../../.claude/commands/commit.md .github/prompts/commit.prompt.md
ln -sf ../../.claude/commands/handoff.md .github/prompts/handoff.prompt.md
ln -sf ../../.claude/commands/save.md .github/prompts/save.prompt.md
```

### Files to Modify

| File | Changes |
|------|---------|
| `CLAUDE.md` | Remove Task Completion Logging section (~45 lines), add task-logging.md to Quick Reference and triggers |
| `.github/agent-common/git-workflows.md` | Remove PR Review and PR Summary procedures, keep reference material only |
| `.github/agent-common/debugging.md` | Slim down Session Management section, reference `/handoff` command |
| `.github/agent-common/methodology.md` | Make Web Research section tool-agnostic |
| `.github/agent-common/commands.md` | Add new commands to Existing Commands table |

---

## Detailed Implementation

### 1. Create task-logging.md

**File:** `.github/agent-common/task-logging.md`

Extract the Task Completion Logging section from CLAUDE.md into this new file. Content includes:
- Purpose explanation (UI rendering delay bug)
- When to log table (todo completion, final completion)
- How to log (bash commands for step and final completion)
- Example session
- User monitoring command (`watch -n 1 cat .cache/claude-status.txt`)
- Why the final signal matters

### 2. Update CLAUDE.md

**Changes:**
1. Add to Quick Reference table:
   ```
   | Task progress logging     | [task-logging.md](agent-common/task-logging.md)       |
   ```

2. Replace Core Rule #7 reference:
   ```
   7. **Log task completion** - When completing a multi-step task, log completion status (see [task-logging.md](agent-common/task-logging.md))
   ```

3. Remove entire "## Task Completion Logging" section (lines 26-70 approximately)

4. Add session trigger:
   ```
   **Read [task-logging.md](agent-common/task-logging.md) when:**

   - Completing a multi-step task with TodoWrite
   - About to return control to user after implementation work
   ```

5. Add to Guide Organization list:
   ```
   - **task-logging.md** - Task completion logging for multi-step work
   ```

### 3. Create Slash Commands

#### 3a. `/pr-review` command

**File:** `.claude/commands/pr-review.md`

```markdown
---
description: Perform comprehensive code review of current branch
---

# PR Review

Comprehensive code review of the current branch against the main branch.

## Process

1. **Analyze the diff**:
   - Fetch latest and compare against `origin/main`
   - Run: `git fetch origin && git diff origin/main...HEAD`
   - Review summary to understand scope and file changes
   - Read full diff for detailed line-by-line analysis

2. **Provide comprehensive review covering**:
   - Overview, Files changed summary, Detailed analysis by file
   - Cross-cutting concerns (architecture, code quality, security, performance, backwards compatibility)
   - Risk assessment (Low/Medium/High)
   - Testing recommendations
   - Final recommendation (Approve / Request changes / Needs discussion)

3. **Review principles**:
   - Be thorough but constructive
   - Cite specific files and line numbers
   - Distinguish blocking issues from nice-to-haves

4. **After review**: Remind about `/bookkeeping`
```

#### 3b. `/pr-summary` command

**File:** `.claude/commands/pr-summary.md`

```markdown
---
description: Generate team-focused PR summary in English and Norwegian
---

# PR Summary

Create team-focused summaries for colleague review.

## Output Files
- `PR-SUMMARY.md` - English version
- `PR-SUMMARY-NO.md` - Norwegian version

## Process
1. Analyze changes (fetch, diff, log)
2. Create both summary files with document structure
3. Reference git-workflows.md for Norwegian translation guidelines

## After Writing
- Provide clickable links to both files
- Remind about `/bookkeeping`
```

#### 3c. `/commit` command

**File:** `.claude/commands/commit.md`

```markdown
---
description: Generate conventional commit message from staged changes
---

# Generate Commit Message

1. Get staged diff: `git diff --cached`
2. Analyze changes (type, purpose)
3. Generate conventional commit message

## Format
- Type prefixes: feat, fix, docs, refactor, test, chore
- Subject ≤50 chars, max 72
- Imperative mood
- Work item in scope: `type(AB#12345): subject`
```

#### 3d. `/handoff` command

**File:** `.claude/commands/handoff.md`

```markdown
---
description: Create debug handoff document for fresh session
---

# Debug Handoff

Create structured handoff document to preserve debugging context.

## When to Use
- 5+ fix attempts without progress
- Revisiting explored hypotheses
- Oscillating between same options
- ~50 exchanges on same problem

## Document Format (DEBUG-HANDOFF.md)
- Problem Statement
- Confirmed Facts (with evidence)
- Ruled Out (with reasons)
- Current Hypotheses (ranked)
- Unexplored Avenues
- Relevant Code Locations
- Session Notes
```

#### 3e. `/save` command

**File:** `.claude/commands/save.md`

```markdown
---
description: Save conversation transcript to file
---

# Save Conversation

Save current conversation as markdown transcript.

## Process
1. Generate filename: `YYYY-MM-DD-slug.md`
2. Create in `conversations/` folder
3. Check for sensitive content

## Format
- Title, timestamp
- Full chronological transcript
- Q/A format with markdown formatting
```

### 4. Update git-workflows.md

**Replace entire file** with slimmed version:
- Keep: Getting the diff section
- Keep: Commit Messages section (reference material for `/commit`)
- Keep: Norwegian Translation Guidelines (reference for `/pr-summary`)
- **Remove**: PR Review section (moved to `/pr-review`)
- **Remove**: PR Summary section (moved to `/pr-summary`)
- **Remove**: Combined Workflow section (redundant)
- **Add**: Header referencing the new slash commands

### 5. Update debugging.md

**Replace Session Management section** (lines 54-128) with slimmed version:
- Keep: When to Reset triggers
- **Remove**: Detailed handoff document format
- **Add**: Reference to `/handoff` command

### 6. Update methodology.md

**Replace Web Research section** (lines 69-110) with tool-agnostic version:

```markdown
## Web Research

When a question requires current documentation, compatibility checks, or external package information.

### If Web Search is Available (Claude Code)
- Use web search directly
- Search proactively
- Cite sources

### If Web Search is Not Available (VS Code Copilot)
- Acknowledge limitation
- Provide specific research prompt for user
- Continue with workspace-based analysis

### When to Search (All Tools)
[Keep existing trigger list]
```

### 7. Update commands.md

**Update Existing Commands table:**

```markdown
| Command                  | Purpose                               | Cross-tool                |
| ------------------------ | ------------------------------------- | ------------------------- |
| `/crystallize`           | Capture session understanding         | Yes (symlinked)           |
| `/bookkeeping`           | Review context and instruction health | Yes (symlinked)           |
| `/pr-review`             | Comprehensive code review             | Yes (symlinked)           |
| `/pr-summary`            | Team-focused PR summary (EN + NO)     | Yes (symlinked)           |
| `/commit`                | Generate conventional commit message  | Yes (symlinked)           |
| `/handoff`               | Create debug handoff document         | Yes (symlinked)           |
| `/save`                  | Save conversation transcript          | Yes (symlinked)           |
| `/signal-task-completed` | Signal task completion                | No (Claude Code specific) |
```

---

## Implementation Order

1. Create `task-logging.md`
2. Update `CLAUDE.md`
3. Create all 5 slash commands
4. Create symlinks for Copilot
5. Update `git-workflows.md`
6. Update `debugging.md`
7. Update `methodology.md`
8. Update `commands.md`

---

## Expected Outcomes

- CLAUDE.md reduced by ~45 lines
- git-workflows.md reduced from ~262 to ~112 lines
- debugging.md reduced by ~50 lines
- 5 new slash commands available in both Claude Code and Copilot
- Web research guidance works for both tools
