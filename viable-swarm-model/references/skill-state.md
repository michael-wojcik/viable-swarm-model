# VSM Skill State — Living Self-Model
> Updated by: `session-start.sh` (read), `session-end.sh` (write), `vsm_meta` (append)
> Read by: S5 at Phase 0
> This file is the organism's proprioception — it knows its own state.

## Capability Matrix
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes |
|-------|--------|-------------|---------------|---------------------|
| vsm_backend_coder | Python/FastAPI | 85% | 4, 4, 4 | Import loops, missing deps in requirements.txt |
| vsm_frontend_coder | React/TS/Vite | 70% | 4, 3, 2 | Stub pages (improving — 0 in FB25-FB26), void-referenced imports |
| vsm_security | Auth/GraphQL | 80% | 4, 4, 3 | Misses enum runtime bugs, type-safety gaps, CORS wildcard severity |
| vsm_auditor | Code review | 80% | 4, 4, 3 | Duplicates checks across foundation/implementation |
| vsm_architect | Design | 85% | 4, 4, 5 | Scope creep without product brief guardrails |
| vsm_coordinator | Integration | 75% | 4, 3, 4 | Drift detection only active on Tier 2+ builds, port parity misses |
| vsm_wiring | Entry-point wiring | 80% | 4, 4, 3 | Router registration misses, ApolloProvider gaps, module-level instantiation orphans |
| vsm_backend_tester | Test writing | 75% | 4, 3, 4 | Incomplete coverage, missing edge cases |
| vsm_frontend_tester | Test writing | 70% | 4, 3, 3 | Build verification gaps (improving — FB25-FB26 green) |
| vsm_devops_coder | Docker/CI | 75% | 4, 3, 4 | Health check omissions, port mapping errors, .dockerignore absence |
| vsm_meta | Meta-evaluation | 70% | 3, 3, 3 | Cannot enforce mutations-applied.md; reports gaps but doesn't prevent them |
| vsm_process_auditor | Process compliance | 65% | 3, 3, 2 | Broker freshness scored as informational not compliance; lenient scoring |

## Current Mood (auto-generated)
> Last updated: 2026-06-03 by comprehensive audit
- **Recent pattern**: "Phase 4 gate legitimate in FB25-FB26 (0 bypasses). Frontend stubs eliminated (0 in FB25-FB26)."
- **Domain struggle**: "Process discipline still deteriorating despite code quality improvements. mutations-applied.md bypassed 4 consecutive builds."
- **Agent concern**: "vsm_meta and vsm_process_auditor cannot enforce their own findings. They detect but cannot prevent."
- **Risk elevation**: "Score regression 4.0→3.6 (FB26) due to foundation collapse + process gaps, not code gaps."
- **CRITICAL (2026-06-02)**: ALL subagents — background, foreground, AND parallel
  foreground — bypass all PreToolUse/PostToolUse hooks. Primary enforcement is
  Layer 1 (in-prompt mandatory rules). Hooks are a secondary safety net for S5
  ONLY.
- **Systemic diagnosis**: "Detection ≠ Enforcement. S5 self-discipline degrades under pressure. The organism senses pain but cannot reliably act on it."

## Hook Enforcement Baseline

### Before (pre-hook, advisory-only)
- Mutation removals per 5 builds: 0
- Measured effect fill rate: ~5%
- S5 bypassed gates (last 5 builds): ~2
- Reference files loaded at Phase 0: 3
- Active hooks: 0
- Tests per gate: advisory only (no enforcement)

### After targets (FB27–FB30, post-comprehensive-audit implementation)
- Mutation removals per 5 builds: ≥2 (enforced by removal gate + cemetery)
- Measured effect fill rate: ≥80% (enforced by Phase 8c-ii hard gate + stop-verifier hook)
- S5 bypassed gates: 0 (enforced by Gate Artifact Protocol — every transition
  requires a verifiable artifact; unlogged overrides are process violations)
- Reference files loaded at Phase 0: 8+ (including knowledge-broker.md and
  mutation-state.md as MANDATORY)
- Active hooks: 9 (secondary layer for S5 ONLY)
- Prompt-hardened agents: ALL agents (primary layer)
- Gate artifact verification: EVERY phase transition
- Knowledge broker freshness: ≤7 days (checked by process auditor + session-start auto-injection)
- Ineffective mutation redesign deadline: FB27 for any new ineffective mutations
- Regression builds executed: Every 5th build (FB30, FB35...) — hard blocked in coach Phase 0
- Trainer spawn: 100% of fitness builds (mandatory gate in coach Phase 1c)
- Decisions.md theater: Resolved by FB30 (either auto-populated or removed)

## Telemetry Archive Note
> **2026-06-02**: All pre-2026-06-02 telemetry in `~/.vsm-telemetry-pre-2026-06-02-archive`
> is INVALID. The 4 measurement hooks (`telemetry-logger`, `subagent-counter`,
> `bypass-logger`, `agent-performance-scorer`) only captured S5 activity, giving
> false confidence. They have been removed. New telemetry (if any) must be
> S5-only and explicitly tagged as such.

