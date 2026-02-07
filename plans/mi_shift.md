# ML Career Focus

**Target role:** AI Engineer
**Deadline:** October 2025

## Key

Build something real, not demoware.

**Domain:** Football/soccer analytics
**Focus:** Pre-match insights, score predictions
**Data source:** Understat (xG focused)
**Scope:** Full Premier League, starting fresh

**Data timeframe:**
- Training: 2025-26 season matches played so far (Aug 2025 - Feb 2026)
- Testing/Prediction: Upcoming 2025-26 matches (Feb 2026 onwards)

**Rationale:** Transfer windows (summer 2025, January 2026) change team strength. Must use current season data only, not outdated rosters from 2024-25.

## Architecture

### Packages

| Package | Language | Purpose |
|---------|----------|---------|
| etl | TypeScript/Node.js | Scrape Understat data |
| ml | Python | Train model |
| api | Python FastAPI | Serve predictions |
| frontend | React + TypeScript | UI and visualizations |

## Data requirements

### Core (must have)

| Field | Description |
|-------|-------------|
| date | Match date |
| season | e.g. 2023-24 |
| home_team | Home team name |
| away_team | Away team name |
| home_goals | Goals scored by home team |
| away_goals | Goals scored by away team |
| home_xg | Expected goals for home team |
| away_xg | Expected goals for away team |
| home_shots | Total shots by home team |
| away_shots | Total shots by away team |
| home_shots_on_target | Shots on target by home team |
| away_shots_on_target | Shots on target by away team |
| home_deep | Deep completions by home team |
| away_deep | Deep completions by away team |
| home_ppda | Pressing intensity (PPDA) by home team |
| away_ppda | Pressing intensity (PPDA) by away team |
| home_xpts | Expected points for home team |
| away_xpts | Expected points for away team |
| matchweek | Fixture round in the season |

### Derived (calculated from core)

| Field | Description |
|-------|-------------|
| home_shot_conversion | home_goals / home_shots |
| away_shot_conversion | away_goals / away_shots |
| home_shots_on_target_pct | home_shots_on_target / home_shots |
| away_shots_on_target_pct | away_shots_on_target / away_shots |

### Phase 2 (adds predictive value)

| Field | Description |
|-------|-------------|
| shots | Shot-level data with xG per shot |
| player_xg | Per-player xG contributions |

### Out of scope (for now)

- Referee data
- Weather conditions
- Attendance figures
- Betting odds

### ETL Verification

Verify scraped data matches Understat source.

#### Understat data structure

League page (`https://understat.com/league/EPL/2025`) embeds `datesData` (380 entries, one per fixture) as a global JS variable. Each entry has: `id`, `isResult`, `h` (id/title/short_title), `a`, `goals` (h/a), `xG` (h/a), `datetime`, `forecast` (w/d/l).

Match page (`https://understat.com/match/{id}`) embeds `match_info` as hex-encoded JSON in a script tag. Fields:

| Understat field | Plan field | Type |
|-----------------|------------|------|
| `id` | match_id | string |
| `date` | date | string (YYYY-MM-DD HH:MM:SS) |
| `season` | season | string (start year, e.g. "2025") |
| `team_h` | home_team | string |
| `team_a` | away_team | string |
| `h_goals` | home_goals | string (numeric) |
| `a_goals` | away_goals | string (numeric) |
| `h_xg` | home_xg | string (float) |
| `a_xg` | away_xg | string (float) |
| `h_shot` | home_shots | string (numeric) |
| `a_shot` | away_shots | string (numeric) |
| `h_shotOnTarget` | home_shots_on_target | string (numeric) |
| `a_shotOnTarget` | away_shots_on_target | string (numeric) |
| `h_deep` | home_deep | string (numeric) |
| `a_deep` | away_deep | string (numeric) |
| `h_ppda` | home_ppda | string (float) |
| `a_ppda` | away_ppda | string (float) |
| `h_w` | home_win_prob | string (float) |
| `h_d` | draw_prob | string (float) |
| `h_l` | away_win_prob | string (float) |

