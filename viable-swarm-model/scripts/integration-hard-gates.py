#!/usr/bin/env python3
"""
Integration Hard Gates — Tool-enforced checks for common integration failures.

Consolidates FB31-5 (broker backfill), FB34-1 (GraphQL stub detection),
FB34-2 (session cleanup verification), and FB34-3 (SocketProvider auth emit).

Usage:
    python3 integration-hard-gates.py --build-dir <BUILD_DIR> [--phase <3c|6>]

Exit codes:
    0 = all gates pass
    1 = one or more hard gates failed
"""

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"[HARD GATE FAIL] {message}")


def check_graphql_stubs(build_dir: Path) -> bool:
    """FB34-1: Detect stubbed GraphQL mutations returning INTERNAL_ERROR or NotImplemented.

    Delegates to scripts/check-graphql-stubs.py for AST-based scanning across the
    whole build directory, replacing the earlier regex-only check on app/graphql.py.
    """
    graphql_file = build_dir / "app" / "graphql.py"
    if not graphql_file.exists():
        print("[SKIP] app/graphql.py not found — no GraphQL layer to check")
        return True

    script_path = Path(__file__).parent / "check-graphql-stubs.py"
    if not script_path.exists():
        fail("FB34-1: check-graphql-stubs.py not found — hard gate cannot run")
        return False

    result = subprocess.run(
        [sys.executable, str(script_path), str(build_dir)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("[PASS] FB34-1: No GraphQL mutation stubs detected")
        return True

    if result.returncode == 1:
        # Count stub lines from the delegated script output
        stub_lines = [line for line in result.stdout.splitlines() if "::" in line]
        fail(
            f"FB34-1: Found {len(stub_lines)} potential GraphQL mutation stub(s). "
            f"Mutations must be fully implemented — no INTERNAL_ERROR, NotImplemented, or bare pass. "
            f"Details:\n{result.stdout}"
        )
        return False

    # returncode 2 = usage/read error
    fail(
        f"FB34-1: check-graphql-stubs.py failed with exit code {result.returncode}. "
        f"Output:\n{result.stdout}\n{result.stderr}"
    )
    return False


PACKAGE_IMPORT_MAP = {
    "strawberry-graphql": "strawberry",
    "strawberry": "strawberry",
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "sqlalchemy": "sqlalchemy",
    "fastapi": "fastapi",
    "httpx": "httpx",
    "celery": "celery",
    "redis": "redis",
    "alembic": "alembic",
    "uvicorn": "uvicorn",
    "pytest": "pytest",
    "pytest-asyncio": "pytest_asyncio",
    "python-jose": "jose",
    "passlib": "passlib",
    "bcrypt": "bcrypt",
    "python-multipart": "multipart",
    "aiofiles": "aiofiles",
    "jinja2": "jinja2",
    "websockets": "websockets",
    "python-socketio": "socketio",
}


def check_environment_imports(build_dir: Path) -> bool:
    """H152: Verify framework dependencies declared in requirements.txt can be imported.

    Prevents dispatching implementation agents into an environment with incompatible
    package versions (e.g., strawberry-graphql that cannot import with installed pydantic).
    """
    requirements_file = build_dir / "requirements.txt"
    if not requirements_file.exists():
        print("[SKIP] H152: requirements.txt not found — no declared dependencies to verify")
        return True

    text = requirements_file.read_text()
    failed = []
    skipped = []
    checked = []

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Strip version specifiers
        pkg = re.split(r"[=<>!~;]", line)[0].strip()
        if not pkg:
            continue
        module = PACKAGE_IMPORT_MAP.get(pkg)
        if not module:
            skipped.append(pkg)
            continue
        checked.append(pkg)
        result = subprocess.run(
            [sys.executable, "-c", f"import {module}"],
            cwd=build_dir,
            capture_output=True,
        )
        if result.returncode != 0:
            failed.append((pkg, module))

    if failed:
        details = ", ".join(f"{pkg} (import {module})" for pkg, module in failed)
        fail(
            f"H152: {len(failed)} declared requirement(s) cannot be imported: {details}. "
            f"Resolve environment incompatibility before dispatching implementation agents."
        )
        return False

    if checked:
        print(f"[PASS] H152: All {len(checked)} declared requirement(s) import successfully")
    else:
        print("[SKIP] H152: No recognized importable requirements in requirements.txt")
    return True


def check_graphql_session_cleanup(build_dir: Path) -> bool:
    """FB34-2: Verify AsyncSession created in get_graphql_context is closed."""
    graphql_file = build_dir / "app" / "graphql.py"
    if not graphql_file.exists():
        print("[SKIP] app/graphql.py not found — no GraphQL context to check")
        return True

    text = graphql_file.read_text()
    # Locate get_graphql_context function; if absent, nothing to check
    match = re.search(r"(async\s+)?def\s+get_graphql_context\b", text)
    if not match:
        print("[SKIP] No get_graphql_context function in app/graphql.py")
        return True

    # Extract the function body (naive: from the def line to the next top-level def/class or EOF)
    start = match.start()
    rest = text[start:]
    # Find next top-level definition
    next_def = re.search(r"\n(?:async\s+)?def\s+|\nclass\s+", rest[1:])
    func_body = rest[: next_def.start() + 1] if next_def else rest

    # Check if get_graphql_context creates an AsyncSession
    if "AsyncSession" not in func_body and "async_session" not in func_body.lower():
        print("[SKIP] No AsyncSession usage in get_graphql_context")
        return True

    # Check for SessionCleanupExtension or similar cleanup mechanism
    has_cleanup_extension = "SessionCleanupExtension" in text or "session.close()" in text
    has_cleanup_middleware = "session.close()" in text or "await session.close()" in text
    has_contextlib = "asynccontextmanager" in text or "contextlib.asynccontextmanager" in text

    if has_cleanup_extension or has_cleanup_middleware or has_contextlib:
        print("[PASS] FB34-2: GraphQL session cleanup mechanism detected")
        return True

    fail(
        "FB34-2: app/graphql.py creates an AsyncSession in get_graphql_context "
        "but has no detected cleanup mechanism (SessionCleanupExtension, session.close(), "
        "or asynccontextmanager). DB connections will leak per request."
    )
    return False


def check_socketprovider_auth_emit(build_dir: Path) -> bool:
    """FB34-3: Verify SocketProvider emits 'authenticate' after connect."""
    provider_file = build_dir / "frontend" / "src" / "sio" / "SocketProvider.tsx"
    if not provider_file.exists():
        provider_file = build_dir / "src" / "sio" / "SocketProvider.tsx"
    if not provider_file.exists():
        # Try to find any SocketProvider file
        candidates = list(build_dir.rglob("SocketProvider.tsx")) + list(build_dir.rglob("SocketProvider.ts"))
        if candidates:
            provider_file = candidates[0]
        else:
            print("[SKIP] SocketProvider.tsx not found — no Socket.IO client to check")
            return True

    text = provider_file.read_text()
    has_emit = 'emit("authenticate"' in text or "emit('authenticate'" in text
    has_listen = 'on("authenticated"' in text or "on('authenticated'" in text

    if has_emit and has_listen:
        print("[PASS] FB34-3: SocketProvider emits 'authenticate' and listens for 'authenticated'")
        return True

    if not has_emit:
        fail(
            f"FB34-3: {provider_file.relative_to(build_dir)} does not emit 'authenticate' "
            f"after socket connect. The server expects an in-band auth event."
        )
    if not has_listen:
        fail(
            f"FB34-3: {provider_file.relative_to(build_dir)} does not listen for 'authenticated' "
            f"after emitting. The provider should handle the server's auth confirmation."
        )
    return False


def check_mutation_state_backfill() -> bool:
    """FB31-5: Verify mutation-state.md has been updated with recent build scores."""
    mutation_state = Path.home() / "vsm" / "viable-swarm-model" / "references" / "mutation-state.md"
    if not mutation_state.exists():
        fail("FB31-5: mutation-state.md not found — cannot verify backfill")
        return False

    text = mutation_state.read_text()
    # Look for probation rows with Builds Tested = 0 — these are stale
    stale_count = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "probation" not in line.lower():
            continue
        parts = [p.strip() for p in line.split("|")]
        parts = [p for p in parts if p]
        if len(parts) >= 6:
            builds_tested = parts[5] if len(parts) > 5 else "0"
            if builds_tested in ("", "—", "0"):
                stale_count += 1

    if stale_count > 0:
        fail(
            f"FB31-5: mutation-state.md contains {stale_count} probation mutation(s) with "
            f"'Builds Tested = 0' or empty score. Run auto-mutation-lifecycle.py to backfill."
        )
        return False

    print("[PASS] FB31-5: mutation-state.md backfill appears current (no stale probation rows)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Integration Hard Gates")
    parser.add_argument("--build-dir", required=True, type=Path, help="Path to build directory")
    parser.add_argument("--phase", choices=["3c", "6"], default="6", help="Which phase is running the gate")
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    if not build_dir.exists():
        print(f"[ERROR] Build directory does not exist: {build_dir}")
        return 1

    results = []

    # All gates run regardless of phase; Phase 3c gets early warning, Phase 6 gets final block
    results.append(check_environment_imports(build_dir))
    results.append(check_graphql_stubs(build_dir))
    results.append(check_graphql_session_cleanup(build_dir))
    results.append(check_socketprovider_auth_emit(build_dir))
    results.append(check_mutation_state_backfill())

    passed = sum(results)
    total = len(results)

    print(f"\n{'=' * 50}")
    print(f"Hard Gates: {passed}/{total} passed")

    if all(results):
        print("RESULT: PASS — all integration hard gates clear")
        return 0
    else:
        print("RESULT: FAIL — one or more hard gates blocked")
        if args.phase == "3c":
            print("NOTE: Phase 3c gate failure is a WARNING; fix before Phase 6 or document.")
        else:
            print("BLOCK: Phase 6 gate failure MUST be resolved before Integration PASS.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
