import re
import sys
from pathlib import Path

from sqlalchemy import Column, ForeignKey

from match_predictor.db_models import Base

REPO_ROOT = Path(__file__).resolve().parents[3]
README_PATH = REPO_ROOT / "README.md"

START_MARKER = "<!-- DB-SCHEMA:START -->"
END_MARKER = "<!-- DB-SCHEMA:END -->"

TYPE_MAP = {
    "VARCHAR": "string",
    "TEXT": "string",
    "INTEGER": "int",
    "BIGINT": "bigint",
    "FLOAT": "float",
    "REAL": "float",
    "NUMERIC": "decimal",
    "BOOLEAN": "bool",
    "DATETIME": "datetime",
    "TIMESTAMP": "timestamp",
    "DATE": "date",
}


def _column_type(column: Column) -> str:
    raw = str(column.type).upper().split("(")[0]
    return TYPE_MAP.get(raw, raw.lower())


def _column_marker(column: Column) -> str:
    if column.primary_key:
        return "PK"
    if column.foreign_keys:
        return "FK"
    return ""


def _render_table(name: str, columns: list[Column]) -> list[str]:
    lines = [f"  {name.upper()} {{"]
    for column in columns:
        marker = _column_marker(column)
        nullable = "" if column.nullable is False else " \"nullable\""
        col_type = _column_type(column)
        line = f"    {col_type} {column.name}"
        if marker:
            line += f" {marker}"
        if nullable:
            line += nullable
        lines.append(line)
    lines.append("  }")
    return lines


def _render_diagram() -> str:
    lines = ["```mermaid", "erDiagram"]

    for table in Base.metadata.sorted_tables:
        lines.extend(_render_table(table.name, list(table.columns)))

    for table in Base.metadata.sorted_tables:
        for column in table.columns:
            for fk in column.foreign_keys:
                target = fk.column.table.name
                lines.append(f"  {target.upper()} ||--o{{ {table.name.upper()} : \"{column.name}\"")

    lines.append("```")
    return "\n".join(lines)


def _update_readme(diagram: str) -> bool:
    text = README_PATH.read_text()
    block = f"{START_MARKER}\n{diagram}\n{END_MARKER}"

    if START_MARKER in text and END_MARKER in text:
        pattern = re.compile(
            re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
            re.DOTALL,
        )
        new_text = pattern.sub(block, text)
    else:
        section = (
            "\n## Database schema\n\n"
            "_Auto-generated from `packages/ml/src/match_predictor/db_models.py` — "
            "run `pnpm db:diagram` to refresh._\n\n"
            f"{block}\n"
        )
        new_text = text.rstrip() + "\n" + section

    if new_text == text:
        return False
    README_PATH.write_text(new_text)
    return True


def main() -> None:
    diagram = _render_diagram()

    if "--check" in sys.argv:
        text = README_PATH.read_text()
        if f"{START_MARKER}\n{diagram}\n{END_MARKER}" in text:
            print("DB schema diagram is up to date.")
            return
        print(
            "DB schema diagram in README.md is out of sync with db_models.py.\n"
            "Run `pnpm db:diagram` to update it.",
            file=sys.stderr,
        )
        sys.exit(1)

    if _update_readme(diagram):
        print(f"Updated {README_PATH}")
    else:
        print("DB diagram already up to date.")


main()
