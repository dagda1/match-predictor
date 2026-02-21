# Claude working agreement

## Goal

Build the smallest correct solution that matches the spec.

## Defaults

- No code comments (no `//`, `/* */`, `#`).
- Prefer small functions and descriptive names over comments.
- Never use single character variables.
- Don't change unrelated files.
- Avoid fixed pixels; use `theme.spacing` from `@mui/material` for spacing.
- Prefer existing npm packages over reimplementing functionality.
- No file extensions on imports (use `import x from './foo'` not `import x from './foo.js'`).
- Use `~/` path alias for imports outside the current directory — never use `../` relative imports.
- Max 150 lines per file.
- Always use braces after `if` conditions.
- No hardcoded colors - always use theme palette.
- Add blank lines between logical sections within functions for readability.
- Use `Readonly<Props>` for component props to prevent mutation.
- Always extract component props to a named `interface` — never inline prop types.
- Never use the `!` non-null assertion operator.
- No local barrel files (`index.ts` that re-exports) — import directly from the source file (e.g. `import { Foo } from './Foo/Foo'` not `import { Foo } from './Foo'`).

## React components

- Use named function declarations with explicit return types: `export function MyComponent(): JSX.Element {`
- Never use `const MyComponent = () =>` or `React.FC` or `FunctionComponent`
- Never use `ReactElement` as the return type — use `JSX.Element`

## Styling

- **Never use inline `sx` props** on MUI components
- All styles go in a separate `styles.ts` file next to the component
- The export is **always** called `sx` — never `styles`, `fooStyles`, `barStyles`, or any other name
- Type it as `Record<string, SxProps<Theme>>`
- Each component that needs styles gets its own `styles.ts` in its own directory (e.g. `Page/Page.tsx` + `Page/styles.ts`)
- Use theme-aware functions: `(theme: Theme) => theme.palette.primary.main`
- No hardcoded colours — always use `theme.palette`

```ts
// BAD — inline sx
<Container sx={{ py: 4, backgroundColor: '#fff' }}>
<Box sx={{ display: 'flex', gap: 2 }}>

// BAD — wrong export name
export const containerStyles = { ... };
export const styles = { ... };
export const appStyles = { ... };

// GOOD — styles.ts
import type { SxProps, Theme } from '@mui/material/styles';

export const sx: Record<string, SxProps<Theme>> = {
  container: {
    py: 4,
    backgroundColor: (theme) => theme.palette.background.default,
  },
  layout: {
    display: 'flex',
    gap: 2,
  },
};

// GOOD — Component.tsx
import { sx } from './styles';
<Container sx={sx.container}>
<Box sx={sx.layout}>
```

## Routing

- Top-level page components are lazy loaded with `const Page = lazy(() => import('~/pages/Page/Page'))`
- Route definitions live in a dedicated routes file, not scattered in App.tsx
- Use `react-router` `Route` / `Routes` components
- Page layout wrapper (`Page`) is a route-level `element`, pages render inside via `Outlet` or as child routes

## Testing

- Tests are colocated with source files: `foo.ts` → `foo.test.ts`, `Bar.tsx` → `Bar.test.tsx`
- No separate `test/` directories
- Shared vitest config lives at root `vitest.shared.ts`

## Output expectations

- Keep diffs minimal.
- If you change behavior, update any docs/tests that describe it.
- Never add "Generated with Claude Code" to PR descriptions or anywhere else.

## Commands

- Install: `pnpm install`
- Run: `pnpm run scan`
- Test: `pnpm test` (if no tests exist, add a single smoke test and wire this command)

## Error handling — never swallow, always context

Errors are signals. If something fails, the developer needs to know what was being attempted, where, and why. Silent failures hide bugs and waste debugging time.

### Never use empty catch blocks

