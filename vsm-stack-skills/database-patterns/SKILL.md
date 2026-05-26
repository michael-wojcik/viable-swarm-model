# Database Patterns

Universal database design and usage patterns. Language-agnostic.

## Schema Design
- Normalize until you have a reason to denormalize
- Use appropriate constraints (NOT NULL, UNIQUE, FOREIGN KEY)
- Version-control all schema changes via migrations

## Query Performance
- N+1 prevention: eager loading, batching, or JOINs
- Index on frequently queried columns
- Avoid SELECT * in production queries

## Connection Management
- Connection factory (avoid module-level instantiation — see `[language]-pitfalls`)
- Connection pooling for production
- Separate read and write connections if scale requires

## Migrations
- Migration files must be reversible
- Test migrations against production-like data volumes
- Never modify existing migration files after deployment
