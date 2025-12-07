# Git Workflows

## Getting the diff

**IMPORTANT**: Always compare against `origin/main` (not local `main`) and fetch first to ensure you have the latest remote state:

**Why `origin/main` instead of `main`?**

- Local `main` may be outdated if not recently pulled
- `origin/main` always reflects the actual remote branch state after fetch
- This ensures accurate PR diffs that match what GitHub will show

### Copilot only

**Always** get the diff by executing `git diff --cached` (or similar) as the default tool for diffs often gives the wrong diff.

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- Use type prefix: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- **Subject line length**:
  - Aim for ≤50 characters total (including type and work item)
  - Maximum 72 characters
  - Reserve space for work item reference: `type(AB#12345): subject`
  - Subject portion should be ≤35 characters to stay within 50-char target
- Keep subject line concise and descriptive
- Use imperative mood ("add feature" not "added feature")
- **Work item references**: Include in scope position: `type(AB#12345): subject`
- Use body for detailed explanations (no line wrapping)
- Examples:
  - `feat(AB#12345): add database migrations`
  - `docs(AB#67890): update copilot instructions`
  - `fix(AB#11111): resolve provider timeout issue`

## PR Review

When user requests a comprehensive code review (triggers: "pr review", "review this pr", "code review of this branch", "review the changes"):

1. **Read and analyze the git diff**:

   - Start with the summary to understand scope and file changes
   - Read the full diff for detailed line-by-line analysis
   - Consider the branch context and recent commits if available

2. **Provide comprehensive review covering**:

   - **Overview**: Brief description of what the PR accomplishes and its purpose
   - **Files changed summary**: List with modification types (Added, Modified, Deleted)
   - **Detailed analysis by file**: For each significant change:
     - **Purpose**: What this file/change does
     - **Strengths** (✅): What's well-done
     - **Concerns/Issues** (⚠️): Problems, risks, or questions
     - **Recommendations** (💡): Suggestions for improvement
   - **Cross-cutting concerns**:
     - Architectural impact and patterns
     - Code quality (type safety, error handling, testing)
     - Security considerations (vulnerabilities, permissions, data handling)
     - Performance implications (if applicable)
     - Backwards compatibility and migration needs
     - Consistency with project conventions
   - **Risk assessment**: Categorize as Low/Medium/High with mitigation strategies
   - **Testing recommendations**: What should be verified before and after merge
   - **Final recommendation**: Approve / Request changes / Needs discussion

3. **Review principles**:
   - Be thorough but constructive and respectful
   - Cite specific files and line numbers using markdown links
   - Distinguish between blocking issues and nice-to-have suggestions
   - Consider impact on other developers and systems
   - Check alignment with documented conventions and patterns
   - Think about maintainability and future changes

---

## PR Summary

When user requests a PR summary for colleagues (triggers: "pr summary", "write pr summary", "summary for teammates", "summary for the team"):

1. **Analyze changes and create team-focused summaries**:

   - **Target audience**: Colleagues reviewing the PR (not the author)
   - **Files to create**:
     - `PR-SUMMARY.md` - English version
     - `PR-SUMMARY-NO.md` - Norwegian version
   - **Purpose**: Help reviewers quickly understand what changed, why it matters, and what to focus on
   - **Tone**: Clear, accessible, and informative (not tutorial-style)

2. **Document structure**:

   ```markdown
   # PR Summary: <Descriptive Title>

   > _This summary was created by [Claude Code/GitHub Copilot] to help reviewers understand the changes in this PR._

   ## Overview

   [2-3 sentences: what this PR does and why]

   ## What's Changed

   ### New Files

   - **filename** - Brief description of purpose

   ### Modified Files

   - **filename** - What changed and why

   ### Deleted Files

   - **filename** - Reason for removal (if applicable)

   ---

   ## Key Changes Explained

   ### 1. <Major Change Category>

   **Problem**: What issue or need this addresses
   **Solution**: How the change solves it
   **Benefits**: Why this approach is better

   [Code examples if helpful]

   **Impact**: What developers need to know or do differently

   [Repeat for each major change area]

   ---

   ## Impact on Development Workflow

   ### For <User Group/Role>

   - Specific changes relevant to this group
   - New patterns or practices to follow

   [Repeat for different user groups: developers, reviewers, ops, etc.]

   ---

   ## Content Organization Improvements

   [If restructuring docs/code]

   ### Better Structure

   - What improved

   ### New Sections Added

   - List new sections/features

   ### Condensed/Removed Sections

   - What was simplified and why

   ---

   ## Testing & Verification

   **Before merging, verify**:

   - [ ] Specific test or check
   - [ ] Another verification step

   **After merging**:

   - [ ] Post-merge actions
   - [ ] Monitoring or validation

   ---

   ## Files to Review

   **Critical**: [Files requiring careful review with links]
   **Important**: [Significant changes]
   **Minor**: [Small or cosmetic changes]

   ---

   ## Questions or Concerns?

   If you have questions about:

   - **Topic 1**: See [link] or check [file]
   - **Topic 2**: Reference to relevant documentation

   ---

   ## Recommendation

   [Overall assessment: Ready to merge / Needs discussion / Blocked by X]

   **Quality**: [Assessment of change quality and thoroughness]
   ```

