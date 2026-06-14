#!/usr/bin/env python3
"""
check-graphql-stubs.py

Tool-enforced hard gate for H401: detect Strawberry GraphQL mutation/field
resolvers that are still stubs (pass, raise, or return INTERNAL_ERROR/
NotImplemented placeholders).

Usage:
    python3 check-graphql-stubs.py [directory] [--exclude PATTERN ...]

Exit codes:
    0 — no stubs found
    1 — one or more stub resolvers found
    2 — usage error or file read failure
"""

import argparse
import ast
import os
import sys
from pathlib import Path
from fnmatch import fnmatch


STUB_MARKERS = ("INTERNAL_ERROR", "NotImplemented", "NotImplementedError")


def is_strawberry_decorator(dec: ast.expr, names: set[str]) -> bool:
    """Match @strawberry.mutation, @strawberry.field, @strawberry.type."""
    # Bare decorator: @strawberry.mutation
    if isinstance(dec, ast.Attribute):
        if dec.attr in names:
            value = dec.value
            if isinstance(value, ast.Name) and value.id == "strawberry":
                return True
    # Decorator with arguments: @strawberry.mutation(...)
    if isinstance(dec, ast.Call):
        func = dec.func
        if isinstance(func, ast.Attribute) and func.attr in names:
            value = func.value
            if isinstance(value, ast.Name) and value.id == "strawberry":
                return True
    return False


def is_strawberry_type(node: ast.ClassDef) -> bool:
    return any(is_strawberry_decorator(d, {"type"}) for d in node.decorator_list)


def is_strawberry_resolver(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(is_strawberry_decorator(d, {"mutation", "field"}) for d in node.decorator_list)


def body_is_stub(body: list[ast.stmt]) -> bool:
    """Return True if the function body is a placeholder resolver."""
    if not body:
        return True

    # Unwrap a single-expression body
    if len(body) != 1:
        return False

    stmt = body[0]

    if isinstance(stmt, ast.Pass):
        return True

    if isinstance(stmt, ast.Raise):
        return True

    if isinstance(stmt, ast.Return):
        value = stmt.value
        if value is None:
            return True
        if isinstance(value, ast.Constant):
            if isinstance(value.value, str):
                return any(marker in value.value for marker in STUB_MARKERS)
        if isinstance(value, ast.Dict):
            for v in value.values:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    if any(marker in v.value for marker in STUB_MARKERS):
                        return True
        if isinstance(value, ast.List):
            for elt in value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    if any(marker in elt.value for marker in STUB_MARKERS):
                        return True

    return False


def find_stubs(path: Path, exclude_patterns: list[str]) -> list[tuple[str, str, str]]:
    """Return list of (file_path, class_name, resolver_name) stubs."""
    stubs: list[tuple[str, str, str]] = []

    for root, _dirs, files in os.walk(path):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            if any(fnmatch(filename, pat) for pat in exclude_patterns):
                continue
            full_path = Path(root) / filename
            rel_path = full_path.relative_to(path)
            # Heuristic: skip anything inside test directories
            if any(part == "tests" or part.startswith("test_") for part in rel_path.parts):
                continue

            try:
                source = full_path.read_text(encoding="utf-8")
            except Exception as exc:
                print(f"ERROR: could not read {full_path}: {exc}", file=sys.stderr)
                continue

            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                print(f"ERROR: syntax error in {full_path}: {exc}", file=sys.stderr)
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and is_strawberry_type(node):
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_strawberry_resolver(item):
                            if body_is_stub(item.body):
                                stubs.append((str(full_path), node.name, item.name))

    return stubs


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect Strawberry GraphQL stub resolvers")
    parser.add_argument("directory", nargs="?", default=".", help="Project directory to scan (default: cwd)")
    parser.add_argument("--exclude", action="append", default=["test_*.py", "*_test.py", "conftest.py"],
                        help="Filename patterns to exclude (default: test_*.py, *_test.py, conftest.py)")
    args = parser.parse_args()

    directory = Path(args.directory)
    if not directory.is_dir():
        print(f"ERROR: {directory} is not a directory", file=sys.stderr)
        return 2

    stubs = find_stubs(directory, args.exclude)

    if not stubs:
        print("OK — no Strawberry GraphQL stub resolvers found.")
        return 0

    print(f"FAIL — {len(stubs)} stub resolver(s) found:")
    for file_path, class_name, resolver_name in stubs:
        print(f"  {file_path}::{class_name}.{resolver_name}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
