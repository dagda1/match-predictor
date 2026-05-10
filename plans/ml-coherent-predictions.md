# Coherent ML predictions

## Problem

The ML side currently trains two independent classifiers:

1. `classifier` — H/D/A outcome (3 classes).
2. `scoreline_classifier` — exact scoreline labels (`"0-0"`, `"1-1"`, ...).

Both produce final answers shown on the card. They can disagree because nothing forces them to share a distribution. Example from screenshot: Poisson side displayed `1-1` but chip showed ✗ because the H/D/A model picked "Liverpool win". Same structural issue exists on the ML side — it just hasn't visibly contradicted yet.

The Poisson baseline is already coherent (one Monte Carlo simulation feeds both the scoreline grid and the H/D/A counts).

## Target design

### Single source of truth: λ_home, λ_away

Two ML regressors:

- `home_goals_regressor` — predicts expected home goals (Poisson loss or gradient boosting with `objective="poisson"`).
- `away_goals_regressor` — predicts expected away goals.

Inference produces one pair `(λ_home, λ_away)` per match.

### Derive everything from the grid

Build a Poisson scoreline grid (rows = home goals 0..6, cols = away goals 0..6, optionally with Dixon-Coles low-score correction):

```
P(home=i, away=j) = Pois(i; λ_home) * Pois(j; λ_away) * τ(i, j)
```

(τ is the Dixon-Coles correction, or `1` if not using it.)

Every display value is read off this grid:

- **Top scoreline** = argmax cell.
- **P(scoreline = a-b)** = `grid[a][b]`.
- **P(home win)** = `sum(grid[i][j] for i > j)`.
- **P(draw)** = `sum(grid[i][j] for i == j)`.
- **P(away win)** = `sum(grid[i][j] for i < j)`.

### Poisson baseline — unchanged role

Still produces `(λ_home, λ_away)`, but from naive historical averages (no features, no learning). Feeds the same grid formula. Comparison with ML is now apples-to-apples: same downstream maths, different λ source.

## Code-level changes

### `packages/ml/src/match_predictor/model.py`

- Remove `classifier` field from `TrainedModel`.
- Remove `scoreline_classifier` field.
- Add `home_goals_regressor` and `away_goals_regressor` fields.
- Rewrite `train()`:\
  - Build features X.
  - `y_home = df["homeGoals"]`, `y_away = df["awayGoals"]`.
  - Fit two regressors with Poisson objective.
- Rewrite `_scoreline_probabilities`:
  - Compute λ_home, λ_away from regressors.
  - Build grid via `scipy.stats.poisson.pmf` (or manual factorial).
  - Optionally apply Dixon-Coles τ for cells in {(0,0), (0,1), (1,0), (1,1)}.
  - Return list of `{homeGoals, awayGoals, probability}` sorted by probability.
- Add `outcome_probabilities(model, X) -> (home, draw, away)`:
  - Compute the same grid.
  - Return three sums.
- Rewrite `evaluate()` to score H/D/A derived from grid, not a separate classifier.

### Call sites — replace `model.classifier.predict_proba(X)` with `outcome_probabilities(model, X)`

- `packages/ml/src/match_predictor/model.py` — `predict_match()` (lines 165-166).
- `packages/ml/src/match_predictor/generate_predictions.py` (lines 74-75).
- `packages/ml/src/match_predictor/generate_upcoming.py` (lines 80-81).
- `packages/api/src/match_predictor_api/main.py` (lines 157-158).

### `packages/ml/src/match_predictor/generate_predictions.py:106 and :114`

`correct` now compares the top scoreline cell to `(actual_home, actual_away)` exactly:

```
"correct": top["homeGoals"] == actual_home and top["awayGoals"] == actual_away
```

### Retraining

- Old `model.joblib` shape no longer matches `TrainedModel`. Won't load.
- Run `pnpm run scan` (or whatever produces the artefact) to retrain.
- Replace EFS-stored model in deployed env.

### Tests to remove

Any test that mocks or asserts on `model.classifier` directly.

## Tests that lock in the design

### Test 1 — marginal sums equal H/D/A (semantic invariant)

In `packages/ml/src/match_predictor/model.test.py`:

