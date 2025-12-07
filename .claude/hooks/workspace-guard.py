#!/usr/bin/env python3
"""
Workspace Protection Hook for Claude Code

Prevents Bash commands from affecting files outside the current workspace.
- Blocks (exit 2): Commands targeting system directories or outside workspace
- Asks (JSON output): Commands with output redirects (even inside workspace)
- Allows (exit 0): Everything else
"""
import json
import sys
import os
import re
from pathlib import Path


def get_workspace_root():
    """Get the workspace root directory."""
    return os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())


def load_settings():
    """Load settings.json from the .claude directory."""
    workspace_root = get_workspace_root()
    settings_path = os.path.join(workspace_root, '.claude', 'settings.json')
    try:
        with open(settings_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def parse_bash_permission_patterns(permission_list):
    """Extract command names from Bash permission patterns.

    Parses patterns like "Bash(sudo:*)" -> "sudo"
    Returns list of (regex_pattern, command_name) tuples.
    """
    commands = []
    pattern = re.compile(r'^Bash\(([^:)]+)(?::\*)?\)$')

    for item in permission_list:
        match = pattern.match(item)
        if match:
            cmd_name = match.group(1)
            # Create regex pattern for the command
            regex = rf'\b{re.escape(cmd_name)}\b'
            commands.append((regex, cmd_name))

    return commands


def get_denied_commands():
    """Get list of denied commands from settings.json.

    Returns list of (regex_pattern, command_name) tuples.
    Includes both 'deny' and 'ask' permissions since both should
    be flagged when bypassing prefix matching via pipes/chains.
    """
    settings = load_settings()
    permissions = settings.get('permissions', {})

    deny_list = permissions.get('deny', [])
    ask_list = permissions.get('ask', [])

    # Combine both lists - commands in ask should also be flagged
    # when they appear in pipes/chains (bypassing prefix matching)
    all_restricted = deny_list + ask_list

    commands = parse_bash_permission_patterns(all_restricted)

    # Fallback to hardcoded list if settings couldn't be loaded
    if not commands:
        return [
            (r'\bcurl\b', 'curl'),
            (r'\bwget\b', 'wget'),
            (r'\bnc\b', 'nc'),
            (r'\bssh\b', 'ssh'),
            (r'\bscp\b', 'scp'),
            (r'\bsudo\b', 'sudo'),
            (r'\beval\b', 'eval'),
            (r'\bchmod\b', 'chmod'),
            (r'\bchown\b', 'chown'),
        ]

    return commands


def has_output_redirect(command):
    """Check if command contains output redirection."""
    # Match > or >> followed by a path (but not 2>&1 style redirects)
    return bool(re.search(r'(?<![0-9&])\s*>{1,2}\s*[^\s>&]', command))


def resolve_path(path_str, cwd):
    """Resolve a path string to absolute, handling ~ and relative paths."""
    if path_str.startswith('~'):
        path_str = os.path.expanduser(path_str)

    if not os.path.isabs(path_str):
        path_str = os.path.join(cwd, path_str)

    try:
        return str(Path(path_str).resolve())
    except (ValueError, OSError):
        return path_str


def is_inside_workspace(path_str, workspace_root, cwd):
    """Check if a resolved path is inside the workspace."""
    # Allow /dev/null as a special case
    if path_str == '/dev/null':
        return True

    resolved = resolve_path(path_str, cwd)
    workspace_resolved = str(Path(workspace_root).resolve())

    return resolved.startswith(workspace_resolved + os.sep) or resolved == workspace_resolved


def extract_paths_from_command(command):
    """
    Extract potential file paths from a bash command.
    Returns list of (path, context) tuples.
    """
    paths = []

    # Patterns for file-modifying commands with their arguments
    # Format: (regex, group_index, description)
    patterns = [
        # Output redirection: > file, >> file
        (r'>{1,2}\s*([^\s;&|]+)', 1, 'output redirect'),
        # Commands that modify files: rm, mv, cp destination, etc.
        (r'\brm\s+(?:-[rfivd]+\s+)*([^\s;&|]+)', 1, 'rm target'),
        (r'\bmv\s+(?:-[fivn]+\s+)*[^\s]+\s+([^\s;&|]+)', 1, 'mv destination'),
        (r'\bcp\s+(?:-[rfivn]+\s+)*[^\s]+\s+([^\s;&|]+)', 1, 'cp destination'),
        (r'\btouch\s+([^\s;&|]+)', 1, 'touch target'),
        (r'\bmkdir\s+(?:-[p]+\s+)*([^\s;&|]+)', 1, 'mkdir target'),
        (r'\bchmod\s+[^\s]+\s+([^\s;&|]+)', 1, 'chmod target'),
        (r'\bchown\s+[^\s]+\s+([^\s;&|]+)', 1, 'chown target'),
        # sed in-place
        (r'\bsed\s+-i[^\s]*\s+[^\s]+\s+([^\s;&|]+)', 1, 'sed -i target'),
    ]

    for pattern, group_idx, context in patterns:
        for match in re.finditer(pattern, command):
            path = match.group(group_idx)
            # Skip shell variables and command substitutions
            if not path.startswith('$') and not path.startswith('`'):
                paths.append((path, context))

    return paths


def extract_subcommands(command):
    """Extract individual commands from pipes and chains.

    Splits on |, &&, ||, ; to get individual commands.
    Returns list of (subcommand, operator) tuples.
    """
    # Simple split on common shell operators
    # Note: This is a basic implementation - doesn't handle quoted strings perfectly
    parts = re.split(r'\s*(\|{1,2}|&&|;)\s*', command)

    subcommands = []
    for i, part in enumerate(parts):
        part = part.strip()
        if part and part not in ('|', '||', '&&', ';'):
            operator = parts[i-1] if i > 0 else None
            subcommands.append((part, operator))

    return subcommands


def check_denied_commands(command):
    """Check if command contains denied patterns that could bypass prefix matching.

    Claude Code's deny rules only match command prefix (e.g., "curl ..." but not "echo | curl").
    This function checks ALL subcommands in pipes/chains.

    The denied patterns are loaded dynamically from settings.json.
    """
    denied_patterns = get_denied_commands()

    subcommands = extract_subcommands(command)
    issues = []

    for subcmd, operator in subcommands:
        for pattern, name in denied_patterns:
            if re.search(pattern, subcmd):
                if operator:
                    issues.append(
                        f"Restricted command '{name}' in pipeline/chain (bypasses prefix matching)")
                # If it's the first command (no operator), Claude's deny rules should catch it
                # But we flag it anyway for safety
                else:
                    issues.append(f"Restricted command '{name}' detected")

    return issues


def check_dangerous_patterns(command):
    """Check for dangerous shell patterns that could bypass workspace restrictions."""
    issues = []

    # Check for denied commands in pipes/chains (security bypass prevention)
    issues.extend(check_denied_commands(command))

    # Absolute paths to system directories
    system_dirs = ['/etc', '/usr', '/var', '/bin',
                   '/sbin', '/lib', '/opt', '/root', '/boot']
    for sys_dir in system_dirs:
        # Use lookarounds instead of \b since paths start with / (non-word char)
        if re.search(rf'(?:^|[^/\w]){sys_dir}(?:/|\s|$)', command):
            issues.append(f"System directory reference: {sys_dir}")

    # Home directory outside workspace
    if re.search(r'(?<![\w])~(?!/)', command) or re.search(r'\$HOME\b', command):
        # Allow ~ only if it's clearly going into workspace
        if not re.search(r'~.*' + re.escape(get_workspace_root().split('/')[-1]), command):
            issues.append("Home directory reference (~)")

    # /tmp can be problematic
    if re.search(r'\b/tmp\b', command):
        issues.append("Temporary directory reference (/tmp)")

    return issues


def validate_command(command, cwd):
    """
    Validate that a bash command only affects workspace files.
    Returns (is_safe, issues_list).
    """
    workspace_root = get_workspace_root()
    issues = []

    # Check for dangerous patterns first
    issues.extend(check_dangerous_patterns(command))

    # Extract and validate file paths
    paths = extract_paths_from_command(command)
    for path, context in paths:
        if not is_inside_workspace(path, workspace_root, cwd):
            resolved = resolve_path(path, cwd)
            issues.append(
                f"Path outside workspace ({context}): {path} -> {resolved}")

    return len(issues) == 0, issues


def allow_command(reason):
    """Return JSON response to allow command, bypassing permission system.

    Uses working format: {"decision": "approve", "reason": "..."}
    """
    response = {
        "decision": "approve",
        "reason": reason
    }
    debug_log(f"Approving: {reason}")
    print(json.dumps(response))
    sys.exit(0)


def defer_to_user(reason):
    """Defer decision to normal permission flow.

    TEST FORMAT A: JSON with reason but NO decision field.
    According to claude-code-hooks-mastery: undefined decision = normal permission flow.
    """
    response = {
        "reason": reason
        # No "decision" field - should defer to normal flow
    }
    debug_log(f"Deferring (format A - no decision): {reason}")
    print(json.dumps(response))
    sys.exit(0)


def ask_user(reason):
    """Ask user for permission using hookSpecificOutput format.

    TEST FORMAT B: The documented format from official Claude Code docs.
    """
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason
        }
    }
    debug_log(f"Asking user (format B - hookSpecificOutput): {reason}")
    print(json.dumps(response))
    sys.exit(0)


