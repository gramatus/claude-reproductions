# Devcontainer Setup for Claude Code Bug Reproductions

This devcontainer is configured to make it easy to reproduce Claude Code bugs in GitHub Codespaces or any VS Code devcontainer environment.

## What's Included

### Automatic Installation
- **Python 3.11** - For running hook scripts
- **Claude Code VS Code Extension** - For testing extension behavior
- **Claude CLI** - For comparing CLI vs extension behavior
- **Prettier** - For code formatting

### Post-Create Setup

When the container is created, it automatically runs [install-claude-cli.sh](install-claude-cli.sh) which:
1. Downloads and installs the latest Claude CLI
2. Verifies the installation
3. Makes `claude` command available in the terminal

## First Time Use

### Authenticate Claude CLI

On first run, you'll need to authenticate:

```bash
claude auth
```

This allows you to compare CLI behavior with the VS Code extension behavior.

### Verify Setup

```bash
# Check Claude CLI is installed
claude --version

# Check Python for hooks
python3 --version

# Verify hook script exists
ls -la ../.claude/hooks/workspace-guard.py
```

## Testing Bug Reproductions

See the specific bug directories for test instructions:
- [permissions-bug/](../permissions-bug/) - Hook "ask" decision ignored in VS Code extension

## Rebuilding the Container

If you need to rebuild after changes to devcontainer.json:

**In VS Code:**
1. Open Command Palette (Cmd/Ctrl + Shift + P)
2. Select "Dev Containers: Rebuild Container"

**In GitHub Codespaces:**
1. The container rebuilds automatically on next launch
2. Or use the Command Palette method above

## Troubleshooting

### Claude CLI not found

If `claude` command is not available after container creation:

```bash
# Manually run the installation script
bash .devcontainer/install-claude-cli.sh
```

### Hook not working

Hooks are cached at session start. To test hook changes:
1. Close the Claude Code panel
2. Reopen it (or restart VS Code)
3. Run your test command

### Permission denied on script

The install script should be executable. If not, git will preserve the executable bit when you commit and push it with:

```bash
git add --chmod=+x .devcontainer/install-claude-cli.sh
```
