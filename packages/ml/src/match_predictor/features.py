import numpy as np
import pandas as pd


def _rolling_stats(
    df: pd.DataFrame, team: str, before_date: pd.Timestamp, n: int = 5
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


def build_feature_row(
    df: pd.DataFrame, match_date: pd.Timestamp,
    home_team: str, away_team: str
) -> dict | None:
    home_stats = _rolling_stats(df, home_team, match_date)
    away_stats = _rolling_stats(df, away_team, match_date)

    if not home_stats or not away_stats:
        return None

    prior = df[df["date"] < match_date]
    ha = _home_advantage(prior) if len(prior) > 0 else 1.0

    return {
        "homeXgFor": home_stats["xgForAvg"],
        "homeXgAgainst": home_stats["xgAgainstAvg"],
        "homeXgOverperf": home_stats["xgOverperformance"],
        "homeShotConv": home_stats["shotConversion"],
        "homeSotPct": home_stats["sotPct"],
        "homePpda": home_stats["ppda"],
        "homeDeep": home_stats["deepAvg"],
        "awayXgFor": away_stats["xgForAvg"],
        "awayXgAgainst": away_stats["xgAgainstAvg"],
        "awayXgOverperf": away_stats["xgOverperformance"],
        "awayShotConv": away_stats["shotConversion"],
        "awaySotPct": away_stats["sotPct"],
        "awayPpda": away_stats["ppda"],
        "awayDeep": away_stats["deepAvg"],
        "homeAdvantage": ha,
    }


def build_training_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    rows = []
    labels = []

    for _, match in df.iterrows():
        features = build_feature_row(
            df, match["date"], match["homeTeam"], match["awayTeam"]
        )
        if features is None:
            continue

        rows.append(features)

        home_goals = match["homeGoals"]
        away_goals = match["awayGoals"]
        if home_goals > away_goals:
            labels.append("home")
        elif home_goals == away_goals:
            labels.append("draw")
        else:
            labels.append("away")

    return pd.DataFrame(rows), pd.Series(labels, name="outcome")
