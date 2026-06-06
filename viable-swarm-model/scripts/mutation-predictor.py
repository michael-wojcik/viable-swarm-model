#!/usr/bin/env python3
"""
Mutation Effectiveness Predictor for the VSM organism.

Before applying a new mutation, estimate its likely effectiveness based on
similar historical mutations from mutation-state.md and mutation-log.md.

Usage:
    python3 mutation-predictor.py --type append-only --target "enum type safety" --file-category agents
"""

import argparse
import os
import re
import sys
from pathlib import Path


STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those",
    "it", "its", "from", "as", "not", "no", "when", "where", "who", "what", "how", "why", "which",
    "than", "then", "into", "out", "up", "down", "over", "under", "again", "further", "once",
    "here", "there", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
    "only", "own", "same", "so", "too", "very", "just", "also", "if", "about", "between", "through",
    "during", "before", "after", "above", "below", "off", "nor", "don", "now", "via", "per",
}


def tokenize(text: str) -> set[str]:
    """Lowercase, split on non-alphanumeric, remove stop words and short tokens."""
    text = text.lower()
    tokens = re.findall(r"[a-z0-9_]+", text)
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 1}


def compute_target_similarity(target1: str, target2: str) -> int:
    """Return 0-3 points based on keyword overlap between two target descriptions."""
    set1 = tokenize(target1)
    set2 = tokenize(target2)
    if not set1 or not set2:
        return 0
    shared = len(set1 & set2)
    total = len(set1 | set2)
    if total == 0:
        return 0
    ratio = shared / total
    if ratio >= 0.4 or shared >= 5:
        return 3
    elif ratio >= 0.2 or shared >= 3:
        return 2
    elif ratio >= 0.05 or shared >= 1:
        return 1
    return 0


def is_separator_row(cells: list[str]) -> bool:
    """Check if a row is a markdown table separator like |---|---|---|."""
    return all(re.match(r'^:?-+$', c) for c in cells)


def clean_id(raw: str) -> str:
    """Remove markdown strikethrough and whitespace from mutation IDs."""
    return raw.replace("~~", "").strip()


def parse_score(raw: str) -> int | None:
    """Parse a score cell, handling '5→redesign' and missing values."""
    raw = raw.strip()
    if not raw or raw == "—":
        return None
    # Take only the part before any arrow
    score_str = raw.split("→")[0].strip()
    try:
        score = int(score_str)
        if 1 <= score <= 5:
            return score
    except ValueError:
        pass
    return None


def parse_builds(raw: str) -> int:
    """Parse builds-tested cell; default to 0 on failure."""
    raw = raw.strip()
    if not raw or raw == "—":
        return 0
    try:
        return int(raw)
    except ValueError:
        return 0


def parse_mutation_state(path: str) -> list[dict]:
    """Parse the master mutation table from mutation-state.md."""
    mutations = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                cells = [c.strip() for c in line.split("|")]
                # Remove empty leading/trailing cells
                cells = [c for c in cells if c]
                if len(cells) != 10:
                    continue
                # Skip header row
                if cells[0].lower() == "id":
                    continue
                # Skip separator rows
                if is_separator_row(cells):
                    continue
                # Skip section header rows (bold text spanning conceptually)
                if cells[0].startswith("**") and cells[0].endswith("**"):
                    continue
                # Some rows have extra blank cells; ensure first cell looks like an ID
                id_raw = cells[0]
                id_clean = clean_id(id_raw)
                if not id_clean:
                    continue
                score = parse_score(cells[6])
                if score is None:
                    continue
                builds = parse_builds(cells[5])
                mutations.append({
                    "id": id_clean,
                    "source": cells[1],
                    "type": cells[2].lower().strip(),
                    "target": cells[3],
                    "status": cells[4].lower().strip(),
                    "builds_tested": builds,
                    "score": score,
                })
    except FileNotFoundError:
        print(f"Warning: {path} not found. Using empty dataset.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: error reading {path}: {e}", file=sys.stderr)
    return mutations


def infer_category_from_files(files_text: str) -> str:
    """Map a File: line from mutation-log.md to a canonical category."""
    files_lower = files_text.lower()
    if "hooks/" in files_lower or "hook" in files_lower:
        return "hooks"
    agent_names = [
        "vsm_architect", "vsm_backend", "vsm_frontend", "vsm_security",
        "vsm_auditor", "vsm_coordinator", "vsm_tester", "vsm_devops",
        "vsm_meta", "vsm_wiring", "vsm_process", "vsm_variety", "vsm_learning",
    ]
    if "agents/" in files_lower or any(a in files_lower for a in agent_names):
        return "agents"
    if "skill.md" in files_lower:
        return "SKILL.md"
    if "references/" in files_lower:
        return "references"
    return "other"


def parse_mutation_log(path: str) -> dict[str, str]:
    """Parse mutation-log.md and return a mapping of mutation ID → file category."""
    id_to_category = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: {path} not found. Skipping log enrichment.", file=sys.stderr)
        return id_to_category
    except Exception as e:
        print(f"Warning: error reading {path}: {e}", file=sys.stderr)
        return id_to_category

    # Split on "## Mutation " headers
    entries = re.split(r'\n## Mutation\s+', content)
    for entry in entries[1:]:
        lines = entry.splitlines()
        if not lines:
            continue
        header = lines[0].strip()
        # Header like "1 — 2026-05-22" or "FB17-1 — 2026-05-25" or "FB9 / P46 — 2026-05-23"
        parts = header.split(" — ", 1)
        if not parts:
            continue
        mut_id = parts[0].strip()
        file_line = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("**File**:"):
                file_line = stripped.split(":", 1)[1].strip()
                break
        if file_line:
            id_to_category[mut_id] = infer_category_from_files(file_line)
    return id_to_category


