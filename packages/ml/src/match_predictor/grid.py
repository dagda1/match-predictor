import numpy as np
from scipy.stats import poisson

MAX_GOALS = 6


def _dixon_coles_tau(
    home_goals: int,
    away_goals: int,
    lambda_home: float,
    lambda_away: float,
    rho: float,
) -> float:
    if home_goals == 0 and away_goals == 0:
        return 1.0 - lambda_home * lambda_away * rho
    if home_goals == 0 and away_goals == 1:
        return 1.0 + lambda_home * rho
    if home_goals == 1 and away_goals == 0:
        return 1.0 + lambda_away * rho
    if home_goals == 1 and away_goals == 1:
        return 1.0 - rho
    return 1.0


def build_grid(
    lambda_home: float,
    lambda_away: float,
    rho: float = 0.0,
    max_goals: int = MAX_GOALS,
) -> np.ndarray:
    ks = np.arange(max_goals + 1)
    home_pmf = poisson.pmf(ks, lambda_home)
    away_pmf = poisson.pmf(ks, lambda_away)
    grid = np.outer(home_pmf, away_pmf)

    if rho != 0.0:
        for i in range(2):
            for j in range(2):
                grid[i, j] *= _dixon_coles_tau(i, j, lambda_home, lambda_away, rho)

    return grid / grid.sum()


def outcome_probs_from_grid(grid: np.ndarray) -> tuple[float, float, float]:
    n = grid.shape[0]
    rows, cols = np.indices((n, n))
    home = float(grid[rows > cols].sum())
    draw = float(grid[rows == cols].sum())
    away = float(grid[rows < cols].sum())
    return home, draw, away


def top_scorelines_from_grid(grid: np.ndarray, n: int = 10) -> list[dict]:
    flat_indices = np.argsort(grid, axis=None)[::-1][:n]
    rows, cols = np.unravel_index(flat_indices, grid.shape)
    return [
        {"homeGoals": int(i), "awayGoals": int(j), "probability": float(grid[i, j])}
        for i, j in zip(rows, cols)
    ]
