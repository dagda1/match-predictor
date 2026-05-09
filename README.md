# Match Predictor

Premier League match outcome predictor using two approaches: a gradient boosting ML model and a Poisson baseline.

## How the predictions work

### ML Model (GradientBoostingClassifier)

Classifies each match as home win, draw, or away win using 15 features derived from each team's last 5 matches.

**Features per team (7 each, 14 total):**

| Feature | What it measures |
|---------|-----------------|
| xgFor | Average expected goals scored |
| xgAgainst | Average expected goals conceded |
| xgOverperf | Actual goals minus xG — are they finishing above or below expectation? |
| shotConv | Goals per shot — finishing efficiency |
| sotPct | Shots on target per shot — shot quality |
| ppda | Passes allowed per defensive action — pressing intensity (lower = more aggressive) |
| deep | Deep completions — passes into the final third |

**Plus 1 global feature:**

| Feature | What it measures |
|---------|-----------------|
| homeAdvantage | League-wide ratio of home xG to away xG from all prior matches |

All features use only data from before the match being predicted (no future leakage). The model outputs probabilities for each outcome (e.g. 48% home, 24% draw, 28% away).

Scorelines are generated separately using Poisson simulation with the team's rolling xG averages as lambda values.

**Training:** scikit-learn GradientBoostingClassifier (200 estimators, max depth 4, learning rate 0.1). Evaluated with 5-fold TimeSeriesSplit cross-validation to prevent data leakage.

### Poisson Baseline

Simulates 10,000 random matches using each team's average xG.

1. Calculate home team's mean xG from all their home matches → `home_lambda`
2. Calculate away team's mean xG from all their away matches → `away_lambda`
3. Draw 10,000 random scorelines: home goals from `Poisson(home_lambda)`, away goals from `Poisson(away_lambda)`
4. Count home wins, draws, away wins across all simulations → probabilities

No form, no features, no training. Just raw xG averages and random simulation.

**Limitation:** Poisson variance equals its mean. Two teams averaging 1.5 xG produce identical predictions regardless of whether one is consistent and the other volatile. The distribution can't distinguish streaky teams from steady ones.

### Why both?

The Poisson baseline is the simplest credible model. If the ML model can't beat it, the extra features are adding noise rather than signal. The gap between them measures whether form, pressing, shot quality etc. actually predict outcomes better than raw xG averages alone.

## Data

621 Premier League matches from Understat (2024-25 full season + 2025-26 to date). Each match includes goals, xG, shots, shots on target, deep completions, PPDA, and pre-match win probabilities.

## Local development

### Prerequisites

- Node.js 22+ (managed by Volta)
- pnpm 10+
- Python 3.12+
- uv (Python package manager)
- Docker

### First time setup

```bash
pnpm install
pnpm setup:local
```

This starts Postgres in Docker, scrapes match data, generates predictions, runs database migrations, and seeds the database.

### Running

```bash
pnpm dev
```

Starts Postgres (Docker), FastAPI (port 4400), and React frontend (port 3300).

### Other commands

```bash
pnpm test             # run all tests
pnpm refresh          # re-scrape data and regenerate predictions
```

## Architecture

_Auto-generated from `cdk.out/DeployStack.template.json` — run `pnpm arch:diagram` to refresh._

