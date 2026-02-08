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
- 2024-25 season (380 matches, complete)
- 2025-26 season matches played so far (Aug 2025 - Feb 2026, ~240 matches)
- Testing/Prediction: Upcoming 2025-26 matches (Feb 2026 onwards)

**Rationale:** Two seasons gives ~620 matches for training. 2024-25 adds sample size; 2025-26 captures current form and post-transfer-window team strength.

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
| season | e.g. 2025 |
| homeTeam | Home team name |
| awayTeam | Away team name |
| homeGoals | Goals scored by home team |
| awayGoals | Goals scored by away team |
| homeXg | Expected goals for home team |
| awayXg | Expected goals for away team |
| homeShots | Total shots by home team |
| awayShots | Total shots by away team |
| homeShotsOnTarget | Shots on target by home team |
| awayShotsOnTarget | Shots on target by away team |
| homeDeep | Deep completions by home team |
| awayDeep | Deep completions by away team |
| homePpda | Pressing intensity (PPDA) by home team |
| awayPpda | Pressing intensity (PPDA) by away team |
| homeWinProb | Home win probability |
| drawProb | Draw probability |
| awayWinProb | Away win probability |

### Derived (calculated from core)

| Field | Description |
|-------|-------------|
| homeShotConversion | homeGoals / homeShots |
| awayShotConversion | awayGoals / awayShots |
| homeShotsOnTargetPct | homeShotsOnTarget / homeShots |
| awayShotsOnTargetPct | awayShotsOnTarget / awayShots |
| homeXpts | 3 * homeWinProb + 1 * drawProb |
| awayXpts | 3 * awayWinProb + 1 * drawProb |

### Phase 2 (adds predictive value)

| Field | Description |
|-------|-------------|
| shots | Shot-level data with xG per shot |
| playerXg | Per-player xG contributions |

### Out of scope (for now)

- Referee data
- Weather conditions
- Attendance figures
- Betting odds

### ETL Verification

Verify scraped data matches Understat source.

#### Understat data structure

League data is fetched via AJAX: `GET https://understat.com/getLeagueData/EPL/{season}` (requires `X-Requested-With: XMLHttpRequest` header). Returns JSON with `dates` (380 entries), `teams`, and `players`. Each `dates` entry has: `id`, `isResult`, `h` (id/title/short_title), `a`, `goals` (h/a), `xG` (h/a), `datetime`, `forecast` (w/d/l).

Match page (`https://understat.com/match/{id}`) embeds `match_info` as hex-escaped JSON in a `JSON.parse()` call inside a script tag. Decode `\xHH` escapes then parse. Fields:

| Understat field | Our field | Type |
|-----------------|-----------|------|
| `id` | id | string |
| `date` | date | string (YYYY-MM-DD HH:MM:SS) |
| `season` | season | string (start year, e.g. "2025") |
| `team_h` | homeTeam | string |
| `team_a` | awayTeam | string |
| `h_goals` | homeGoals | string (numeric) |
| `a_goals` | awayGoals | string (numeric) |
| `h_xg` | homeXg | string (float) |
| `a_xg` | awayXg | string (float) |
| `h_shot` | homeShots | string (numeric) |
| `a_shot` | awayShots | string (numeric) |
| `h_shotOnTarget` | homeShotsOnTarget | string (numeric) |
| `a_shotOnTarget` | awayShotsOnTarget | string (numeric) |
| `h_deep` | homeDeep | string (numeric) |
| `a_deep` | awayDeep | string (numeric) |
| `h_ppda` | homePpda | string (float) |
| `a_ppda` | awayPpda | string (float) |
| `h_w` | homeWinProb | string (float) |
| `h_d` | drawProb | string (float) |
| `h_l` | awayWinProb | string (float) |

**xPTS** is derived: `xPTS = 3 * winProb + 1 * drawProb`.

**matchweek** is not in `match_info` — must be derived from fixture order or league `dates` data.

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

#### Test fixtures (packages/etl/src/)

Colocated with test file as `expected-matches.json` using our camelCase `MatchInfo` shape (all stats verified).

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

### Data persistence

JSON files in `packages/etl/data/`, one file per season:

```
packages/etl/data/
  matches-2024.json   (2024-25 season, 380 matches)
  matches-2025.json   (2025-26 season, ~240 matches and growing)
```

Each file is an array of `MatchInfo` objects (camelCase, same shape as scraper output). Files are committed to git to avoid re-scraping. Re-scrape via `pnpm --filter @match-predictor/etl fetch-data`.

The `fetch-data` script is incremental:
1. Reads existing JSON to find the max `date` already scraped
2. Hits the league API (`/getLeagueData/EPL/{season}`) and filters for matches after that date
3. Only scrapes new matches with `scrapeMatch`
4. Appends to the existing season file

