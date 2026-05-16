import tomllib
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[4]


def mlflow_version() -> str:
    lock = REPO_DIR / "packages" / "ml" / "uv.lock"
    data = tomllib.loads(lock.read_text())
    for pkg in data["package"]:
        if pkg["name"] == "mlflow":
            return pkg["version"]
    raise RuntimeError("mlflow not found in uv.lock")
