# ML Career Focus

**Target role:** AI Engineer
**Deadline:** October 2025

## Key

Build something real, not demoware.

**Domain:** Football/soccer analytics
**Focus:** Pre-match insights, score predictions
**Data source:** Understat (xG focused)
**Scope:** Full Premier League, starting fresh

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
| matchweek | Fixture round in the season |

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

## Model features

### Phase 1

- Team strength ratings (attack/defense learned from historical data)
- Recent form (last 5 matches: points, goals, xG trend)
- Home advantage
- xG over/underperformance

### Phase 2

- Player-level xG aggregation
- Shot quality trends
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