def allow_hookspec(reason):
    """Allow command using hookSpecificOutput format.

    TEST FORMAT: hookSpecificOutput with permissionDecision: "allow"
    Testing if this format works like {"decision": "approve"}
    """
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason
        }
    }
    debug_log(f"Allowing (hookSpecificOutput format): {reason}")
    print(json.dumps(response))
    sys.exit(0)


def deny_hookspec(reason):
    """Deny command using hookSpecificOutput format.

    TEST FORMAT: hookSpecificOutput with permissionDecision: "deny"
    Testing if this format works like {"decision": "block"}
    """
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }
    debug_log(f"Denying (hookSpecificOutput format): {reason}")
    print(json.dumps(response))
    sys.exit(0)


def block_for_review(reason):
    """Block command and provide reason to Claude.

    TEST FORMAT D: Confirmed working format.
    """
    response = {
        "decision": "block",
        "reason": reason
    }
    debug_log(f"Blocking (format D): {reason}")
    print(json.dumps(response))
    sys.exit(0)


def block_command(issues):
    """Block command with error message."""
    workspace_root = get_workspace_root()
    error_msg = "Workspace Protection: Command blocked\n\n"
    error_msg += "Issues detected:\n"
    for issue in issues:
        error_msg += f"  - {issue}\n"
    error_msg += f"\nWorkspace: {workspace_root}\n"
    error_msg += "Modify the command to use workspace-relative paths."

    print(error_msg, file=sys.stderr)
    sys.exit(2)  # Exit code 2 blocks the tool call


