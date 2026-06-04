#!/usr/bin/env python3
"""
Lesson Mining Engine for the VSM organism.

Scans all fitness build lesson files and extracts longitudinal patterns.
Reads: ~/vsm-fitness-builds/coach/FB*/.kimi/lessons.md
Writes (append-only): ~/vsm/viable-swarm-model/references/lesson-patterns.md

Pure Python 3 stdlib. Uses pathlib.
"""

from __future__ import annotations

import re
import sys
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUILDS_ROOT = Path.home() / "vsm-fitness-builds" / "coach"
OUTPUT_FILE = Path.home() / "vsm" / "viable-swarm-model" / "references" / "lesson-patterns.md"

SKILL_FILES = [
    Path.home() / "vsm" / "viable-swarm-model" / "references" / "security-lessons.md",
    Path.home() / "vsm" / "viable-swarm-model" / "references" / "pattern-library.md",
    Path.home() / "vsm" / "viable-swarm-model" / "references" / "anti-patterns.md",
    Path.home() / "vsm" / "viable-swarm-model" / "references" / "integration-checklist.md",
]

STOP_WORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was",
    "one", "our", "out", "day", "get", "has", "him", "his", "how", "its", "may", "new",
    "now", "old", "see", "two", "way", "who", "boy", "did", "she", "use", "too",
    "any", "say", "try", "let", "put", "end", "why", "also", "each",
    "which", "their", "time", "will", "about", "up", "many", "then", "them",
    "these", "so", "some", "would", "make", "like", "into", "more", "very", "what",
    "know", "just", "first", "over", "think", "your", "work", "life", "even", "want",
    "here", "look", "down", "most", "long", "last", "find", "give", "does", "made",
    "part", "such", "take", "than", "only", "other", "still", "being", "own", "under",
    "never", "same", "another", "could", "state", "year", "good", "where", "much",
    "back", "after", "man", "great", "world", "should", "through", "before", "between",
    "both", "few", "those", "while", "this", "that", "with", "have", "from", "they",
    "been", "were", "said", "there", "when", "would", "could",
    "app", "backend", "frontend", "file", "files", "code", "test", "tests", "error",
    "phase", "build", "agent", "missing", "fix", "found", "used", "using", "added",
    "call", "called", "need", "needs", "must", "should", "correctly", "incorrectly",
    "check", "checked", "verify", "verified", "exists", "existing", "correct",
    "issue", "issues", "bug", "bugs", "failure", "fail", "pass", "passed",
}

AGENT_NAMES = {
    "vsm_backend_coder", "vsm_frontend_coder", "vsm_security",
    "vsm_auditor", "vsm_architect", "vsm_coordinator", "vsm_wiring",
    "vsm_tester", "vsm_meta", "vsm_devops_coder",
    "vsm_backend_tester", "vsm_frontend_tester", "vsm_process_auditor",
    "vsm_product", "vsm_backend_fix_agent", "vsm_frontend_fix_agent",
    "vsm_variety_engineer", "vsm_learning_curator", "vsm_explore",
    "foundation auditor", "implementation auditor", "security auditor",
    "backend fix agent", "frontend fix agent", "process auditor",
    "backend coder", "frontend coder", "backend tester", "frontend tester",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, file=sys.stderr, **kwargs)


def extract_words(text: str) -> set[str]:
    words = re.findall(r"[a-z][a-z0-9_]*", text.lower())
    return {w for w in words if len(w) >= 3 and w not in STOP_WORDS}


def extract_sentences(text: str) -> list[str]:
    raw = re.split(r'[.!?]+(?:\s+|\n)', text)
    sentences = []
    for s in raw:
        s = s.strip().replace("\n", " ")
        if len(s) >= 10:
            sentences.append(s)
    return sentences


def find_meta_reports(build_dir: Path) -> list[Path]:
    candidates = []
    for name in ("meta-report.md", "meta-evaluation-report.md"):
        p = build_dir / ".kimi" / name
        if p.exists():
            candidates.append(p)
        p2 = build_dir / name
        if p2.exists():
            candidates.append(p2)
    return candidates


