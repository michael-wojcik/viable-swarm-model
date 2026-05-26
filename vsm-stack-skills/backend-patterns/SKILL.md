# Backend Patterns

Universal backend architectural patterns. Language-agnostic.

## Auth Flow
1. Registration with role allowlist (exclude superuser roles)
2. Login returns structured response with token + role
3. JWT payload with `sub`, `role`, `exp`, `iat`
4. `get_current_user` raises 401 on ALL failure paths — never returns None
5. Refresh token queries DB for user before minting new tokens

## API Design
- REST: resource-oriented URLs, consistent error shapes
- GraphQL: depth limiting, complexity analysis, auth context propagation
  (see `security-patterns` for GraphQL security details)
- All list endpoints must filter by authenticated user (ownership)

## Middleware Ordering
CORS → Rate Limiting → Auth → Logging → Router

## Server Architecture
- Lazy initialization of shared resources (see `[language]-pitfalls` for specifics)
- Separate config from implementation
- Router-per-domain organization
