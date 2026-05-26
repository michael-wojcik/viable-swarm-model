# DevOps Patterns

Universal infrastructure and deployment principles. Language-agnostic.

## Dockerfile
- CMD must use JSON exec form (not shell form)
- Copy dependency manifests BEFORE application source
- Pin base image versions, never `latest`
- `.dockerignore` must exclude secrets and build artifacts

## Docker Compose
- Every exposed service must have a healthcheck
- Use `depends_on` with `condition: service_healthy`
- Custom bridge network; never `network_mode: host`
- Port consistency: Dockerfile EXPOSE = compose ports = app bind port
- No `:-` default-value fallbacks for secrets

## Environment Variables
- Triple parity: `.env.example` = `docker-compose.yml` = code env var reads
- Identical names across all three files
- Secrets never hardcoded or committed

## Healthchecks
- Every service exposes a `/health` endpoint returning HTTP 200
- Healthcheck probes use the service's own protocol
