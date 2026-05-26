# Research Patterns

How to investigate unfamiliar technologies effectively.

## When to Research
- Unfamiliar framework or library
- Version mismatch between documentation and installed package
- Parameter exists in docs but not in installed version
- Skill stub or missing coverage for your language/stack

## How to Research
1. Read the relevant `*-patterns` and `[language]-pitfalls` skills FIRST
2. `SearchWeb` for official framework documentation
3. `FetchURL` the specific docs page
4. Verify against installed version with `pip show`, `npm list`, `go version`, etc.
5. Read source code if docs are ambiguous
6. Prefer official docs over blog posts

## When to Stop Researching
- NEVER skip skill reading — skills contain empirical traps that docs don't mention
- For large projects (3000+ lines), research only genuinely unfamiliar technologies
- If the skill is a stub, rely on `SearchWeb` and report the gap to S5