First run scrapes everything. Subsequent runs only fetch new fixtures.

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

- Train on both seasons (621 matches), weight recent matches higher (e.g. exponential decay)
- Validate with rolling time-based cross-validation: for each matchweek, predict using only past data
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

### Navigation

TopNav (`packages/theme`) currently has a static title and theme switcher. Needs nav links added.

| Path | Nav label | Page component |
|------|-----------|----------------|
| `/` | Predictor | Match Predictor — select two teams, get predictions |
| `/results` | Results | Matchweek Review — model predictions vs actual results |

TopNav changes:
- Add nav links ("Predictor", "Results") to the left of the theme switcher
- Active link highlighted
- Links use `react-router` `Link` or `NavLink`
- TopNav is in the theme package so it needs to accept routes as props or children (keep it generic, don't hardcode routes in the shared package)

Routes (`apps/frontend/src/routes/AppRoutes.tsx`):
- `/` → lazy-loaded `Home` (Match Predictor)
- `/results` → lazy-loaded `Results` (Matchweek Review)
- Both wrapped by `Page` layout (which includes TopNav + MaxWidthContainer + Outlet)

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
Request:  { homeTeamId: string, awayTeamId: string }
Response: {
  ml: {
    homeWin: number,    // 0-1
    draw: number,       // 0-1
    awayWin: number,    // 0-1
    scorelines: { homeGoals: number, awayGoals: number, probability: number }[]
  },
  poisson: {
    homeWin: number,
    draw: number,
    awayWin: number,
    scorelines: { homeGoals: number, awayGoals: number, probability: number }[],
    homeLambda: number,
    awayLambda: number,
  }
}

GET /teams
Response: { id: string, name: string }[]
```

### Matchweek Review page

Compare model predictions against actual results for a matchweek (a 7-day window of fixtures).

#### Purpose

Show how the model performed on real matches. This is the credibility test — did the model's probabilities reflect reality? Lets you browse week by week and see where the model got it right or wrong.

#### Matchweek definition

A matchweek runs Saturday 00:00 to Friday 23:59 (covers Saturday 3pm kickoffs through Monday night football). First matchweek starts Saturday 2nd February 2026. Week numbers are sequential from that date.

The model predicts each match using only data available before kick-off (no leakage). After the matches are played, we compare predicted outcome against actual outcome.

#### Routes

| Route | Page | Purpose |
|-------|------|---------|
| `/results` | Matchweek list | All matchweeks with summary stats, click to drill in |
| `/results/:week` | Matchweek detail | Per-match predictions vs actuals for one week |

#### Matchweek list page (`/results`)

Clickable table of all matchweeks, most recent first.

```
┌──────────────────────────────────────────────────────────┐
│  Results                                                  │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Week    │ Dates              │ Matches │ ML    │ Poi  │ │
│  │ Week 1  │ 2 Feb – 8 Feb     │ 10      │ 5/10  │ 4/10 │ │
│  │ Week 2  │ 9 Feb – 15 Feb    │ 8       │ 6/8   │ 5/8  │ │
│  │ Week 3  │ 16 Feb – 22 Feb   │ 10      │ 4/10  │ 6/10 │ │
│  │ ...                                                   │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

#### Matchweek detail page (`/results/:week`)

Back link to list. Each match is a card showing the actual result and a mini version of the predictor output (same ML + Poisson probability bars, compact).

```
┌──────────────────────────────────────────────────────────┐
│  ← Back to results                                        │
│                                                           │
│  Week 1 · 2 Feb – 8 Feb 2026 · 10 matches                │
│  ML 5/10 (50%) · Poisson 4/10 (40%)                      │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Liverpool 2 – 1 Man City              ML ✓  Poi ✗  │ │
│  │  ML predicted: 2–1 14.2%   Poisson predicted: 1–1 13.4% │
│  │                                                       │ │
│  │  ML Model               │  Poisson Baseline           │ │
│  │  Liverpool win ██████ 48.2% │  Liverpool win ███ 29.9%│ │
│  │  Draw         ███ 24.1%     │  Draw         ███ 26.3%│ │
│  │  Man City win ████ 27.7%    │  Man City win █████43.8%│ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Arsenal 1 – 0 Aston Villa             ML ✓  Poi ✓  │ │
│  │  ML predicted: 1–0 15.8%   Poisson predicted: 2–1 11.8% │
│  │                                                       │ │
│  │  ML Model               │  Poisson Baseline           │ │
│  │  Arsenal win  ███████ 55.1% │  Arsenal win  █████43.8%│ │
│  │  Draw         ███ 22.4%     │  Draw         ████ 28.1%│ │
│  │  Villa win    ███ 22.5%     │  Villa win    ████ 28.1%│ │
│  └──────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Chelsea 1 – 1 Tottenham               ML ✗  Poi ✗  │ │
│  │  ML predicted: 2–1 11.2%   Poisson predicted: 1–1 12.8% │
│  │                                                       │ │
│  │  ML Model               │  Poisson Baseline           │ │
│  │  Chelsea win  █████ 42.3%   │  Chelsea win  ████ 35.2%│ │
│  │  Draw         ███ 24.1%     │  Draw         ████ 29.5%│ │
│  │  Spurs win    ████ 33.6%    │  Spurs win    █████35.3%│ │
│  └──────────────────────────────────────────────────────┘ │
│  ...                                                      │
└──────────────────────────────────────────────────────────┘
```

Each match card shows:
- Actual score and team names as the header
- ML ✓/✗ and Poisson ✓/✗ top-right — instant glance at who got it right
- Top predicted scoreline per model with probability (e.g. "ML predicted: 2–1 14.2%" / "Poisson predicted: 1–1 13.4%")
- Mini probability bars for both models side by side (reuses `ModelProbBars` + `ProbBar` components from the predictor page in compact mode)
- Card border/tint: green if both correct, red if both wrong, neutral if they disagree

#### UI fields per match row

| Field | Source | Purpose |
|-------|--------|---------|
| homeTeam | match data | Row label |
| awayTeam | match data | Row label |
| date | match data | Sort order within week |
| actualHomeGoals | match data | Show actual score |
| actualAwayGoals | match data | Show actual score |
| actualOutcome | derived (home/draw/away) | Compare against predictions |
| mlHomeWin | ML model | Probability percentage |
| mlDraw | ML model | Probability percentage |
| mlAwayWin | ML model | Probability percentage |
| mlPredictedOutcome | derived (highest prob) | ✓/✗ indicator |
| mlTopScore | ML model (rank 1 scoreline) | Top predicted scoreline + probability |
| mlCorrect | derived | Green/red row tint |
| poissonHomeWin | Poisson | Probability percentage |
| poissonDraw | Poisson | Probability percentage |
| poissonAwayWin | Poisson | Probability percentage |
| poissonPredictedOutcome | derived (highest prob) | ✓/✗ indicator |
| poissonTopScore | Poisson model (rank 1 scoreline) | Top predicted scoreline + probability |
| poissonCorrect | derived | Green/red row tint |
| poissonHomeLambda | Poisson | Show the xG inputs |
| poissonAwayLambda | Poisson | Show the xG inputs |

#### Matchweek summary fields

| Field | Purpose |
|-------|---------|
| week | Identifier |
| startDate | Week picker label |
| endDate | Week picker label |
| matchCount | "10 matches" |
| mlCorrect | "ML 5/10 (50%)" |
| poissonCorrect | "Poisson 4/10 (40%)" |

#### API

```
GET /matchweeks
Response: {
  week: number,
  startDate: string,
  endDate: string,
  matchCount: number,
  mlCorrect: number,
  poissonCorrect: number,
}[]

GET /matchweeks/{week}
Response: {
  week: number,
  startDate: string,
  endDate: string,
  matches: {
    homeTeam: string,
    awayTeam: string,
    date: string,
    actualHomeGoals: number,
    actualAwayGoals: number,
    actualOutcome: "home" | "draw" | "away",
    ml: { homeWin: number, draw: number, awayWin: number, predictedOutcome: "home" | "draw" | "away", correct: boolean, topScore: { homeGoals: number, awayGoals: number, probability: number } },
    poisson: { homeWin: number, draw: number, awayWin: number, predictedOutcome: "home" | "draw" | "away", correct: boolean, homeLambda: number, awayLambda: number, topScore: { homeGoals: number, awayGoals: number, probability: number } },
  }[],
  summary: {
    mlCorrect: number,
    mlTotal: number,
    poissonCorrect: number,
    poissonTotal: number,
  }
}
```

#### Data pipeline

Predictions are pre-computed at import time, not on the fly. The `fetch-data` script does three things:

1. **Scrape** — incrementally fetch new completed matches from Understat (only matches after the max date in existing JSON)
2. **Predict** — for each new match, run both models using only data available before kick-off (`date < match_date`), producing probabilities and predicted outcome
3. **Save** — append match result + predictions to a pre-computed predictions file

```
packages/etl/data/
  matches-2024.json        # raw match data (2024-25 season)
  matches-2025.json        # raw match data (2025-26 season)
  predictions-2025.json    # pre-computed: actual result + ML + Poisson per match
```

The predictions file is an array of objects matching the matchweek detail `matches[]` shape from the API contract above. The `/matchweeks` endpoint just reads this file and groups by Saturday-to-Friday windows — no model execution at request time.

Command: `pnpm --filter @match-predictor/etl fetch-data` (scrapes + predicts + saves in one step).

#### Prediction integrity

The key constraint: predictions must use only data from before the match. The existing code handles this — `_rolling_stats` filters `df["date"] < before_date` and Poisson's `_team_xg` can be filtered the same way.

For the ML model, honest evaluation requires either:
- **Option A:** Retrain per matchweek (train only on matches before that week, predict, compare) — correct but slow
- **Option B:** Use TimeSeriesSplit CV predictions from `evaluate()` — already out-of-sample, just need to preserve the match-to-prediction mapping

Option B is preferred for the initial implementation. Extend `evaluate()` to return per-match predictions alongside overall metrics.

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

## Experiment tracking (MLflow)

Every model change is an experiment measured against a baseline (H_0).

### Setup

- `pip install mlflow` (added to ml package dependencies)
- Data stored locally in `mlruns/` (gitignored)
- View results with `mlflow ui` (default port 5000)

### What gets logged per run

| Item | Example |
|------|---------|
| Description | "Added xG std dev features" |
| Feature list | `["homeXgFor", "homeXgAgainst", ..., "homeXgStdDev"]` |
| Hyperparameters | `n_estimators=200, max_depth=4, learning_rate=0.1` |
| Overall metrics | accuracy, brier score, log loss, ROC-AUC |
| Per-match predictions | For every match: predicted outcome + probabilities vs actual outcome |

### Workflow

1. Log the current 15-feature model as H_0 (baseline run)
2. Make a change (add features, tune hyperparameters, try a different algorithm)
3. Log the new run
4. Compare against H_0 in MLflow UI — did metrics improve?
5. Matchweek review shows which specific matches flipped right/wrong
6. If the change doesn't beat H_0, reject it and move on

### Planned model experiments

| Experiment | Hypothesis |
|-----------|-----------|
| Add xG std dev (volatility) | Volatile teams produce more extreme results; SD features let the model distinguish them |
| Recency weighting | Recent form matters more than old results; exponential decay on rolling window |
| Per-team home advantage | Replace league-wide home advantage with team-specific home/away xG ratios |
| XGBoost / LightGBM | Gradient boosting alternatives may handle the feature space better |

### Deployment path

MLflow stores data locally by default (SQLite + flat files). Scales without code changes:
- SQLite → Postgres (swap connection string)
- Local artifacts → S3/GCS (swap path)
- Local UI → hosted MLflow server (one env var)

## Dev scripts

- `pnpm dev` — starts API (port 4400) + frontend (port 3300) concurrently
- `pnpm start:api` — API only
- `pnpm start:frontend` — frontend only
- `pnpm --filter @match-predictor/etl fetch-data` — incremental data scrape
- API Swagger docs at http://localhost:4400/docs

## Progress

- [x] ETL scraper (`scrapeMatch`, `scrapeLeague`, Zod schema, 20 passing tests)
- [x] Data fetched: 380 matches (2024-25) + 241 matches (2025-26) = 621 total
- [x] Incremental fetch-data script (only scrapes matches after max date in existing JSON)
- [x] Frontend scaffold (App, routing, Page layout, TopNav, theme switching)
- [x] Python ML package (`packages/ml`) — GradientBoostingClassifier, 15 features, TimeSeriesSplit CV
- [x] FastAPI (`packages/api`) — `/teams`, `/predict`, `/metrics` endpoints
- [x] Poisson baseline model (`poisson_baseline.py`) — raw xG averages, no hardcoded multipliers, for comparison
- [ ] Improve model (currently 40.9% accuracy vs 41.5% baseline — underperforming)
- [ ] Add recency weighting to ML model (current form not reflected, e.g. City's decline)
- [ ] Fix home advantage bias (62% home win for Liverpool vs City is too high)
- [ ] Compare ML model vs Poisson baseline predictions side by side
- [ ] Frontend Match Predictor page (prototype exists at `plans/match-predictor-prototype.html`)

### Current model metrics

| Metric | Value | Target |
|--------|-------|--------|
| Accuracy | 0.409 | >0.46 |
| Brier score | 0.304 | <0.25 |
| Log loss | 2.190 | <1.0 |
| ROC-AUC | 0.560 | >0.55 |
| Baseline (always home) | 0.415 | — |

## Next action

Improve the model to beat the baseline:
1. Add recency weighting so current form matters more than old results
2. Fix the home advantage feature — it shouldn't apply a flat league-wide boost regardless of away team strength
3. Compare ML model vs Poisson baseline to see which produces more realistic predictions
4. Tune hyperparameters, try XGBoost/LightGBM
5. Then build the frontend Match Predictor page
