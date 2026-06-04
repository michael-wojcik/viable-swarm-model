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

---

## Rule: API Doc Verification Workflows

**Status**: Active (FB26, FB28 empirical)
**Severity**: BLOCKER (if skipped)
**Applies to**: vsm_architect, vsm_backend_coder, vsm_frontend_coder, vsm_explore

Official documentation often reflects the latest version of a library, but the project's manifest may pin an older version. Using a parameter or API that exists only in newer docs causes `TypeError` or `AttributeError` at runtime.

**Verification workflow**:
1. **Identify installed version** BEFORE reading docs:
   ```bash
   # Python
   pip show strawberry-graphql | grep Version
   # Node
   npm list strawberry-graphql --depth=0
   # Go
   go list -m github.com/some/package
   ```
2. **Fetch docs for that exact version**. Append version to URL when possible:
   ```
   https://strawberry.rocks/docs/types/scalars  # latest
   https://strawberry.rocks/docs/0.235.0/types/scalars  # pinned version (if available)
   ```
3. **Verify signature with `inspect` or source** when docs are ambiguous:
   ```python
   import inspect, strawberry
   "validation_rules" in inspect.signature(strawberry.Schema.__init__).parameters
   ```
4. **Check changelog** for breaking changes between installed and latest:
   ```bash
   SearchWeb "strawberry-graphql 0.235.2 to 0.316.0 changelog"
   ```

**Prevention rules**:
1. Backend/frontend coder MUST verify installed version before using ANY API parameter not already proven in the codebase.
2. If docs and installed version mismatch, trust the installed version.
3. Report version mismatch to S5 — it may indicate a needed manifest update.

**Source**: FB26 assumed `UploadFile.read(max_bytes=...)` existed based on generic docs; actual Starlette signature is `read(size=-1)`. FB28 assumed `strawberry.Schema` accepted `validation_rules`; parameter did not exist in installed version.

---

## Rule: Version-Mismatch Detection Heuristics

**Status**: Active (FB23, FB26 empirical)
**Severity**: HIGH
**Applies to**: vsm_backend_coder, vsm_frontend_coder, vsm_coordinator

These symptoms strongly indicate a version mismatch between documentation and installed package:

| Symptom | Likely Cause | Verification |
|---|---|---|
| `TypeError: unexpected keyword argument 'X'` | Parameter added in newer version | `inspect.signature()` or source |
| `AttributeError: module 'X' has no attribute 'Y'` | Attribute renamed or removed | Check changelog / source |
| `ImportError: cannot import name 'Z'` | Name moved between submodules | Check installed package structure |
| `DeprecationWarning` flood | Using deprecated API from older version | Check docs for replacement |
| `PydanticDeprecatedSince20` | Pydantic V1 API on V2 install | Read `python-pitfalls` Pydantic rules |
| Tests pass locally but fail in CI | Local environment has newer resolved version | Run `pip freeze` diff locally vs CI |

**Prevention rules**:
1. When encountering any symptom above, FIRST verify installed version vs docs version.
2. NEVER add a workaround (e.g., `try/except ImportError`) without confirming it's a version issue, not a missing dependency.
3. Coordinator MUST include manifest-environment parity check in integration (see `dependency-drift-pitfalls`).

**Source**: FB23 `strawberry-graphql` 0.235.2 vs 0.316.0 caused `ImportError: cannot import name 'is_new_type'`. FB26 Starlette version mismatch caused `TypeError` on `UploadFile.read()`.

---

## Rule: Technology Evaluation Checklist

**Status**: Active (theoretical — awaiting validation)
**Severity**: LOW (strategic)
**Applies to**: vsm_architect, vsm_product, vsm_meta

Before adopting a new library, framework, or tool, score it against these criteria. A tool scoring ≤2 on any critical criterion should be avoided or require an explicit risk acceptance.

| Criterion | Weight | Questions |
|---|---|---|
| **Maturity** | Critical | ≥1.0? Stable release? Changelog maintained? |
| **Community** | Critical | Active GitHub issues/PRs? Stack Overflow presence? |
| **Security track record** | Critical | CVE history? Dependabot alerts? Security policy? |
| **Integration complexity** | High | Adds new runtime (Docker, DB, broker)? Config overhead? |
| **Testability** | High | Can it be mocked in unit tests? Test containers available? |
| **Documentation quality** | Medium | Official docs current? API reference complete? Examples? |
| **Type safety** | Medium | First-class TypeScript / Python types? |
| **License** | Medium | Compatible with project license? No copyleft surprises? |
| **Team familiarity** | Low | Has any team member used it before? |

**Decision matrix**:
| Score | Action |
|---|---|
| 8–9 | Adopt freely |
| 6–7 | Adopt with monitoring (probationary mutation) |
| 4–5 | Avoid unless no alternative; document risk |
| ≤3 | Reject; find alternative or build in-house |

**Prevention rules**:
1. Architect MUST produce a 1-paragraph evaluation for any new dependency proposed in design docs.
2. Product MUST flag adoption of ≤5 scoring tools as a project risk.
3. Meta MUST track technology adoption decisions and revisit scores after 3 builds.

**Source**: Theoretical — derived from software architecture best practices. No direct build failure yet, but FB22's adoption of `strawberry_sqlalchemy_mapper` (immature, undocumented) wasted significant agent time.
