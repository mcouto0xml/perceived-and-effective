"""FastAPI application entry point for the agents service."""

import logging

from fastapi import FastAPI

# Config must be imported first so GOOGLE_API_KEY is set before the ADK agents are initialised.
import src.core.config  # noqa: F401

from src.routes import appraisal, recommendation

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Perceived & Effective — Agents")

app.include_router(appraisal.router)
app.include_router(recommendation.router)
