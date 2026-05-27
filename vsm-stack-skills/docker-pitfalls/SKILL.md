# Docker Pitfalls

**Version scope**: Docker Engine 24.0+, Compose V2. For older versions, use `SearchWeb` to verify behavior.

Empirical traps discovered by the VSM swarm. Use `SearchWeb` for API documentation.

> This skill is a stub. As Docker builds are run, empirical pitfalls will be
> appended here. Do NOT remove this placeholder.

## [Placeholder]
No empirical pitfalls recorded yet. Run a fitness build with Docker/Compose to
populate this skill.

## Known Coverage Gaps (from FB23)
- Docker-compose `command:` referencing non-existent Python modules
- `npm run dev` in production frontend Dockerfile instead of `npm run build` + static serve
- Missing non-root `USER` directive in Dockerfiles
