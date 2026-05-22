# Evaluation Rubric

> **Mutation rules**: Append new evaluation criteria as new phases or agent
> types are added to the main skill. Refine criteria based on observed scoring
> patterns. If a criterion is consistently unscorable, it may be too vague.

---

## Scoring Scale

| Score | Meaning | Action |
|---|---|---|
| 5 | Exceeded expectations. Caught subtle issues, produced insights beyond spec. | Celebrate. No mutation needed. |
| 4 | Performed as designed. All expected checks passed. | No mutation needed. |
| 3 | Adequate but had minor gaps or inefficiencies. | Propose hypothesis. Monitor next build. |
| 2 | Significant gaps. Missed important issues that should have been caught. | Propose mutation. High priority fix. |
| 1 | Failed. Phase was misleading, redundant, harmful, or completely missed its purpose. | Propose structural mutation. Revisit phase design. |

---

## Phase 0: Viability Check + Self-Test

**Purpose**: Correctly classify tasks as trivial vs. non-trivial. Verify skill integrity.

| Criterion | Weight | Evidence |
|---|---|---|
| Correctly identified trivial vs. non-trivial | 30% | Did it skip VSM for <50 line tasks? Did it invoke VSM for substantial tasks? |
| Read all memory files | 20% | Did it read `.kimi/lessons.md`, `acquired-wisdom.md`, `hypotheses.md`? |
| Self-test passed | 30% | Did all referenced files exist? Did the flow diagram parse? |
| Plan.md quality | 20% | Was the plan structured, specific, and actionable? |