def extract_overall_score(text: str) -> float | None:
    m = re.search(r"[Oo]verall\s+[Ss]core[:\s]+(\d+(?:\.\d+)?)\s*/\s*100", text)
    if m:
        return float(m.group(1))

    m = re.search(r"[Ss]core[:\s]+(\d+(?:\.\d+)?)\s*/\s*100", text)
    if m:
        return float(m.group(1))

    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*5\.0?", text)
    if m:
        return float(m.group(1)) * 20.0

    m = re.search(r"[Oo]verall\s+[Bb]uild\s+[Ss]core[:\s]+(\d+(?:\.\d+)?)", text)
    if m:
        val = float(m.group(1))
        if val <= 5.0:
            return val * 20.0
        return val

    lines = text.splitlines()
    in_trend = False
    for line in lines:
        if "Score Trend" in line or "score trend" in line.lower():
            in_trend = True
        if in_trend and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            for part in parts:
                if re.match(r"^\d+(?:\.\d+)?$", part):
                    val = float(part)
                    if val <= 5.0:
                        return val * 20.0
                    if val <= 100.0:
                        return val

    m = re.search(r"([\d.]+)\s+overall", text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        if val <= 5.0:
            return val * 20.0
        return val

    return None


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def scan_lessons() -> list[dict[str, Any]]:
    files = sorted(BUILDS_ROOT.rglob(".kimi/lessons.md"))
    eprint(f"Found {len(files)} lessons.md files")

    entries: list[dict[str, Any]] = []

    for fpath in files:
        build_id = fpath.parent.parent.name
        if not build_id.startswith("FB"):
            continue

        text = fpath.read_text(encoding="utf-8")
        parts = re.split(r"\n##\s+", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            first_line = part.split("\n", 1)[0].strip()
            is_lesson = bool(
                re.match(r"(?:Lesson|Entry|L)\s*\d+[:.\-\s]", first_line, re.IGNORECASE)
            )
            if not is_lesson:
                if "**Finding**" in part or "**Source**" in part:
                    is_lesson = True
                else:
                    continue

            def grab_field(label: str) -> str:
                pat = re.compile(
                    rf"\*\*{re.escape(label)}\*\*[:\s]*(.+?)(?=\n\*\*|$)",
                    re.DOTALL | re.IGNORECASE,
                )
                m = pat.search(part)
                if m:
                    return re.sub(r"\s+", " ", m.group(1).strip())
                return ""

            finding = grab_field("Finding")
            fix = grab_field("Fix")
            phase = grab_field("Phase")
            source = grab_field("Source")

            prevention = ""
            for label in ("Prevention rule", "Prevention", "Mutation", "Recommendation"):
                prevention = grab_field(label)
                if prevention:
                    break

            source_file = ""
            for haystack in (source, finding):
                m = re.search(r"`?([\w/\-_]+\.\w+)`?", haystack)
                if m:
                    source_file = m.group(1)
                    break

            entries.append({
                "build_id": build_id,
                "phase": phase or "",
                "finding": finding,
                "fix": fix,
                "prevention_rule": prevention,
                "source_file": source_file,
                "raw_title": first_line,
            })

    eprint(f"Parsed {len(entries)} lesson entries")
    return entries


def extract_patterns(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not entries:
        return []

    entry_words: list[set[str]] = []
    for e in entries:
        words = extract_words(e["finding"])
        if not words:
            words = extract_words(e["raw_title"])
        entry_words.append(words)

    n = len(entries)
    adj = defaultdict(set)

    for i in range(n):
        for j in range(i + 1, n):
            shared = entry_words[i] & entry_words[j]
            if len(shared) >= 2:
                adj[i].add(j)
                adj[j].add(i)

    visited = [False] * n
    clusters: list[list[int]] = []
    for i in range(n):
        if visited[i]:
            continue
        stack = [i]
        comp: list[int] = []
        visited[i] = True
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nxt in adj[cur]:
                if not visited[nxt]:
                    visited[nxt] = True
                    stack.append(nxt)
        if len(comp) >= 2:
            clusters.append(comp)

    patterns: list[dict[str, Any]] = []
    for comp in clusters:
        findings = [entries[i]["finding"] or entries[i]["raw_title"] for i in comp]
        builds = sorted({entries[i]["build_id"] for i in comp})
        fixes = [entries[i]["fix"] for i in comp if entries[i]["fix"]]
        most_common_fix = ""
        if fixes:
            fix_counts = Counter(fixes)
            most_common_fix = fix_counts.most_common(1)[0][0]

        all_words: list[str] = []
        for i in comp:
            all_words.extend(entry_words[i])
        top = Counter(all_words).most_common(3)
        name = " / ".join(w for w, _ in top) if top else "Unnamed Pattern"

        patterns.append({
            "name": name,
            "occurrences": len(comp),
            "builds": builds,
            "most_common_fix": most_common_fix,
            "findings": findings,
            "recommended_mutation": f"Consider consolidating prevention rule for '{name}'",
        })

    patterns.sort(key=lambda x: x["occurrences"], reverse=True)
    return patterns


def detect_lesson_orphans(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skill_texts: list[str] = []
    for sf in SKILL_FILES:
        if sf.exists():
            skill_texts.append(sf.read_text(encoding="utf-8"))
        else:
            eprint(f"Warning: skill file not found: {sf}")

    skill_sentences: list[tuple[str, set[str]]] = []
    for text in skill_texts:
        for sent in extract_sentences(text):
            skill_sentences.append((sent, extract_words(sent)))

    orphans: list[dict[str, Any]] = []
    seen_rules: dict[str, bool] = {}

    for e in entries:
        rule = e["prevention_rule"]
        if not rule or len(rule) < 15:
            continue

        if rule in seen_rules:
            if not seen_rules[rule]:
                orphans.append({
                    "rule": rule,
                    "build_id": e["build_id"],
                    "source_file": e["source_file"],
                })
            continue

        rule_words = extract_words(rule)
        if len(rule_words) < 3:
            seen_rules[rule] = True
            continue

        matched = False
        for sent, sent_words in skill_sentences:
            shared = rule_words & sent_words
            if len(shared) >= 4 or (len(rule_words) > 0 and len(shared) / len(rule_words) >= 0.5):
                matched = True
                break

        seen_rules[rule] = matched
        if not matched:
            orphans.append({
                "rule": rule,
                "build_id": e["build_id"],
                "source_file": e["source_file"],
            })

    return orphans


def correlate_with_scores(entries: list[dict[str, Any]]) -> dict[str, Any]:
    build_lessons: Counter[str] = Counter()
    for e in entries:
        build_lessons[e["build_id"]] += 1

    build_scores: dict[str, float] = {}
    for build_dir in sorted(BUILDS_ROOT.glob("FB*")):
        if not build_dir.is_dir():
            continue
        build_id = build_dir.name
        reports = find_meta_reports(build_dir)
        for rpath in reports:
            text = rpath.read_text(encoding="utf-8")
            score = extract_overall_score(text)
            if score is not None:
                build_scores[build_id] = score
                break

    eprint(f"Found scores for {len(build_scores)} builds")

    common_builds = sorted(set(build_lessons.keys()) & set(build_scores.keys()))
    if len(common_builds) < 2:
        return {
            "common_builds": common_builds,
            "build_lessons": dict(build_lessons),
            "build_scores": build_scores,
            "correlation": None,
            "interpretation": "Insufficient data for correlation",
        }

    xs = [build_lessons[b] for b in common_builds]
    ys = [build_scores[b] for b in common_builds]

    n = len(common_builds)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = sum((x - mean_x) ** 2 for x in xs)
    den_y = sum((y - mean_y) ** 2 for y in ys)

    correlation = None
    if den_x > 0 and den_y > 0:
        correlation = num / math.sqrt(den_x * den_y)

    interpretation = "No clear correlation"
    if correlation is not None:
        if correlation < -0.3:
            interpretation = f"Negative correlation (r={correlation:.2f}): more lessons tend to associate with lower scores"
        elif correlation > 0.3:
            interpretation = f"Positive correlation (r={correlation:.2f}): more lessons tend to associate with higher scores"
        else:
            interpretation = f"Weak correlation (r={correlation:.2f}): lesson count and score are largely independent"

    return {
        "common_builds": common_builds,
        "build_lessons": {b: build_lessons[b] for b in common_builds},
        "build_scores": {b: build_scores[b] for b in common_builds},
        "correlation": correlation,
        "interpretation": interpretation,
    }


def compute_agent_risk(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    agent_counts: Counter[str] = Counter()
    for e in entries:
        text = f"{e.get('phase', '')} {e.get('finding', '')} {e.get('fix', '')} {e.get('raw_title', '')}"
        for agent in AGENT_NAMES:
            if re.search(rf"\b{re.escape(agent)}\b", text, re.IGNORECASE):
                agent_counts[agent] += 1
    results = []
    for agent, count in agent_counts.most_common():
        if count >= 1:
            results.append({"agent": agent, "lesson_count": count})
    return results


def generate_report(
    entries: list[dict[str, Any]],
    patterns: list[dict[str, Any]],
    orphans: list[dict[str, Any]],
    correlation: dict[str, Any],
    agent_risks: list[dict[str, Any]],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_builds = len({e["build_id"] for e in entries})
    total_lessons = len(entries)

    lines: list[str] = [
        "---",
        "",
        f"# Lesson Patterns Report -- {now}",
        "",
        "## Header",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Date | {now} |",
        f"| Builds scanned | {total_builds} |",
        f"| Total lessons | {total_lessons} |",
        "",
        "## Recurring Patterns",
        "",
    ]

    if patterns:
        lines.append("| Pattern | Occurrences | Builds Affected | Most Common Fix | Recommended Mutation |")
        lines.append("|---|---|---|---|---|")
        for p in patterns:
            builds_str = ", ".join(p["builds"])
            fix = p["most_common_fix"]
            fix_short = fix[:80] + "..." if len(fix) > 80 else fix
            lines.append(
                f"| {p['name']} | {p['occurrences']} | {builds_str} | {fix_short} | {p['recommended_mutation']} |"
            )
    else:
        lines.append("*No recurring patterns detected.*")

    lines.extend([
        "",
        "## Lesson Orphans",
        "",
        "*Prevention rules mentioned in lessons.md that do NOT appear in skill files.*",
        f"*Orphaned rules: {len(orphans)}*",
        "",
    ])

    if orphans:
        lines.append("| Build ID | Rule (excerpt) | Source File |")
        lines.append("|---|---|---|")
        for o in orphans:
            rule_excerpt = o["rule"][:100] + "..." if len(o["rule"]) > 100 else o["rule"]
            lines.append(f"| {o['build_id']} | {rule_excerpt} | {o['source_file'] or '--'} |")
    else:
        lines.append("*All prevention rules are reflected in skill files.*")

    lines.extend([
        "",
        "## Agent Risk",
        "",
        "*Agents most frequently associated with lessons (indicates where knowledge gaps or process friction concentrate).",
        "",
    ])

    if agent_risks:
        lines.append("| Agent | Lesson Mentions |")
        lines.append("|---|---|")
        for a in agent_risks:
            lines.append(f"| {a['agent']} | {a['lesson_count']} |")
    else:
        lines.append("*No agent associations detected.*")

    lines.extend([
        "",
        "## Score Correlation",
        "",
        "*Correlation between lesson count per build and overall build score.*",
        "",
        f"{correlation['interpretation']}",
        "",
    ])

    if correlation["common_builds"]:
        lines.append("| Build | Lessons | Score |")
        lines.append("|---|---|---|")
        for b in correlation["common_builds"]:
            score = correlation["build_scores"].get(b, "--")
            lessons = correlation["build_lessons"].get(b, "--")
            lines.append(f"| {b} | {lessons} | {score} |")
    else:
        lines.append("*No builds with both lessons and scores available.*")

    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    eprint("[lesson-miner] Starting scan...")

    entries = scan_lessons()
    if not entries:
        eprint("[lesson-miner] No lesson entries found. Exiting.")
        print("No lessons found.")
        return 0

    eprint("[lesson-miner] Extracting patterns...")
    patterns = extract_patterns(entries)

    eprint("[lesson-miner] Detecting orphans...")
    orphans = detect_lesson_orphans(entries)

    eprint("[lesson-miner] Computing agent risk...")
    agent_risks = compute_agent_risk(entries)

    eprint("[lesson-miner] Correlating with scores...")
    correlation = correlate_with_scores(entries)

    eprint("[lesson-miner] Generating report...")
    report = generate_report(entries, patterns, orphans, correlation, agent_risks)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        f.write(report)

    eprint(f"[lesson-miner] Appended report to {OUTPUT_FILE}")

    print("Lesson Mining Complete")
    print(f"  Builds scanned: {len({e['build_id'] for e in entries})}")
    print(f"  Total lessons:  {len(entries)}")
    print(f"  Patterns found: {len(patterns)}")
    print(f"  Orphaned rules: {len(orphans)}")
    print(f"  Report written: {OUTPUT_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