def infer_category_heuristic(mtype: str, target: str) -> str:
    """Guess file category for mutations not found in mutation-log.md."""
    target_lower = target.lower()
    if "hook" in target_lower:
        return "hooks"
    if "agent" in target_lower or "auditor spawn" in target_lower:
        return "agents"
    if mtype == "structural":
        return "SKILL.md"
    if mtype == "refinement":
        return "agents"
    return "references"


def enrich_categories(mutations: list[dict], id_to_category: dict[str, str]) -> list[dict]:
    """Add 'category' field to each mutation using log data or heuristics."""
    for m in mutations:
        cat = id_to_category.get(m["id"])
        if cat is None or cat == "other":
            cat = infer_category_heuristic(m["type"], m["target"])
        m["category"] = cat
    return mutations


def compute_similarity(proposed: dict, historical: dict) -> int:
    """Compute similarity score between proposed and historical mutation."""
    score = 0
    if proposed["type"] == historical["type"]:
        score += 2
    score += compute_target_similarity(proposed["target"], historical["target"])
    if proposed["category"] == historical["category"]:
        score += 1
    return score


def determine_confidence(top_mutations: list[dict]) -> str:
    """Determine confidence level based on top similar mutations."""
    similar = [m for m in top_mutations if m.get("similarity_score", 0) > 0]
    count_3plus = sum(1 for m in similar if m["builds_tested"] >= 3)
    count_2plus = sum(1 for m in similar if m["builds_tested"] >= 2)

    if len(similar) >= 3 and count_3plus >= 3:
        return "HIGH"
    elif len(similar) >= 1 and count_2plus >= 1:
        return "MEDIUM"
    return "LOW"


def recommendation(confidence: str, predicted: float) -> str:
    """Generate a human-readable recommendation."""
    if confidence == "HIGH":
        if predicted >= 4.0:
            return "Proceed with high confidence"
        return "Proceed with moderate confidence"
    elif confidence == "MEDIUM":
        if predicted >= 3.0:
            return "Proceed with caution"
        return "Consider redesign or additional testing"
    return "Insufficient data — run a gym experiment first"


def main():
    parser = argparse.ArgumentParser(
        description="Predict the effectiveness of a proposed mutation based on historical data."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["append-only", "refinement", "structural"],
        help="Mutation type",
    )
    parser.add_argument(
        "--target",
        help="Target failure mode description (text). If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--file-category",
        required=True,
        choices=["agents", "references", "SKILL.md", "hooks"],
        help="File category the mutation affects",
    )
    args = parser.parse_args()

    target = args.target
    if target is None:
        if not sys.stdin.isatty():
            target = sys.stdin.read().strip()
        if not target:
            parser.error("--target is required when not reading from stdin")

    proposed = {
        "type": args.type.lower().strip(),
        "target": target,
        "category": args.file_category,
    }

    # Resolve paths (env vars allow testing with temp files)
    home = Path.home()
    state_path = Path(os.environ.get("MUTATION_PREDICTOR_STATE", home / "vsm" / "viable-swarm-model" / "references" / "mutation-state.md"))
    log_path = Path(os.environ.get("MUTATION_PREDICTOR_LOG", home / "vsm" / "viable-swarm-model" / "references" / "mutation-log.md"))

    mutations = parse_mutation_state(str(state_path))
    id_to_category = parse_mutation_log(str(log_path))
    mutations = enrich_categories(mutations, id_to_category)

    if not mutations:
        print("No historical mutations with scores found.")
        print("Predicted effectiveness: N/A")
        print("Confidence: LOW")
        print("Recommendation: Insufficient data — run a gym experiment first")
        sys.exit(0)

    # Compute similarity for all historical mutations
    for m in mutations:
        m["similarity_score"] = compute_similarity(proposed, m)

    # Sort by similarity descending, then by builds tested descending, then by score descending
    mutations.sort(key=lambda m: (-m["similarity_score"], -m["builds_tested"], -m["score"]))

    top5 = mutations[:5]
    similar = [m for m in top5 if m["similarity_score"] > 0]

    if not similar:
        print("Predicted effectiveness: N/A")
        print("Based on 0 similar mutations")
        print("Confidence: LOW")
        print("Recommendation: Insufficient data — run a gym experiment first")
        sys.exit(0)

    # Weighted average by builds tested
    total_weight = sum(m["builds_tested"] for m in similar)
    if total_weight == 0:
        predicted = sum(m["score"] for m in similar) / len(similar)
    else:
        predicted = sum(m["score"] * m["builds_tested"] for m in similar) / total_weight

    avg_score = sum(m["score"] for m in similar) / len(similar)
    avg_builds = sum(m["builds_tested"] for m in similar) / len(similar)
    confidence = determine_confidence(top5)
    rec = recommendation(confidence, predicted)

    print(f"Predicted effectiveness: {predicted:.1f}/5")
    print(f"Based on {len(similar)} similar mutations (avg {avg_score:.1f}/5, {avg_builds:.1f} builds)")
    print(f"Confidence: {confidence}")
    print(f"Recommendation: {rec}")
    print()
    print("Similar mutations:")
    for m in similar:
        print(f"- {m['id']} ({m['target']}): {m['score']}/5, {m['builds_tested']} build{'s' if m['builds_tested'] != 1 else ''}")


if __name__ == "__main__":
    main()