**xPTS is not in `match_info`** — it's computed client-side: `xPTS = 3 * h_w + 1 * h_d` (home), `xPTS = 3 * h_l + 1 * h_d` (away).

**matchweek** is not in `match_info` — must be derived from fixture order or `datesData`.

Also available on match pages: `shotsData` (per-shot xG, player, coordinates) and `rostersData` (lineups).

#### Test fixture matches (10)

Verify each by clicking Stats tab on the Understat page.

| # | Match | Score | xG | Link |
|---|-------|-------|----|------|
| 1 | Aston Villa vs Newcastle | 0-0 | 0.32 - 1.40 | https://understat.com/match/28779 |
| 2 | Chelsea vs Crystal Palace | 0-0 | 1.37 - 1.03 | https://understat.com/match/28784 |
| 3 | Liverpool vs Bournemouth | 4-2 | 2.33 - 1.57 | https://understat.com/match/28778 |
| 4 | West Ham vs Chelsea | 1-5 | 0.98 - 3.95 | https://understat.com/match/28788 |
| 5 | Arsenal vs Leeds | 5-0 | 2.74 - 0.16 | https://understat.com/match/28793 |
| 6 | Brighton vs Fulham | 1-1 | 1.44 - 0.90 | https://understat.com/match/28780 |
| 7 | Nott. Forest vs Crystal Palace | 1-1 | 0.99 - 1.65 | https://understat.com/match/29013 |
| 8 | Tottenham vs Man City | 2-2 | 1.50 - 2.04 | https://understat.com/match/29016 |
| 9 | Sunderland vs Burnley | 3-0 | 1.89 - 0.13 | https://understat.com/match/29011 |
| 10 | Brentford vs Burnley | 3-1 | 3.72 - 0.87 | https://understat.com/match/28899 |

Edge cases covered: two 0-0 draws, two 1-1 draws, high-scoring (5-0, 1-5, 4-2), early season, mid season, late season.

#### Test fixtures (packages/etl/test/fixtures/)

Store as `expected-matches.json` using the raw `match_info` shape from Understat.

#### Automated verification

```typescript
const scrapedMatch = await scrapeMatch(matchId);
const expectedMatch = fixtures.find(m => m.id === matchId);
expect(scrapedMatch).toEqual(expectedMatch);
```

#### Schema validation

Use Zod to validate correct types and required fields. Fail fast if schema invalid.

#### Acceptance criteria

- All 10 test fixtures pass
- Zero schema validation errors

## Model approach: Monte Carlo simulation

### How it works

1. Estimate expected goals for each team from xG history, form, home/away strength
2. Model each team's goals as a Poisson distribution
3. Simulate the match N times (e.g. 10,000)
4. Count home wins, draws, away wins across simulations to get probabilities

### Phase 1 inputs

- Team xG averages (attack/defense)
- Recent form (last 5 matches: xG, shots, shots on target)
- Home advantage adjustment
- xG over/underperformance (actual goals vs xG)
- Shots on target percentage
- PPDA (pressing intensity)

### Phase 2 inputs

- Shot-level simulation (simulate individual shots using per-shot xG)
- Player-level xG aggregation
- Head-to-head history

## Evaluation

### Validation strategy

- Time-based split: train on seasons 2020-2023, test on 2024
- No data leakage: form calculated only from past matches

### Metrics

| Metric | Purpose | Target |
|--------|---------|--------|
| Accuracy | Overall correctness | >46% (home-win baseline) |
| Brier score | Probability calibration | <0.25 |
| Log loss | Confidence quality | <1.0 |
| ROC-AUC | Ranking ability | >0.55 |

### Baselines

- Random (33% each outcome)
- Always predict home win (~46%)
- Predict based on league position

### Output

- Confusion matrix
- Metrics report
- Predictions vs actuals table
- Performance over time chart

## Frontend

### Architecture

- React + TypeScript
- MUI (Material UI) component library
- FastAPI backend (Python) serving REST endpoints
- Communication via fetch/axios

### Match Predictor page (build first)

#### States

1. **Empty** — no teams selected, predict button disabled
2. **Ready** — both teams selected, predict button enabled
3. **Simulating** — live simulation visualisation (see below)
4. **Result** — final prediction displayed

