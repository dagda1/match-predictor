import math

import numpy as np

from match_predictor.grid import (
    build_grid,
    outcome_probs_from_grid,
    top_scorelines_from_grid,
)


def test_grid_sums_to_one():
    grid = build_grid(1.5, 1.2)
    assert math.isclose(grid.sum(), 1.0, abs_tol=1e-9)


def test_grid_sums_to_one_with_dixon_coles_correction():
    grid = build_grid(1.5, 1.2, rho=-0.1)
    assert math.isclose(grid.sum(), 1.0, abs_tol=1e-9)


def test_outcome_probs_sum_to_one():
    grid = build_grid(1.5, 1.2)
    home, draw, away = outcome_probs_from_grid(grid)
    assert math.isclose(home + draw + away, 1.0, abs_tol=1e-9)


def test_outcome_probs_match_grid_marginals():
    grid = build_grid(2.1, 0.8)
    home, draw, away = outcome_probs_from_grid(grid)

    n = grid.shape[0]
    expected_home = sum(grid[i, j] for i in range(n) for j in range(n) if i > j)
    expected_draw = sum(grid[i, i] for i in range(n))
    expected_away = sum(grid[i, j] for i in range(n) for j in range(n) if i < j)

    assert math.isclose(home, expected_home, abs_tol=1e-9)
    assert math.isclose(draw, expected_draw, abs_tol=1e-9)
    assert math.isclose(away, expected_away, abs_tol=1e-9)


def test_higher_home_lambda_means_higher_home_win_probability():
    home_strong = outcome_probs_from_grid(build_grid(2.5, 0.8))
    away_strong = outcome_probs_from_grid(build_grid(0.8, 2.5))

    assert home_strong[0] > home_strong[2]
    assert away_strong[2] > away_strong[0]


def test_top_scoreline_is_argmax_cell():
    grid = build_grid(1.4, 1.2)
    top = top_scorelines_from_grid(grid, n=1)[0]

    flat_argmax = np.unravel_index(np.argmax(grid), grid.shape)
    assert top["homeGoals"] == flat_argmax[0]
    assert top["awayGoals"] == flat_argmax[1]


def test_top_scorelines_sorted_by_probability_descending():
    grid = build_grid(1.5, 1.2)
    top = top_scorelines_from_grid(grid, n=10)
    probs = [s["probability"] for s in top]
    assert probs == sorted(probs, reverse=True)


def test_dixon_coles_increases_low_score_draw_probability():
    grid_no_correction = build_grid(1.4, 1.2, rho=0.0)
    grid_with_correction = build_grid(1.4, 1.2, rho=-0.1)

    assert grid_with_correction[0, 0] > grid_no_correction[0, 0]
    assert grid_with_correction[1, 1] > grid_no_correction[1, 1]