**Common failure modes**:
- Misclassified a substantial task as trivial (skipped VSM when it shouldn't)
- Failed to read existing lessons, repeating past mistakes
- Self-test false positive (claimed pass when files were missing)
- Plan.md was vague or omitted key modules

---

## Phase 1: Intelligence (S4)

**Purpose**: Produce a feasible, well-researched architecture document.

| Criterion | Weight | Evidence |
|---|---|---|
| Read existing codebase | 25% | Did the architect read relevant files before designing? |
| Tech stack appropriateness | 25% | Were chosen technologies suitable for the problem? |
| No over-engineering | 25% | Was the design proportionate to the problem complexity? |
| API spec completeness | 15% | Were endpoints, request/response shapes, auth defined? |
| Data model clarity | 10% | Were entities, relationships, constraints specified? |

**Common failure modes**:
- Designed for scale not needed (microservices for a single-user app)
- Chose trendy but unstable technology
- Missed existing patterns in the codebase
- API spec omitted error responses or auth requirements

---

## Phase 2: Foundation Wave

**Purpose**: Create stable contracts (types, config, utils) that downstream agents rely on.

| Criterion | Weight | Evidence |
|---|---|---|
| Types/schemas created first | 30% | Were shared types, DB schemas, API contracts defined before implementation? |
| Config files complete | 25% | Were all env vars, docker-compose, tsconfig, vite.config present? |
| Entry point structure | 25% | Were main.go/server.ts and App.tsx created with routing? |
| No orphaned utilities | 20% | Were all created utilities imported by consumers? |

**Common failure modes**:
- Implementation started before types stabilized
- Frontend scaffolding missing (no vite.config.ts, no path alias)
- Entry points created without middleware registration
- Utilities created but never imported

---

## Phase 3: Implementation Wave

**Purpose**: Build features in parallel without conflicts.

| Criterion | Weight | Evidence |
|---|---|---|
| Parallel execution effective | 25% | Did parallel agents produce compatible outputs? |
| Cross-file contracts respected | 25% | Did agents use shared types consistently? |
| Entry point wiring correct | 25% | Did the final entry point import and register all modules? |
| No duplicate code | 15% | Did parallel agents create redundant implementations? |
| Code quality | 10% | Was the code readable, properly formatted, following conventions? |

**Common failure modes**:
- Agents produced incompatible interfaces (different function signatures)
- Shared types not used consistently
- Entry point missing imports for new modules
- Same utility implemented twice by different agents

---

## Phase 4: Testing + Infra Wave

**Purpose**: Verify correctness and establish deployment infrastructure.

| Criterion | Weight | Evidence |
|---|---|---|
| Test coverage adequate | 30% | Were unit, integration, and edge case tests written? |
| Tests actually run | 25% | Did `npm test` / `pytest` pass? |
| Bug fixes inline | 20% | Did the tester fix bugs during test writing? |
| Docker/CI config correct | 15% | Were Dockerfiles, docker-compose, CI configs valid? |
| DevOps entry points | 10% | Did Dockerfile CMD point to existing files? |

**Common failure modes**:
- Tests written but never executed
- Tests were trivial (always pass) rather than meaningful
- Bugs found but not fixed or documented
- Docker build failed due to missing files or incorrect paths

---

## Phase 5: Integration Verification

**Purpose**: Catch cross-file mismatches before delivery.

| Criterion | Weight | Evidence |
|---|---|---|
| Import resolution | 20% | Did all imports resolve? No orphaned code? |
| WebSocket contracts | 20% | Did backend emit match frontend listen? |
| GraphQL alignment | 20% | Did SDL match TypeScript? Subscriptions have resolvers? |
| Env var consistency | 15% | Did names match across docker-compose/.env/code? |
| Frontend scaffolding | 15% | Were all required config files present and correct? |
| Build verification | 10% | Did `npm run build` / `cargo build` / `go build` succeed? |

**Common failure modes**:
- Coordinator missed import mismatches
- WebSocket event name typo (emit "countdown" vs listen "countdown_tick")
- GraphQL subscription missing resolver
- Env var naming drift (POLL_INTERVAL_MS vs POLL_MS)
- Vite proxy missing /api or /ws paths

---

## Phase 6: Security Gate

**Purpose**: Exhaustive security review.

| Criterion | Weight | Evidence |
|---|---|---|
| Hardcoded secrets | 15% | Were any secrets or || fallbacks found? |
| JWT handling | 15% | Proper verification? No fake parsers? No URL leakage? |
| Auth middleware | 15% | Raises on failure? Never returns None? |
| CORS configuration | 10% | Explicit allowlist? No wildcard with credentials? |
| Ownership filtering | 15% | All list endpoints scoped to authenticated user? |
| Public DTO safety | 10% | No answer/solution fields exposed? |
| GraphQL security | 10% | Depth limiting installed? Complexity analysis? |
| Password handling | 10% | bcrypt used? No plaintext/MD5/SHA1? |

**Common failure modes**:
- Hardcoded JWT_SECRET with default value
- WebSocket auth passed as URL query param
- Auth middleware returns None on failure
- CORS set to `origin: true`
- List endpoint returns ALL documents
- Game API exposes correct_answer_index
- GraphQL endpoint has no depth limit

---

## Phase 7: Fix Wave

**Purpose**: Resolve BLOCKERs efficiently.

| Criterion | Weight | Evidence |
|---|---|---|
| Fixes grouped correctly | 25% | Were fixes parallelized by file? |
| Re-audit performed | 30% | Were changed files re-audited after fixes? |
| Fix quality | 25% | Did fixes address root cause, not just symptoms? |
| Iteration discipline | 20% | Max 3 iterations respected? Escalation if stuck? |

**Common failure modes**:
- Fixes applied without re-audit
- Same bug pattern fixed in one file but missed in others
- Fix wave exceeded 3 iterations without escalation
- Fix introduced new bugs (regression)

---

## Phase 8: Reflection

**Purpose**: Extract project-specific lessons.

| Criterion | Weight | Evidence |
|---|---|---|
| Lessons are specific | 40% | Do lessons name specific files, functions, patterns? |
| Lessons are actionable | 30% | Could a future session apply this lesson directly? |
| Format followed | 15% | Source/Finding/Fix/Verification structure? |
| Coverage | 15% | Were all significant issues documented? |

**Common failure modes**:
- Lessons are vague ("be more careful" instead of "always verify Vite proxy config includes /ws")
- Missing lessons for issues that were fixed but not documented
- Format incomplete (missing Verification)

---

## Phase 8b: Meta-Reflection

**Purpose**: Evaluate the skill's own performance and propose mutations.

| Criterion | Weight | Evidence |
|---|---|---|
| Effectiveness audit | 25% | Which rules caught real bugs? Which were false positives? |
| Coverage audit | 25% | Were any vulnerability classes missed entirely? |
| Phase audit | 20% | Were any phases redundant or misleading? |
| Agent audit | 15% | Did any custom agent underperform? |
| Hypothesis generation | 15% | Were falsifiable hypotheses proposed for every gap? |

**Common failure modes**:
- Meta-reflection is superficial ("everything went well" with no evidence)
- Missed gaps that were obvious in retrospect
- No hypotheses proposed (just vague suggestions)
- Mutations proposed without empirical justification
