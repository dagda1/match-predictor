import dataclasses
import math

import pandas as pd
import pytest

from match_predictor.data import holdout_set, load_matches, training_set
from match_predictor.features import build_feature_row
from match_predictor.model import (
    TrainedModel,
    outcome_probabilities,
    scoreline_probabilities,
    train,
)


@pytest.fixture(scope="module")
def trained_model() -> TrainedModel:
    df = load_matches()
    return train(training_set(df))


@pytest.fixture(scope="module")
def sample_features() -> pd.DataFrame:
    df = load_matches()
    match = holdout_set(df).iloc[0]
    features = build_feature_row(df, match["date"], match["homeTeam"], match["awayTeam"])
    return pd.DataFrame([features])


def test_outcome_probabilities_equal_scoreline_marginals(trained_model, sample_features):
    home, draw, away = outcome_probabilities(trained_model, sample_features)
    scorelines = scoreline_probabilities(trained_model, sample_features, n=49)

    sum_home = sum(s["probability"] for s in scorelines if s["homeGoals"] > s["awayGoals"])
    sum_draw = sum(s["probability"] for s in scorelines if s["homeGoals"] == s["awayGoals"])
    sum_away = sum(s["probability"] for s in scorelines if s["homeGoals"] < s["awayGoals"])

    assert math.isclose(home, sum_home, abs_tol=1e-9)
    assert math.isclose(draw, sum_draw, abs_tol=1e-9)
    assert math.isclose(away, sum_away, abs_tol=1e-9)


def test_outcome_probabilities_sum_to_one(trained_model, sample_features):
    home, draw, away = outcome_probabilities(trained_model, sample_features)
    assert math.isclose(home + draw + away, 1.0, abs_tol=1e-9)


def test_scoreline_probabilities_sum_to_one_when_complete(trained_model, sample_features):
    scorelines = scoreline_probabilities(trained_model, sample_features, n=49)
    total = sum(s["probability"] for s in scorelines)
    assert math.isclose(total, 1.0, abs_tol=1e-9)


def test_trained_model_has_no_outcome_classifier():
    field_names = [f.name for f in dataclasses.fields(TrainedModel)]
    assert "classifier" not in field_names
    assert "scoreline_classifier" not in field_names


def test_trained_model_exposes_two_regressors():
    field_names = [f.name for f in dataclasses.fields(TrainedModel)]
    assert "home_goals_regressor" in field_names
    assert "away_goals_regressor" in field_names


def test_dixon_coles_rho_fitted_to_negative_value(trained_model):
    assert -0.2 <= trained_model.rho <= 0.0
    assert trained_model.rho != 0.0
