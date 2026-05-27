# Docker Pitfalls

**Version scope**: Docker Engine 24.0+, Compose V2. For older versions, use `SearchWeb` to verify behavior.

Empirical traps discovered by the VSM swarm. Use `SearchWeb` for API documentation.

## Pitfall 1: Docker-Compose `command:` referencing non-existent Python modules
**Source**: FB23 `docker-compose.yml:49`  
**Symptom**: Worker service declares `command: celery -A app.celery_app worker ...` but there is no `app` package in the container. The module is `celery_app.py` at `/app` WORKDIR. Container crashes on startup with `ModuleNotFoundError: No module named 'app'`.

**Prevention rule**:
1. Before declaring docker-compose valid, verify every `command:` references an existing module/script.
2. For Celery: `celery -A <module>` must match the actual Python module name (not a guessed package path).
3. Check `WORKDIR` in Dockerfile against module import paths.

## Pitfall 2: `npm run dev` in production frontend Dockerfile
**Source**: FB23 `frontend/Dockerfile`  
**Symptom**: Frontend Dockerfile runs `npm run dev` (Vite dev server) instead of `npm run build` + static serve. This creates a development server in production, missing optimization, source maps exposed, and no proper static asset serving.

**Prevention rule**:
1. Frontend Dockerfiles MUST use multi-stage build: `npm run build` in builder stage, then `nginx:alpine` or `node:slim` serving the `dist/` folder.
2. `npm run dev` is NEVER acceptable in a production Dockerfile.
3. Verify `EXPOSE` port matches the static server (not Vite's dev port 5173).

## Pitfall 3: Missing non-root `USER` directive
**Symptom**: Containers run as root. If the app is compromised, attacker has root access to container filesystem.

**Prevention rule**:
1. Add `RUN useradd -m appuser && USER appuser` (or equivalent) before `CMD`/`ENTRYPOINT`.
2. Verify files the app needs to read are readable by the non-root user.

## Pitfall 4: Dockerfile CMD target does not exist
**Source**: FB17, FB22  
**Symptom**: `CMD ["uvicorn", "app.main:app", ...]` but `app/main.py` is missing or named differently. Container exits immediately.

**Prevention rule**:
1. Verify the target module in `CMD`/`ENTRYPOINT` exists in the build context.
2. For FastAPI: `app.main:app` requires `app/__init__.py` AND `app/main.py` with `app = FastAPI()`.

## Known Coverage Gaps
- Docker networking between services (backend can't reach database hostname)
- Volume mount permissions in dev vs production
- Healthcheck directives missing or incorrect
