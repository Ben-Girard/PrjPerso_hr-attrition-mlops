from __future__ import annotations

from fastapi import FastAPI

from technova_attrition.api.routers.predict import router as predict_router

app = FastAPI(
    title="TechNova Attrition API",
    version="1.0.0",
    description="API de scoring de probabilité de démission (POC) avec traçabilité DB.",
)

app.include_router(predict_router)