```python
def test_outcome_probabilities_match_scoreline_marginals():
    model = train(load_test_fixtures())
    X = build_test_features()
    home, draw, away = outcome_probabilities(model, X)
    scorelines = _scoreline_probabilities(model, X, top_n=None)  # full grid

    sum_home = sum(s["probability"] for s in scorelines if s["homeGoals"] > s["awayGoals"])
    sum_draw = sum(s["probability"] for s in scorelines if s["homeGoals"] == s["awayGoals"])
    sum_away = sum(s["probability"] for s in scorelines if s["homeGoals"] < s["awayGoals"])

    assert abs(home - sum_home) < 1e-9
    assert abs(draw - sum_draw) < 1e-9
    assert abs(away - sum_away) < 1e-9
```

Fails if anyone adds a second classifier producing independent H/D/A numbers.

### Test 2 — single-source structural guard

```python
def test_trained_model_has_no_outcome_classifier():
    fields = dataclasses.fields(TrainedModel)
    forbidden = [f for f in fields if f.name == "classifier"]
    assert forbidden == [], "TrainedModel must not contain a separate H/D/A classifier"
```

Fails at the type level if a parallel classifier is reintroduced.

### Test 3 — grid sums to 1

```python
def test_scoreline_grid_is_a_valid_distribution():
    model = train(load_test_fixtures())
    X = build_test_features()
    scorelines = _scoreline_probabilities(model, X, top_n=None)
    total = sum(s["probability"] for s in scorelines)
    assert abs(total - 1.0) < 1e-6
```

Catches Dixon-Coles τ being applied without renormalisation, or grid truncation losing mass.

### Test 4 — API coherence

In `packages/api/src/match_predictor_api/main.test.py`:

```python
def test_predict_response_outcome_matches_scoreline_marginals():
    response = client.get("/predict?home=Liverpool&away=Chelsea").json()
    grid = response["ml"]["scorelines"]
    home, draw, away = response["ml"]["homeWin"], response["ml"]["draw"], response["ml"]["awayWin"]

    sum_home = sum(s["probability"] for s in grid if s["homeGoals"] > s["awayGoals"])
    # ... etc
    assert abs(home - sum_home) < 1e-9
```

Guards the user-facing surface against the library being right but the API serialiser bolting on a second source.

## Implementation checklist

Structural gates make the model coherent. Quality gates make it a real model rather than a naive Poisson regressor with two features. **All gates are mandatory.** A naive baseline that ticks every structural box and beats nothing on RPS is a fail.

### A. Structural (coherence)

- [ ] `TrainedModel.classifier` removed.
- [ ] `TrainedModel.scoreline_classifier` removed.
- [ ] `TrainedModel.home_goals_regressor` added.
- [ ] `TrainedModel.away_goals_regressor` added.
- [ ] `train()` fits both regressors with Poisson objective.
- [ ] `_scoreline_probabilities()` rewritten to build grid from λ_home, λ_away.
- [ ] **Dixon-Coles τ correction applied** (not optional). Implements the canonical low-score adjustment from Dixon & Coles 1997 §4.1. Single tunable parameter ρ, fit by maximum likelihood on the same training set as the regressors.
- [ ] Grid renormalised after τ correction.
- [ ] `outcome_probabilities(model, X)` helper exists, returns `(home, draw, away)` from grid sums.
- [ ] `evaluate()` scores H/D/A derived from grid, not a separate classifier.

### B. Features (no toy model)

The regressors must use a non-trivial feature set. A model with only "team played at home" and "opponent name" is the naive baseline — it doesn't earn ML's complexity.

- [ ] **Recent form**: rolling goals scored / conceded over last 5 and last 10 matches, computed separately for home and away contexts.
- [ ] **Opponent-adjusted strength**: each team's attack and defence rating updated as goals scored/conceded relative to opponent quality (e.g. simple Elo-style ratings, or rolling means weighted by opponent strength).
- [ ] **Home advantage**: explicit feature, not just leaked through home/away labels.
- [ ] **Rest days**: days since each team's last competitive match.
- [ ] **Head-to-head history**: last N meetings between the two teams (mean goals, win rate).
- [ ] **xG features when available**: rolling xG for / against. If the data source doesn't carry xG, skip and document.
- [ ] **No leakage**: every feature for match `t` is computed only from matches strictly before `t`. Verified by an explicit test that re-runs feature generation with future matches dropped and asserts identical features.
- [ ] Feature list and rationale documented in `plans/ml-features.md`. Each feature: source column(s), window, transformation, why it should help.

### C. Training methodology

