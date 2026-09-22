"""
Background Collection & Index Scheduler using APScheduler.
Coordinates periodic data acquisition and daily APIx index recalculations.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import date
from backend.app.db.database import SessionLocal

logger = logging.getLogger("airfare_x.scheduler")

scheduler = BackgroundScheduler()


def scheduled_daily_pipeline():
    """Daily pipeline run at 05:30 UTC / 11:00 IST."""
    logger.info("Executing scheduled daily airfare collection and index calculation...")
    db = SessionLocal()
    try:
        from backend.app.ingestion.collector import collector
        from backend.app.index.calculator import index_calculator

        # 1. Collect today's quotes
        collect_res = collector.run_collection(db, target_date=date.today())
        logger.info(f"Daily collection completed: {collect_res.get('records_inserted')} records.")

        # 2. Calculate today's index
        idx_res = index_calculator.calculate_daily_index(db, target_date=date.today())
        logger.info(f"Daily index calculation completed: APIx = {idx_res.get('index_value')}")

    except Exception as e:
        logger.error(f"Error in scheduled daily pipeline: {e}")
    finally:
        db.close()


def start_scheduler():
    """Starts the background scheduler if not already running."""
    if not scheduler.running:
        # Schedule daily at 05:30 UTC
        scheduler.add_job(
            scheduled_daily_pipeline,
            trigger=CronTrigger(hour=5, minute=30),
            id="daily_airfare_pipeline",
            name="Daily Airfare Collection & APIx Index",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler initialized: Scheduled daily run at 05:30 UTC.")


def shutdown_scheduler():
    """Safely shuts down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
