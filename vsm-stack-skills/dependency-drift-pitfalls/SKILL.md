# Dependency Drift Pitfalls

**Version scope**: All languages. Use `SearchWeb` for package manager documentation.

Empirical traps discovered by the VSM swarm.

## Pitfall 1: Phase 0 environment fix not persisted to manifest
**Source**: FB23 Phase 0  
**Symptom**: Build environment upgrades `strawberry-graphql` from `0.235.2` to `0.316.0` to resolve a Pydantic incompatibility, but `requirements.txt` still specifies `0.235.2`. A clean install from the manifest fails with `ImportError: cannot import name 'is_new_type'`.

**Prevention rule**:
1. After ANY Phase 0 environment fix that changes a resolved version, update the manifest file (`requirements.txt`, `package.json`, `Cargo.toml`, etc.) to match.
2. Before declaring Phase 0 complete, run a clean install in a fresh virtual environment/container from the manifest ONLY.
3. If the clean install fails, the manifest is drifted — fix it before proceeding.

## Pitfall 2: Manifest specifies incompatible versions
**Source**: FB23 `backend/requirements.txt`  
**Symptom**: `requirements.txt` pins `strawberry-graphql==0.235.2` but the project uses Pydantic 2.13.4 features that require `strawberry-graphql>=0.240.0`. Tests pass in the dev environment (which has 0.316.0) but fail on CI or fresh clone.

**Prevention rule**:
1. Add a manifest-environment parity check to Phase 0 or Phase 4:
   ```bash
   # Python example
   pip freeze | grep -E "(strawberry|pydantic|sqlalchemy)" > resolved.txt
   diff <(sort requirements.txt) <(sort resolved.txt) || echo "DRIFT DETECTED"
   ```
2. If drift is detected, update the manifest or pin compatible versions.

## Pitfall 3: No agent verifies manifest-environment parity
**Source**: FB23 meta-report  
**Symptom**: No checklist item, no agent prompt, and no automated verification ensures the manifest matches the environment after fixes. This is a reproducibility vulnerability.

**Prevention rule**:
1. `vsm_coordinator` integration checklist MUST include: "Verify `requirements.txt` / `package.json` matches versions actually resolved in the build environment after any Phase 0 fixes."
2. `vsm_backend_tester` MUST verify that a clean install from `requirements.txt` succeeds before declaring tests complete.
3. `vsm_devops_coder` MUST verify Docker builds use the manifest, not pre-installed packages.

## Known Coverage Gaps
- Lockfile hygiene (`package-lock.json`, `poetry.lock`, `uv.lock` not committed)
- Transitive dependency conflicts (A requires B>=2.0, C requires B<2.0)
- Dev vs production dependency separation (`devDependencies` leaking into production)
