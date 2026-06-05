#!/usr/bin/env python3
"""
Test Split Orchestrator — Concrete spawn planner for vsm_backend_tester
and vsm_frontend_tester to prevent timeouts.

Given a list of test domains, build tier, and stack, estimates test lines
per domain and groups them into chunks < 300 lines. Outputs a structured
spawn plan that S5 can execute sequentially.

Usage:
    python3 test-split-orchestrator.py --domains "auth,courses,uploads" \
        --tier 2 --backend --build-dir <dir>

Heuristics derived from fitness builds FB25–FB32.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Heuristics — lines of test code per domain (median from fitness builds)
# ---------------------------------------------------------------------------

BACKEND_HEURISTICS = {
    "auth": 120,          # login, register, me, role checks, token refresh
    "authentication": 120,
    "authorization": 100,
    "roles": 80,
    "jwt": 60,
    "graphql": 100,       # queries, mutations, schema introspection
    "queries": 80,
    "mutations": 80,
    "subscriptions": 80,
    "websocket": 80,      # socket.io, realtime events
    "ws": 80,
    "realtime": 80,
    "socketio": 80,
    "upload": 70,         # file upload, storage
    "uploads": 70,
    "files": 60,
    "media": 60,
    "user": 60,           # basic CRUD per entity
    "users": 60,
    "profile": 50,
    "course": 60,
    "courses": 60,
    "recipe": 60,
    "recipes": 60,
    "ingredient": 50,
    "ingredients": 50,
    "meal": 50,
    "meals": 50,
    "shopping": 50,
    "list": 50,
    "lists": 50,
    "item": 40,
    "items": 40,
    "order": 60,
    "orders": 60,
    "payment": 70,
    "payments": 70,
    "notification": 50,
    "notifications": 50,
    "search": 60,
    "admin": 70,
    "settings": 50,
    "config": 40,
    "health": 30,
    "docker": 30,         # infra tests
    "db": 40,
    "database": 40,
    "migration": 40,
    "celery": 60,         # background task tests
    "tasks": 50,
    "worker": 50,
    "social": 60,         # follows, likes, comments
    "follow": 50,
    "like": 40,
    "comment": 50,
    "review": 50,
    "rating": 40,
}

FRONTEND_HEURISTICS = {
    "auth": 90,           # login page, register page, route guards
    "login": 70,
    "register": 70,
    "home": 60,
    "dashboard": 60,
    "profile": 60,
    "user": 60,
    "settings": 50,
    "course": 60,
    "courses": 60,
    "recipe": 60,
    "recipes": 60,
    "list": 50,
    "detail": 50,
    "form": 60,
    "modal": 50,
    "component": 50,
    "components": 50,
    "store": 50,          # zustand/pinia store tests
    "state": 50,
    "graphql": 60,        # query tests, cache tests
    "queries": 60,
    "mutation": 50,
    "apollo": 50,
    "router": 50,
    "routing": 50,
    "navigation": 50,
    "upload": 60,
    "uploads": 60,
    "search": 50,
    "filter": 40,
    "sort": 40,
    "pagination": 40,
    "admin": 70,
    "table": 50,
    "chart": 50,
    "build": 40,          # build verification (npm run build)
}


def estimate_lines(domain: str, is_backend: bool) -> int:
    """Return estimated test lines for a domain."""
    table = BACKEND_HEURISTICS if is_backend else FRONTEND_HEURISTICS
    d = domain.lower().strip()
    return table.get(d, 50)  # Default 50 lines for unknown domains


def group_domains(domains: list[str], max_lines: int, is_backend: bool) -> list[dict]:
    """Group domains into chunks where estimated total < max_lines."""
    groups = []
    current = []
    current_lines = 0

    # Sort by descending estimated lines (largest first) for better packing
    sorted_domains = sorted(domains, key=lambda d: estimate_lines(d, is_backend), reverse=True)

    for d in sorted_domains:
        lines = estimate_lines(d, is_backend)
        if current_lines + lines > max_lines and current:
            groups.append({
                "domains": current.copy(),
                "estimated_lines": current_lines,
            })
            current = [d]
            current_lines = lines
        else:
            current.append(d)
            current_lines += lines

    if current:
        groups.append({
            "domains": current.copy(),
            "estimated_lines": current_lines,
        })

    return groups


def generate_plan(
    domains: list[str],
    tier: int,
    is_backend: bool,
    max_lines: int,
    build_dir: Optional[Path],
) -> str:
    """Generate the Markdown spawn plan."""
    groups = group_domains(domains, max_lines, is_backend)
    stack = "Backend" if is_backend else "Frontend"
    tier_min = {1: 3, 2: 6, 3: 10} if is_backend else {1: 2, 2: 5, 3: 8}
    min_tests = tier_min.get(tier, 6)

    lines = [
        f"# Test Split Orchestrator — {stack} Spawn Plan",
        f"**Tier**: {tier} | **Max lines per spawn**: {max_lines} | **Domains**: {len(domains)}",
        f"**Total estimated test lines**: {sum(g['estimated_lines'] for g in groups)}",
        f"**Recommended spawns**: {len(groups)}",
        f"**Tier minimum meaningful tests**: {min_tests}",
        "",
        "> This plan is auto-generated by `scripts/test-split-orchestrator.py`.",
        "> S5 may override groupings based on domain coupling (e.g., auth + user profile).",
        "",
        "## Spawn Schedule",
        "",
        "| Spawn # | Domains | Est. Lines | Agent |",
        "|---|---|---|---|",
    ]

    agent_type = "vsm_backend_tester" if is_backend else "vsm_frontend_tester"
    for i, g in enumerate(groups, 1):
        domains_str = ", ".join(g["domains"])
        lines.append(f"| {i} | {domains_str} | {g['estimated_lines']} | {agent_type} |")

    lines.extend([
        "",
        "## Execution Protocol",
        "",
        f"1. **Spawn {agent_type} for group 1**. Include explicit domain list in task prompt.",
        "2. **Wait for completion** before spawning group 2. Do NOT spawn all groups in parallel — this causes context pressure and timeout.",
        "3. **After final group**, run full test suite (`pytest` or `npm test`) to verify no regressions.",
        "4. **Count meaningful tests** across all groups. If total < tier minimum, spawn additional agent for missing coverage.",
        "",
        "## Agent Task Template (copy-paste per spawn)",
        "",
        "```markdown",
        f"**Role**: {stack} Testing Specialist — Spawn [N] of [{len(groups)}]",
        f"**Domains**: [list from Spawn Schedule above]",
        "**Scope**: Write tests ONLY for the listed domains. Do NOT test other domains.",
        f"**Target**: < {max_lines} lines of test code.",
        "**Minimum meaningful tests**: [tier minimum / number of spawns, rounded up]",
        "**Exit criteria**: All tests pass. Report test count and coverage.",
        "```",
        "",
    ])

    if len(groups) == 1 and sum(g["estimated_lines"] for g in groups) > max_lines * 0.8:
        lines.extend([
            "## ⚠️ WARNING",
            "",
            f"Total estimated lines ({sum(g['estimated_lines'] for g in groups)}) is close to the {max_lines}-line single-spawn limit.",
            "Consider manually splitting the largest domain or reducing scope per spawn.",
            "",
        ])

    if build_dir:
        lines.append("> **Build directory**: " + str(build_dir))

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Split Orchestrator")
    parser.add_argument("--domains", required=True, help="Comma-separated test domains")
    parser.add_argument("--tier", type=int, default=2, choices=[1, 2, 3])
    parser.add_argument("--backend", action="store_true", help="Backend test planning")
    parser.add_argument("--frontend", action="store_true", help="Frontend test planning")
    parser.add_argument("--max-lines", type=int, default=300, help="Max lines per spawn")
    parser.add_argument("--build-dir", help="Build directory to write plan to")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args()

    if not args.backend and not args.frontend:
        print("ERROR: Specify --backend or --frontend", file=sys.stderr)
        return 1

    domains = [d.strip() for d in args.domains.split(",") if d.strip()]
    if not domains:
        print("ERROR: No domains provided", file=sys.stderr)
        return 1

    is_backend = args.backend
    groups = group_domains(domains, args.max_lines, is_backend)

    if args.json:
        data = {
            "stack": "backend" if is_backend else "frontend",
            "tier": args.tier,
            "domains": domains,
            "max_lines": args.max_lines,
            "spawn_count": len(groups),
            "total_estimated_lines": sum(g["estimated_lines"] for g in groups),
            "groups": groups,
        }
        print(json.dumps(data, indent=2))
    else:
        plan = generate_plan(domains, args.tier, is_backend, args.max_lines,
                            Path(args.build_dir) if args.build_dir else None)
        print(plan)
        if args.build_dir:
            out_path = Path(args.build_dir) / ".kimi" / "test-spawn-plan.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(plan)

    return 0


if __name__ == "__main__":
    sys.exit(main())
