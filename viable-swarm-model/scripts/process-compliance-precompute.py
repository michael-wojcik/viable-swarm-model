#!/usr/bin/env python3
"""
Process Compliance Pre-computation — S3* Process Auditor workload reducer.

Scans .kimi/ artifacts and pre-computes compliance findings for all 10
process auditor checks. The vsm_process_auditor agent reads the output
and verifies/elevates findings rather than scanning files from scratch.

Usage:
    python3 process-compliance-precompute.py <build-directory>

Writes:
    <build-dir>/.kimi/process-compliance-precomputed.json
    <build-dir>/.kimi/process-compliance-precomputed.md
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

VSM_ROOT = Path.home() / "vsm" / "viable-swarm-model"
REFS_DIR = VSM_ROOT / "references"


def read_file(path: Path) -> str:
    if path.exists():
        return path.read_text()
    return ""


def check_phase4_gate(build_dir: Path) -> dict:
    path = build_dir / ".kimi" / "phase4-gate.md"
    text = read_file(path)
    has_pass = bool(re.search(r"\bPASS\b", text, re.IGNORECASE))
    has_block = bool(re.search(r"\bBLOCK\b", text, re.IGNORECASE))
    has_verified = (build_dir / ".kimi" / ".gate-guardian-verified").exists()
    return {
        "check": "Phase 4 Gate Compliance",
        "file_exists": path.exists(),
        "has_pass": has_pass,
        "has_block": has_block,
        "has_verification_marker": has_verified,
        "status": "PASS" if (has_pass and not has_block) else "FAIL" if has_block else "MISSING",
        "evidence": f"PASS={has_pass}, BLOCK={has_block}, verified={has_verified}",
    }


def check_phase7_reaudit(build_dir: Path) -> dict:
    path = build_dir / ".kimi" / "re-audit-report.md"
    text = read_file(path)
    has_files = bool(re.search(r"\bfile\b|\bmodified\b", text, re.IGNORECASE))
    has_verdicts = bool(re.search(r"\bPASS\b|\bISSUE\b|\bBLOCKER\b", text, re.IGNORECASE))
    has_regression = bool(re.search(r"regress", text, re.IGNORECASE))
    return {
        "check": "Phase 7 Fix Wave Compliance",
        "file_exists": path.exists(),
        "lists_files": has_files,
        "has_verdicts": has_verdicts,
        "mentions_regressions": has_regression,
        "status": "PASS" if (path.exists() and has_files and has_verdicts) else "FAIL",
        "evidence": f"exists={path.exists()}, files={has_files}, verdicts={has_verdicts}, regressions={has_regression}",
    }


def check_phase7c_security(build_dir: Path) -> dict:
    """Check if fix wave touched auth/GraphQL/WS files and security re-check was done."""
    reaudit = read_file(build_dir / ".kimi" / "re-audit-report.md")
    sec_report = read_file(build_dir / ".kimi" / "security-report.md")
    sec_audit = read_file(build_dir / ".kimi" / "security-audit.md")
    sec_text = sec_report + sec_audit
    fix_wave_modified_auth = bool(re.search(r"auth|graphql|websocket|ws", reaudit, re.IGNORECASE))
    has_post_fix_security = bool(re.search(r"post.fix|re.check|regress", sec_text, re.IGNORECASE))
    return {
        "check": "Phase 7c Security Re-Check Compliance",
        "fix_wave_touched_security_files": fix_wave_modified_auth,
        "has_post_fix_security_check": has_post_fix_security,
        "status": "PASS" if (not fix_wave_modified_auth or has_post_fix_security) else "FAIL",
        "evidence": f"auth_files_modified={fix_wave_modified_auth}, post_fix_check={has_post_fix_security}",
    }


def check_phase8_reflection(build_dir: Path) -> dict:
    lessons = read_file(build_dir / ".kimi" / "lessons.md")
    meta = read_file(build_dir / ".kimi" / "meta-report.md")
    has_lessons = bool(lessons.strip())
    has_agent_scores = bool(re.search(r"Agent Performance|Performance Score", meta, re.IGNORECASE))
    has_phase_audit = bool(re.search(r"Phase Audit|Audit Summary", meta, re.IGNORECASE))
    has_hypotheses = bool(re.search(r"Hypotheses", meta, re.IGNORECASE))
    has_mutations = bool(re.search(r"Mutations Proposed|mutations", meta, re.IGNORECASE))
    sections = sum([has_agent_scores, has_phase_audit, has_hypotheses, has_mutations])
    return {
        "check": "Phase 8 Reflection Compliance",
        "lessons_exists": has_lessons,
        "meta_has_agent_scores": has_agent_scores,
        "meta_has_phase_audit": has_phase_audit,
        "meta_has_hypotheses": has_hypotheses,
        "meta_has_mutations": has_mutations,
        "meta_sections_present": sections,
        "status": "PASS" if (has_lessons and sections >= 3) else "ISSUES" if sections >= 2 else "FAIL",
        "evidence": f"lessons={has_lessons}, sections={sections}/4",
    }


def check_phase8b_mutations(build_dir: Path) -> dict:
    path = build_dir / ".kimi" / "mutations-applied.md"
    text = read_file(path)
    has_tracking = bool(re.search(r"\|.*Applied\b|\|.*Deferred\b|\|.*Rejected\b|\|.*Overlooked\b", text))
    has_overlooked_unjustified = bool(re.search(r"Overlooked.*(?!justif)", text, re.IGNORECASE))
    state_path = REFS_DIR / "mutation-state.md"
    state_text = read_file(state_path)
    # Try to extract build ID from plan.md
    plan_text = read_file(build_dir / "plan.md")
    build_id_match = re.search(r"FB\d+|Build\s+\w+", plan_text, re.IGNORECASE)
    build_id = build_id_match.group(0) if build_id_match else ""
    in_state = build_id in state_text if build_id else False
    return {
        "check": "Phase 8b Mutation Tracking Compliance",
        "file_exists": path.exists(),
        "has_status_tracking": has_tracking,
        "has_unjustified_overlooked": has_overlooked_unjustified,
        "mutations_in_state": in_state,
        "status": "PASS" if (path.exists() and has_tracking) else "FAIL",
        "evidence": f"exists={path.exists()}, tracking={has_tracking}, in_state={in_state}",
    }


def check_broker(build_dir: Path) -> dict:
    path = REFS_DIR / "knowledge-broker.md"
    text = read_file(path)
    match = re.search(r"\*\*Last updated\*\*:\s*(\d{4}-\d{2}-\d{2})", text)
    has_content = len(text) > 200  # More than just template
    age_days = 999
    if match:
        try:
            updated = datetime.strptime(match.group(1), "%Y-%m-%d").date()
            age_days = (datetime.now(timezone.utc).date() - updated).days
        except ValueError:
            pass
    return {
        "check": "Knowledge Broker Compliance",
        "file_exists": path.exists(),
        "has_structured_content": has_content,
        "staleness_days": age_days,
        "status": "PASS" if (has_content and age_days <= 7) else "FAIL" if age_days > 7 else "ISSUES",
        "evidence": f"content={has_content}, age={age_days}d",
    }


def check_phase0_broker_read(build_dir: Path) -> dict:
    plan = read_file(build_dir / "plan.md")
    has_broker_ref = bool(re.search(r"knowledge-broker|broker trap|Active Constraints", plan, re.IGNORECASE))
    has_mutation_ref = bool(re.search(r"mutation.state|probationary|effective mutation", plan, re.IGNORECASE))
    score = 0
    if has_broker_ref and has_mutation_ref:
        score = 10
    elif has_broker_ref or has_mutation_ref:
        score = 5
    return {
        "check": "Phase 0 Broker/State Read Compliance",
        "plan_has_broker_ref": has_broker_ref,
        "plan_has_mutation_ref": has_mutation_ref,
        "score": score,
        "status": "PASS" if score == 10 else "ISSUES" if score == 5 else "FAIL",
        "evidence": f"broker_ref={has_broker_ref}, mutation_ref={has_mutation_ref}, score={score}/10",
    }


def check_portfolio_review(build_dir: Path) -> dict:
    path = build_dir / ".kimi" / "mutation-portfolio-review.md"
    has_recommendations = bool(re.search(r"recommend|promot|remov|consolidat", read_file(path), re.IGNORECASE))
    return {
        "check": "Phase 8c-iii Portfolio Review Compliance",
        "file_exists": path.exists(),
        "has_recommendations": has_recommendations,
        "status": "PASS" if (path.exists() and has_recommendations) else "FAIL" if not path.exists() else "ISSUES",
        "evidence": f"exists={path.exists()}, recommendations={has_recommendations}",
    }


def check_causal_index(build_dir: Path) -> dict:
    path = REFS_DIR / "causal-index.md"
    text = read_file(path)
    plan_text = read_file(build_dir / "plan.md")
    build_id_match = re.search(r"FB\d+", plan_text, re.IGNORECASE)
    build_id = build_id_match.group(0) if build_id_match else ""
    in_index = build_id in text if build_id else False
    return {
        "check": "Causal Index Compliance",
        "file_exists": path.exists(),
        "build_in_index": in_index,
        "status": "PASS" if in_index else "FAIL",
        "evidence": f"index_exists={path.exists()}, build={build_id} in_index={in_index}",
    }


def check_stack_skills(build_dir: Path) -> dict:
    """Heuristic: check if agent spawn logs or output files mention skill reads."""
    kimi_dir = build_dir / ".kimi"
    all_text = ""
    if kimi_dir.exists():
        for f in kimi_dir.glob("*.md"):
            all_text += f.read_text()
    skill_patterns = {
        "python-pitfalls": r"python-pitfalls",
        "sqla-patterns": r"sqla-patterns",
        "backend-patterns": r"backend-patterns",
        "testing-patterns": r"testing-patterns",
        "tester-backend": r"tester-backend",
        "typescript-pitfalls": r"typescript-pitfalls",
        "frontend-patterns": r"frontend-patterns",
        "security-patterns": r"security-patterns",
        "graphql-pitfalls": r"graphql-pitfalls",
        "docker-pitfalls": r"docker-pitfalls",
    }
    found = []
    missing = []
    for skill, pattern in skill_patterns.items():
        if re.search(pattern, all_text, re.IGNORECASE):
            found.append(skill)
        else:
            missing.append(skill)
    return {
        "check": "Stack Skill Read Compliance",
        "skills_found": found,
        "skills_missing": missing,
        "status": "PASS" if len(missing) <= 3 else "ISSUES" if len(missing) <= 6 else "FAIL",
        "evidence": f"found={len(found)}/{len(skill_patterns)}, missing={missing}",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Process Compliance Pre-computation")
    parser.add_argument("build_dir", help="Build directory to scan")
    args = parser.parse_args()

    build_path = Path(args.build_dir)
    if not build_path.exists():
        print(f"ERROR: Build directory not found: {build_path}", file=sys.stderr)
        return 1

    results = [
        check_phase4_gate(build_path),
        check_phase7_reaudit(build_path),
        check_phase7c_security(build_path),
        check_phase8_reflection(build_path),
        check_phase8b_mutations(build_path),
        check_broker(build_path),
        check_phase0_broker_read(build_path),
        check_portfolio_review(build_path),
        check_causal_index(build_path),
        check_stack_skills(build_path),
    ]

    # Compute overall compliance score
    score_map = {"PASS": 10, "ISSUES": 5, "FAIL": 0, "MISSING": 0}
    total_score = sum(score_map.get(r["status"], 0) for r in results)
    max_score = len(results) * 10

    json_data = {
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "build_dir": str(build_path),
        "total_score": total_score,
        "max_score": max_score,
        "compliance_percentage": round((total_score / max_score) * 100, 1),
        "checks": results,
    }

    # Write JSON
    json_path = build_path / ".kimi" / "process-compliance-precomputed.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(json_data, indent=2))

    # Write Markdown
    md_lines = [
        "# Process Compliance — Pre-computed",
        f"**Date**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        f"**Scanner**: scripts/process-compliance-precompute.py",
        f"**Build**: {build_path.name}",
        "",
        "> This file is auto-generated by `scripts/process-compliance-precompute.py`.",
        "> The vsm_process_auditor should read this file first, then verify and write `.kimi/process-audit.md`.",
        "",
        f"## Compliance Score: {total_score} / {max_score} ({json_data['compliance_percentage']}%)",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]
    for r in results:
        status_icon = "✅" if r["status"] == "PASS" else "⚠️" if r["status"] == "ISSUES" else "❌"
        md_lines.append(f"| {r['check']} | {status_icon} {r['status']} | {r['evidence']} |")

    md_lines.extend([
        "",
        "## Recommendations",
        "",
    ])

    fails = [r for r in results if r["status"] in ("FAIL", "MISSING")]
    issues = [r for r in results if r["status"] == "ISSUES"]

    if total_score < 50:
        md_lines.append(f"**HARD BLOCK**: Compliance score {total_score}/{max_score} is below 50/100 threshold. S5 MUST address violations before declaring build complete.")
    elif total_score < 80:
        md_lines.append(f"**ISSUES**: Compliance score {total_score}/{max_score} is below 80/100 threshold. Review failures and issues before proceeding.")
    else:
        md_lines.append(f"**PASS**: Compliance score {total_score}/{max_score} meets threshold.")

    if fails:
        md_lines.append("")
        md_lines.append("### FAIL Items")
        for r in fails:
            md_lines.append(f"- **{r['check']}**: {r['evidence']}")

    if issues:
        md_lines.append("")
        md_lines.append("### ISSUE Items")
        for r in issues:
            md_lines.append(f"- **{r['check']}**: {r['evidence']}")

    # Spot-check guidance for the process auditor agent
    md_lines.extend([
        "",
        "## Spot-Check Guidance (for vsm_process_auditor)",
        "",
        "If you are the process auditor agent, follow this guidance:",
        "- For PASS checks: No spot-check needed. Trust the pre-computed result.",
        "- For ISSUE checks: Quick visual confirmation of the evidence is sufficient.",
        "- For FAIL checks: Read the specific artifact mentioned in the evidence to add qualitative depth.",
        "",
        "| Check | If FAIL, read this file | What to look for |",
        "|---|---|---|",
        "| Phase 4 Gate | `.kimi/phase4-gate.md` | Why blocked — missing, retroactive, or content issue |",
        "| Phase 7 Re-Audit | `.kimi/re-audit-report.md` | Missing files, missing verdicts, no regression mention |",
        "| Phase 7c Security | `.kimi/security-report.md` | Post-fix security check evidence |",
        "| Phase 8 Reflection | `.kimi/meta-report.md` | Missing Agent Performance Scores or sections |",
        "| Phase 8b Mutations | `.kimi/mutations-applied.md` | Missing tracking or unjustified Overlooked |",
        "| Knowledge Broker | `references/knowledge-broker.md` | Empty or stale content |",
        "| Phase 0 Broker Read | `plan.md` | Missing broker or mutation state references |",
        "| Phase 8c-iii Portfolio | `.kimi/mutation-portfolio-review.md` | Missing file or recommendations |",
        "| Causal Index | `references/causal-index.md` | Missing build entry |",
        "| Stack Skill Reads | `.kimi/*.md` agent outputs | Missing skill-read citations |",
        "",
        "**Limit**: Maximum 3 spot-checks. If more than 3 FAIL, check the 3 most severe.",
    ])

    md_path = build_path / ".kimi" / "process-compliance-precomputed.md"
    md_path.write_text("\n".join(md_lines))

    print(f"Compliance pre-computed: {total_score}/{max_score} ({json_data['compliance_percentage']}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
