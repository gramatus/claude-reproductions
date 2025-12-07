# Commands

How to create and manage slash commands that work across AI coding tools.

## Command Locations

| Tool           | Location            | Extension    | Invocation |
| -------------- | ------------------- | ------------ | ---------- |
| Claude Code    | `.claude/commands/` | `.md`        | `/name`    |
| GitHub Copilot | `.github/prompts/`  | `.prompt.md` | `/name`    |

## Command Structure

Both tools use similar formats: YAML frontmatter + markdown body.

```markdown
---
description: Short description shown in command list
---

# Command Title

Instructions for the AI when this command is invoked.

## Sections as needed

Details, checklists, examples, etc.
```

**Frontmatter fields:**

- `description` (required) - Used by both tools
- Copilot supports additional fields (`agent`, `model`, `tools`, `mode`) - Claude Code ignores these

## Cross-tool Compatibility

Commands can work in both Claude Code and GitHub Copilot via symlinks.

**Pattern:**

1. Create the command in `.claude/commands/name.md` (source of truth)
2. Symlink to `.github/prompts/name.prompt.md` for Copilot

```bash
# Example: make crystallize command available in both tools
ln -s ../../.claude/commands/crystallize.md .github/prompts/crystallize.prompt.md
```

**When to symlink (compatible):**

- Commands that are pure instructions/checklists
- Commands that don't rely on tool-specific features
- Commands like `/crystallize`, `/bookkeeping`

**When NOT to symlink (tool-specific):**

- Commands using `$ARGUMENTS` (Claude Code variable, may not work in Copilot)
- Commands relying on specific tool behaviors (e.g., triggering dialogs)
- Commands using tool-specific frontmatter features

## Existing Commands

| Command                  | Purpose                               | Cross-tool                |
| ------------------------ | ------------------------------------- | ------------------------- |
| `/signal-task-completed` | Signal task completion                | No (Claude Code specific) |

## Creating New Commands

1. **Decide scope**: Will this work for both tools, or is it tool-specific?

2. **Create in primary location**:

   - Cross-tool: `.claude/commands/name.md`
   - Claude-only: `.claude/commands/name.md`
   - Copilot-only: `.github/prompts/name.prompt.md`

3. **Add symlink if cross-tool**:

   ```bash
   ln -s ../../.claude/commands/name.md .github/prompts/name.prompt.md
   ```

4. **Test in both tools** if symlinked

5. **Update this table** with the new command

## Variables and Arguments

**Claude Code:**

- `$ARGUMENTS` - Captures text after command name
- Example: `/signal check this` → `$ARGUMENTS` = "check this"

**GitHub Copilot:**

- Different variable handling - test before assuming compatibility
- Commands with arguments may need tool-specific versions
