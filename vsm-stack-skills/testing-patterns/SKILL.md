# Testing Patterns

Universal testing strategy and philosophy. Language-agnostic.

## Test Pyramid
- Unit tests: fast, isolated, many
- Integration tests: API boundaries, fewer
- E2E tests: critical user flows, fewest

## Fixtures and Setup
- Database reset per test (transaction rollback or cleanup)
- Auth fixtures for each role
- Test data factories, not hardcoded data

## Mocking
- Mock external services, not internal logic
- Mock time for time-dependent tests
- Mock randomness for deterministic tests

## Coverage
- Every endpoint: at least one test
- Every auth guard: valid AND invalid token tests
- Every role guard: wrong-role user tests
- Trivial tests do not count toward coverage
