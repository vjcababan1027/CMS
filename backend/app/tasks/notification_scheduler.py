from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.parent_notification_service import run_biweekly_dispatch, run_high_risk_dispatch

_scheduler = None


def _biweekly_job():
    db = SessionLocal()
    try:
        run_biweekly_dispatch(db)
    finally:
        db.close()


def _high_risk_job():
    db = SessionLocal()
    try:
        run_high_risk_dispatch(db)
    finally:
        db.close()


def start_notification_scheduler():
    global _scheduler

    if not settings.NOTIFICATIONS_ENABLED:
        return None

    if _scheduler and _scheduler.running:
        return _scheduler

    scheduler = BackgroundScheduler(timezone="UTC")

    scheduler.add_job(
        _biweekly_job,
        trigger="interval",
        days=settings.BIWEEKLY_REPORT_INTERVAL_DAYS,
        id="biweekly_parent_reports",
        replace_existing=True,
    )
    scheduler.add_job(
        _high_risk_job,
        trigger="interval",
        minutes=settings.HIGH_RISK_SCAN_INTERVAL_MINUTES,
        id="high_risk_parent_alerts",
        replace_existing=True,
    )

    scheduler.start()
    _scheduler = scheduler
    return _scheduler


def stop_notification_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None
