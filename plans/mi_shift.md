# ML Career Focus

**Target role:** AI Engineer
**Domain:** Football/soccer analytics — pre-match insights, score predictions
**Data source:** Understat (xG focused)

## Architecture

| Package | Language | Purpose |
|---------|----------|---------|
| etl | TypeScript/Node.js | Scrape Understat data |
| ml | Python | Train model, generate predictions |
| api | Python FastAPI | Serve predictions |
| frontend | React + TypeScript | UI and visualizations |

## Data

- 2024-25 season (380 matches) + 2025-26 season (~240+ matches)
- JSON files in `packages/etl/data/`: `matches-2024.json`, `matches-2025.json`, `predictions-2026.json`, `upcoming.json`
- `pnpm --filter @match-predictor/etl fetch-data` — incremental scrape + predict + save

## Model separation — non-negotiable

ML model and Poisson baseline are **completely separate prediction approaches**. They must never share prediction logic.

- **ML model** (`model.py`): GradientBoosting classifier for outcome probabilities and scorelines. No Poisson anywhere in the ML path.
- **Poisson baseline** (`poisson_baseline.py`): Raw xG averages as Poisson lambda parameters. Statistical baseline for comparison.

## Evaluation targets

| Metric | Current | Target |
|--------|---------|--------|
| Accuracy | 0.409 | >0.46 |
| Brier score | 0.304 | <0.25 |
| Log loss | 2.190 | <1.0 |
| ROC-AUC | 0.560 | >0.55 |
| Baseline (always home) | 0.415 | — |

## Frontend

### Pages

| Path | Page | Status |
|------|------|--------|
| `/` | Match Predictor — select two teams, get predictions | Done |
| `/results` | Results — model predictions vs actual results by week | Done |

### Results page

- Navigates by Monday-to-Sunday week windows
- API: `GET /results?startDate=...&endDate=...`
- Response includes `earlierMatchDate` / `laterMatchDate` (actual dates of nearest matches outside the window) for prev/next navigation
- Predictions are pre-computed at import time, not on the fly

### API endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /teams` | List all teams |
| `POST /predict` | Get ML + Poisson prediction for a matchup |
| `GET /metrics` | Model evaluation metrics |
| `GET /results` | Pre-computed predictions vs actuals by date range |

## Dev scripts

- `pnpm dev` — starts API (port 4400) + frontend (port 3300) concurrently
- `pnpm start:api` — API only
- `pnpm start:frontend` — frontend only
- `pnpm --filter @match-predictor/etl fetch-data` — incremental data scrape + predictions
- API Swagger docs at http://localhost:4400/docs

## Progress

- [x] ETL scraper (scrapeMatch, scrapeLeague, Zod schema, tests)
- [x] Data fetched: 380 + 240+ matches
- [x] Incremental fetch-data script
- [x] Frontend scaffold (routing, Page layout, TopNav, theme switching)
- [x] Python ML package — GradientBoosting, 15 features, TimeSeriesSplit CV
- [x] FastAPI — /teams, /predict, /metrics, /results endpoints
- [x] Poisson baseline model
- [x] Match Predictor page (team picker, simulation animation, probability bars, scorelines)
- [x] Results page (Monday-Sunday weeks, match day grouping, prev/next navigation, empty states)
- [x] Pre-computed predictions pipeline (predictions-2026.json + upcoming.json)
- [ ] Improve model (currently 40.9% accuracy vs 41.5% baseline — underperforming)

## How the ML model works — code map

### 1. Features — what the model sees (`features.py`)

- [ ] `_rolling_stats()` — takes a team + date, finds their last 5 matches, averages these stats:
  - [ ] xG for / against — expected goals scored and conceded
  - [ ] xG overperformance — actual goals minus xG (finishing above/below expectation)
  - [ ] Shot conversion — goals / total shots
  - [ ] Shots on target % — shots on target / total shots
  - [ ] PPDA — passes per defensive action (pressing intensity)
  - [ ] Deep completions — passes completed near the box
- [ ] `build_feature_row()` — calls `_rolling_stats()` for home team and away team, adds one global stat:
  - [ ] Home advantage — league-wide ratio of home xG to away xG
  - [ ] That gives 7 stats × 2 teams + 1 = **15 columns per match**
- [ ] `build_training_data()` — loops every match, calls `build_feature_row()` using only data from before that match (no future leakage), returns:
  - [ ] `X` — table of 15-column rows, one per match
  - [ ] `y_outcome` — "home", "draw", or "away" for each match
  - [ ] `y_scoreline` — "2-1", "0-0", etc. for each match

### 2. Training — how the model learns (`model.py` `train()`)

- [ ] Calls `build_training_data(df)` to get X, y_outcome, y_scoreline
- [ ] Creates a `GradientBoostingClassifier` (200 trees, max depth 4, learning rate 0.1)
  - [ ] Each tree splits on feature thresholds ("is homeXgFor > 1.8?")
  - [ ] Each new tree corrects the mistakes of all previous trees (boosting)
  - [ ] Learning rate 0.1 shrinks each tree's contribution to avoid overfitting
  - [ ] Final output: sum of all 200 trees → softmax → probabilities for home/draw/away
- [ ] Trains a second identical classifier for scoreline prediction (same features, different labels)

### 3. Evaluation — how we know if it's any good (`model.py` `evaluate()`)

- [ ] `TimeSeriesSplit(n_splits=5)` — splits data into 5 chunks in chronological order
- [ ] For each fold: train on earlier matches, test on later matches
- [ ] Collects predictions across all folds, then calculates:
  - [ ] Accuracy — % correct
  - [ ] Brier score — how far off the probabilities are (lower = better)
  - [ ] Log loss — punishes confident wrong answers hard (lower = better)
  - [ ] ROC AUC — can the model distinguish outcomes (higher = better)
  - [ ] Baseline accuracy — what you'd get always picking "home"

### 4. Prediction — what happens at match time (`model.py` `predict_match()`)

- [ ] `build_feature_row()` for the two teams using current data
- [ ] Outcome classifier outputs probabilities for home/draw/away
- [ ] Scoreline classifier outputs probabilities for each scoreline, returns top 10

## Next action

Improve the model to beat the baseline:
1. Add recency weighting so current form matters more than old results
2. Fix home advantage — shouldn't apply flat league-wide boost regardless of away team strength
3. Tune hyperparameters, try XGBoost/LightGBM
