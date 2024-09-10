import json
import time
import shutil
from collections import OrderedDict
from src.config import load_config
from src.logger import get_logger

logger = get_logger()
config = load_config()
flood_wait_times = OrderedDict()
slow_mode_wait_times = OrderedDict()
error_frequency = OrderedDict()
cooldown_times = OrderedDict()

def load_persistent_data():
    global flood_wait_times, slow_mode_wait_times, error_frequency, cooldown_times
    logger.info("Loading persistent data")
    try:
        with open(config['PERSISTENT_DATA_FILE'], 'r') as f:
            data = json.load(f)
            flood_wait_times = OrderedDict((k, v) for k, v in data.get('flood_wait_times', {}).items() if v > time.time())
            slow_mode_wait_times = OrderedDict((k, v) for k, v in data.get('slow_mode_wait_times', {}).items() if v > time.time())
            error_frequency = OrderedDict(data.get('error_frequency', {}))
            cooldown_times = OrderedDict((k, v) for k, v in data.get('cooldown_times', {}).items() if v > time.time())
        logger.info(f"Loaded {len(flood_wait_times)} flood wait, {len(slow_mode_wait_times)} slow mode, {len(error_frequency)} error frequency, and {len(cooldown_times)} cooldown entries")
    except FileNotFoundError:
        logger.info("No persistent data file found. Starting with empty data.")
    except json.JSONDecodeError:
        logger.error("Error decoding persistent data file. Starting with empty data.")

def save_persistent_data():
    logger.info("Saving persistent data")
    data = {
        'flood_wait_times': dict(flood_wait_times),
        'slow_mode_wait_times': dict(slow_mode_wait_times),
        'error_frequency': dict(error_frequency),
        'cooldown_times': dict(cooldown_times)
    }
    with open(config['PERSISTENT_DATA_FILE'], 'w') as f:
        json.dump(data, f)
    logger.info(f"Saved {len(flood_wait_times)} flood wait, {len(slow_mode_wait_times)} slow mode, {len(error_frequency)} error frequency, and {len(cooldown_times)} cooldown entries")
    backup_persistent_data()

def backup_persistent_data():
    src = config['PERSISTENT_DATA_FILE']
    dst = f"{src}.backup"
    shutil.copy2(src, dst)
    logger.info(f"Created backup of persistent data: {dst}")

def clean_wait_times():
    global flood_wait_times, slow_mode_wait_times, cooldown_times
    logger.info("Cleaning wait times")
    current_time = time.time()
    flood_wait_times = OrderedDict((k, v) for k, v in flood_wait_times.items() if v > current_time)
    slow_mode_wait_times = OrderedDict((k, v) for k, v in slow_mode_wait_times.items() if v > current_time)
    cooldown_times = OrderedDict((k, v) for k, v in cooldown_times.items() if v > current_time)
    logger.info(f"Cleaned to {len(flood_wait_times)} flood wait, {len(slow_mode_wait_times)} slow mode, and {len(cooldown_times)} cooldown entries")
    save_persistent_data()

def update_error_frequency(group):
    error_frequency[group] = error_frequency.get(group, 0) + 1
    logger.info(f"Updated error frequency for {group}: {error_frequency[group]}")
    if error_frequency[group] > config['ERROR_THRESHOLD']:
        cooldown_times[group] = time.time() + config['COOLDOWN_DURATION']
        logger.info(f"Added {group} to cooldown for {config['COOLDOWN_DURATION']} seconds due to frequent errors")
    save_persistent_data()

def get_adjusted_interval(group):
    frequency = error_frequency.get(group, 0)
    base_interval = config['BASE_INTERVAL']
    adjusted_interval = base_interval * (2 ** frequency)
    max_interval = config['MAX_INTERVAL']
    final_interval = min(adjusted_interval, max_interval)
    logger.info(f"Adjusted interval for {group}: {final_interval:.2f} seconds")
    return final_interval
