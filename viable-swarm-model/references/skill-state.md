# VSM Skill State — Living Self-Model
> Updated by: `session-start.sh` (read), `session-end.sh` (write), `vsm_meta` (append)
> Read by: S5 at Phase 0
> This file is the organism's proprioception — it knows its own state.

## Capability Matrix
| Agent | Domain | Success Rate | Last 3 Scores | Known Failure Modes |
|-------|--------|-------------|---------------|---------------------|
| vsm_backend_coder | Python/FastAPI | 85% | 4, 4, 3 | Import loops, missing deps in requirements.txt |
| vsm_frontend_coder | React/TS/Vite | 65% | 3, 2, 2 | Stub pages, void-referenced imports, build failures |
| vsm_security | Auth/GraphQL | 80% | 4, 4, 3 | Misses enum runtime bugs, type-safety gaps |
| vsm_auditor | Code review | 75% | 4, 3, 3 | Duplicates checks across foundation/implementation |
| vsm_architect | Design | 85% | 3,  4, 5 | Scope creep without product brief guardrails |
| vsm_coordinator | Integration | 70% | 3, 3, 4 | Drift detection only active on Tier 2+ builds |
| vsm_wiring | Entry-point wiring | 80% | 4, 4, 3 | Router registration misses, ApolloProvider gaps |
| vsm_backend_tester | Test writing | 70% | 3, 3, 4 | Incomplete coverage, missing edge cases |
| vsm_frontend_tester | Test writing | 65% | 3, 2, 3 | Build verification gaps, no npm run build check |
| vsm_devops_coder | Docker/CI | 75% | 4, 3, 4 | Health check omissions, port mapping errors |

## Current Mood (auto-generated)
> Last updated: 2026-06-02 by meta-reflection Entry 3
- **Recent pattern**: "Phase 4 gate bypassed 3 of last 5 builds (FB20, FB21, FB24)"
- **Domain struggle**: "Frontend builds: 4 consecutive stub pages (FB21–FB24)"
- **Agent concern**: "vsm_frontend_coder consistency declining (scores: 3→2→2)"
- **Risk elevation**: "Time pressure detected — high file-write velocity in FB24"
- **CRITICAL (2026-06-02)**: ALL subagents — background, foreground, AND parallel
  foreground — bypass all PreToolUse/PostToolUse hooks. Primary enforcement is
  Layer 1 (in-prompt mandatory rules). Hooks are a secondary safety net for S5
  ONLY. See plan `iron-fist-moon-knight-namor.md`.
- **Systemic diagnosis**: "Detection ≠ Enforcement. S5 self-discipline degrades under pressure."

## Hook Enforcement Baseline

### Before (pre-hook, advisory-only)
- Mutation removals per 5 builds: 0
- Measured effect fill rate: ~5%
- S5 bypassed gates (last 5 builds): ~2
- Reference files loaded at Phase 0: 3
- Active hooks: 0
- Tests per gate: advisory only (no enforcement)

### After targets (FB26–FB30, post-comprehensive-audit)
- Mutation removals per 5 builds: ≥2 (enforced by removal gate + cemetery)
- Measured effect fill rate: ≥80% (enforced by Phase 8c-ii hard gate)
- S5 bypassed gates: 0 (enforced by Gate Artifact Protocol — every transition
  requires a verifiable artifact; unlogged overrides are process violations)
- Reference files loaded at Phase 0: 8+ (including knowledge-broker.md and
  mutation-state.md as MANDATORY)
- Active hooks: 9 (secondary layer for S5 ONLY)
- Prompt-hardened agents: ALL agents (primary layer)
- Gate artifact verification: EVERY phase transition
- Knowledge broker freshness: ≤7 days (checked by process auditor)
- Ineffective mutation redesign deadline: FB26 for all 3 remaining

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
| Agents spawned | 12.4 | 14 | ↑ |
| File writes | 47.2 | 52 | ↑ |
| Session time (min) | 45 | 38 | ↓ |
| Context compactions | 2.1 | 3 | ↑ |
| Tool calls per build | ~180 | ~195 | ↑ |

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
| FB24 | 3 | 1 | 2 | 67% |
| FB23 | 2 | 0 | 2 | 100% |
| FB22 | 1 | 1 | 0 | 0% |
| FB21 | 3 | 2 | 1 | 33% |
| FB20 | 2 | 0 | 2 | 100% |

## Temporal Patterns
> Auto-generated by session-end hook after every 3 builds
- **T1**: "Frontend builds: 4 consecutive stub pages (FB21–FB24)" (Confidence: HIGH)
  - Action: Pre-emptively inject "no stubs" constraint to vsm_frontend_coder
- **T2**: "Phase 4 gate bypassed when exactly 1 test fails" (Confidence: HIGH)
  - Action: Prompt-hardened gate rule in ALL agent prompts + gate-guardian hook
- **T3**: "Inline fixes during Phase 6/7 boundary in 3 of last 5 builds" (Confidence: HIGH)
  - Action: Prompt-hardened boundary rule in ALL agent prompts + boundary-guardian hook
- **T4**: "Security gate misses enum runtime bugs in 2 consecutive builds" (Confidence: MEDIUM)
  - Action: Elevate enum type-safety to BLOCKER in security audit

## Session Telemetry Log
> See individual entries appended by session-end hook
