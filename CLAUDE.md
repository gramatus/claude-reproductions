# Agent Instructions

## Quick Reference

| Need help with...         | Read this file                                        |
| ------------------------- | ----------------------------------------------------- |
| Task progress logging     | [task-logging.md](agent-common/task-logging.md)       |

## Core Rules (Always Apply)

1. **Think first, act later** - Reason before implementing. Start with assumptions → evidence → options → trade-offs → decision
2. **Two strikes rule** - Two failed fixes → stop and add logging before trying a third
3. **Ask before modifying** - First action in a session needs approval
4. **State hypotheses** - Before each fix, state what you believe the root cause is and what evidence would confirm or refute it
5. **Discuss strategic decisions** - Before implementing new patterns, architectures, or approaches that deviate from existing conventions, discuss with the user first
6. **Stop after 3 reads** - After reading 3 files without stating a hypothesis, STOP and write down your current hypothesis before continuing
7. **Log task completion** - When completing a multi-step task, log completion status (see [task-logging.md](agent-common/task-logging.md))

## Session Triggers

**Read [task-logging.md](agent-common/task-logging.md) when:**

- Completing a multi-step task with TodoWrite
- About to return control to user after implementation work

## Guide Organization

### Common Guides (`agent-common/`)

These are portable best practices that work across projects:

- **task-logging.md** - Task completion logging for multi-step work
