# Frontend Patterns

Universal frontend architectural patterns. Language-agnostic.

## State Management
- Server state (API/GraphQL) ≠ client state (UI/forms)
- Use caching library for server state, lightweight store for client state
- Never duplicate server state in local store without sync strategy

## Routing
- Role-aware route guards for restricted pages
- Route params validated before component render
- Deep links must work (no state required to render)

## Build Pipeline
- Type-checking must pass before build succeeds
- Path aliases configured in build tool AND type checker
- Proxy targets must match backend service ports

## Cross-Origin
- `credentials: "include"` when backend allows credentials
- No wildcard CORS with credentials

## Testing
- Every page: at least render test
- Every store: state transition test
- Every form: validation edge case test

---

## Rule: React useEffect Dependency Array Traps

**Status**: Active (FB24–FB29 empirical)
**Severity**: BLOCKER
**Applies to**: vsm_frontend_coder, vsm_frontend_fix, vsm_frontend_tester, vsm_auditor

Missing or incorrect `useEffect` dependencies are the single most common source of frontend bugs in the swarm's fitness builds. They cause stale closures, infinite re-render loops, and missed state updates.

**Trap 1: Missing dependencies** (FB24, FB26)
```tsx
// WRONG — missing `userId` dependency
useEffect(() => {
    fetchUser(userId).then(setUser);
}, []); // Stale closure: always fetches initial userId

// CORRECT
useEffect(() => {
    fetchUser(userId).then(setUser);
}, [userId]);
```

**Trap 2: Object / array literal in dependency array** (FB25, FB27)
```tsx
// WRONG — new object every render → infinite loop
useEffect(() => {
    fetchData(filters);
}, [{ status: "active" }]);

// CORRECT — stringify or memoize
useEffect(() => {
    fetchData(filters);
}, [JSON.stringify(filters)]);
// OR memoize the object itself
const stableFilters = useMemo(() => ({ status: "active" }), []);
useEffect(() => { fetchData(stableFilters); }, [stableFilters]);
```

**Trap 3: Missing cleanup for subscriptions / timers** (FB28)
```tsx
// WRONG — timer leaks on unmount
useEffect(() => {
    setInterval(() => pollStatus(), 5000);
}, []);

// CORRECT — cleanup
useEffect(() => {
    const id = setInterval(() => pollStatus(), 5000);
    return () => clearInterval(id);
}, []);
```

**Prevention rules**:
1. Frontend coder MUST run `eslint-plugin-react-hooks` (`react-hooks/exhaustive-deps`) and treat warnings as ISSUEs.
2. Auditor MUST grep for `useEffect` calls and verify dependency arrays match referenced variables.
3. Frontend tester MUST verify components re-fetch or re-calculate when props change.

**Source**: FB24 had stale auth token in `useEffect`; FB25 infinite loop with filter object; FB26 missing `userId`; FB28 timer leak causing memory accumulation.

---

## Rule: Zustand Store Hydration Patterns

**Status**: Active (FB27-sourced, FB29 confirmed)
**Severity**: MEDIUM
**Applies to**: vsm_frontend_coder, vsm_frontend_tester

Zustand with `persist` middleware causes hydration mismatch when the server-rendered HTML does not match the client-side persisted state. This produces React hydration errors in development and can flash incorrect UI in production.

**Correct pattern**:
```tsx
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useStore = create(
    persist(
        (set) => ({ ... }),
        {
            name: 'app-storage',
            skipHydration: true, // ✅ Defer hydration to client
        }
    )
);

// In root component or layout
useEffect(() => {
    useStore.persist.rehydrate();
}, []);
```

**Incorrect pattern** (MEDIUM):
```tsx
const useStore = create(
    persist((set) => ({ theme: "dark" }), { name: 'app-storage' })
    // ❌ No skipHydration — SSR HTML has "light", client has "dark" from localStorage
);
```

**Prevention rules**:
1. Any Zustand store using `persist` MUST set `skipHydration: true`.
2. Rehydration MUST happen inside `useEffect` (client-only).
3. Components reading persisted state MUST handle `undefined` / default state during SSR.

**Source**: FB27 dashboard flashed wrong theme on load; FB29 settings page had hydration mismatch with persisted user preferences.

---

## Rule: React Router Loader / Action Patterns

**Status**: Active (FB28-sourced)
**Severity**: MEDIUM
**Applies to**: vsm_frontend_coder, vsm_coordinator

React Router v6+ loaders and actions replace `useEffect` data fetching but introduce new failure modes: unhandled thrown responses, missing `json()` wrappers, and loader data shape mismatches with component props.

