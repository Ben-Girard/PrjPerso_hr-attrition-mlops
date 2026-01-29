from __future__ import annotations

import os

from sqlalchemy import create_engine


def get_database_url() -> str:
    """
    Retourne DATABASE_URL si présent, sinon reconstruit depuis DB_*.
    On ne charge PAS les .env ici : c'est le job de env.load_env() dans les scripts/app.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "technova_attrition")
    user = os.getenv("DB_USER", "technova")
    pwd = os.getenv("DB_PASSWORD", "technova_pwd")

    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}"


def get_engine():
    url = get_database_url()

    # Supabase: SSL requis si oublié sslmode=require
    connect_args = {}
    if "supabase.co" in url and "sslmode" not in url:
        connect_args = {"sslmode": "require"}

    return create_engine(url, pool_pre_ping=True, connect_args=connect_args)
