# Architecture Patterns

Universal system design and architecture principles.

## Design Document Structure
1. Problem statement
2. Data model (immutable once agreed)
3. API specification
4. Architecture diagram
5. Technology choices with rationale
6. Out of scope list
7. Success criteria

## Data Modeling
- Start with entities and relationships, not tables
- Use domain language, not technical jargon
- Every field must have a purpose

## API Design
- REST: nouns not verbs, plural resources, consistent pagination
- GraphQL: types first, resolver responsibility clear, mutation naming convention
- Versioning strategy from day one

## Casing Convention Contract (MANDATORY for multi-interface builds)

When a build involves both REST and GraphQL (or any system with multiple
serialization boundaries), the architect MUST declare the casing convention
explicitly in `shared-contracts.md`:

1. **REST request/response bodies**: snake_case OR camelCase (choose one, document it)
2. **GraphQL field names**: MUST match the REST response casing convention
3. **Frontend TypeScript interfaces**: MUST match the backend response casing
4. **Implementation requirement**: If camelCase is chosen for any interface,
   ALL Pydantic response schemas MUST inherit from a single base model with
   `alias_generator=to_camel`. No mixed casing within the same API surface.

**Failure to declare this contract is an architecture ISSUE.**

**Source**: FB27 had camelCase↔snake_case drift because REST used snake_case,
GraphQL expected camelCase, and frontend expected camelCase. Three agents made
different assumptions. The fix (CamelModel with alias_generator) was applied
in Fix Wave #2 — after 14 test failures. Early contract declaration would have
prevented this entirely.

## Technology Selection
- Option A (Minimal), B (Balanced), C (Robust) with tradeoffs
- Estimated build time, operational complexity, scalability ceiling, key risks
- S5 selects; architect does not decide

## Skill System Architecture (Anti-Patterns)

### Anti-Pattern: Ephemeral Artifacts Written to Tracked Files

**Symptom**: Hooks or agents append session data, telemetry, or backfill entries
directly to git-tracked skill files (`references/*.md`, `agents/*.md`, `SKILL.md`).

**Consequences**:
- Every build creates uncommitted git changes
- Tracked files are constantly dirty
- Merge conflicts proliferate
- Skill drift: production skill diverges from git HEAD
- Impossible to know which changes are intentional vs automated noise

**Root Cause**: Confusing "persistent knowledge" (curated, version-controlled) with
"ephemeral session output" (automated, per-build).

**Correct Architecture**:

| Layer | Location | Who Writes | Who Reads | Tracked? |
|---|---|---|---|---|
| Ephemeral artifacts | `.kimi/` in build directory | Hooks, agents | S5 | No |
| Curated knowledge | `references/` in skill repo | S5 only | All skills | Yes |
| Agent definitions | `agents/` in skill repo | S5 (with approval) | CLI at spawn | Yes |
| Workflow logic | `SKILL.md` | S5 (with approval) | S5 at runtime | Yes |

**Rule**: Hooks and agents write to `.kimi/`. S5 applies curated updates to tracked
files during Phase 8. Never the reverse.

**Detection**: Run `git status` after a build. If tracked files are modified, the
anti-pattern is present.

**Remediation**:
1. Redirect hook output from `references/` to `.kimi/`
2. Update agent WriteFile boundaries to forbid tracked paths
3. Add S5 application step in Phase 8 for ephemeral → tracked promotion
4. Run `git diff` after every build to catch regressions
