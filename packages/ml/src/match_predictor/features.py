import pandas as pd

WINDOWS = (5, 10)


def _rolling_stats(
    df: pd.DataFrame, team: str, before_date: pd.Timestamp, n: int
) -> dict:
    home = df[(df["homeTeam"] == team) & (df["date"] < before_date)].copy()
    home = home.rename(columns={
        "homeXg": "xgFor", "awayXg": "xgAgainst",
        "homeGoals": "goalsFor", "awayGoals": "goalsAgainst",
        "homeShots": "shotsFor", "awayShots": "shotsAgainst",
        "homeShotsOnTarget": "sotFor", "awayShotsOnTarget": "sotAgainst",
        "homePpda": "ppda", "awayPpda": "ppdaAgainst",
        "homeDeep": "deepFor", "awayDeep": "deepAgainst",
    })
    home["isHome"] = 1

    away = df[(df["awayTeam"] == team) & (df["date"] < before_date)].copy()
    away = away.rename(columns={
        "awayXg": "xgFor", "homeXg": "xgAgainst",
        "awayGoals": "goalsFor", "homeGoals": "goalsAgainst",
        "awayShots": "shotsFor", "homeShots": "shotsAgainst",
        "awayShotsOnTarget": "sotFor", "homeShotsOnTarget": "sotAgainst",
        "awayPpda": "ppda", "homePpda": "ppdaAgainst",
        "awayDeep": "deepFor", "homeDeep": "deepAgainst",
    })
    away["isHome"] = 0

    cols = [
        "date", "xgFor", "xgAgainst", "goalsFor", "goalsAgainst",
        "shotsFor", "shotsAgainst", "sotFor", "sotAgainst",
        "ppda", "ppdaAgainst", "deepFor", "deepAgainst", "isHome",
    ]
    matches = pd.concat([home[cols], away[cols]]).sort_values("date")

    if len(matches) < n:
        return {}

    recent = matches.tail(n)

    xg_for = recent["xgFor"].mean()
    xg_against = recent["xgAgainst"].mean()
    goals_for = recent["goalsFor"].mean()
    goals_against = recent["goalsAgainst"].mean()

    return {
        "xgForAvg": xg_for,
        "xgAgainstAvg": xg_against,
        "xgOverperformance": goals_for - xg_for,
        "shotConversion": goals_for / recent["shotsFor"].sum() if recent["shotsFor"].sum() > 0 else 0,
        "sotPct": recent["sotFor"].sum() / recent["shotsFor"].sum() if recent["shotsFor"].sum() > 0 else 0,
        "ppda": recent["ppda"].mean(),
        "deepAvg": recent["deepFor"].mean(),
        "goalsForAvg": goals_for,
        "goalsAgainstAvg": goals_against,
    }


def _home_advantage(df: pd.DataFrame) -> float:
    return df["homeXg"].mean() / df["awayXg"].mean()


_ROLLING_KEYS = (
    "xgForAvg", "xgAgainstAvg", "xgOverperformance",
    "shotConversion", "sotPct", "ppda", "deepAvg",
)


def build_feature_row(
    df: pd.DataFrame, match_date: pd.Timestamp,
    home_team: str, away_team: str
) -> dict | None:
    home_primary = _rolling_stats(df, home_team, match_date, n=WINDOWS[0])
    away_primary = _rolling_stats(df, away_team, match_date, n=WINDOWS[0])

    if not home_primary or not away_primary:
        return None

    features: dict = {}
    for window in WINDOWS:
        home_stats = _rolling_stats(df, home_team, match_date, n=window)
        away_stats = _rolling_stats(df, away_team, match_date, n=window)
        for key in _ROLLING_KEYS:
            features[f"home_{key}_{window}"] = home_stats[key] if home_stats else float("nan")
            features[f"away_{key}_{window}"] = away_stats[key] if away_stats else float("nan")

    prior = df[df["date"] < match_date]
    features["homeAdvantage"] = _home_advantage(prior) if len(prior) > 0 else 1.0

    return features


def build_training_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    rows = []
    home_goals = []
    away_goals = []

    for _, match in df.iterrows():
        features = build_feature_row(
            df, match["date"], match["homeTeam"], match["awayTeam"]
        )
        if features is None:
            continue

        rows.append(features)
        home_goals.append(int(match["homeGoals"]))
        away_goals.append(int(match["awayGoals"]))

    return (
        pd.DataFrame(rows),
        pd.Series(home_goals, name="homeGoals"),
        pd.Series(away_goals, name="awayGoals"),
    )