def debug_log(message):
    """Write debug message to a log file."""
    log_path = os.path.join(get_workspace_root(),
                            '.claude', 'hooks', 'debug.log')
    with open(log_path, 'a') as f:
        import datetime
        f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")


def main():
    """Main hook execution."""
    try:
        input_data = json.load(sys.stdin)
        debug_log(f"Hook invoked with: {json.dumps(input_data)[:200]}")
    except json.JSONDecodeError as e:
        print(f"Hook error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get('tool_name', '')
    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')
    cwd = input_data.get('cwd', os.getcwd())

    # Only validate Bash commands
    if tool_name != 'Bash' or not command:
        sys.exit(0)

    # === TEST 18-19: Defer pipe/chain to permission system ===
    # These must be checked BEFORE dangerous patterns check
    if 'test-18' in command:
        defer_to_user(
            "TEST-18: Deferring pipe to denied command to permission system")

    if 'test-19' in command:
        defer_to_user(
            "TEST-19: Deferring chain to denied command to permission system")
    # === END TEST 18-19 ===

    # 1. Check for dangerous paths (block these)
    is_safe, issues = validate_command(command, cwd)
    if not is_safe:
        block_command(issues)

    # 2. Check for output redirects
    # Exceptions: Allow redirects to known safe locations
    if has_output_redirect(command):
        safe_redirects = [
            '.cache/claude-status.txt',  # Task status logging
            '/dev/null',                  # Suppress output
            # Stderr to stdout (not really a file redirect)
            '2>&1',
        ]
        if any(safe in command for safe in safe_redirects):
            debug_log(f"Allowing redirect to safe location: {command}")
            allow_command("Redirect to safe location")
        else:
            # === TEST FORMAT SELECTION ===
            # Only ONE format should be active. Change requires new session.
            #
            # FORMAT A: JSON with reason, no decision (should defer)
            defer_to_user("Command contains output redirect")
            #
            # FORMAT B: hookSpecificOutput with permissionDecision: ask
            # ask_user("Command contains output redirect")
            #
            # FORMAT C: exit 0 with no output (pure defer)
            # debug_log(f"Deferring (format C - no output): {command}")
            # sys.exit(0)
            #
            # FORMAT D: decision: block (confirmed working)
            # block_for_review("Command contains output redirect - please confirm")

    # === TEST-SPECIFIC CODE (remove after testing) ===
    # Tests 11-15: Each tests a different hook response mechanism
    # Tests 16-17: Use normal hook logic (pipe/chain to denied commands)

    if 'test-11' in command:
        # Test allow_command() - {"decision": "approve", "reason": "..."}
        allow_command("TEST-11: Hook explicitly approving this command")

    if 'test-12' in command:
        # Test defer_to_user() - {"reason": "..."} with no decision field
        defer_to_user("TEST-12: Hook deferring to normal permission flow")

    if 'test-13' in command:
        # Test ask_user() - {"hookSpecificOutput": {"permissionDecision": "ask", ...}}
        # Use distinct text to differentiate from Bash tool description
        ask_user("FROM-HOOK-OUTPUT")

    if 'test-14' in command:
        # Test block_for_review() - {"decision": "block", "reason": "..."}
        block_for_review("TEST-14: Hook blocking this command for review")

    if 'test-15' in command:
        # Test block_command() - exit 2 + stderr message
        block_command(["TEST-15: Blocked via exit 2 and stderr"])

    # === TEST 20-23: Hook vs Permission List Precedence ===
    if 'test-20' in command:
        # Hook returns ask, permission list has echo in ALLOW
        ask_user("TEST-20: Hook asking, echo is in allow list")

    if 'test-21' in command:
        # Hook returns ask, permission list has echo in DENY
        ask_user("TEST-21: Hook asking, echo is in deny list")

    if 'test-22' in command:
        # Hook returns approve, permission list has echo in DENY
        allow_command("TEST-22: Hook approving, echo is in deny list")

    if 'test-23' in command:
        # Hook returns block, permission list has echo in ALLOW
        block_for_review("TEST-23: Hook blocking, echo is in allow list")

    # === TEST 24-25: hookSpecificOutput with allow/deny ===
    # These test if hookSpecificOutput format works the same as decision format

    if 'test-24' in command:
        # hookSpecificOutput with permissionDecision: "allow", echo in DENY list
        # Compare with Test 22 (decision: "approve")
        allow_hookspec(
            "TEST-24: hookSpecificOutput allow, echo is in deny list")

    if 'test-25' in command:
        # hookSpecificOutput with permissionDecision: "deny", echo in ALLOW list
        # Compare with Test 23 (decision: "block")
        deny_hookspec(
            "TEST-25: hookSpecificOutput deny, echo is in allow list")
    # === END TEST 24-25 ===
    # === END TEST-SPECIFIC CODE ===

    # 3. Allow echo commands without redirects (replaces "Bash(echo:*)" in allow list)
    if command.strip().startswith('echo ') or command.strip() == 'echo':
        allow_command("Echo command without redirect")

    # 4. All other commands - defer to Claude Code's permission rules
    sys.exit(0)


if __name__ == '__main__':
    main()
