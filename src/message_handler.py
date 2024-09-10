import asyncio
import random
import os
import time
from telethon import errors
from src.group_handler import load_groups, load_blacklist, add_to_blacklist
from src.data_handler import flood_wait_times, slow_mode_wait_times, cooldown_times, save_persistent_data, update_error_frequency, get_adjusted_interval
from src.logger import get_logger, generate_session_id
from src.cache import Cache
from src.config import load_config

logger = get_logger()
cache = Cache()
config = load_config()

rate_limit = asyncio.Semaphore(config['RATE_LIMIT_MESSAGES'])

async def send_message(client, group, message, session_id):
    current_time = time.time()
    if group in flood_wait_times and current_time < flood_wait_times[group]:
        logger.debug(f"[{session_id}] Skipping {group} due to active FloodWaitError. Time remaining: {int(flood_wait_times[group] - current_time)} seconds")
        return
    if group in slow_mode_wait_times and current_time < slow_mode_wait_times[group]:
        logger.debug(f"[{session_id}] Skipping {group} due to SlowModeWaitError. Time remaining: {int(slow_mode_wait_times[group] - current_time)} seconds")
        return
    if group in cooldown_times and current_time < cooldown_times[group]:
        logger.debug(f"[{session_id}] Skipping {group} due to cooldown. Time remaining: {int(cooldown_times[group] - current_time)} seconds")
        return

    try:
        async with rate_limit:
            logger.debug(f"[{session_id}] Sending message to group: {group}")
            start_time = time.time()
            await client.send_message(group, message)
            end_time = time.time()
            send_time = end_time - start_time
            logger.info(f"[{session_id}] Message sent to {group}. Time taken: {send_time:.2f} seconds")
            cache.update_group_performance(group, send_time, True)
            await asyncio.sleep(config['MESSAGE_INTERVAL'])  # Add delay between messages
    except errors.FloodWaitError as e:
        wait_time = e.seconds
        logger.warning(f"[{session_id}] FloodWaitError: Need to wait {wait_time} seconds for {group}")
        flood_wait_times[group] = current_time + wait_time + get_adjusted_interval(group)
        update_error_frequency(group)
        cache.update_group_performance(group, 0, False)
        save_persistent_data()
    except errors.SlowModeWaitError as e:
        wait_time = e.seconds
        logger.warning(f"[{session_id}] SlowModeWaitError: Need to wait {wait_time} seconds for {group}")
        slow_mode_wait_times[group] = current_time + wait_time + get_adjusted_interval(group)
        update_error_frequency(group)
        cache.update_group_performance(group, 0, False)
        save_persistent_data()
    except errors.ChatWriteForbiddenError:
        logger.error(f"[{session_id}] ChatWriteForbiddenError: Cannot send message to {group}. Bot might not have permission.")
        add_to_blacklist(group)
        logger.info(f"[{session_id}] Added {group} to blacklist due to ChatWriteForbiddenError")
    except errors.UserBannedInChannelError:
        logger.error(f"[{session_id}] UserBannedInChannelError: Bot is banned from sending messages in {group}")
        add_to_blacklist(group)
        logger.info(f"[{session_id}] Added {group} to blacklist due to UserBannedInChannelError")
    except Exception as e:
        logger.error(f"[{session_id}] Error sending message to {group}: {str(e)}", exc_info=True)
        update_error_frequency(group)
        cache.update_group_performance(group, 0, False)

async def send_mass_message(client):
    session_id = generate_session_id()
    logger.info(f"[{session_id}] Starting mass message send")
    groups = load_groups()
    blacklist = load_blacklist()
    valid_groups = [group for group in groups if group not in blacklist]
    random.shuffle(valid_groups)
    logger.info(f"[{session_id}] Sending messages to {len(valid_groups)} groups")

    message_queue = asyncio.Queue()
    
    async def process_message_queue():
        while True:
            group, message = await message_queue.get()
            await send_message(client, group, message, session_id)
            message_queue.task_done()

    tasks = []
    for _ in range(config['MAX_CONCURRENT_SENDS']):
        task = asyncio.create_task(process_message_queue())
        tasks.append(task)

    for group in valid_groups:
        message = get_random_message(group)
        await message_queue.put((group, message))

    await message_queue.join()

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    success_count = sum(1 for group in valid_groups if cache.get_group_performance(group)['success_count'] > 0)
    logger.info(f"[{session_id}] Mass message send completed. Success rate: {success_count}/{len(valid_groups)}")

def get_random_message(group):
    logger.debug(f"Selecting message for group: {group}")
    message_files = [f for f in os.listdir('data') if f.startswith('messages') and f.endswith('.txt')]
    chosen_file = random.choice(message_files)
    
    cached_message = cache.get_message(chosen_file)
    if cached_message:
        return cached_message
    
    with open(os.path.join('data', chosen_file), 'r') as f:
        message = f.read().strip()
    cache.set_message(chosen_file, message)
    return message
