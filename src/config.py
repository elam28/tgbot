import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger('BOT')

def load_config():
    logger.info("Loading configuration")
    load_dotenv('data/.env')
    config = {
        'API_ID': os.getenv('TELEGRAM_API_ID'),
        'API_HASH': os.getenv('TELEGRAM_API_HASH'),
        'PHONE_NUMBER': os.getenv('PHONE_NUMBER'),
        'SESSION_FILE': 'session/telegram.session',
        'PERSISTENT_DATA_FILE': 'data/persistent_data.json',
        'MAX_CONCURRENT_SENDS': int(os.getenv('MAX_CONCURRENT_SENDS', 10)),
        'RATE_LIMIT_MESSAGES': int(os.getenv('RATE_LIMIT_MESSAGES', 30)),
        'RATE_LIMIT_PERIOD': int(os.getenv('RATE_LIMIT_PERIOD', 60)),
        'RETRY_ATTEMPTS': int(os.getenv('RETRY_ATTEMPTS', 3)),
        'RETRY_DELAY': int(os.getenv('RETRY_DELAY', 60)),
        'HEALTH_CHECK_INTERVAL': int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),
        'LOG_ROTATION_INTERVAL': int(os.getenv('LOG_ROTATION_INTERVAL', 86400)),
        'DYNAMIC_UPDATE_INTERVAL': int(os.getenv('DYNAMIC_UPDATE_INTERVAL', 3600)),
        'ANALYTICS_INTERVAL': int(os.getenv('ANALYTICS_INTERVAL', 3600)),
        'BACKUP_INTERVAL': int(os.getenv('BACKUP_INTERVAL', 86400)),
        'REPORT_INTERVAL': int(os.getenv('REPORT_INTERVAL', 86400)),
        'ERROR_THRESHOLD': int(os.getenv('ERROR_THRESHOLD', 5)),
        'COOLDOWN_DURATION': int(os.getenv('COOLDOWN_DURATION', 3600)),
        'BASE_INTERVAL': int(os.getenv('BASE_INTERVAL', 30)),
        'MAX_INTERVAL': int(os.getenv('MAX_INTERVAL', 3600)),
        'MESSAGE_INTERVAL': float(os.getenv('MESSAGE_INTERVAL', 18)),  # New setting
    }
    logger.info("Configuration loaded successfully")
    return config
