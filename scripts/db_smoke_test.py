from __future__ import annotations

from sqlalchemy import text

from technova_attrition.db import get_engine
from technova_attrition.env import load_env


def main() -> None:
    load_env()

    engine = get_engine()
    with engine.connect() as conn:
        n_emp = conn.execute(text("SELECT COUNT(*) FROM employees")).scalar_one()
        n_pred = conn.execute(text("SELECT COUNT(*) FROM predictions")).scalar_one()

    print("✅ DB smoke test")
    print("employees:", n_emp)
    print("predictions:", n_pred)


if __name__ == "__main__":
    main()