- [ ] **Time-decay weighting** in the likelihood. Half-life parameter (e.g. `ξ` in Dixon-Coles' notation) chosen by held-out RPS, not picked by hand. Search range and chosen value recorded.
- [ ] **TimeSeriesSplit cross-validation** (already used in `evaluate()`). No random shuffle — football data is temporal and shuffling is leakage.
- [ ] **Hyperparameter tuning**: at minimum, search over `n_estimators`, `max_depth`, `learning_rate` for each regressor with `GridSearchCV(cv=TimeSeriesSplit)`. Best params and CV scores recorded.
- [ ] **Trained on at least 3 full Premier League seasons** of historical data. If less is available, document and accept that the model will be weak.

### D. Evaluation gates (must beat the baseline)

The whole point of ML is to beat naive Poisson. If it doesn't, the ML adds nothing. Evaluation runs on a held-out final season (or final 6 months) that the model never saw during training or hyperparameter search.

- [ ] **Ranked Probability Score (RPS)** computed for both ML and Poisson baseline on held-out matches. Lower is better. **ML RPS must be ≤ baseline RPS × 0.97** (i.e. a 3% improvement at minimum). RPS is the standard for football outcome forecasts (Constantinou & Fenton 2012).
- [ ] **Log loss** computed for H/D/A predictions on held-out set. ML must beat baseline.
- [ ] **Brier score** computed for H/D/A. ML must beat baseline.
- [ ] **Accuracy** of top-outcome and top-scoreline reported (informational — not a gate, since accuracy is a poor metric for probabilistic forecasts).
- [ ] **Calibration plot**: bin predictions by predicted probability into deciles, plot observed frequency. Curve must lie within ±5% of the diagonal in the 0.2–0.8 range. Save plot to `packages/ml/reports/calibration.png`.
- [ ] **Per-outcome breakdown**: confusion matrix on H/D/A. Document any class the model systematically misses.
- [ ] **Comparison table** committed to `packages/ml/reports/evaluation.md`: rows = {ML, Poisson baseline, bookmaker odds if available}, columns = {RPS, log loss, Brier, accuracy}. Held-out set described in detail.
- [ ] **Bookmaker comparison** if odds data is available: compute the same metrics on consensus odds (implied probabilities, normalised to remove the overround). The bookmaker is the proper benchmark — beating it is hard; getting close is the realistic goal.

### E. Call sites

- [ ] `model.py:predict_match` uses `outcome_probabilities`.
- [ ] `generate_predictions.py` uses `outcome_probabilities`.
- [ ] `generate_upcoming.py` uses `outcome_probabilities`.
- [ ] `api/main.py` uses `outcome_probabilities`.
- [ ] `rg "model\.classifier"` returns nothing.

### F. Correctness flag

- [ ] `generate_predictions.py:106` (ML) compares top scoreline to actual scoreline.
- [ ] `generate_predictions.py:114` (Poisson) compares top scoreline to actual scoreline.

### G. Retraining and deployment

- [ ] Local `model.joblib` rebuilt with new shape.
- [ ] Deployed model on EFS replaced.
- [ ] Old test fixtures regenerated if they encoded the old `TrainedModel` shape.
- [ ] **Reproducibility**: `random_state` set on every estimator. Two consecutive `pnpm run scan` runs produce identical model artefacts (verified by checksumming).

### H. Tests (gates)

- [ ] Test 1 (marginal-equals-sum) added and passing.
- [ ] Test 2 (structural guard) added and passing.
- [ ] Test 3 (grid sums to 1) added and passing.
- [ ] Test 4 (API coherence) added and passing.
- [ ] **Test 5 (no leakage)**: regenerate features for a known match with future data masked, assert identical to non-masked features.
- [ ] **Test 6 (baseline beat)**: load held-out fixture, compute RPS for ML and baseline, assert `rps_ml < rps_baseline`. Treat as a benchmark test, not a unit test — runs in CI but allowed to be slow.

### I. Verification

- [ ] `pnpm test` green.
- [ ] `packages/ml/reports/evaluation.md` exists, shows ML beating baseline on RPS, log loss, Brier.
- [ ] `packages/ml/reports/calibration.png` exists, curve within tolerance.
- [ ] Open the UI, view a played match, confirm chip ✓/✗ matches displayed scoreline vs actual scoreline.
- [ ] Inspect three different matches: confirm scoreline grid sums to 1 and H/D/A bars equal grid marginals (manually, by adding cells from the API response).

### J. What "done" actually means

- [ ] All structural gates pass (coherence locked in).
- [ ] All quality gates pass (model earns its complexity).
- [ ] Evaluation report committed showing the ML model beats the Poisson baseline on RPS, log loss, and Brier on a held-out final season.
- [ ] If any quality gate fails, the answer is **not** "ship anyway" — it's either improve the features/tuning, or document that ML doesn't beat baseline and stop pretending it does.