3. **Writing guidelines**:

   - **Clarity**: Use plain language accessible to all team members
   - **Focus**: Emphasize "what" and "why" over implementation details
   - **Examples**: Include code snippets where they clarify complex changes
   - **Formatting**: Use ✅/❌/⚠️ symbols and formatting for scannability
   - **Breaking changes**: Highlight prominently with clear migration steps
   - **Decisions**: Explain technical choices and trade-offs made
   - **Actionable**: Make it clear what reviewers should focus on

4. **After writing**:
   - Create both `PR-SUMMARY.md` (English) and `PR-SUMMARY-NO.md` (Norwegian)
   - Provide clickable markdown links to both files
   - Both files should have identical structure and content, just different languages

---

## Norwegian Translation Guidelines

When creating Norwegian versions of PR summaries:

- Technical terms stay in English (e.g., "backend", "commit message", "type safety", "PR review", "source of truth", "conditionals", "callback", "state", "discovery", "runtime")
- Code concepts stay in English (e.g., "interface", "mock", "async/await", "hooks")
- Tool/framework names stay in English (e.g., "Backstage", "TypeScript", "Jest", "Prettier")
- File paths and code snippets stay in English
- **Precision over translation**: Use English when Norwegian translation would be ambiguous or lose technical precision, even if a Norwegian word exists (e.g., "conditionals" not "betingelser", "callback" not "tilbakekall", "state" not "tilstand", "discovery" not "oppdagelse")
- **Technical phase/time descriptors**: Keep compound technical terms for phases or timing in English (e.g., "form-time validation", "runtime validation", "execution time", "repository creation actions")
- Translate explanatory text, headings, and general descriptions
- **Italics for special named concepts**: Use italics sparingly, only for semantic emphasis when introducing or referring to special named things:
  - ✅ Use italics: Specific named systems, artifacts, or special terms being introduced (e.g., "_repository vending system_" as your specific system, "_Vending Portal_" as the plugin name, "_wrapper templates_" when introducing a specific pattern, "_agent instructions_" when referring to the specific file)
  - ❌ Don't italicize: Standard technical vocabulary developers use naturally, even in compounds (e.g., "backend", "templates", "type safety", "hooks", "scaffolder", "vending-prosess", "template-velger")
  - **Key principle**: Italics signal "this is a special named thing" not "this is English" - most English technical terms should stay without italics
- Prefer natural Norwegian sentence structure over word-for-word translation
- Use correct Norwegian spellings (e.g., "heng" not "hang", "kommandoer" not "kommandos")

**Examples:**

- "Code quality standards" → "Kodekvalitetsstandarder"
- "type safety rules" → "type safety-regler" (no italics, standard technical vocabulary)
- "source of truth" → "source of truth" (keep in English, standard technical term)
- "validation, conditions, fetching" → "validering, conditionals, henting av eksterne data" (use English for precise technical terms)
- "template discovery/organization" → "template discovery/organisering" (discovery is technical term)
- "validation at form-time vs template-execution-time" → "form-time validation vs. runtime validation" (keep phase descriptors in English)
- "repo creation actions" → "repository creation actions" (keep compound technical terms together)
- "our repository vending system" → "vårt _repository vending system_" (italics, specific named system)
- "the Vending Portal plugin" → "_Vending Portal_-plugin" (italics, specific plugin name)
- "template wrapper pattern" → "_wrapper templates_" (italics when introducing as a special concept)
- "development workflows" → "arbeidsflyten når vi utvikler" (natural phrasing over literal translation)
- "AI Agent behavioral guidelines" → "retningslinjer for AI Agentens atferd" (natural word order)
- "experiences hangs" → "opplever heng" (correct Norwegian spelling)

---

## Combined Workflow

When user requests both (triggers: "review and summarize", "full pr review with summary"):

1. First perform the comprehensive code review
2. Then generate the PR summary document
3. The summary should reference insights from the review but be written for the team

**Common usage patterns**:

- "pr review" → Comprehensive code review only
- "pr summary" → Team-focused summary document only
- "review and summarize" → Both in sequence
