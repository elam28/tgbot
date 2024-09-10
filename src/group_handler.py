from src.cache import Cache
from src.logger import get_logger
import os

logger = get_logger()
cache = Cache()

def load_groups():
    logger.info("Loading groups")
    cached_groups = cache.get_groups()
    if cached_groups:
        logger.info(f"Loaded {len(cached_groups)} groups from cache")
        return cached_groups
    with open('data/groups.txt', 'r') as f:
        groups = [line.strip() for line in f if line.strip()]
    cache.set_groups(groups)
    logger.info(f"Loaded {len(groups)} groups from file and updated cache")
    return groups

def load_blacklist():
    logger.info("Loading blacklist")
    cached_blacklist = cache.get_blacklist()
    if cached_blacklist:
        logger.info(f"Loaded {len(cached_blacklist)} blacklisted items from cache")
        return cached_blacklist
    with open('data/blacklist.txt', 'r') as f:
        blacklist = [line.strip() for line in f if line.strip()]
    cache.set_blacklist(blacklist)
    logger.info(f"Loaded {len(blacklist)} blacklisted items from file and updated cache")
    return blacklist

def add_to_blacklist(group):
    logger.info(f"Adding group to blacklist: {group}")
    with open('data/blacklist.txt', 'a') as f:
        f.write(f"{group}\n")
    blacklist = cache.get_blacklist()
    blacklist.append(group)
    cache.set_blacklist(blacklist)
    logger.info(f"Added {group} to blacklist. Total blacklisted: {len(blacklist)}")

def update_groups_dynamically():
    logger.info("Updating groups dynamically")
    new_groups = load_groups()
    cache.set_groups(new_groups)
    logger.info(f"Updated groups. Total groups: {len(new_groups)}")

def update_messages_dynamically():
    logger.info("Updating messages dynamically")
    message_files = [f for f in os.listdir('data') if f.startswith('messages') and f.endswith('.txt')]
    for file in message_files:
        with open(os.path.join('data', file), 'r') as f:
            content = f.read().strip()
        cache.set_message(file, content)
    logger.info(f"Updated {len(message_files)} message files")
