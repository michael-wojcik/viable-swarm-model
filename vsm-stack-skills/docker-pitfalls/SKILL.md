# Docker / Compose Pitfalls

**Version scope**: Docker Engine 24+, Compose spec 3.8+.

Empirical traps discovered by the VSM swarm in containerization and orchestration.

## Docker-Compose `:-` Fallbacks (L37, FB2, FB18)
NEVER use `${VAR:-default}` or hardcoded literal passwords in `docker-compose.yml`.
Services must fail to start if required env vars are missing. Fallbacks silently
embed credentials and bypass fail-safe configuration.

**Verification**:
```bash
grep -n ':-' docker-compose.yml && echo "BLOCKER: :- fallback found" || echo "PASS"
```

## Dockerfile Layer Ordering
Copy dependency manifests (`requirements.txt`, `package.json`) BEFORE installing
dependencies. Copy application source AFTER. This maximizes layer cache reuse.

## `.dockerignore` Mandatory (FB2)
Every project with a Dockerfile MUST have a `.dockerignore` that excludes:
`.env`, `.git/`, `node_modules/`, `__pycache__/`, `.kimi/`, `*.md` (except README).

**Verification**:
```bash
test -f .dockerignore && grep -q '\.env' .dockerignore && echo "PASS" || echo "BLOCKER"
```

## Dockerfile CMD Exec Form
Use JSON array syntax:
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Never shell form: `CMD uvicorn app.main:app`. Shell form breaks signal handling
and `docker stop` graceful shutdown.

## Healthchecks in docker-compose
Every service that exposes a port MUST have a `healthcheck` defined:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```
Backend code MUST implement a `/health` endpoint that returns HTTP 200.

## Compose `depends_on` with Condition
Use `depends_on` with `condition: service_healthy` (not just `service_started`).
Without this, the API container starts before Postgres is ready and crashes on
first connection attempt.

## Never `latest` Tag
Pin image versions explicitly: `postgres:15-alpine`, `redis:7-alpine`.
`latest` is non-reproducible and breaks builds when upstream updates.

## Port Consistency Triple-Check
The port exposed in `Dockerfile` (`EXPOSE 8000`), the port mapped in
`docker-compose.yml` (`ports: - "8000:8000"`), and the port the app actually
binds to (`--port 8000` or `PORT` env var) MUST be identical.

## Network Isolation
Use a custom bridge network in docker-compose. Never use `network_mode: host`.
Host networking breaks port isolation and conflicts on shared development machines.

## Volume Mount Safety
Do not mount the entire project root (`.`) into a container that writes files
back (e.g., `node_modules` bind-mount). Use named volumes for persistent data
and explicit file mounts for config.

## CMD / ENTRYPOINT Target Exists
The file referenced by `CMD` or `ENTRYPOINT` must actually exist in the image.
If the Dockerfile has `CMD ["python", "app/main.py"]`, then `app/main.py` must exist.

## Frontend Dockerfile Production Build (FB3, FB24)
Frontend Dockerfiles MUST run `npm run build` and serve static assets.
`npm run dev` or Vite dev server is NEVER acceptable in a production Dockerfile.

**Verification**:
```bash
grep -q 'npm run dev' frontend/Dockerfile && echo "BLOCKER: dev server in prod" || echo "PASS"
```

## Environment Variable Triple Parity (FB18, FB22)
`.env.example` MUST list every variable referenced in `docker-compose.yml`.
If `config.py` exists, verify `os.getenv()` calls use IDENTICAL names.
A 3-way split (e.g., `DATABASE_URL` in compose, `DB_CONNECTION` in `.env.example`,
`DB_URL` in config.py) is a BLOCKER.

## Dockerfile Build Args for Frontend (FB3)
`VITE_API_URL` and `VITE_WS_URL` MUST be passed as `ARG` in the frontend Dockerfile.
Runtime env vars are not available at build time and will bake as `undefined`
into static bundles if not passed as `ARG`.

## Docker-Compose Command Module Verification (FB23)
For every `command:` or `CMD` in `docker-compose.yml` that references a Python
module (e.g., `celery -A app.celery_app`), verify the module path matches the
actual file layout inside the container. If `WORKDIR` is `/app` and the module is
`celery_app.py` at the root, the correct command is `celery -A celery_app`, NOT
`celery -A app.celery_app`.

## Dockerfile COPY Syntax Purity (FB25)
Dockerfile `COPY`, `ADD`, and non-`RUN` instructions MUST use pure Dockerfile
syntax ONLY. Never embed shell operators (`||`, `&&`, `>`, `2>/dev/null`,
`|`, `;`) in COPY/ADD instructions. If a file might not exist, use a separate
`RUN` step or omit the COPY and document the fallback.

**Source**: FB25 `frontend/Dockerfile` contained
`COPY nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null || true`,
which Docker's COPY parser rejected as invalid syntax.

## Rule: Env-Var Port Parity

**Status**: Active (FB26-sourced)
**Severity**: ISSUE
**Applies to**: vsm_devops_coder, vsm_coordinator

For every `VITE_*_URL` or `*_URL` in `.env.example`, verify the port matches the corresponding service port in `docker-compose.yml`. Mismatches cause runtime connection failures that are hard to debug.

**Check**:
```bash
grep -E "VITE_.*_URL|API_URL|WS_URL" .env.example
grep "ports:" docker-compose.yml
```

## Rule: `.dockerignore` Co-Creation with Dockerfile

**Status**: Active (FB26-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_devops_coder, vsm_coordinator

Every `Dockerfile` created MUST have a `.dockerignore` in the same directory. The `.dockerignore` MUST at minimum exclude:
```
.env
node_modules/
__pycache__/
*.pyc
.venv/
```

**Check**: Before completing foundation wave, verify `find . -name Dockerfile | while read f; do dir=$(dirname "$f"); [ -f "$dir/.dockerignore" ] || echo "MISSING: $dir/.dockerignore"; done` returns nothing.
