#!/bin/bash
# Install Claude CLI in the devcontainer

set -e

echo "Installing Claude CLI..."

# Download and install the latest Claude CLI
# Using the official installation method from Claude Code docs
curl -fsSL https://claude.ai/install.sh | bash

# Verify installation
if command -v claude &> /dev/null; then
    echo "✓ Claude CLI installed successfully"
    claude --version
else
    echo "✗ Claude CLI installation failed"
    exit 1
fi

echo "Claude CLI is ready for use!"
echo "Note: You'll need to authenticate with 'claude auth' on first use"
