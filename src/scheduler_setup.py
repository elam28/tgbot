from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.message_handler import send_mass_message
from src.data_handler import clean_wait_times, backup_persistent_data
from src.logger import get_logger, rotate_logs
from src.group_handler import update_groups_dynamically, update_messages_dynamically
from src.analytics import generate_analytics_report
from src.config import load_config

logger = get_logger()
config = load_config()

def setup_scheduler(client):
    logger.info("Setting up scheduler")
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(send_mass_message, 'interval', minutes=90, args=[client])
    logger.info(f"Scheduled mass message job to run every 90 minutes")
    
    scheduler.add_job(clean_wait_times, 'interval', hours=6)
    scheduler.add_job(rotate_logs, 'interval', hours=24)
    scheduler.add_job(update_groups_dynamically, 'interval', hours=1)
    scheduler.add_job(update_messages_dynamically, 'interval', hours=1)
    scheduler.add_job(generate_analytics_report, 'interval', hours=24)
    scheduler.add_job(backup_persistent_data, 'interval', hours=24)
    
    return scheduler
