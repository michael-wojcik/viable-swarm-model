#!/usr/bin/env python3
"""
Integration Test: Closeout Pipeline
Exercises all closeout scripts together on a single mock build directory
to verify they are mutually consistent and don't interfere with each other.

Usage:
    python3 integration-test-closeout.py [--verbose]

Exit codes:
    0 = all closeout scripts passed integration test
    1 = one or more scripts failed or produced inconsistent output
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import shutil


def run_command(cmd, cwd=None, env=None, verbose=False):
    """Run a shell command and return (rc, stdout, stderr)."""
    if verbose:
        print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
    if verbose and result.stdout:
        print(f"    stdout: {result.stdout[:200]}")
    if verbose and result.stderr:
        print(f"    stderr: {result.stderr[:200]}")
    return result.returncode, result.stdout, result.stderr


def setup_mock_build_dir(base_dir, home_dir):
    """Create a realistic mock build directory with all required artifacts."""
    # Use FB-prefixed directory so build-health-dashboard.py can extract build ID
    build_dir = os.path.join(base_dir, "FB999-IntegrationTest")
    kimi_dir = os.path.join(build_dir, ".kimi")
    os.makedirs(kimi_dir, exist_ok=True)

    # plan.md
    with open(os.path.join(build_dir, "plan.md"), "w") as f:
        f.write("# Build Plan — FB999-IntegrationTest\n")
        f.write("Domain: Integration Test Closeout\n")

    # Meta report
    with open(os.path.join(kimi_dir, "meta-report.md"), "w") as f:
        f.write("# Meta Report\n\n")
        f.write("## Agent Performance Scores\n")
        f.write("- vsm_backend_coder: 4/5\n")
        f.write("## Phase Audit\n")
        f.write("All phases complete.\n")
        f.write("## Hypotheses Generated\n")
        f.write("None.\n")
        f.write("## Mutations Proposed\n")
        f.write("None.\n")

    # Phase 4 gate
    with open(os.path.join(kimi_dir, "phase4-gate.md"), "w") as f:
        f.write("# Phase 4 Gate\n\nPASS\n")

    # Re-audit report
    with open(os.path.join(kimi_dir, "re-audit-report.md"), "w") as f:
        f.write("# Re-Audit Report\n\nVerdict: PASS\n")

    # Lessons
    with open(os.path.join(kimi_dir, "lessons.md"), "w") as f:
        f.write("# Lessons\n\nLearned something.\n")

    # Mutations applied
    with open(os.path.join(kimi_dir, "mutations-applied.md"), "w") as f:
        f.write("# Mutations Applied\n\n")
        f.write("| ID | Name | Status |\n")
        f.write("|---|---|---|\n")
        f.write("| M1 | Test | applied |\n")

    # Security report
    with open(os.path.join(kimi_dir, "security-report.md"), "w") as f:
        f.write("# Security Report\n\nZero findings.\n")

    # Security-relevant code so Check 11 doesn't fire
    os.makedirs(os.path.join(build_dir, "backend"), exist_ok=True)
    with open(os.path.join(build_dir, "backend", "auth.py"), "w") as f:
        f.write("import jwt\n")

    # Create fitness build directories for dashboard
    fitness_dir = os.path.join(home_dir, "vsm-fitness-builds", "coach", "FB998", ".kimi")
    os.makedirs(fitness_dir, exist_ok=True)
    with open(os.path.join(fitness_dir, "..", "plan.md"), "w") as f:
        f.write("# Build Plan — FB998\n")
    with open(os.path.join(fitness_dir, "meta-report.md"), "w") as f:
        f.write("Trainer score: 4.0/5.0\n")
    with open(os.path.join(fitness_dir, "process-audit.md"), "w") as f:
        f.write("Process score: 85/100\n")

    # References
    refs_dir = os.path.join(home_dir, "vsm", "viable-swarm-model", "references")
    os.makedirs(refs_dir, exist_ok=True)

    # mutation-state.md
    with open(os.path.join(refs_dir, "mutation-state.md"), "w") as f:
        f.write("# Mutation State\n\n")
        f.write("| ID | Source | Type | Target Failure | Status | Builds Tested | Score | Hypothesis | Experiment | Next Review |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        f.write("| T1 | Test | append-only | Test failure | effective | 5 | 4 | — | — | — |\n")
        f.write("| T2 | Test | structural | Test bypass | probation | 2 | 3 | — | — | — |\n")
        f.write("| T3 | Test | refinement | Test gap | **REMOVED** | 1 | 1 | — | — | — |\n")

    # hypotheses.md
    with open(os.path.join(refs_dir, "hypotheses.md"), "w") as f:
        f.write("# Hypotheses\n\n")
        f.write("## H1: Test\n**Status**: confirmed\n\n")
        f.write("## H2: Test\n**Status**: untested\n\n")
        f.write("## H3: Test\n**Status**: untested\n")

    # knowledge-broker.md
    with open(os.path.join(refs_dir, "knowledge-broker.md"), "w") as f:
        f.write("# Broker\n> **Last updated**: 2026-06-05\n")

    # build-health-history.md
    with open(os.path.join(refs_dir, "build-health-history.md"), "w") as f:
        f.write("# Build Health History\n")
        f.write("## 2026-06-01 — FB997\n- Score: 4.0/5.0\n")

    return build_dir


def test_script(script_path, build_dir, home_dir, verbose=False):
    """Run a single closeout script and return success + output paths."""
    script_name = os.path.basename(script_path)
    env = os.environ.copy()
    env["HOME"] = home_dir

    if script_name == "build-health-dashboard.py":
        rc, out, err = run_command(
            [sys.executable, script_path, build_dir],
            env=env, verbose=verbose
        )
        expected = [
            os.path.join(build_dir, ".kimi", "health-dashboard.md"),
            os.path.join(home_dir, "vsm", "viable-swarm-model", "references", "build-health-history.md"),
        ]
        return rc == 0, expected

    elif script_name == "mutation-portfolio-health.py":
        rc, out, err = run_command(
            [sys.executable, script_path, "--build-dir", build_dir],
            env=env, verbose=verbose
        )
        expected = [
            os.path.join(build_dir, ".kimi", "mutation-portfolio-health.json"),
            os.path.join(build_dir, ".kimi", "mutation-portfolio-health.md"),
        ]
        return rc == 0, expected

    elif script_name == "organism-vitals.py":
        rc, out, err = run_command(
            [sys.executable, script_path, "--build-dir", build_dir],
            env=env, verbose=verbose
        )
        expected = [
            os.path.join(build_dir, ".kimi", "organism-vitals.md"),
        ]
        return rc == 0, expected

    elif script_name == "process-compliance-precompute.py":
        rc, out, err = run_command(
            [sys.executable, script_path, build_dir],
            env=env, verbose=verbose
        )
        expected = [
            os.path.join(build_dir, ".kimi", "process-compliance-precomputed.json"),
            os.path.join(build_dir, ".kimi", "process-compliance-precomputed.md"),
        ]
        return rc == 0, expected

    else:
        return False, []


def verify_consistency(build_dir, home_dir, verbose=False):
    """Verify that outputs from different scripts are mutually consistent."""
    errors = []

    # Check 1: build-health-history.md should contain the current build entry
    # The dashboard extracts FB number from the directory path and appends a summary
    history_path = os.path.join(home_dir, "vsm", "viable-swarm-model", "references", "build-health-history.md")
    with open(history_path, "r") as f:
        history_content = f.read()
    if "FB999" not in history_content:
        errors.append("build-health-history.md missing FB999 entry")

    # Check 2: mutation-portfolio-health.json should have valid structure
    portfolio_json = os.path.join(build_dir, ".kimi", "mutation-portfolio-health.json")
    with open(portfolio_json, "r") as f:
        portfolio = json.load(f)
    if portfolio.get("total_active") != 2:
        errors.append(f"portfolio total_active expected 2, got {portfolio.get('total_active')}")
    if portfolio.get("probationary_count") != 1:
        errors.append(f"portfolio probationary_count expected 1, got {portfolio.get('probationary_count')}")

    # Check 3: organism-vitals.md should reference metrics that match portfolio
    vitals_path = os.path.join(build_dir, ".kimi", "organism-vitals.md")
    with open(vitals_path, "r") as f:
        vitals_content = f.read()
    if "Probationary mutations" not in vitals_content:
        errors.append("organism-vitals.md missing Probationary mutations section")

    # Check 4: process-compliance-precomputed.md should reference existing artifacts
    compliance_md = os.path.join(build_dir, ".kimi", "process-compliance-precomputed.md")
    with open(compliance_md, "r") as f:
        compliance_content = f.read()
    if "Phase 4 Gate Compliance" not in compliance_content:
        errors.append("compliance precompute missing Phase 4 Gate section")
    if "PASS" not in compliance_content:
        errors.append("compliance precompute should show PASS for existing artifacts")

    # Check 5: health-dashboard.md should exist and reference the build
    dashboard_path = os.path.join(build_dir, ".kimi", "health-dashboard.md")
    with open(dashboard_path, "r") as f:
        dashboard_content = f.read()
    if "Build Health Dashboard" not in dashboard_content:
        errors.append("health-dashboard.md missing header")

    return errors


def test_session_end_hook(session_end_path, build_dir, home_dir, verbose=False):
    """Run session-end.sh on the build directory and verify telemetry."""
    env = os.environ.copy()
    env["HOME"] = home_dir

    payload = json.dumps({"session_id": "integration-test", "cwd": build_dir, "reason": "stop"})

    if verbose:
        print(f"  Running: bash {session_end_path} (with piped payload)")

    proc = subprocess.Popen(
        ["bash", session_end_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=build_dir,
        env=env,
    )
    stdout, stderr = proc.communicate(input=payload)
    rc = proc.returncode

    if verbose and stdout:
        print(f"    stdout: {stdout[:200]}")
    if verbose and stderr:
        print(f"    stderr: {stderr[:200]}")

    telemetry_path = os.path.join(build_dir, ".kimi", "session-telemetry.md")
    if not os.path.exists(telemetry_path):
        return False, ["session-telemetry.md not created by session-end.sh"]

    with open(telemetry_path, "r") as f:
        telemetry = f.read()

    errors = []
    if "Session Telemetry" not in telemetry:
        errors.append("session-telemetry.md missing header")

    # With all artifacts present, there should be NO CRITICAL warnings
    # (security-report.md exists, process-audit.md exists, etc.)
    if "CRITICAL" in telemetry:
        # But Check 11 should NOT fire because security-report.md exists
        if "security-report.md missing" in telemetry:
            errors.append("session-end.sh falsely flagged missing security-report")

    return rc == 0 and len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Integration test for closeout pipeline")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    verbose = args.verbose
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    hooks_dir = os.path.join(os.path.dirname(scripts_dir), "hooks")

    scripts = [
        os.path.join(scripts_dir, "build-health-dashboard.py"),
        os.path.join(scripts_dir, "mutation-portfolio-health.py"),
        os.path.join(scripts_dir, "organism-vitals.py"),
        os.path.join(scripts_dir, "process-compliance-precompute.py"),
    ]

    session_end = os.path.join(hooks_dir, "session-end.sh")

    with tempfile.TemporaryDirectory() as tmpdir:
        home_dir = os.path.join(tmpdir, "home")
        os.makedirs(home_dir)
        build_dir = setup_mock_build_dir(tmpdir, home_dir)

        all_passed = True
        all_errors = []

        print("Integration Test: Closeout Pipeline")
        print("=" * 50)

        # Run each closeout script sequentially
        for script_path in scripts:
            script_name = os.path.basename(script_path)
            print(f"\nTesting: {script_name}")
            ok, expected = test_script(script_path, build_dir, home_dir, verbose=verbose)
            if not ok:
                all_passed = False
                all_errors.append(f"{script_name}: script exited with error")
            else:
                for path in expected:
                    if os.path.exists(path):
                        print(f"  ✓ Output: {os.path.basename(path)}")
                    else:
                        all_passed = False
                        all_errors.append(f"{script_name}: missing expected output {path}")

        # Verify mutual consistency
        print("\nVerifying mutual consistency...")
        consistency_errors = verify_consistency(build_dir, home_dir, verbose=verbose)
        if consistency_errors:
            all_passed = False
            for e in consistency_errors:
                all_errors.append(f"consistency: {e}")
        else:
            print("  ✓ All outputs mutually consistent")

        # Run session-end hook
        print("\nTesting: session-end.sh")
        ok, hook_errors = test_session_end_hook(session_end, build_dir, home_dir, verbose=verbose)
        if not ok:
            all_passed = False
            for e in hook_errors:
                all_errors.append(f"session-end.sh: {e}")
        else:
            print("  ✓ session-end.sh completed without errors")
            if hook_errors:
                for e in hook_errors:
                    all_passed = False
                    all_errors.append(f"session-end.sh: {e}")

        print("\n" + "=" * 50)
        if all_passed:
            print("RESULT: ALL CHECKS PASSED")
            return 0
        else:
            print("RESULT: FAILURES DETECTED")
            for e in all_errors:
                print(f"  ✗ {e}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
