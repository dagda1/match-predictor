from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    name = Column(String, primary_key=True)


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    season = Column(String, nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    home_goals = Column(Integer, nullable=False)
    away_goals = Column(Integer, nullable=False)
    home_xg = Column(Float, nullable=False)
    away_xg = Column(Float, nullable=False)
    home_shots = Column(Integer, nullable=False)
    away_shots = Column(Integer, nullable=False)
    home_shots_on_target = Column(Integer, nullable=False)
    away_shots_on_target = Column(Integer, nullable=False)
    home_deep = Column(Integer, nullable=False)
    away_deep = Column(Integer, nullable=False)
    home_ppda = Column(Float, nullable=False)
    away_ppda = Column(Float, nullable=False)
    home_win_prob = Column(Float, nullable=False)
    draw_prob = Column(Float, nullable=False)
    away_win_prob = Column(Float, nullable=False)


class TeamFeatures(Base):
    __tablename__ = "team_features"

    team_name = Column(String, primary_key=True)
    xg_for_avg = Column(Float, nullable=False)
    xg_against_avg = Column(Float, nullable=False)
    xg_overperformance = Column(Float, nullable=False)
    shot_conversion = Column(Float, nullable=False)
    sot_pct = Column(Float, nullable=False)
    ppda = Column(Float, nullable=False)
    deep_avg = Column(Float, nullable=False)
    goals_for_avg = Column(Float, nullable=False)
    goals_against_avg = Column(Float, nullable=False)
    home_advantage = Column(Float, nullable=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    actual_home_goals = Column(Integer)
    actual_away_goals = Column(Integer)
    actual_outcome = Column(String)
    ml_home_win = Column(Float, nullable=False)
    ml_draw = Column(Float, nullable=False)
    ml_away_win = Column(Float, nullable=False)
    ml_predicted_outcome = Column(String, nullable=False)
    ml_correct = Column(Boolean)
    ml_top_home_goals = Column(Integer, nullable=False)
    ml_top_away_goals = Column(Integer, nullable=False)
    ml_top_probability = Column(Float, nullable=False)
    poisson_home_win = Column(Float, nullable=False)
    poisson_draw = Column(Float, nullable=False)
    poisson_away_win = Column(Float, nullable=False)
    poisson_predicted_outcome = Column(String, nullable=False)
    poisson_correct = Column(Boolean)
    poisson_home_lambda = Column(Float, nullable=False)
    poisson_away_lambda = Column(Float, nullable=False)
    poisson_top_home_goals = Column(Integer, nullable=False)
    poisson_top_away_goals = Column(Integer, nullable=False)
    poisson_top_probability = Column(Float, nullable=False)


class Upcoming(Base):
    __tablename__ = "upcoming"

    id = Column(Integer, primary_key=True, autoincrement=True)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    ml_home_win = Column(Float, nullable=False)
    ml_draw = Column(Float, nullable=False)
    ml_away_win = Column(Float, nullable=False)
    ml_predicted_outcome = Column(String, nullable=False)
    ml_top_home_goals = Column(Integer, nullable=False)
    ml_top_away_goals = Column(Integer, nullable=False)
    ml_top_probability = Column(Float, nullable=False)
    poisson_home_win = Column(Float, nullable=False)
    poisson_draw = Column(Float, nullable=False)
    poisson_away_win = Column(Float, nullable=False)
    poisson_predicted_outcome = Column(String, nullable=False)
    poisson_home_lambda = Column(Float, nullable=False)
    poisson_away_lambda = Column(Float, nullable=False)
    poisson_top_home_goals = Column(Integer, nullable=False)
    poisson_top_away_goals = Column(Integer, nullable=False)
    poisson_top_probability = Column(Float, nullable=False)
