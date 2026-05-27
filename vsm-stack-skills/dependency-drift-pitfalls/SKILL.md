# Dependency Drift Pitfalls

**Version scope**: All languages. Use `SearchWeb` for package manager documentation.

Empirical traps discovered by the VSM swarm.

> This skill is a stub. As builds are run, empirical pitfalls will be appended
> here. Do NOT remove this placeholder.

## [Placeholder]
No empirical pitfalls recorded yet. Run a fitness build to populate this skill.

## Known Coverage Gaps (from FB23)
- Phase 0 environment fix not persisted to `requirements.txt` / `package.json`
- `requirements.txt` specifies incompatible versions that fail on clean install
- No agent verifies manifest-environment parity after Phase 0 fixes
