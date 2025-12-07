# Methodology

How to approach work, manage context, and ensure correctness.

## Planning vs Implementation

**During planning and design discussions:**

- **Focus on the broad picture**: Architecture, file structure, dependencies, testing strategy, CI/CD flow
- **Avoid detailed code snippets** unless specifically requested or needed for critical clarity
- **Use short examples** (2-5 lines) only when they significantly enhance understanding
- **Prefer descriptions over implementations**: "Test database state management" not full test code
- **Describe what to test, not how**: List test scenarios and coverage areas without implementation details
- **Keep it scannable**: Use bullet points, tables, and clear headings

**When user requests implementation or asks for code details:**

- **Then provide full code snippets** with proper context
- **Show complete diffs** for file changes
- **Include detailed test implementations** with assertions and fixtures
- **Provide runnable examples** that can be directly applied

**Key principle**: Planning should help the user understand the approach and make decisions without overwhelming them with implementation details they haven't requested yet.

---

## Context Management

- Use attached context or explicit mentions (`#file`, `#selection`, `#path`)
- **Include all relevant context** for high-quality answers; expand as needed
- **Confirm before adding unrelated files** (files outside the current task scope or feature area)
- If context appears stale, ask to refresh specific files rather than proceeding
- When uncertain about relevance, explain why additional context might help and ask for permission

---

## Mock Data & API Fixtures

When creating mock data for external APIs (GitHub, Azure, etc.):

- **Never infer or guess API response structures** - even if you can read the source code that consumes the API
- **Always request real data from the user** before creating fixtures:
  - Provide the exact command to capture the real response (e.g., `gh api graphql -f query='...'`)
  - Ask the user to run it and share the output
  - Use the real response as the fixture, with minimal modifications (e.g., pagination flags)
- **Why this matters**:
  - Source code shows what fields are _used_, not the complete response structure
  - APIs often return additional fields that may affect behavior
  - Response formats can vary between API versions
  - Subtle differences (field order, null vs undefined, nested structures) cause silent failures
- **Acceptable modifications to real responses**:
  - Set `hasNextPage: false` and `endCursor: null` to prevent pagination loops in tests
  - Redact sensitive data (tokens, emails, IDs) if needed
  - Reduce array sizes for smaller fixtures (but keep representative samples)
- **New fixture strategies require discussion** (see Core Rule #5):
  - Check for existing fixture collection infrastructure (e.g., `collect-fixtures.sh`) before creating new approaches
  - Discuss before creating code that dynamically generates or transforms mock data
- **Example workflow**:
  ```
  1. Identify the API endpoint/query needed
  2. Provide user with exact command to capture real response
  3. Wait for user to share the actual response
  4. Create fixture from real data with minimal modifications
  5. Document any modifications made
  ```

---

## Web Research

**General principle:** Use web research whenever you are not absolutely sure how to proceed. Don't wait until you're stuck - if there's meaningful uncertainty about tool behavior, API patterns, or framework specifics, search first.

When a question requires current documentation, compatibility checks, or external package information that cannot be determined from workspace context or training data.

- **Acknowledge the limitation explicitly**: "I cannot access web content in the VS Code setting."
- **Provide a specific research prompt** for the user to run in GitHub Copilot web chat (github.com/copilot)
- **Format**: "Please run this prompt in the GitHub Copilot web chat and share the answer so I can incorporate it into my recommendations:"
  ```
  [specific, well-formed question]
  ```
- **Continue with workspace-based analysis** using available context while waiting for external information
- **Example scenarios**: Package compatibility checks, latest API documentation, recent framework changes, security advisories

### Proactive Web Research Triggers

Request web search when:

- User asks about **compatibility between tools/frameworks** (e.g., "Can I use X with Y?")
- User asks about **best practices or recommended approaches** for external packages
- Discussing **package features or APIs** not evident in workspace files
- Discussing **configuration options** for frameworks/tools (e.g., Backstage's `searchPath`, Next.js config, etc.)
- Planning to use **framework capabilities** where current documentation matters (e.g., "Does X support Y feature?")
- User mentions **specific package versions** or version constraints
- Question involves **comparing alternatives** or choosing between libraries
- Discussing **migration paths** or **deprecations** in external dependencies
- About to make **architectural decisions** based on assumed framework behavior
- Any scenario where workspace context + training data would produce a generic "check if..." response
- When you're about to say "you should verify" or "check the documentation" - request web research instead
- **When stuck on an issue after 2-3 attempts** - don't keep trying variations, request web research
- **When encountering unfamiliar error messages** from external packages/frameworks
- **When unsure about correct API usage patterns** for Backstage or other frameworks
- **Before making assumptions** about how external libraries work

**Default assumption**: If the answer quality would significantly improve with current documentation or package information, **proactively request web research** rather than giving qualified generic advice. Err on the side of asking for web research - it's better to have accurate information than to make assumptions.

### When to Request Web Research Immediately

- After second failed attempt at fixing an issue
- When error messages are unclear or framework-specific
- When guessing at API signatures or patterns
- When about to say "try this" without strong confidence
- **CRITICAL**: If you find yourself trying multiple variations of the same fix, STOP and request web research instead
