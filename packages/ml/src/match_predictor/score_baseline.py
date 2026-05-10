import mlflow
import pandas as pd

from match_predictor.data import HOLDOUT_SIZE, holdout_set, load_matches, training_set
from match_predictor.evaluate import evaluate
from match_predictor.features import build_feature_row
from match_predictor.model import TrainedModel, train
from match_predictor.tracking import REPO_ROOT, configure


def make_predict_fn(model: TrainedModel):
    def predict_fn(home: str, away: str, date: pd.Timestamp, df: pd.DataFrame):
        features = build_feature_row(df, date, home, away)
        if features is None:
            return None
        X = pd.DataFrame([features])
        proba = model.classifier.predict_proba(X)[0]
        classes = list(model.classifier.classes_)
        return (
            float(proba[classes.index("home")]),
            float(proba[classes.index("draw")]),
            float(proba[classes.index("away")]),
        )

    return predict_fn


def main() -> None:
    configure()

    df = load_matches()
    train_df = training_set(df)
    holdout = holdout_set(df)

    print(f"training on {len(train_df)} matches (holdout: last {HOLDOUT_SIZE} played)")

    with mlflow.start_run(run_name="baseline-2classifier") as run:
        mlflow.log_params({
            "architecture": "2-classifier",
            "outcome_classifier": "GradientBoostingClassifier",
            "scoreline_classifier": "GradientBoostingClassifier",
            "n_estimators": 200,
            "max_depth": 4,
            "learning_rate": 0.1,
            "training_matches": len(train_df),
            "holdout_size": HOLDOUT_SIZE,
            "holdout_first_date": str(holdout["date"].min().date()),
            "holdout_last_date": str(holdout["date"].max().date()),
        })

        model = train(train_df)

        print(f"scoring on {len(holdout)} holdout matches")
        metrics = evaluate(make_predict_fn(model), df, holdout)

        mlflow.log_metrics({
            "rps": metrics["rps"],
            "log_loss": metrics["log_loss"],
            "brier": metrics["brier"],
            "n_scored": metrics["n"],
            "n_skipped": metrics["skipped"],
        })

        mlflow.sklearn.log_model(model.classifier, name="outcome_classifier")
        mlflow.sklearn.log_model(model.scoreline_classifier, name="scoreline_classifier")

        print()
        print(f"=== run {run.info.run_id} ===")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
        print()
        print(f"view: mlflow ui --backend-store-uri file://{REPO_ROOT}/mlruns")


if __name__ == "__main__":
    main()