```ts
// BAD — error disappears, nobody knows what happened
try {
  await fetchMatchData(matchId);
} catch (error) {}

// BAD — swallows error and returns misleading default
try {
  const data = await fetchMatchData(matchId);
  return data;
} catch (_error) {
  return null;
}

// GOOD — log context and rethrow
try {
  await fetchMatchData(matchId);
} catch (error) {
  console.error('fetchMatchData failed', { matchId }, error);
  throw error;
}
```

### Prefer letting errors propagate

Only catch when you can add value — retry, structured error, or meaningful recovery. If you're just going to rethrow unchanged, don't catch at all.

```ts
// BAD — catch adds nothing
try {
  return await getLeagueTable(leagueId);
} catch (error) {
  throw error;
}

// GOOD — just let it propagate
return await getLeagueTable(leagueId);

// GOOD — catch adds context that callers don't have
try {
  return await getLeagueTable(leagueId);
} catch (error) {
  throw new Error(`failed loading table for league ${leagueId}`, { cause: error });
}
```

### Always include context in error messages

A bare `console.error(error)` is nearly useless. Include what was being attempted and the relevant identifiers.

```ts
// BAD — no context
console.error(error);
console.error('something went wrong');

// GOOD — what, where, and the original error
console.error('failed to fetch fixtures', { leagueId, season }, error);
console.error('parseMatchStats: invalid response shape', { matchId }, error);
```

### Async code — never leave promises unhandled

Every promise must have error handling. Unhandled rejections crash the process or silently disappear.

```ts
// BAD — fire and forget
fetchMatchData(matchId);
void fetchMatchData(matchId);

// BAD — .catch that swallows
fetchMatchData(matchId).catch(() => {});

// GOOD — handle or await
await fetchMatchData(matchId);

// GOOD — explicit catch with logging if fire-and-forget is intentional
fetchMatchData(matchId).catch((error) => {
  console.error('background fetch failed', { matchId }, error);
});
```

### Don't catch to recover — let it crash

If an operation fails, it failed. Don't catch and return a fallback that hides the failure. The caller needs to know something went wrong.

```ts
// BAD — silently substitutes a fallback, caller thinks everything worked
try {
  return await fetchMatchData(matchId);
} catch {
  return defaultMatchData;
}

// BAD — slightly better but still hides the failure from the caller
try {
  return await fetchMatchData(matchId);
} catch (error) {
  console.warn('using fallback', { matchId }, error);
  return defaultMatchData;
}

// GOOD — let the error propagate, handle it at the top level
return await fetchMatchData(matchId);
```

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

## Testing — test behaviour, not code

Tests must verify what a user sees and does, not internal implementation details. A test that calls `onChange` and asserts it was called proves nothing. A test that renders a full component tree, populates it with data, and asserts the user sees the correct output in the DOM is useful.

### Always render through the real component tree

- Never test components in isolation with mock props when they exist inside a larger tree.
- Render the way the app renders — with real providers, real data flow.

### Assert what the user sees

```ts
// BAD — testing internal wiring, proves nothing
expect(props.onChange).toHaveBeenCalledWith('Arsenal');

// GOOD — testing what the user actually sees
expect(screen.getByRole('cell', { name: 'Arsenal' })).toBeInTheDocument();
```

### Interact like a user

```ts
// BAD — calling handlers directly
fireEvent.change(input, { target: { value: 'foo' } });

// GOOD — simulating real user actions
const user = userEvent.setup();
await user.click(screen.getByRole('button', { name: 'Select' }));
const option = await screen.findByRole('option', { name: 'Arsenal' });
await user.click(option);
expect(screen.getByText('Arsenal')).toBeInTheDocument();
```

### Use real data structures

- Use real data shapes from the API, not hand-crafted fragments.
- If testing existing data display, pass it through the same path the app uses.

## When unsure

Stop and ask for clarification before coding.

# Code Modification Policy

- Do NOT modify code unless explicitly asked
- When the user complains about something, ask if they want it changed
- Do not add features that weren't requested
- Do not add code comments
