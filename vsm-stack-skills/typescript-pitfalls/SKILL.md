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
