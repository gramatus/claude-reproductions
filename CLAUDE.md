# Agent Instructions

## Quick Reference

| Need help with...         | Read this file                                        |
| ------------------------- | ----------------------------------------------------- |
| Debugging / test failures | [debugging.md](agent-common/debugging.md)             |
| Git / PRs / commits       | [git-workflows.md](agent-common/git-workflows.md)     |
| Planning / context / data | [methodology.md](agent-common/methodology.md)         |
| Task progress logging     | [task-logging.md](agent-common/task-logging.md)       |
| Slash commands            | [commands.md](agent-common/commands.md)               |

## Core Rules (Always Apply)

1. **Think first, act later** - Reason before implementing. Start with assumptions → evidence → options → trade-offs → decision
2. **Two strikes rule** - Two failed fixes → stop and add logging before trying a third
3. **Ask before modifying** - First action in a session needs approval
4. **State hypotheses** - Before each fix, state what you believe the root cause is and what evidence would confirm or refute it
5. **Discuss strategic decisions** - Before implementing new patterns, architectures, or approaches that deviate from existing conventions, discuss with the user first
6. **Stop after 3 reads** - After reading 3 files without stating a hypothesis, STOP and write down your current hypothesis before continuing
7. **Log task completion** - When completing a multi-step task, log completion status (see [task-logging.md](agent-common/task-logging.md))

## Session Triggers

**Read [debugging.md](agent-common/debugging.md) when:**

- Session mentions "fix attempts", "still failing", "not working"
- `DEBUG-HANDOFF.md` exists in the project root
- About to try a third fix for the same issue
- You've been going in circles on a problem

**Read [git-workflows.md](agent-common/git-workflows.md) when:**

- User requests "pr review", "review this pr", or similar
- User requests "pr summary", "summary for teammates", or similar
- Writing commit messages

**Read [methodology.md](agent-common/methodology.md) when:**

- **Not absolutely sure how to proceed** - search first, don't guess
- Planning a feature, architecture, or significant change
- About to implement based on assumed API/framework behavior
- Discussing package compatibility, versions, or framework capabilities
- Stuck after 2-3 failed attempts (trigger web research)
- Creating mock data, fixtures, or test data for external APIs
- About to say "you should verify" or "check the documentation"

**Read [commands.md](agent-common/commands.md) when:**

- Creating a new slash command
- Making a command work across Claude Code and GitHub Copilot
- Working with command arguments or variables

**Read [task-logging.md](agent-common/task-logging.md) when:**

- Completing a multi-step task with TodoWrite
- About to return control to user after implementation work

## Guide Organization

### Common Guides (`agent-common/`)

These are portable best practices that work across projects:

- **debugging.md** - Debugging protocol, two-strikes rule, hypothesis-driven debugging, test failure analysis, session handoffs
- **methodology.md** - Planning vs implementation, context management, mock data approach, web research
- **git-workflows.md** - PR reviews, PR summaries, commit messages, Norwegian translation guidelines
- **task-logging.md** - Task completion logging for multi-step work
- **commands.md** - Slash command patterns, cross-tool compatibility, symlink approach
