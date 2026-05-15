from apscheduler.schedulers.background import BackgroundScheduler
from app.services.email_service import send_daily_transaction_email

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def start_scheduler():
    scheduler.add_job(
        send_daily_transaction_email,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_transaction_email",
        replace_existing=True
    )

    scheduler.start()