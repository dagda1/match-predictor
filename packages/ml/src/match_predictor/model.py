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
    scoreline_classifier: GradientBoostingClassifier
    df: pd.DataFrame
    metrics: EvalMetrics | None = None
    feature_names: list[str] = field(default_factory=list)


def train(df: pd.DataFrame) -> TrainedModel:
    X, y_outcome, y_scoreline = build_training_data(df)

    clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    clf.fit(X, y_outcome)

    scoreline_clf = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
    )
    scoreline_clf.fit(X, y_scoreline)

    metrics = evaluate(clf, X, y_outcome)

    return TrainedModel(
        classifier=clf,
        scoreline_classifier=scoreline_clf,
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


def _scoreline_probabilities(
    model: TrainedModel, X: pd.DataFrame,
) -> list[dict]:
    proba = model.scoreline_classifier.predict_proba(X)[0]
    classes = list(model.scoreline_classifier.classes_)

    scored = sorted(
        zip(classes, proba), key=lambda x: x[1], reverse=True,
    )[:10]

    return [
        {
            "homeGoals": int(label.split("-")[0]),
            "awayGoals": int(label.split("-")[1]),
            "probability": float(prob),
        }
        for label, prob in scored
    ]


def predict_match(
    model: TrainedModel,
    home_team: str,
    away_team: str,
) -> Prediction:
    features = build_feature_row(model.df, pd.Timestamp.now(), home_team, away_team)
    if features is None:
        raise ValueError(f"not enough match history for {home_team} or {away_team}")

    X = pd.DataFrame([features])
    proba = model.classifier.predict_proba(X)[0]
    classes = list(model.classifier.classes_)

    return Prediction(
        home_win=float(proba[classes.index("home")]),
        draw=float(proba[classes.index("draw")]),
        away_win=float(proba[classes.index("away")]),
        scorelines=_scoreline_probabilities(model, X),
    )
