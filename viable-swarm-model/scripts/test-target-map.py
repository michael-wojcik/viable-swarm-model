#!/usr/bin/env python3
"""
Test Target Map — Pre-computation for tester agents.

Analyzes backend and frontend source files to identify testable targets:
- FastAPI endpoints (router decorators)
- GraphQL resolvers (strawberry decorators)
- Pydantic / SQLAlchemy models
- React components and hooks
- Store actions and API clients

Outputs structured `.kimi/test-target-map.md` so tester agents can focus
on writing tests rather than discovering what to test.

Usage:
    python3 test-target-map.py <build-directory>

Writes:
    <build-dir>/.kimi/test-target-map.md
"""

import argparse
import re
import sys
from pathlib import Path


def scan_python_file(filepath: Path) -> dict:
    """Extract testable targets from a Python file."""
    targets = {
        'endpoints': [],
        'resolvers': [],
        'models': [],
        'auth_handlers': [],
    }
    try:
        content = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return targets

    lines = content.split('\n')

    # FastAPI endpoints: @router.get("/path") or @app.get("/path")
    for i, line in enumerate(lines):
        m = re.search(r'@(?:router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', line, re.IGNORECASE)
        if m:
            method = m.group(1).upper()
            path = m.group(2)
            func_name = 'unknown'
            # Look ahead for function definition
            for j in range(i + 1, min(i + 5, len(lines))):
                fm = re.search(r'(?:async\s+)?def\s+(\w+)', lines[j])
                if fm:
                    func_name = fm.group(1)
                    break
            targets['endpoints'].append({
                'method': method,
                'path': path,
                'function': func_name,
                'line': i + 1,
            })

    # GraphQL resolvers: @strawberry.field or @strawberry.mutation
    for i, line in enumerate(lines):
        m = re.search(r'@strawberry\.(field|mutation)', line, re.IGNORECASE)
        if m:
            resolver_type = m.group(1).lower()
            func_name = 'unknown'
            for j in range(i + 1, min(i + 5, len(lines))):
                fm = re.search(r'(?:async\s+)?def\s+(\w+)', lines[j])
                if fm:
                    func_name = fm.group(1)
                    break
            targets['resolvers'].append({
                'type': resolver_type,
                'name': func_name,
                'line': i + 1,
            })

    # Pydantic / SQLAlchemy models
    for i, line in enumerate(lines):
        m = re.search(r'class\s+(\w+)\s*\(\s*(BaseModel|SQLModel|DeclarativeBase|Base)', line)
        if m:
            targets['models'].append({
                'name': m.group(1),
                'base': m.group(2),
                'line': i + 1,
            })

    # Auth handlers (heuristic: functions with auth-related parameters)
    for i, line in enumerate(lines):
        m = re.search(r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\b(?:user|current_user|token|auth|role)\b', line, re.IGNORECASE)
        if m:
            func_name = m.group(1)
            # Avoid duplicating endpoints already captured
            if not any(e['function'] == func_name for e in targets['endpoints']):
                targets['auth_handlers'].append({
                    'name': func_name,
                    'line': i + 1,
                })

    return targets


def scan_typescript_file(filepath: Path) -> dict:
    """Extract testable targets from a TypeScript file."""
    targets = {
        'components': [],
        'hooks': [],
        'store_actions': [],
        'api_functions': [],
    }
    try:
        content = filepath.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return targets

    lines = content.split('\n')
    file_str = str(filepath)

    # Determine file category from path
    is_store = 'store' in file_str.lower()
    is_api = any(x in file_str.lower() for x in ['api', 'client', 'graphql', 'query', 'mutation'])

    for i, line in enumerate(lines):
        # React components: export function ComponentName or export default function
        cm = re.search(r'export\s+(?:default\s+)?(?:async\s+)?(?:function|const)\s+(\w+)', line)
        if cm:
            name = cm.group(1)
            # Heuristic: components start with uppercase
            if name[0].isupper() and not name.startswith('use'):
                targets['components'].append({
                    'name': name,
                    'line': i + 1,
                })
            # Hooks start with use
            elif name.startswith('use') and name[3:4].isupper():
                targets['hooks'].append({
                    'name': name,
                    'line': i + 1,
                })
            # Store actions in store files
            elif is_store and name[0].islower():
                targets['store_actions'].append({
                    'name': name,
                    'line': i + 1,
                })
            # API functions in api files
            elif is_api and name[0].islower():
                targets['api_functions'].append({
                    'name': name,
                    'line': i + 1,
                })

    return targets


def scan_backend(backend_dir: Path) -> dict:
    """Scan backend directory for all testable targets."""
    all_targets = {
        'endpoints': [],
        'resolvers': [],
        'models': [],
        'auth_handlers': [],
    }
    for py_file in sorted(backend_dir.rglob('*.py')):
        # Skip common non-testable files
        if any(part.startswith('.') for part in py_file.parts):
            continue
        rel = py_file.relative_to(backend_dir)
        file_targets = scan_python_file(py_file)
        for category in all_targets:
            for t in file_targets[category]:
                t['file'] = str(rel)
                all_targets[category].append(t)
    return all_targets


def scan_frontend(src_dir: Path) -> dict:
    """Scan frontend/src directory for all testable targets."""
    all_targets = {
        'components': [],
        'hooks': [],
        'store_actions': [],
        'api_functions': [],
    }
    for ext in ['*.tsx', '*.ts']:
        for ts_file in sorted(src_dir.rglob(ext)):
            if any(part.startswith('.') for part in ts_file.parts):
                continue
            rel = ts_file.relative_to(src_dir)
            file_targets = scan_typescript_file(ts_file)
            for category in all_targets:
                for t in file_targets[category]:
                    t['file'] = str(rel)
                    all_targets[category].append(t)
    return all_targets


def generate_report(build_dir: Path, backend_targets: dict, frontend_targets: dict) -> str:
    """Generate the test target map markdown report."""
    lines = [
        '# Test Target Map',
        '',
        f'> **Build**: {build_dir.name}',
        f'> **Generated**: {__import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC',
        f'> **Scanner**: scripts/test-target-map.py',
        '',
        'This file lists all testable targets discovered in the codebase.',
        'Tester agents should use this as their test plan rather than',
        're-discovering targets by reading source files.',
        '',
    ]

    has_backend = any(backend_targets.get(cat) for cat in backend_targets)
    has_frontend = any(frontend_targets.get(cat) for cat in frontend_targets)

    if has_backend:
        lines.append('## Backend Test Targets')
        lines.append('')

        if backend_targets['endpoints']:
            lines.append(f'### HTTP Endpoints ({len(backend_targets["endpoints"])})')
            lines.append('')
            lines.append('| Method | Path | Function | File |')
            lines.append('|---|---|---|---|')
            for ep in backend_targets['endpoints'][:30]:  # Limit to avoid overwhelming
                lines.append(f"| {ep['method']} | `{ep['path']}` | `{ep['function']}` | `{ep['file']}` |")
            lines.append('')

        if backend_targets['resolvers']:
            lines.append(f'### GraphQL Resolvers ({len(backend_targets["resolvers"])})')
            lines.append('')
            lines.append('| Type | Name | File |')
            lines.append('|---|---|---|')
            for r in backend_targets['resolvers'][:30]:
                lines.append(f"| {r['type']} | `{r['name']}` | `{r['file']}` |")
            lines.append('')

        if backend_targets['models']:
            lines.append(f'### Data Models ({len(backend_targets["models"])})')
            lines.append('')
            lines.append('| Name | Base Class | File |')
            lines.append('|---|---|---|')
            for m in backend_targets['models'][:20]:
                lines.append(f"| `{m['name']}` | {m['base']} | `{m['file']}` |")
            lines.append('')

        if backend_targets['auth_handlers']:
            lines.append(f'### Auth-Related Handlers ({len(backend_targets["auth_handlers"])})')
            lines.append('')
            for ah in backend_targets['auth_handlers'][:15]:
                lines.append(f"- `{ah['name']}` — `{ah['file']}`:{ah['line']}")
            lines.append('')

    if has_frontend:
        lines.append('## Frontend Test Targets')
        lines.append('')

        if frontend_targets['components']:
            lines.append(f'### Components ({len(frontend_targets["components"])})')
            lines.append('')
            for c in frontend_targets['components'][:30]:
                lines.append(f"- `{c['name']}` — `{c['file']}`:{c['line']}")
            lines.append('')

        if frontend_targets['hooks']:
            lines.append(f'### Hooks ({len(frontend_targets["hooks"])})')
            lines.append('')
            for h in frontend_targets['hooks'][:15]:
                lines.append(f"- `{h['name']}` — `{h['file']}`:{h['line']}")
            lines.append('')

        if frontend_targets['store_actions']:
            lines.append(f'### Store Actions ({len(frontend_targets["store_actions"])})')
            lines.append('')
            for a in frontend_targets['store_actions'][:20]:
                lines.append(f"- `{a['name']}` — `{a['file']}`:{a['line']}")
            lines.append('')

        if frontend_targets['api_functions']:
            lines.append(f'### API Functions ({len(frontend_targets["api_functions"])})')
            lines.append('')
            for f in frontend_targets['api_functions'][:20]:
                lines.append(f"- `{f['name']}` — `{f['file']}`:{f['line']}")
            lines.append('')

    lines.extend([
        '---',
        '',
        '**Tester Agent Instructions**:',
        '1. Use this map as your starting test plan.',
        '2. Prioritize: auth endpoints → model validation → GraphQL resolvers → components.',
        '3. If a target has trivial logic (e.g., pass-through endpoint), write a minimal',
        '   smoke test and note it as "trivial" in your report.',
        '4. Do NOT re-scan source files to discover targets — this map is authoritative.',
        '5. If you discover targets missing from this map, append them to the report',
        '   and flag the gap for S5.',
        '',
    ])

    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate test target map from source code')
    parser.add_argument('build_dir', help='Build directory to scan')
    args = parser.parse_args()

    build_dir = Path(args.build_dir)
    if not build_dir.exists():
        print(f'ERROR: Build directory not found: {build_dir}', file=sys.stderr)
        return 1

    backend_dir = build_dir / 'backend'
    frontend_dir = build_dir / 'frontend' / 'src'

    backend_targets = scan_backend(backend_dir) if backend_dir.exists() else {}
    frontend_targets = scan_frontend(frontend_dir) if frontend_dir.exists() else {}

    report = generate_report(build_dir, backend_targets, frontend_targets)
    output_path = build_dir / '.kimi' / 'test-target-map.md'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')

    total = sum(len(v) for v in backend_targets.values()) + sum(len(v) for v in frontend_targets.values())
    print(f'Test target map: {total} targets found → {output_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
