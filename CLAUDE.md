# Claude working agreement

## Goal

Build the smallest correct solution that matches the spec.

## Defaults

- No code comments (no `//`, `/* */`, `#`).
- Prefer small functions and descriptive names over comments.
- Don't change unrelated files.
- Avoid fixed pixels; use `theme.space` from `@mui/material` for spacing.
- Prefer existing npm packages over reimplementing functionality.

## React components

- Use named function declarations with explicit return types: `export function MyComponent(): JSX.Element {`
- Never use `const MyComponent = () =>` or `React.FC` or `FunctionComponent`
- Never use `ReactElement` as the return type — use `JSX.Element`

## Testing

- Tests are colocated with source files: `foo.ts` → `foo.test.ts`, `Bar.tsx` → `Bar.test.tsx`
- No separate `test/` directories
- Shared vitest config lives at root `vitest.shared.ts`

## Output expectations

- Keep diffs minimal.
- If you change behavior, update any docs/tests that describe it.

## Commands

- Install: `pnpm install`
- Run: `pnpm run scan`
- Test: `pnpm test` (if no tests exist, add a single smoke test and wire this command)

## Error handling

- Never use empty `catch` blocks — every caught error must be logged or rethrown
- When catching, log to `console.error` with context: what was being attempted, where, and the original error
- Prefer letting errors propagate over catching them — only catch when you can add value (retry, fallback, structured error)
- If you catch and recover, still log the original error at warn level
- In async code, never silently swallow rejected promises — always attach `.catch()` or use try/catch
- Bad: `catch (e) {}`, `catch (_e) { return null }`, `.catch(() => {})`
- Good: `catch (e) { console.error('failed to fetch match', matchId, e); throw e; }`

## Trust the types — no defensive programming

If the type says a value exists, trust it. Don't add runtime guards for things TypeScript already guarantees.

### No unnecessary optional chaining

```ts
// BAD — match is Match, not Match | undefined
const team = match?.team_h ?? '';
const goals = match?.h_goals ?? 0;
const shots = data?.results?.map(r => r?.score) ?? [];

// GOOD — match is Match, access it directly
const team = match.team_h;
const goals = match.h_goals;
const shots = data.results.map(r => r.score);
```

### No fallback values that hide bugs

```ts
// BAD — if xg is missing, that's a data bug, don't hide it with 0
const xg = parseFloat(match.h_xg ?? '0');
const items = response.data ?? [];

// GOOD — if it's required, let it fail loudly
const xg = parseFloat(match.h_xg);
const items = response.data;
```

### No redundant null checks

```ts
// BAD — teams is Team[], it's always an array
if (teams && teams.length > 0) { ... }
if (typeof matchId !== 'undefined') { ... }

// GOOD
if (teams.length > 0) { ... }
```

### No widening types to add optionality

```ts
// BAD — adding | null when the field is always present
interface Match {
  home_team: string | null;
  away_team: string | null;
  h_xg: number | undefined;
}

// GOOD — if the API always returns it, the type should reflect that
interface Match {
  home_team: string;
  away_team: string;
  h_xg: number;
}
```

### Assert at boundaries, don't default

When receiving data from external sources (API responses, scraped HTML, parsed JSON), use `assert` from `@cutting/assert` to validate before proceeding. Never silently default.

```ts
// BAD — silently masks missing data
const team = response.team_h ?? 'Unknown';

// GOOD — fails immediately with a clear message
assert(!!response.team_h, 'match response missing home team');
const team = response.team_h;
```

### Only use `?.` and `??` when the type is actually optional

`?.` is for `T | undefined | null`. If the type is `T`, use `.` and let TypeScript catch the mistake at compile time, not mask it at runtime.

## When unsure

Stop and ask for clarification before coding.

# Code Modification Policy

- Do NOT modify code unless explicitly asked
- When the user complains about something, ask if they want it changed
- Do not add features that weren't requested
- Do not add code comments
