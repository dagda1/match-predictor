import pandas as pd

from match_predictor.data import HOLDOUT_SIZE, holdout_set, training_set


def _build_df(n_played: int, n_unplayed: int) -> pd.DataFrame:
    rows = []
    for i in range(n_played):
        rows.append({
            "id": f"p{i}",
            "date": pd.Timestamp("2025-08-01") + pd.Timedelta(days=i),
            "homeGoals": 1.0,
            "awayGoals": 0.0,
        })
    for i in range(n_unplayed):
        rows.append({
            "id": f"u{i}",
            "date": pd.Timestamp("2026-06-01") + pd.Timedelta(days=i),
            "homeGoals": None,
            "awayGoals": None,
        })
    return pd.DataFrame(rows)


def test_holdout_returns_last_n_played_matches():
    df = _build_df(n_played=100, n_unplayed=10)
    holdout = holdout_set(df, n=60)

    assert len(holdout) == 60
    assert list(holdout["id"]) == [f"p{i}" for i in range(40, 100)]


def test_holdout_excludes_unplayed_matches():
    df = _build_df(n_played=80, n_unplayed=20)
    holdout = holdout_set(df, n=60)

    assert holdout["homeGoals"].notna().all()


def test_holdout_uses_default_size():
    df = _build_df(n_played=200, n_unplayed=0)
    holdout = holdout_set(df)

    assert len(holdout) == HOLDOUT_SIZE


def test_training_set_excludes_holdout():
    df = _build_df(n_played=100, n_unplayed=10)
    train = training_set(df, n=60)
    holdout = holdout_set(df, n=60)

    assert set(train["id"]).isdisjoint(set(holdout["id"]))
    assert len(train) == 100 + 10 - 60


def test_training_set_keeps_unplayed_matches():
    df = _build_df(n_played=80, n_unplayed=20)
    train = training_set(df, n=60)

    assert (train["homeGoals"].isna()).sum() == 20
