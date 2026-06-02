# Shared Cross-Agent Contracts

> Rules that apply to multiple agents. Include this file in coder and fixer
> agents rather than duplicating the text.

---

## Cross-File Integration Contracts

The backend and frontend agents implement the same system independently.
These contracts MUST be honored or integration will fail:

1. **Auth Token Key Parity**: The key returned by the backend login endpoint
   (e.g., `access_token`) MUST match exactly what the frontend stores in
   `localStorage`.

2. **Role Enum Parity**: `Role` / `UserRole` enum values MUST be used verbatim
   on both sides. No renaming, no case changes.

3. **GraphQL Auto-CamelCase**: Strawberry auto-camelCases snake_case Python
   fields. The frontend queries camelCase names. Example: backend `created_at`
   → GraphQL `createdAt`. Do NOT query snake_case from the frontend.

4. **CORS Credentials**: If `allow_credentials=True`, the frontend origin MUST
   be in `allow_origins`. Wildcard `*` with credentials is a BLOCKER on both
   sides.

5. **Error Response Shape**: Auth failures MUST return `{"detail": "..."}` so
   the frontend's error handler can parse them consistently.

6. **WebSocket Event Names (if applicable)**: Event names emitted by the backend
   MUST match exactly what the frontend listens for. Prefer a shared constants
   file.

---

## Fix Agent Universal Safety Rules

1. Never weaken or remove security controls (auth, CORS, rate limiting) to fix
   a test or bug.
2. Never expose internal fields in response DTOs/API responses to fix
   serialization errors.
3. If the security gate flagged a finding, your fix MUST NOT introduce new
   security issues.

---

## Re-audit Report Artifact

Before declaring any fix complete, produce `.kimi/re-audit-report.md`
documenting: file changed, change description, test result, regression check.

Use this table template:

```markdown
| File | Change | Test Result | Import Check | Regression? |
```

If ANY test fails or import check fails, the fix is NOT complete.

---

## Phase Discipline — No Inline Fixes

- **Phase 4 (Testing)**: If tests reveal bugs in application code, report them
  as test failures. Do NOT fix application code inline. Inline fixes bypass the
  Phase 4 Exit Gate and the Phase 7 Fix Wave protocol.
- **Phase 6 (Integration)**: You are a Phase 7 agent. If invoked during Phase 6,
  STOP and route back to Phase 7 proper. Inline fixes bypass re-audit and
  post-fix security re-check.