#### Simulation visualisation (Simulating state)

The API streams simulation progress via SSE (Server-Sent Events) or the API returns quickly and we animate client-side using the final data. Either way, the user sees the simulation "running":

- **Progress bar**: MUI `LinearProgress` with label — "Simulating... 12%" ticking up to 100%
- **Counter**: "1,247 / 10,000 matches" beneath the progress bar
- **Live probability bars**: Home Win / Draw / Away Win bars that shift and settle as simulations accumulate (start unstable, converge to final values)
- **Live scoreline tally**: The top scorelines table fills in and reorders as counts come in — scores jump up/down the ranking before settling

This gives the feel of watching 10,000 matches play out. The animation runs for ~2-3 seconds regardless of actual API speed (buffer the result, animate the reveal).

**Implementation approach**: API returns the full result in one response. The frontend animates by interpolating from uniform (33/33/33) to the final probabilities over ~2s using `requestAnimationFrame`. The counter ticks from 0 to 10,000 in sync. No SSE needed for v1.

#### Team picker

- MUI `Autocomplete` component (`@mui/material/Autocomplete`)
- Data source: `GET /teams` returns `{ id: string, name: string }[]`
- Two instances: "Home team" and "Away team"
- `disableClearable: false` (user can reset)
- `freeSolo: false` — select only, no free text input
- Away picker filters out the selected home team (can't play yourself)
- Options sorted alphabetically
- Shows team name as label

#### Prototype

See `plans/match-predictor-prototype.html` — a standalone HTML prototype with light/dark mode, all 4 states (empty, ready, simulating, result), animated simulation with converging probability bars, scoreline reveal, and mock data. Open in browser to preview.

#### Layout

```
┌─────────────────────────────────────────────┐
│  Match Predictor                            │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Home team [v]   │  │ Away team [v]   │  │
│  └─────────────────┘  └─────────────────┘  │
│                                             │
│           [ Predict ]                       │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Win / Draw / Lose probability bars │    │
│  │  (horizontal stacked bar or 3 arcs) │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │  Top 10 scorelines table            │    │
│  │  Rank | Score | Probability         │    │
│  │  1    | 1-0   | 14.2%              │    │
│  │  2    | 2-1   | 11.8%              │    │
│  │  ...                                │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

#### Prediction output

**Outcome probabilities:**
- Three values: Home win %, Draw %, Away win % (must sum to 100)
- Display as horizontal stacked bar (Recharts `BarChart` or plain MUI)
- Colour-coded: home win / draw / away win
- Show percentage labels on each segment

**Top scorelines:**
- MUI `Table` with columns: Rank, Score (e.g. "2-1"), Probability (e.g. "14.2%")
- 10 rows, sorted by probability descending
- Score column shows "Home - Away" format

#### API contract

```
POST /predict
Request:  { home_team_id: string, away_team_id: string }
Response: {
  home_win: number,    // 0-1
  draw: number,        // 0-1
  away_win: number,    // 0-1
  scorelines: { home_goals: number, away_goals: number, probability: number }[]
}

GET /teams
Response: { id: string, name: string }[]
```

### Future pages

| Page | Purpose |
|------|---------|
| Team Analysis | View team stats, form, xG trends |
| Model Performance | Display evaluation metrics, accuracy over time |

### Visualizations

| Chart | Data | Library |
|-------|------|---------|
| Form line chart | Last 10 matches: points, goals, xG | Recharts |
| xG trend | xG vs actual goals over season | Recharts |
| Prediction bars | Win/draw/lose probabilities | Recharts |
| Head-to-head | Historical results between two teams | Table + bars |
| Performance over time | Model accuracy by matchweek | Recharts |

### API Endpoints

- `POST /predict` - Get match prediction
- `GET /teams/{team}/stats` - Team statistics and form
- `GET /teams/{team}/xg-trend` - xG data over time
- `GET /model/metrics` - Model evaluation metrics

## Next action

Fetch Understat Premier League data: explore their site structure, find or write a scraper, pull match data with xG into packages/etl.
