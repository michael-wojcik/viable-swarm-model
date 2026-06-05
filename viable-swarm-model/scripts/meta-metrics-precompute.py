#!/usr/bin/env python3
"""
Meta Metrics Pre-computation Script
Reads all .kimi/ artifacts in a build directory and extracts ground-truth metrics.
Outputs structured markdown to .kimi/meta-metrics-precomputed.md

This reduces vsm_meta's workload by pre-extracting verifiable data from all
build artifacts, eliminating "false TBD claims" where the agent marks metrics
as "to be determined" when they are actually present in artifacts.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


def extract_from_phase4_gate(content: str) -> dict:
    """Extract test counts and build status from phase4-gate.md."""
    metrics = {}
    # Backend tests: X/Y passed
    m = re.search(
        r'Backend tests.*?(\d+)/(\d+)\s+passed',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        metrics['backend_tests_passed'] = int(m.group(1))
        metrics['backend_tests_total'] = int(m.group(2))
    # Frontend tests
    m = re.search(
        r'Frontend tests.*?(\d+)/(\d+)\s+passed',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        metrics['frontend_tests_passed'] = int(m.group(1))
        metrics['frontend_tests_total'] = int(m.group(2))
    # Frontend build
    m = re.search(
        r'Frontend build.*?\|\s*(PASS|FAIL)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        metrics['frontend_build'] = m.group(1).upper()
    # Import sanity
    m = re.search(
        r'Import sanity.*?\|\s*(PASS|FAIL)',
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if m:
        metrics['import_sanity'] = m.group(1).upper()
    # Security status post-fix
    for level in ['BLOCKER', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        pat = rf'{level}\s*:\s*(\d+)'
        m = re.search(pat, content, re.IGNORECASE)
        if m:
            metrics[f'post_fix_{level.lower()}'] = int(m.group(1))
    return metrics


def extract_from_pytest_log(content: str) -> dict:
    """Extract test counts from pytest-output.log."""
    metrics = {}
    # "X passed, Y failed, Z errors" or "X passed in"
    m = re.search(
        r'(\d+)\s+passed.*?(?:(\d+)\s+failed)?.*?(?:(\d+)\s+error)?',
        content,
        re.IGNORECASE,
    )
    if m:
        metrics['pytest_passed'] = int(m.group(1))
        if m.group(2):
            metrics['pytest_failed'] = int(m.group(2))
        if m.group(3):
            metrics['pytest_errors'] = int(m.group(3))
    # Collect-only mode
    m = re.search(r'(\d+)\s+test\s+case', content, re.IGNORECASE)
    if m:
        metrics['pytest_collected'] = int(m.group(1))
    return metrics


def extract_from_security_report(content: str) -> dict:
    """Extract finding counts from security-report.md."""
    metrics = {}
    # Strip markdown bold for easier parsing
    clean = re.sub(r'\*\*', '', content)
    for level in ['BLOCKER', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        m = re.search(
            rf'{level}(?:\s+count)?\s*[:=]?\s*(\d+)',
            clean,
            re.IGNORECASE,
        )
        if m:
            metrics[f'security_{level.lower()}'] = int(m.group(1))
    # Verdict
    m = re.search(
        r'Verdict\s*[:=|]?\s*(PASS|ISSUES|FAIL)',
        clean,
        re.IGNORECASE,
    )
    if m:
        metrics['security_verdict'] = m.group(1).upper()
    return metrics


def extract_from_auditor_report(content: str) -> dict:
    """Extract BLOCKER/ISSUE counts from auditor reports."""
    metrics = {}
    # Count headings or list items with BLOCKER/ISSUE
    blocker_count = len(
        re.findall(r'^\s*[-*]\s*\*\*BLOCKER\b', content, re.MULTILINE)
    )
    issue_count = len(
        re.findall(r'^\s*[-*]\s*\*\*ISSUE\b', content, re.MULTILINE)
    )
    # Also count markdown headings
    blocker_headings = len(
        re.findall(r'^#{1,3}\s+.*BLOCKER', content, re.MULTILINE | re.IGNORECASE)
    )
    issue_headings = len(
        re.findall(r'^#{1,3}\s+.*ISSUE', content, re.MULTILINE | re.IGNORECASE)
    )
    metrics['blocker_count'] = max(blocker_count, blocker_headings)
    metrics['issue_count'] = max(issue_count, issue_headings)
    return metrics


def extract_from_meta_report(content: str) -> dict:
    """Extract score and verdict from meta-report.md."""
    metrics = {}
    clean = re.sub(r'\*\*', '', content)
    m = re.search(
        r'Verdict\s*[:=|]?\s*(PASS|ISSUES|FAIL)',
        clean,
        re.IGNORECASE,
    )
    if m:
        metrics['meta_verdict'] = m.group(1).upper()
    # Score like 4.2/5.0 or 84/100
    m = re.search(r'(\d+(?:\.\d+)?)\s*/\s*(5\.0|100)', content)
    if m:
        metrics['meta_score'] = float(m.group(1))
        metrics['meta_score_scale'] = m.group(2)
    return metrics


def extract_from_process_audit(content: str) -> dict:
    """Extract compliance score from process-audit.md."""
    metrics = {}
    clean = re.sub(r'\*\*', '', content)
    m = re.search(
        r'(?:Score|Compliance|Total).*?(\d+)\s*/\s*100',
        clean,
        re.IGNORECASE,
    )
    if m:
        metrics['compliance_score'] = int(m.group(1))
    # PASS/ISSUES/FAIL per check
    metrics['checks_pass'] = len(re.findall(r'\bPASS\b', clean))
    metrics['checks_issues'] = len(re.findall(r'\bISSUES?\b', clean))
    metrics['checks_fail'] = len(re.findall(r'\bFAIL\b', clean))
    return metrics


def extract_from_mutations_applied(content: str) -> dict:
    """Count mutations from mutations-applied.md."""
    metrics = {}
    # Count bold list items or markdown list items
    count = len(re.findall(r'^\s*[-*]\s*\*\*', content, re.MULTILINE))
    if count == 0:
        count = len(re.findall(r'^\s*[-*]\s*\w', content, re.MULTILINE))
    metrics['mutations_count'] = count
    return metrics


def extract_from_lessons(content: str) -> dict:
    """Count lessons from lessons.md."""
    metrics = {}
    count = len(re.findall(r'^##\s+', content, re.MULTILINE))
    metrics['lessons_count'] = count
    return metrics


def extract_from_synthesis(content: str) -> dict:
    """Extract metrics from synthesis-integration.md."""
    metrics = {}
    m = re.search(
        r'(?:Status|Verdict)\s*[:=]?\s*(PASS|ISSUES|FAIL|BLOCK)',
        content,
        re.IGNORECASE,
    )
    if m:
        metrics['integration_status'] = m.group(1).upper()
    blocker_count = len(
        re.findall(r'^\s*[-*]\s*\*\*BLOCKER\b', content, re.MULTILINE)
    )
    if blocker_count > 0:
        metrics['blocker_count'] = blocker_count
    return metrics


EXTRACTORS = {
    'phase4-gate.md': extract_from_phase4_gate,
    'pytest-output.log': extract_from_pytest_log,
    'security-report.md': extract_from_security_report,
    'foundation-audit.md': extract_from_auditor_report,
    'implementation-audit.md': extract_from_auditor_report,
    'meta-report.md': extract_from_meta_report,
    'process-audit.md': extract_from_process_audit,
    'mutations-applied.md': extract_from_mutations_applied,
    'lessons.md': extract_from_lessons,
    'synthesis-integration.md': extract_from_synthesis,
}


def generate_report(build_dir: Path, all_metrics: dict) -> str:
    """Generate the precomputed metrics markdown report."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    artifacts = all_metrics.get('artifacts_present', [])
    lines = [
        '# Meta Metrics — Pre-computed',
        '',
        f'> **Build**: {build_dir.name}',
        f'> **Artifacts found**: {all_metrics.get("artifact_count", 0)}',
        f'> **Generated**: {now}',
        '',
        '## Artifact Inventory',
        '',
    ]
    for name in artifacts:
        lines.append(f'- `{name}`')
    lines.append('')

    # Health summary section for quick meta-agent overview
    if '_health_summary' in all_metrics:
        lines.append('## Build Health at a Glance')
        lines.append('')
        for metric_name, value in sorted(all_metrics['_health_summary'].items()):
            lines.append(f'- {metric_name}: {value}')
        lines.append('')

    # For each extractor that produced data, add a section
    for key in sorted(all_metrics.keys()):
        if key in ('artifact_count', 'artifacts_present', 'errors', '_health_summary'):
            continue
        if not isinstance(all_metrics[key], dict):
            continue
        section_title = key.replace('-', ' ').title()
        lines.append(f'## {section_title}')
        lines.append('')
        for metric_name, value in sorted(all_metrics[key].items()):
            lines.append(f'- {metric_name}: {value}')
        lines.append('')

    if 'errors' in all_metrics and all_metrics['errors']:
        lines.append('## Extraction Errors')
        lines.append('')
        for err in all_metrics['errors']:
            lines.append(f'- {err}')
        lines.append('')

    lines.append('---')
    lines.append('')
    lines.append(
        '> **For vsm_meta**: Use these pre-extracted metrics as ground truth. '
        'Do NOT claim "TBD" for any metric listed above. If a metric is absent '
        'from this file, verify the source artifact before writing.'
    )
    lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Pre-compute meta-evaluation metrics from build artifacts'
    )
    parser.add_argument('--build-dir', required=True, help='Build directory path')
    args = parser.parse_args()

    build_dir = Path(args.build_dir)
    kimi_dir = build_dir / '.kimi'
    output_file = kimi_dir / 'meta-metrics-precomputed.md'

    if not build_dir.exists():
        print(f"ERROR: Build directory does not exist: {build_dir}", file=sys.stderr)
        sys.exit(1)

    kimi_dir.mkdir(parents=True, exist_ok=True)

    # Discover all .md and .log files in .kimi/
    artifact_files = []
    if kimi_dir.exists():
        artifact_files = sorted(kimi_dir.glob('*.md')) + sorted(kimi_dir.glob('*.log'))

    all_metrics = {
        'artifact_count': len(artifact_files),
        'artifacts_present': [f.name for f in artifact_files],
    }

    for filename, extractor in EXTRACTORS.items():
        filepath = kimi_dir / filename
        if filepath.exists():
            try:
                content = filepath.read_text(encoding='utf-8')
                extracted = extractor(content)
                if extracted:
                    all_metrics[filename.replace('.md', '').replace('.log', '')] = extracted
            except Exception as e:
                all_metrics.setdefault('errors', []).append(f"{filename}: {e}")

    # Build a quick health summary for the meta agent
    summary = {}
    # Tests
    p4g = all_metrics.get('phase4-gate', {})
    pytest = all_metrics.get('pytest-output', {})
    summary['backend_tests'] = f"{p4g.get('backend_tests_passed', '?')}/{p4g.get('backend_tests_total', '?')} passed"
    summary['frontend_tests'] = f"{p4g.get('frontend_tests_passed', '?')}/{p4g.get('frontend_tests_total', '?')} passed"
    summary['pytest'] = f"{pytest.get('pytest_passed', '?')} passed"
    summary['frontend_build'] = p4g.get('frontend_build', 'N/A')
    # Security
    sec = all_metrics.get('security-report', {})
    sec_total = sum(sec.get(f'security_{l.lower()}', 0) for l in ['BLOCKER', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])
    summary['security_findings'] = sec_total
    summary['security_verdict'] = sec.get('security_verdict', 'N/A')
    # Audit
    fa = all_metrics.get('foundation-audit', {})
    ia = all_metrics.get('implementation-audit', {})
    summary['audit_blockers'] = fa.get('blocker_count', 0) + ia.get('blocker_count', 0)
    summary['audit_issues'] = fa.get('issue_count', 0) + ia.get('issue_count', 0)
    # Compliance
    pa = all_metrics.get('process-audit', {})
    summary['compliance_score'] = f"{pa.get('compliance_score', 'N/A')}/100"
    # Integration
    syn = all_metrics.get('synthesis-integration', {})
    summary['integration_status'] = syn.get('integration_status', 'N/A')
    # Mutations & lessons
    ma = all_metrics.get('mutations-applied', {})
    summary['mutations_count'] = ma.get('mutations_count', 0)
    les = all_metrics.get('lessons', {})
    summary['lessons_count'] = les.get('lessons_count', 0)

    all_metrics['_health_summary'] = summary

    report = generate_report(build_dir, all_metrics)
    output_file.write_text(report, encoding='utf-8')
    print(f"Wrote {output_file}")


if __name__ == '__main__':
    main()
