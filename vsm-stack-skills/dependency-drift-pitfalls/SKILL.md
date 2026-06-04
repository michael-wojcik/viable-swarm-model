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

---

## Pitfall 4: Lockfile Hygiene — Outdated or Missing Lockfile

**Source**: FB22, FB25  
**Symptom**: `package-lock.json` is not committed to git, or `poetry.lock` / `uv.lock` is stale relative to `pyproject.toml`. CI installs resolve different transitive versions than the developer's machine, causing "works on my machine" failures.

**Prevention rules**:
1. **Lockfile MUST be committed** to version control for every project using npm, Poetry, uv, or Cargo. The only exception is pip with `requirements.txt` (which is itself a flat lockfile).
2. **Regenerate lockfile after ANY manifest change**:
   ```bash
   # Node
   npm install && npm update  # updates lockfile
   # Python (Poetry)
   poetry lock --no-update
   # Python (uv)
   uv lock
   ```
3. **CI MUST install from lockfile**, not from manifest alone:
   ```bash
   # Node — ci uses lockfile exactly
   npm ci
   # Python (Poetry)
   poetry install --no-interaction --no-ansi
   # Python (uv)
   uv sync --frozen
   ```
4. **Coordinator MUST verify** lockfile timestamp is newer than manifest timestamp in git history.

**Source**: FB22 CI failed because `package-lock.json` was gitignored; CI resolved a newer `vite` minor version with breaking changes. FB25 `poetry.lock` was stale after `pyproject.toml` was updated; fresh install pulled incompatible `httpx` version.

---

## Pitfall 5: Transitive Dependency Conflict Detection

**Source**: FB23, FB26  
**Symptom**: Package A requires `B>=2.0`, package C requires `B<2.0`. The package manager silently installs a compromised middle version (e.g., `B==2.0.0rc1`) or resolves unexpectedly. Runtime behavior changes without any direct manifest change.

**Python example**:
```
strawberry-graphql==0.235.2  → requires pydantic>=2.0
some-other-package==1.2.3    → requires pydantic<2.0
# pip resolver may fail OR install a pre-release that satisfies both
```

**Prevention rules**:
1. **After adding a new dependency**, verify resolution in a fresh environment:
   ```bash
   python -m venv .fresh_env
   source .fresh_env/bin/activate
   pip install -r requirements.txt
   pip check  # Reports dependency conflicts
   ```
2. **Node**: `npm ls` after install shows peer dependency warnings. Treat `ERESOLVE` warnings as BLOCKERs in Phase 0.
3. **Coordinator MUST run `pip check` or `npm audit`** as part of Phase 0 integration.
4. If a conflict is detected, pin the transitive dependency explicitly in the manifest with a comment explaining why.

**Source**: FB23 `pip install` resolved a `strawberry-graphql` pre-release that satisfied both Pydantic constraints but had a breaking API change. FB26 `npm install` produced `ERESOLVE` warnings that were ignored; frontend build broke on CI.

---

## Pitfall 6: Dev vs Production Dependency Separation

**Source**: FB22, FB25  
**Symptom**: Dev dependencies (`pytest`, `black`, `vite`, `@types/*`) are installed in the production Docker image, bloating image size and increasing attack surface. Python projects sometimes install `requirements-dev.txt` into the production container.

**Prevention rules**:
1. **Node**: `package.json` MUST use `devDependencies` for test/build tooling. Production install MUST use:
   ```bash
   npm ci --omit=dev
   ```
2. **Python**: Separate `requirements.txt` (production) from `requirements-dev.txt`. Dockerfile MUST use:
   ```dockerfile
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   # NEVER copy or install requirements-dev.txt in production stage
   ```
3. **Docker multi-stage builds**: Build stage may have dev deps, but the runtime stage MUST copy only production artifacts:
   ```dockerfile
   # Build stage
   FROM node:20 AS builder
   COPY package*.json ./
   RUN npm ci  # includes dev deps for build
   COPY . .
   RUN npm run build

   # Runtime stage
   FROM node:20-alpine
   COPY package*.json ./
   RUN npm ci --omit=dev  # production only
   COPY --from=builder /app/dist ./dist
   ```
4. **Auditor MUST verify** production image does not contain test frameworks, type checkers, or debug tools.

**Source**: FB22 production image contained `pytest` and `black` because `requirements-dev.txt` was concatenated into `requirements.txt`. FB25 Docker image was 400MB larger than necessary because `node_modules` included all `devDependencies`.

---

## Known Coverage Gaps (Closed)
- ✅ Lockfile hygiene (`package-lock.json`, `poetry.lock`, `uv.lock` not committed) — addressed in Pitfall 4
- ✅ Transitive dependency conflicts (A requires B>=2.0, C requires B<2.0) — addressed in Pitfall 5
- ✅ Dev vs production dependency separation (`devDependencies` leaking into production) — addressed in Pitfall 6