<!-- ARCH:START -->
```mermaid
graph LR
  subgraph VPC
    ApiApiFunctionAA82C666["Api<br/>Lambda"]
    DatabaseBootstrapHandlerFunction53F1278C["DatabaseBootstrap<br/>Lambda"]
    DatabaseMigrationHandlerFunction71FE854B["DatabaseMigration<br/>Lambda"]
    DatabasePostgres277EF4CB[("Postgres<br/>RDS")]
    EtlFunctionsPredictorFunctionE33E3D43["Predictor<br/>Lambda"]
    EtlFunctionsScraperFunctionF099BA00["Scraper<br/>Lambda"]
  end
  ApiHttpApi4C294DC0(["HttpApi<br/>API Gateway"])
  ApiWarmupRuleFD0BC37F("WarmupRule<br/>EventBridge")
  CdnDistribution149FA6C8{{"Cdn<br/>CloudFront"}}
  DatabasePostgresSecret6EBE3413[/"Postgres<br/>Secrets Manager"/]
  EventBridgeDailyScraperRule9BFD8304("DailyScraperRule<br/>EventBridge")
  FirehoseFunctionsLogTransformerFunctionE1614C32["LogTransformer<br/>Lambda"]
  ModelStorageModelFileSystem7131CD34[\"ModelFileSystem<br/>EFS"/]
  QueuingScraperToPredictor12C65B00>"ScraperToPredictor<br/>SQS"]
  SecretsOriginVerifySecret2207D00B[/"OriginVerifySecret<br/>Secrets Manager"/]
  StorageBucket5CB7C8EA[("Storage<br/>S3")]
  StorageFrontendBucketC065FEEF[("FrontendBucket<br/>S3")]
  ApiApiFunctionAA82C666 --> DatabasePostgres277EF4CB
  ApiApiFunctionAA82C666 --> ModelStorageModelFileSystem7131CD34
  ApiApiFunctionAA82C666 --> SecretsOriginVerifySecret2207D00B
  ApiApiFunctionAA82C666 --> StorageBucket5CB7C8EA
  ApiHttpApi4C294DC0 --> ApiApiFunctionAA82C666
  ApiWarmupRuleFD0BC37F --> ApiApiFunctionAA82C666
  CdnDistribution149FA6C8 --> ApiHttpApi4C294DC0
  CdnDistribution149FA6C8 --> SecretsOriginVerifySecret2207D00B
  CdnDistribution149FA6C8 --> StorageFrontendBucketC065FEEF
  DatabaseBootstrapHandlerFunction53F1278C --> DatabasePostgres277EF4CB
  DatabaseBootstrapHandlerFunction53F1278C --> DatabasePostgresSecret6EBE3413
  DatabaseMigrationHandlerFunction71FE854B --> DatabasePostgres277EF4CB
  EtlFunctionsPredictorFunctionE33E3D43 --> DatabasePostgres277EF4CB
  EtlFunctionsPredictorFunctionE33E3D43 --> ModelStorageModelFileSystem7131CD34
  EtlFunctionsPredictorFunctionE33E3D43 --> StorageBucket5CB7C8EA
  EtlFunctionsScraperFunctionF099BA00 --> DatabasePostgres277EF4CB
  EtlFunctionsScraperFunctionF099BA00 --> QueuingScraperToPredictor12C65B00
  EtlFunctionsScraperFunctionF099BA00 --> StorageBucket5CB7C8EA
  EventBridgeDailyScraperRule9BFD8304 --> EtlFunctionsScraperFunctionF099BA00
  QueuingScraperToPredictor12C65B00 --> EtlFunctionsPredictorFunctionE33E3D43
```
<!-- ARCH:END -->

## Database schema

_Auto-generated from `packages/ml/src/match_predictor/db_models.py` — run `pnpm db:diagram` to refresh._

<!-- DB-SCHEMA:START -->
```mermaid
erDiagram
  MATCHES {
    string id PK
    datetime date
    string season
    string home_team
    string away_team
    int home_goals
    int away_goals
    float home_xg
    float away_xg
    int home_shots
    int away_shots
    int home_shots_on_target
    int away_shots_on_target
    int home_deep
    int away_deep
    float home_ppda
    float away_ppda
    float home_win_prob
    float draw_prob
    float away_win_prob
  }
  PREDICTIONS {
    int id PK
    string home_team
    string away_team
    datetime date
    int actual_home_goals "nullable"
    int actual_away_goals "nullable"
    string actual_outcome "nullable"
    float ml_home_win
    float ml_draw
    float ml_away_win
    string ml_predicted_outcome
    bool ml_correct "nullable"
    int ml_top_home_goals
    int ml_top_away_goals
    float ml_top_probability
    float poisson_home_win
    float poisson_draw
    float poisson_away_win
    string poisson_predicted_outcome
    bool poisson_correct "nullable"
    float poisson_home_lambda
    float poisson_away_lambda
    int poisson_top_home_goals
    int poisson_top_away_goals
    float poisson_top_probability
  }
  TEAM_FEATURES {
    string team_name PK
    float xg_for_avg
    float xg_against_avg
    float xg_overperformance
    float shot_conversion
    float sot_pct
    float ppda
    float deep_avg
    float goals_for_avg
    float goals_against_avg
    float home_advantage
  }
  TEAMS {
    string name PK
  }
  UPCOMING {
    int id PK
    string home_team
    string away_team
    datetime date
    float ml_home_win
    float ml_draw
    float ml_away_win
    string ml_predicted_outcome
    int ml_top_home_goals
    int ml_top_away_goals
    float ml_top_probability
    float poisson_home_win
    float poisson_draw
    float poisson_away_win
    string poisson_predicted_outcome
    float poisson_home_lambda
    float poisson_away_lambda
    int poisson_top_home_goals
    int poisson_top_away_goals
    float poisson_top_probability
  }
```
<!-- DB-SCHEMA:END -->
