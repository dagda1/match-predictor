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

Verify scraped data matches Understat source:

**Test fixtures (packages/etl/test/fixtures/):**
- Manually record 10 known matches from Understat with all fields
- Include edge cases: high-scoring, 0-0 draws, different seasons
- Store as `expected-matches.json`

**Automated verification:**
```typescript
// Test: scraper produces correct data
const scrapedMatch = await scrapeMatch(matchId);
const expectedMatch = fixtures.find(m => m.id === matchId);
expect(scrapedMatch).toEqual(expectedMatch);
```

**Manual spot checks:**
- After each scrape run, randomly select 5 matches
- Open Understat page for each
- Verify: date, teams, goals, xG values match exactly
- Document in `verification-log.md`

**Schema validation:**
- Use Zod to ensure correct types and required fields
- Fail fast if schema invalid

**Acceptance criteria:**
- All 10 test fixtures pass
- 5/5 manual spot checks match Understat exactly
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
- FastAPI backend (Python) serving REST endpoints
- Communication via fetch/axios

### Pages

| Page | Purpose |
|------|---------|
| Match Predictor | Select teams, get win/draw/lose probabilities |
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
