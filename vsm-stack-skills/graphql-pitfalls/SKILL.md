# GraphQL Pitfalls

Framework-agnostic and framework-specific GraphQL traps discovered by the VSM
swarm through fitness builds. Covers Strawberry (Python) and Apollo Client
(TypeScript) stacks.

## Schema Parameter Verification (Strawberry)

NEVER assume `strawberry.Schema` accepts `validation_rules` or any parameter.
Verify BEFORE using:
```python
import inspect
"validation_rules" in inspect.signature(strawberry.Schema.__init__).parameters
```
Using non-existent parameters causes `TypeError` on import.
**Source**: FB2 `graphql.py` agent assumed `validation_rules` existed.

## Depth Limiting + Complexity Analysis

GraphQL APIs WITHOUT `@graphql-depth-limit` or complexity analysis are HIGH
severity findings. Depth limit max 10 is the minimum baseline.
**Source**: Anti-pattern #8, `security-lessons.md` L25.

## Context Builder Fail-Closed

`get_context` or equivalent context builders MUST propagate auth exceptions
(JWT errors, missing tokens). Never silently catch auth exceptions and return
an anonymous/unauthenticated context. Auth failures MUST result in GraphQL
errors or `AuthenticationError`, not `user = None`.
**Source**: `security-lessons.md` L63, FB21.

## Ownership Filtering on ALL List Queries

ALL list queries MUST filter by authenticated user. Unscoped list queries that
return all documents regardless of ownership are a HIGH severity finding.
This applies to both REST list endpoints AND GraphQL list resolvers.
**Source**: FB10, FB14, FB21.

## RBAC Parity Between REST and GraphQL

REST endpoints and GraphQL resolvers MUST enforce identical access control.
Ambiguous natural-language labels like "(owner-filtered)" in `api-spec.md`
cause interpretation drift. Require explicit `RBAC: [roles]` arrays for every
endpoint.
**Source**: Anti-pattern #54, FB17.

## Auto-CamelCase Verification (Strawberry)

Strawberry auto-camelCases field names. If the frontend introspects the schema
and writes queries with camelCase, but the backend resolver expects snake_case,
queries fail at runtime. Architect MUST declare the casing convention explicitly;
implementer MUST verify field names match.
**Source**: `security-lessons.md` L44, FB17.

## Subscription Ownership Verification

GraphQL subscription resolvers MUST verify resource ownership BEFORE yielding
events. A subscription that yields updates for ALL users' resources is an IDOR
vulnerability.
**Source**: `security-lessons.md` L57, FB20.

## Orphaned Queries (Apollo Client)

Every export from `queries.ts` MUST be imported by at least one page or
component. Orphaned exports are dead code that bloat bundles.
**Source**: Anti-pattern #52, FB17.

## Apollo Client Initialized but Unused

If `main.tsx` wraps the app in `ApolloProvider` but ALL pages use REST `fetch()`,
the GraphQL infrastructure is initialized but never exercised. Integration
checklist must verify Apollo Client is actually used.
**Source**: Anti-pattern #53, FB17.

## SQLAlchemy Enum → GraphQL Type Mismatch

`Mapped[EnumType] = mapped_column(sa.String(50))` stores enum values as strings
in the database. When the GraphQL resolver returns the enum, Strawberry may
expect an Enum object but receive a string, causing `AttributeError: 'str'
object has no attribute 'value'`.
**Prevention**: Use `mapped_column(sa.Enum(EnumType))` or convert strings to
enums in the resolver before returning.
**Source**: FB24, H203.
