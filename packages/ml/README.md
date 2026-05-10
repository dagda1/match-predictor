# Match Predictor ML

Two competing models predict Premier League match outcomes (home/draw/away): a **Gradient Boosting Classifier** and a **Poisson Baseline**. Comparing them shows whether engineered features add value over a simple statistical model.

## Gradient Boosting Classifier

`model.py` + `features.py`

### Features (15)

For each team, the last 5 matches (home and away combined) are averaged into 7 stats:

| Feature | What it measures |
|---|---|
| xG for / against | Expected goals scored and conceded |
| xG overperformance | Actual goals minus xG — finishing above or below expectation |
| Shot conversion | Goals / total shots |
| Shots on target % | Shots on target / total shots |
| PPDA | Passes per defensive action — pressing intensity |
| Deep completions | Passes completed in the final third |

That gives 7 x 2 teams = 14 features, plus one global feature:

- **Home advantage** — league-wide `mean(homeXg) / mean(awayXg)`

### How gradient boosting works

1. **Decision trees** split data on feature thresholds ("is homeXgFor > 1.8?"). Each leaf holds a class distribution over home/draw/away.

2. **Boosting** trains 200 trees sequentially. Each tree fits the *residual errors* of the ensemble so far — it learns what the previous trees got wrong. This is gradient descent in function space, minimising **log loss** (cross-entropy):

   ```
   L = -sum(y_i * log(p_i))
   ```

3. **Learning rate** (0.1) shrinks each tree's contribution to prevent overfitting. The final prediction sums all 200 trees' outputs, each scaled by 0.1.

4. **Softmax** converts the raw outputs (logits) into probabilities:

   ```
   p_k = exp(f_k) / sum(exp(f_j))   for k in {home, draw, away}
   ```

### Scoreline prediction

A second Gradient Boosting classifier is trained on the same 15 features but with scoreline labels (e.g. "2-1", "0-0") instead of outcome labels. Scores are capped at 4 goals per side. At prediction time it outputs probabilities for each scoreline class and returns the top 10.

### Evaluation

Uses **TimeSeriesSplit** with 5 folds — always trains on past data and tests on future data, respecting chronological order.

| Metric | What it measures |
|---|---|
| Accuracy | % of correct outcome predictions |
| Brier score | Mean squared error of predicted probabilities: `mean((p - actual)^2)` |
| Log loss | Penalises confident wrong predictions: `-mean(y * log(p))` |
| ROC AUC | Area under the receiver operating characteristic curve — discrimination ability across all thresholds |

### Why gradient boosting over neural nets?

Tree ensembles (XGBoost, LightGBM, sklearn GBM) consistently outperform deep learning on small tabular datasets. With 15 features and a few thousand rows, a neural net would overfit far worse.

### Known weakness

The model is overconfident — it predicts some matches at 95%+ probability. This is a calibration issue. The fix is **Platt scaling** or **isotonic regression** via `CalibratedClassifierCV`, which learns a mapping from raw model outputs to well-calibrated probabilities.

## Poisson Baseline

`poisson_baseline.py`

A simpler statistical model that uses only historical xG averages.

### How it works

1. **Lambda estimation** — the home team's lambda is their average home xG across all prior matches. The away team's lambda is their average away xG.

2. **Poisson distribution** — models the count of goals as independent random events with rate lambda:

   ```
   P(k goals) = (lambda^k * e^(-lambda)) / k!
   ```

3. **Monte Carlo simulation** — draw 10,000 pairs of `(home_goals, away_goals)` from the two Poisson distributions, then count:
   - Home wins = count(home > away) / 10,000
   - Draws = count(home == away) / 10,000
   - Away wins = count(home < away) / 10,000

Scoreline probabilities come from the same simulation — count occurrences of each (h, a) pair.

### Why this baseline?

Poisson-xG is the standard naive model in football analytics. If the ML model can't beat it, the engineered features aren't adding signal. It sets the floor that any more complex model needs to clear.

## Held-out evaluation

The last 60 played matches by date are reserved as a held-out set (`data.py:holdout_set`). Training never sees these — `data.py:training_set` excludes them.

`score_baseline.py` retrains the current 2-classifier architecture on the training set, scores it on the holdout, and logs the run to MLflow:

```
uv run python -m match_predictor.score_baseline
```

Metrics logged:
- **RPS** (Ranked Probability Score) — primary metric. Lower is better. Penalises confident wrong predictions and respects the H/D/A ordering.
- **Log loss** — penalises overconfidence in the wrong class.
- **Brier score** — multi-class mean squared error of predicted probabilities.

To browse runs:

```
uv run mlflow ui --backend-store-uri file://$PWD/../../mlruns
```

Open `http://localhost:5000`. Runs appear under the `match-predictor` experiment with parameters, metrics, and the model artefacts attached. Compare any two runs by selecting them in the UI.

The `mlruns/` directory at the repo root is gitignored — experiment tracking is local.

## Data integrity

Both models only use data from *before* the match being predicted — no future data leakage. The feature builder filters `df[df["date"] < match_date]` for every prediction.

## File structure

```
src/match_predictor/
  features.py          Rolling stats + feature engineering
  model.py             Gradient Boosting training, evaluation, prediction
  poisson_baseline.py  Poisson baseline model
  generate_predictions.py  Pre-compute predictions for played matches
  generate_upcoming.py     Fetch and predict upcoming fixtures
```
