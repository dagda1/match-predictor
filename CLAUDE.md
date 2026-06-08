# Claude working agreement

## Goal

Build the smallest correct solution that matches the spec.

## Response length (hard rule)

Default to 1-3 sentences. No tables, no bullet dumps, no recaps of what you just did, no restating the question. Expand only when explicitly asked. One code block max unless asked for more.

## Skills

All conventions live as skills under `.claude/skills/` (symlinked from `~/claude/skills/`). Read the relevant ones before working in that area.

**Always-on (read every session):**
- `assistant-communication` — no follow-up nudges, ask one question when unsure, terse replies
- `assistant-modification-policy` — only modify when asked, no unrequested features
- `assistant-output-expectations` — minimal diffs, update related docs/tests, no Claude attribution

**Code (any language):**
- `code-style-defaults` — no comments, naming, braces, dependencies, scope
- `code-error-handling` — never swallow, always context, propagate by default
- `code-trust-the-types` — no defensive `?.` / `??`, no `as unknown as`, no `!`
- `code-test-colocation` — tests next to source, no `test/` dirs

**Frontend (React/MUI/TS):**
- `frontend-react-typescript` — imports, event types, component declaration, props, return types
- `frontend-mui-theming` — `styles.ts`, `sx` export, `theme.palette`, no hardcoded colors/pixels
- `frontend-component-structure` — companion files, no barrel `index.ts`, max 150 lines, `~/` alias
- `frontend-routing` — lazy pages, central routes file, layout via `Outlet`
- `frontend-zod-validation` — Zod at boundaries
- `frontend-react-query` — query keys, mutation invalidation
- `frontend-testing` — RTL discipline, `userEvent`, real component tree

**CDK (TS or Python):**
- `cdk-construct-conventions` — typed props, deterministic IDs, tagging, file organisation
- `cdk-iam-least-privilege` — no wildcards, scoped resources, conditions on trust policies
- `cdk-stateful-resources` — explicit removal policies, deletion protection, backups
- `cdk-custom-resources` — `Version` bumping, idempotent handlers, stable `PhysicalResourceId`

**Review (used by `/branch-review`):**
- `review-pr-size`, `review-commit-hygiene`, `review-secret-scanning`, `review-report-format`

If something below conflicts with a skill, this file wins (project-specific override).

## Project-specific

### Testing

- Shared vitest config lives at root `vitest.shared.ts`.

### Commands

- Install: `pnpm install`
- Run: `pnpm run scan`
- Test: `pnpm test` (if no tests exist, add a single smoke test and wire this command)
