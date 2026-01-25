import importlib

import pytest
from fastapi.testclient import TestClient

from technova_attrition.api.settings import reset_config_cache
from technova_attrition.db import get_engine
from technova_attrition.serving_db_ops import apply_schema, truncate_predictions


@pytest.fixture(scope="session")
def engine():
    eng = get_engine()
    apply_schema(eng)
    return eng


@pytest.fixture(autouse=True)
def _test_env(monkeypatch):
    # Empêche tout dotenv de polluer
    monkeypatch.setenv("SKIP_DOTENV", "1")

    # Config test
    monkeypatch.setenv("API_KEY", "test_key")
    monkeypatch.setenv("MODEL_THRESHOLD", "0.5")
    monkeypatch.setenv("MODEL_VERSION", "test")

    # DB docker locale (assure-toi que docker compose up -d tourne)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://technova:technova_pwd@localhost:5432/technova_attrition",
    )

    reset_config_cache()


@pytest.fixture(autouse=True)
def clean_predictions(engine):
    truncate_predictions(engine)
    yield


@pytest.fixture()
def client():
    import technova_attrition.api.main as main

    importlib.reload(main)
    return TestClient(main.app)
