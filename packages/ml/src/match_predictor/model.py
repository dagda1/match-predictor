from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    log_loss,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.preprocessing import LabelBinarizer

from match_predictor.features import build_training_data, build_feature_row


@dataclass
class Prediction:
    home_win: float
    draw: float
    away_win: float
    scorelines: list[dict]


@dataclass
class EvalMetrics:
    accuracy: float
    brier_score: float
    log_loss_val: float
    roc_auc: float
    confusion: np.ndarray
    baseline_accuracy: float


@dataclass
class TrainedModel:
    classifier: GradientBoostingClassifier
    df: pd.DataFrame
    metrics: EvalMetrics | None = None
    feature_names: list[str] = field(default_factory=list)


def train(df: pd.DataFrame) -> TrainedModel:
    X, y = build_training_data(df)

    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    clf.fit(X, y)

    metrics = evaluate(clf, X, y)

    return TrainedModel(
        classifier=clf,
        df=df,
        metrics=metrics,
        feature_names=list(X.columns),
    )


def evaluate(
    clf: GradientBoostingClassifier,
    X: pd.DataFrame,
    y: pd.Series,
) -> EvalMetrics:
    tscv = TimeSeriesSplit(n_splits=5)
    all_y_true = []
    all_y_pred = []
    all_y_proba = []

    for train_idx, test_idx in tscv.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        fold_clf = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            random_state=42,
        )
        fold_clf.fit(X_train, y_train)

        all_y_true.extend(y_test)
        all_y_pred.extend(fold_clf.predict(X_test))
        all_y_proba.extend(fold_clf.predict_proba(X_test))

    y_true = np.array(all_y_true)
    y_pred = np.array(all_y_pred)
    y_proba = np.array(all_y_proba)

    lb = LabelBinarizer()
    y_true_bin = lb.fit_transform(y_true)

    classes = clf.classes_
    baseline_acc = (y_true == "home").mean()

    return EvalMetrics(
        accuracy=accuracy_score(y_true, y_pred),
        brier_score=np.mean([
            brier_score_loss(y_true_bin[:, i], y_proba[:, i])
            for i in range(len(classes))
        ]),
        log_loss_val=log_loss(y_true, y_proba, labels=classes),
        roc_auc=roc_auc_score(y_true_bin, y_proba, multi_class="ovr", average="weighted"),
        confusion=confusion_matrix(y_true, y_pred, labels=list(classes)),
        baseline_accuracy=baseline_acc,
    )


def predict_match(
    model: TrainedModel,
    home_team: str,
    away_team: str,
    n_simulations: int = 10_000,
) -> Prediction:
    features = build_feature_row(model.df, pd.Timestamp.now(), home_team, away_team)
    if features is None:
        raise ValueError(f"not enough match history for {home_team} or {away_team}")

    X = pd.DataFrame([features])
    proba = model.classifier.predict_proba(X)[0]
    classes = list(model.classifier.classes_)

    home_win_prob = float(proba[classes.index("home")])
    draw_prob = float(proba[classes.index("draw")])
    away_win_prob = float(proba[classes.index("away")])

    home_xg = features["homeXgFor"]
    away_xg = features["awayXgFor"]

    rng = np.random.default_rng()
    home_goals = rng.poisson(home_xg, n_simulations)
    away_goals = rng.poisson(away_xg, n_simulations)

    scoreline_counts: dict[tuple[int, int], int] = {}
    for h, a in zip(home_goals, away_goals):
        key = (int(h), int(a))
        scoreline_counts[key] = scoreline_counts.get(key, 0) + 1

    top_scorelines = sorted(
        scoreline_counts.items(), key=lambda x: x[1], reverse=True
    )[:10]

    return Prediction(
        home_win=home_win_prob,
        draw=draw_prob,
        away_win=away_win_prob,
        scorelines=[
            {
                "homeGoals": score[0],
                "awayGoals": score[1],
                "probability": count / n_simulations,
            }
            for score, count in top_scorelines
        ],
    )
