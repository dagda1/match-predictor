import mlflow
import pandas as pd

from match_predictor.data import HOLDOUT_SIZE, holdout_set, load_matches, training_set
from match_predictor.evaluate import evaluate
from match_predictor.features import build_feature_row
from match_predictor.model import TrainedModel, outcome_probabilities, train
from match_predictor.tracking import REPO_ROOT, configure


def make_predict_fn(model: TrainedModel):
    def predict_fn(home: str, away: str, date: pd.Timestamp, df: pd.DataFrame):
        features = build_feature_row(df, date, home, away)
        if features is None:
            return None
        X = pd.DataFrame([features])
        return outcome_probabilities(model, X)

    return predict_fn


def main() -> None:
    configure()

    df = load_matches()
    train_df = training_set(df)
    holdout = holdout_set(df)

    print(f"training on {len(train_df)} matches (holdout: last {HOLDOUT_SIZE} played)")

    with mlflow.start_run(run_name="regressor-2-poisson") as run:
        mlflow.log_params({
            "architecture": "2-regressor",
            "home_goals_regressor": "HistGradientBoostingRegressor(loss=poisson)",
            "away_goals_regressor": "HistGradientBoostingRegressor(loss=poisson)",
            "max_iter": 200,
            "max_depth": 4,
            "learning_rate": 0.1,
            "training_matches": len(train_df),
            "holdout_size": HOLDOUT_SIZE,
            "holdout_first_date": str(holdout["date"].min().date()),
            "holdout_last_date": str(holdout["date"].max().date()),
        })

        model = train(train_df)
        mlflow.log_param("rho", model.rho)

        print(f"scoring on {len(holdout)} holdout matches (fitted rho={model.rho:.4f})")
        metrics = evaluate(make_predict_fn(model), df, holdout)

        mlflow.log_params({
            "n_scored": metrics["n"],
            "n_skipped": metrics["skipped"],
        })

        mlflow.log_metrics({
            "rps": metrics["rps"],
            "log_loss": metrics["log_loss"],
            "brier": metrics["brier"],
        })

        mlflow.sklearn.log_model(model.home_goals_regressor, name="home_goals_regressor")
        mlflow.sklearn.log_model(model.away_goals_regressor, name="away_goals_regressor")

        print()
        print(f"=== run {run.info.run_id} ===")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        print()
        print(f"view: mlflow ui --backend-store-uri file://{REPO_ROOT}/mlruns")


if __name__ == "__main__":
    main()
