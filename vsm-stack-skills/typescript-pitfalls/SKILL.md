# TypeScript Pitfalls

**Version scope**: TypeScript 5.0+. For older versions, use `SearchWeb` to verify behavior.

Empirical traps discovered by the VSM swarm. Use `SearchWeb` for API documentation.

## Vite Alias Key (FB16)
Use `"@"` (not `"@/"`) as the alias key in `vite.config.ts`:
```ts
alias: { "@": path.resolve(__dirname, "./src") }
```
`"@/"` resolves in dev but fails in production builds because Rollup does not 
match the trailing slash. BLOCKER-level.

## Build vs Type-Check Gap
`vite build` does NOT run `tsc`. Always run `npm run build` (which usually includes 
`tsc -b`) to catch type errors that Vite misses.

## `as any` Bypasses
NEVER use `as any` to destructure fields from Zustand stores or contexts.
If the field doesn't exist in the type definition, update the type — do NOT 
suppress TypeScript. `as any` hides real contract mismatches.

## Orphaned GraphQL Queries
Every export from `queries.ts` MUST be imported by at least one page or component.
Orphaned exports are dead code that bloat bundles.

## Config Fallbacks
NEVER use `||` fallbacks for API/WS/GraphQL URLs:
```typescript
// WRONG — bakes localhost into production bundles
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
// CORRECT
const API_URL = import.meta.env.VITE_API_URL;
```

## tsconfig Include Scope
If `tsconfig.json` includes `vite.config.ts`, verify `@types/node` is installed 
or `tsc -b` will fail with missing type errors.

## Duplicate Vite Config Files (Discovered FB23)
If both `vite.config.ts` and `vite.config.js` exist, Vite prefers `.ts` but the
`.js` file becomes dead weight that confuses tooling and reviewers. Remove the
`.js` version when the `.ts` version is authoritative.

## Test Files in Production tsconfig (Discovered FB23)
If `tsconfig.json` includes test files (e.g., via `"include": ["src"]` which
picks up `src/test/*.tsx`), production `tsc -b` can fail due to test-only
dependencies (`@testing-library/react`) or missing browser API mocks. Either:
- Exclude `src/test/` from the production `tsconfig.json`, OR
- Use a separate `tsconfig.app.json` for the app and `tsconfig.node.json` for
  the build tool, with `tsconfig.json` as a solution-style config.

## Page Implementation Verification (FB24)
Before declaring frontend code complete, verify at least ONE page contains a
live GraphQL query, REST fetch, or store subscription that renders actual data.
Pages that are `<div>Label</div>` stubs with void-referenced imports are a
BLOCKER. Every page MUST implement at least one of: data fetching, state
management, conditional rendering, or interactive elements.

**Source**: FB24 stub pages detected — pages had import statements but no
actual data fetching (H158).

## Vite Config Must Not Contain `test` Property (FB28)

**Status**: Active (FB28-sourced)
**Severity**: BLOCKER
**Applies to**: vsm_frontend_coder, vsm_frontend_tester, vsm_wiring

The `test` property is NOT part of Vite's `UserConfigExport` type. If `vite.config.ts`
contains a `test` block (for Vitest configuration), `tsc -b` will fail with:
```
Object literal may only specify known properties, and 'test' does not exist in type 'UserConfigExport'
```

**Correct pattern**:
```typescript
// vite.config.ts — Vite ONLY
import { defineConfig } from "vite";
export default defineConfig({
  plugins: [react()],
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
  server: { port: 5173 },
});
```
```typescript
// vitest.config.ts — Vitest ONLY, imports from vitest/config
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: { globals: true, environment: "jsdom" },
  resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
});
```

**Incorrect pattern** (BLOCKER):
```typescript
// vite.config.ts — DO NOT put test here
import { defineConfig } from "vite";
export default defineConfig({
  plugins: [react()],
  test: { globals: true, environment: "jsdom" },  // TypeScript error!
});
```

**Prevention rules**:
1. `vite.config.ts` MUST import from `"vite"`, NEVER from `"vitest/config"`.
2. `vitest.config.ts` MUST be a separate file importing from `"vitest/config"`.
3. Frontend config validation (Phase 3e) MUST verify BOTH files exist and use correct imports.
4. `tsc -b` MUST pass with zero errors before `npm run build` is attempted.

**Source**: FB28 `vite.config.ts` initially contained a `test` block. `tsc -b` failed
with a type error. The fix was separating into `vite.config.ts` + `vitest.config.ts`.
