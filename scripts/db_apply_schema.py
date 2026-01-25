from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from technova_attrition.db import get_engine
from technova_attrition.env import load_env


def main() -> None:
    load_env()

    engine = get_engine()
    sql_path = Path("sql/serving/01_schema.sql")
    sql = sql_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("✅ Schema applied")


if __name__ == "__main__":
    main()