**Correct pattern**:
```tsx
// loader.ts
export async function dashboardLoader({ request }: LoaderFunctionArgs) {
    const res = await fetch("/api/dashboard", { credentials: "include" });
    if (!res.ok) {
        throw new Response("Failed to load dashboard", { status: res.status });
    }
    return json(await res.json()); // ✅ Always wrap in json()
}

// component.tsx
export default function DashboardPage() {
    const data = useLoaderData<typeof dashboardLoader>(); // ✅ Typed
    return <DashboardView data={data} />;
}
```

**Incorrect pattern** (MEDIUM):
```tsx
export async function badLoader() {
    const res = await fetch("/api/dashboard");
    return res.json(); // ❌ Missing json() wrapper — may return Promise
}

// Component assumes object but gets Promise or undefined
const data = useLoaderData(); // Untyped — shape drift risk
```

**Prevention rules**:
1. Every loader MUST return `json(...)` or `redirect(...)`.
2. Every action MUST handle errors and return `json({ error: "..." }, { status: 400 })` on failure.
3. Coordinator MUST verify loader data shape matches the component's TypeScript interface.
4. Frontend tester MUST test the error boundary path for each loader (simulate 4xx/5xx).

**Source**: FB28 `DashboardPage` crashed when loader returned raw `Promise`; error boundary caught it but UX was broken. FB29 loader data shape drifted from backend DTO.

---

## Rule: Vite Proxy Config Pitfalls

**Status**: Active (FB25, FB26 empirical)
**Severity**: MEDIUM
**Applies to**: vsm_frontend_coder, vsm_coordinator

Vite's `server.proxy` configuration is a common source of integration failures. Misconfigured proxy paths, missing `changeOrigin`, or incorrect target ports cause CORS errors in development that do not appear in production.

**Correct pattern**:
```ts
// vite.config.ts
export default defineConfig({
    server: {
        proxy: {
            "/api": {
                target: "http://localhost:8000", // ✅ Matches backend port
                changeOrigin: true,               // ✅ Required for virtual hosts
                secure: false,                    // ✅ Dev only
            },
            "/graphql": {
                target: "http://localhost:8000",
                changeOrigin: true,
                ws: true, // ✅ WebSocket proxy for GraphQL subscriptions
            },
        },
    },
});
```

**Incorrect pattern** (MEDIUM):
```ts
server: {
    proxy: {
        "/api": "http://localhost:8000" // ❌ Missing changeOrigin
        // ❌ No /graphql proxy — GraphQL calls hit Vite dev server, 404
    }
}
```

**Prevention rules**:
1. Proxy target port MUST match the backend service port declared in `docker-compose.yml`.
2. Every API path prefix (`/api`, `/graphql`, `/auth`, `/ws`) MUST have a proxy entry.
3. `changeOrigin: true` MUST be set for all proxy entries.
4. Coordinator MUST verify `vite.config.ts` proxy matches `api-spec.md` base URL.

**Source**: FB25 `/graphql` calls 404'd because proxy only covered `/api`. FB26 WebSocket subscriptions failed because `ws: true` was missing.

---

## Rule: Frontend Build Verification Patterns

**Status**: Active (FB23-sourced, confirmed FB24–FB29)
**Severity**: BLOCKER
**Applies to**: vsm_frontend_tester, vsm_frontend_fix, vsm_coordinator

Frontend test runners (Vitest) transpile with esbuild and do NOT run full TypeScript type checking. A test suite can pass while `tsc -b` fails. Only `npm run build` (which invokes `tsc -b && vite build`) is a reliable Phase 4 gate.

**Correct pattern** (Phase 4 checklist):
```markdown
- [ ] `npm test -- --run` passes (all tests green)
- [ ] `npm run build` passes with exit code 0
- [ ] `tsc -b` produces zero errors
- [ ] No console warnings about missing exports or circular dependencies
```

**Incorrect pattern** (gate bypass):
```markdown
- [ ] `npm test -- --run` passes
# MISSING: npm run build — tsc errors leak to Phase 6
```

**Prevention rules**:
1. Frontend tester MUST run `npm run build` before declaring Phase 4 complete.
2. Coordinator MUST verify `npm run build` exit code is 0 during integration.
3. `package.json` SHOULD define `"build": "tsc -b && vite build"` so type checking is mandatory.
4. Any build failure in Phase 6 that `tsc -b` would have caught in Phase 4 is a **process violation**.

**Source**: FB23 frontend build failed in Phase 6 because `tsc -b` errors were not caught in Phase 4. FB24–FB29 consistently reproduce: Vitest passes, `npm run build` fails on unused imports. See `testing-patterns` for full H154 rule.
