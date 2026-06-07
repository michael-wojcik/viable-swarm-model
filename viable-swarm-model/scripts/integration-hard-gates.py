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
    """FB34-1: Detect stubbed GraphQL mutations returning INTERNAL_ERROR or NotImplemented."""
    graphql_file = build_dir / "app" / "graphql.py"
    if not graphql_file.exists():
        print("[SKIP] app/graphql.py not found — no GraphQL layer to check")
        return True

    text = graphql_file.read_text()
    # Look for mutation resolvers that contain only pass/raise/INTERNAL_ERROR/NotImplemented
    stub_patterns = [
        r'raise\s+\w*Error\s*\(',
        r'return\s*\{\s*["\']errors["\']?\s*:\s*\[?\s*\{\s*["\']message["\']?\s*:\s*["\']INTERNAL_ERROR',
        r'return\s*\{\s*["\']message["\']?\s*:\s*["\']INTERNAL_ERROR',
        r'pass\s*\n\s*\n\s*@strawberry\.mutation',
        r'@strawberry\.mutation[\s\S]{0,200}?pass\s*$',
        r'@strawberry\.mutation[\s\S]{0,200}?raise\s+NotImplementedError',
        r'@strawberry\.mutation[\s\S]{0,200}?return\s*\{\s*["\']message["\']?\s*:\s*["\']Not implemented',
    ]

    found_stubs = []
    for pattern in stub_patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            # Extract line number
            lineno = text[:match.start()].count("\n") + 1
            found_stubs.append(lineno)

    if found_stubs:
        fail(
            f"FB34-1: Found {len(found_stubs)} potential GraphQL mutation stub(s) "
            f"in app/graphql.py at line(s): {sorted(set(found_stubs))}. "
            f"Mutations must be fully implemented — no INTERNAL_ERROR, NotImplemented, or bare pass."
        )
        return False

    print("[PASS] FB34-1: No GraphQL mutation stubs detected")
    return True


def check_graphql_session_cleanup(build_dir: Path) -> bool:
    """FB34-2: Verify AsyncSession created in get_graphql_context is closed."""
    graphql_file = build_dir / "app" / "graphql.py"
    if not graphql_file.exists():
        print("[SKIP] app/graphql.py not found — no GraphQL context to check")
        return True

    text = graphql_file.read_text()
    # Check if get_graphql_context creates an AsyncSession
    if "AsyncSession" not in text and "async_session" not in text.lower():
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
            f"'Builds Tested = 0' or empty score. Run update-mutation-state.sh to backfill."
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