## Active Mutation Portfolio
| Mutation ID | Target Failure | Applied | Measured Effect | Status |
|-------------|---------------|---------|-----------------|--------|
| FB25-S1 | False hook claim removal | 2026-06-02 | **PENDING** | Awaiting FB26 |
| FB25-S2 | Mutation checkpoint hard gate | 2026-06-02 | **PENDING** | Awaiting FB26 |
| FB24-1 | Phase 4 bypass when 1 test fails | 2026-06-02 | **PENDING** | Awaiting FB26 |
| FB24-2 | Enum type safety audit | 2026-06-02 | **PENDING** | Awaiting FB26 |
| FB23-4 | Frontend build script verification | 2026-06-01 | **PENDING** | Awaiting FB26 |
| FB21-8 | Security-lessons topical reorg | 2026-05-25 | Effective | No duplicate L-numbers since |
| FB21-24 | Process auditor spawn | 2026-05-25 | Effective | Process auditor now checks 6 items |
| R19 | Contract repopulation | 2026-05-26 | Effective | Contracts present in FB25 |
| R20 | Validate agent files script | 2026-05-26 | Effective | All validators pass |

## Removed Mutation Portfolio (Cemetery)
| Mutation ID | Target Failure | Removed | Rationale |
|-------------|---------------|---------|-----------|
| FB19-7 | Cross-skill log review | 2026-06-02 | Skills share git repo; separation artificial |
| FB23-3 | Inline fix prevention (prompt-only) | 2026-06-02 | Redundant with hook + vsm-main.md Layer 1 |

## Ineffective Mutations Awaiting Redesign
| Mutation ID | Target Failure | Builds Failed | Action |
|-------------|---------------|---------------|--------|
| FB22-2 | Frontend stub prevention | FB23, FB24 | Redesign — add live-data-fetch verification |
| FB18-10 | Mutation tracking checkpoint | FB23, FB24, FB25 | Redesign — hard gate in vsm_meta.md |
| FB9/P46 | Test-First Exit Gate | FB20, FB21, FB24 | Redesign — explicit S5 verification command |

## Efficiency Baselines
> Populated by session-end hook telemetry. Initial values are estimates.
| Metric | Rolling Avg (5 builds) | Last Build | Trend |
|--------|----------------------|------------|-------|
| Agents spawned | 13.2 | 14 | ↑ |
| File writes | 49.0 | 52 | ↑ |
| Session time (min) | 42 | 38 | ↓ |
| Context compactions | 2.4 | 3 | ↑ |
| Tool calls per build | ~190 | ~195 | ↑ |
| Process violations per build | 2.1 | 3 | → |
| Mutation backfill rate | 0.15 | 0.2 | ↑ |

## Known Unknowns (with confidence)
| Hypothesis | Confidence | Last Tested | Priority | Status |
|------------|-----------|-------------|----------|--------|
| H150: Dependency verification prevents 100% of bad imports | 75% | FB21 | HIGH | untested |
| H154: `npm run build` as Phase 4 hard gate prevents TS leaks | 80% | FB24 | CRITICAL | partially confirmed (FB24 still leaked) |
| H157: Frontend stubs correlate with missed checklist items | 70% | FB24 | HIGH | confirmed (stubs + missed checks) |
| H201: Custom agent files reduce tokens by >30% | 60% | NEVER | HIGH | untested |
| H202: Tool-enforced read-only boundaries > prompt-only | 85% | NEVER | CRITICAL | untested — hooks now test this |
| H203: SQLAlchemy Mapped[Enum] = mapped_column(String) bug | 80% | NEVER | MEDIUM | untested |
| H300: Background subagents bypass hooks | **CONFIRMED** | 2026-06-02 | CRITICAL | confirmed — BackgroundAgentRunner lacks set_hook_engine |
| H301: Prompt-hardened rules prevent background bypasses | 70% | NEVER | HIGH | untested — implemented 2026-06-02 |
| H302: session-end audit catches residual bypasses | 50% | NEVER | MEDIUM | untested — implemented 2026-06-02 |

## Algedonic Telemetry
| Build | Emissions | Heeded | Ignored | Ignored Rate |
|-------|-----------|--------|---------|--------------|
| FB26 | 2 | 1 | 1 | 50% |
| FB25 | 1 | 1 | 0 | 0% |
| FB24 | 3 | 1 | 2 | 67% |
| FB23 | 2 | 0 | 2 | 100% |
| FB22 | 1 | 1 | 0 | 0% |
| FB21 | 3 | 2 | 1 | 33% |
| FB20 | 2 | 0 | 2 | 100% |

## Temporal Patterns
> Auto-generated by session-end hook after every 3 builds
- **T1**: "Frontend builds: ZERO stub pages in FB25-FB26" (Confidence: HIGH)
  - Status: **RESOLVED** — FB22-2 mutation effective. Continue monitoring.
- **T2**: "Phase 4 gate bypassed when exactly 1 test fails" (Confidence: HIGH)
  - Status: **RESOLVED** — FB24-1 mutation effective. FB25-FB26 both legitimate gates.
- **T3**: "Inline fixes during Phase 6/7 boundary in 3 of last 5 builds" (Confidence: HIGH)
  - Status: **IMPROVED** — FB25 had 0 inline fixes. FB26 had 0 inline fixes. Layer 1 + hook working.
- **T4**: "Security gate misses enum runtime bugs in 2 consecutive builds" (Confidence: MEDIUM)
  - Status: **RESOLVED** — FB24-2 mutation effective. FB25-FB26 zero enum crashes.
- **T5**: "mutations-applied.md bypassed for 4 consecutive builds (FB23-FB26)" (Confidence: HIGH)
  - Status: **ACTIVE** — FB26-S3 structural mutation applied post-build. Awaiting FB27 validation.
- **T6**: "Score regression without alarm: 4.0→3.6 (FB26)" (Confidence: HIGH)
  - Status: **ACTIVE** — FB26-A3 score trend tracking rule applied. Awaiting FB27 validation.

## Session Telemetry Log
> See individual entries appended by session-end hook
