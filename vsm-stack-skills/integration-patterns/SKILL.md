---
name: integration-patterns
description: >
  Dead code and cross-layer integration anti-patterns for full-stack builds.
  Detects when frontend, backend, or shared layers exist but are not actually
  wired together. Covers unused GraphQL operations, unexercised real-time
  clients, orphaned shared types, and dead API contracts.
type: reference
---

# Integration Patterns — Cross-Layer Dead Code Detection

> **Purpose**: Prevent the common anti-pattern where a complete layer exists
> (GraphQL schema, Socket.IO server, shared types) but is never actually used
> by its consumer. Current `frontend-patterns` and `backend-patterns` cover
> intra-layer quality but not cross-layer integration health.
>
> **Created**: FB33 — trainer identified this as a systemic gap.

---

## Anti-Pattern 1: GraphQL Schema Exists but Frontend Uses 0% GraphQL

**Applies to**: vsm_coordinator, vsm_frontend_coder, vsm_auditor

**Symptoms**:
- `src/graphql/queries.ts` has exports but zero `.tsx` files import from it
- `src/main.tsx` wraps `<App />` in `<ApolloProvider>` but no page uses `useQuery`/`useMutation`
- Backend GraphQL resolvers are fully implemented and tested
- All frontend pages use `fetch()` against REST endpoints

**Detection**:
```bash
# Count .tsx files importing from queries.ts
 grep -r "from.*graphql/queries" src/pages/ | wc -l
# If result is 0 and queries.ts has >0 exports → dead GraphQL layer
```

**Severity**: ISSUE
**Fix**: Mandate ≥2 pages use GraphQL operations (see frontend-patterns FB33-2).

---

## Anti-Pattern 2: Socket.IO Events Defined but Never Emitted

**Applies to**: vsm_coordinator, vsm_backend_coder, vsm_auditor

**Symptoms**:
- `shared/sio-events.ts` (or equivalent) defines server→client events
- `app/sio.py` has `connect`/`disconnect`/`join_room` handlers
- Zero `sio.emit("EVENT_NAME", ...)` calls in any router or mutation handler
- Frontend `sio/client.ts` listens for events that never arrive

**Detection**:
```bash
# For each event in shared contracts, check for emit
for event in "NEW_COMMENT" "VIEWER_COUNT_UPDATE" "CONTENT_PUBLISHED"; do
    grep -r "sio.emit.*$event" app/ || echo "MISSING: $event"
done
```

**Severity**: ISSUE
**Fix**: Add Socket.IO emission checklist to coordinator (see backend-patterns FB33-3).

---

## Anti-Pattern 3: Shared Types Imported by Nobody

**Applies to**: vsm_coordinator, vsm_auditor

**Symptoms**:
- `shared/types.ts` (or `src/shared/types.ts`) exports enums, interfaces, DTOs
- Grepping the entire `src/` and `app/` trees shows zero imports of some exports
- Types were created during foundation wave but never used by implementers

**Detection**:
```bash
# For each export in shared/types.ts, count imports
grep -o "export \(interface\|type\|enum\) \w" shared/types.ts | while read line; do
    name=$(echo "$line" | awk '{print $3}')
    count=$(grep -r "$name" src/ app/ | grep -v "shared/types" | wc -l)
    echo "$name: $count imports"
done
```

**Severity**: LOW (cleanup issue)
**Fix**: Coordinator should flag unused shared exports as cleanup items.

---

## Anti-Pattern 4: REST API Endpoints with No Frontend Consumer

**Applies to**: vsm_coordinator, vsm_frontend_coder, vsm_devops_coder

**Symptoms**:
- Backend has routes for `/api/v1/admin/users`, `/api/v1/reports/export`, etc.
- No frontend page, hook, or utility calls these endpoints
- Swagger/docs list endpoints that are never exercised

**Detection**:
```bash
# Extract all API paths from backend routers
# Cross-reference with frontend fetch() calls
grep -rP "fetch\(.*\/api\/v1" src/ | grep -oP "/api/v1/[^\"']+" | sort -u
```

**Severity**: LOW (may be intentional for external consumers)
**Fix**: Document intentionally unexposed endpoints. Flag unexpectedly unused ones.

---

## Anti-Pattern 5: Feature Flag / Config Exists but Never Checked

**Applies to**: vsm_coordinator, vsm_backend_coder, vsm_auditor

**Symptoms**:
- `config.py` defines `ENABLE_ANALYTICS: bool = True`
- No code path ever checks this flag; analytics always runs
- The config is dead — it creates false confidence in configurability

**Severity**: LOW
**Fix**: Remove unused config fields or wire them into conditional logic.

---

## Coordinator Integration Checklist

The coordinator SHOULD verify these cross-layer health checks during Phase 6:

| Check | Command/Method | Threshold | Severity |
|---|---|---|---|
| GraphQL adoption rate | Count `.tsx` importing `queries.ts` | ≥ 2 pages | ISSUE if 0 |
| Socket.IO emission coverage | Count `sio.emit()` per defined event | 100% emitted | ISSUE if < 100% |
| Shared type usage | Count imports per shared export | All used | LOW if unused |
| REST endpoint consumers | Cross-reference with frontend fetches | Documented | LOW if unexpected |
| Config flag usage | Grep for config field references | All referenced | LOW if unused |

---

## Source

- **Fitness Build**: FB33 (StreamLine)
- **Trainer Gap**: "Frontend-backend paradigm disconnect — frontend used 100% REST while complete GraphQL layer and Apollo Client setup exist as dead code."
- **Score Impact**: 3/5 (moderate gap)
