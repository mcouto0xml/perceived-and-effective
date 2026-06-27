"""FastAPI application entry point."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from src.api.routes import auth, appraisals, tasks
from src.core.config import settings
from src.core.database import create_tables
from src.pipeline.gitlab_sync.sync import run_sync

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Perceived & Effective API")

app.include_router(auth.router)
app.include_router(appraisals.router)
app.include_router(tasks.router)

scheduler = BackgroundScheduler()


@app.on_event("startup")
def startup():
    create_tables()
    scheduler.add_job(
        run_sync,
        "interval",
        minutes=settings.poll_interval_minutes,
        id="gitlab_sync",
        replace_existing=True,
    )
    scheduler.start()


@app.on_event("shutdown")
def shutdown():
    scheduler.shutdown(wait=False)
