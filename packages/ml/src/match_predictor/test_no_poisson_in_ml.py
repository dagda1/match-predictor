import ast
from pathlib import Path

ML_FILES = [
    "model.py",
    "generate_predictions.py",
    "generate_upcoming.py",
]

PACKAGE_DIR = Path(__file__).parent

BANNED_PATTERNS = ["poisson", "rng.poisson", "np.random.default_rng"]


def _extract_ml_poisson_usage(filepath: Path) -> list[str]:
    source = filepath.read_text()
    tree = ast.parse(source)
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "poisson":
            violations.append(
                f"{filepath.name}:{node.lineno} uses .poisson()"
            )

    return violations


def test_no_poisson_in_ml_prediction_path():
    violations = []
    for filename in ML_FILES:
        filepath = PACKAGE_DIR / filename
        assert filepath.exists(), f"{filename} not found"
        violations.extend(_extract_ml_poisson_usage(filepath))

    assert violations == [], (
        "Poisson found in ML prediction path:\n" + "\n".join(violations)
    )
