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
| vsm_architect | Design | 85% | 4, 5, 4 | Scope creep without product brief guardrails |
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
- **CRITICAL (2026-06-02)**: Background subagents bypass all PreToolUse/PostToolUse hooks.
  Primary enforcement shifted to in-prompt mandatory rules. Hooks remain as
  secondary safety net for S5 + foreground agents. See plan amendment
  `winter-soldier-aqualad-power-girl-amendment.md`.
- **Systemic diagnosis**: "Detection ≠ Enforcement. S5 self-discipline degrades under pressure."

## Hook Enforcement Baseline

### Before (pre-hook, advisory-only)
- Mutation removals per 5 builds: 0
- Measured effect fill rate: ~5%
- S5 bypassed gates (last 5 builds): ~2
- Reference files loaded at Phase 0: 3
- Active hooks: 0
- Tests per gate: advisory only (no enforcement)

### After targets (FB25–FB29, under layered enforcement)
- Mutation removals per 5 builds: ≥1
- Measured effect fill rate: ≥60% (revised from 80% — prompt enforcement is
  probabilistic, not deterministic like hooks)
- S5 + subagent bypassed gates: ≤1 (revised from 0 — prompt rules are strong
  but not absolute; combined with hooks for foreground + session audit)
- Reference files loaded at Phase 0: 7+
- Active hooks: 13 (secondary layer for S5 + foreground)
- Prompt-hardened agents: ALL writing agents (primary layer)
- Tests per gate: automated + live + prompt-rule verification

## Active Mutation Portfolio
| Mutation ID | Target Failure | Applied | Measured Effect | Status |
|-------------|---------------|---------|-----------------|--------|
| FB24-1 | Phase 4 bypass when 1 test fails | 2026-06-02 | **PENDING** | Awaiting FB25 |
| FB24-2 | Enum type safety audit | 2026-06-02 | **PENDING** | Awaiting FB25 |
| FB23-3 | Inline fix prevention (Phase 6/7) | 2026-06-01 | Ineffective | Inline fixes occurred in FB23, FB24 |
| FB23-4 | Frontend build script verification | 2026-06-01 | **PENDING** | Awaiting FB25 |
| FB22-2 | Frontend stub prevention | 2026-05-30 | Ineffective | Stubs in FB23, FB24 |
| FB21-8 | Security-lessons topical reorg | 2026-05-25 | Effective | No duplicate L-numbers since |
| FB21-24 | Process auditor spawn | 2026-05-25 | **PENDING** | Awaiting FB25 |
| FB19-7 | Cross-skill mutation log review | 2026-05-25 | Ineffective | Main log still records gym/coach mutations |
| FB18-10 | Mutation tracking checkpoint | 2026-05-24 | Ineffective | FB24 missing mutations-applied.md |
| FB9 | Pattern 46 (Test-First Exit Gate) | 2026-05-23 | Ineffective | Bypassed in FB20, FB21, FB24 |

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
