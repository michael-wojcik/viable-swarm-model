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
