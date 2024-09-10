from collections import OrderedDict
from src.logger import get_logger
import time

logger = get_logger()

class Cache:
    def __init__(self, max_size=1000, eviction_policy='lru'):
        self.messages = OrderedDict()
        self.groups = OrderedDict()
        self.blacklist = set()
        self.message_rotation = OrderedDict()
        self.group_performance = OrderedDict()
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        logger.info(f"Cache initialized with max size: {max_size} and eviction policy: {eviction_policy}")

    def _evict(self, cache):
        if self.eviction_policy == 'lru':
            cache.popitem(last=False)
        elif self.eviction_policy == 'lfu':
            min_freq = min(cache.values(), key=lambda x: x['frequency'])['frequency']
            for key, value in cache.items():
                if value['frequency'] == min_freq:
                    del cache[key]
                    break

    def _check_size(self, cache):
        if len(cache) > self.max_size:
            self._evict(cache)

    def set_message(self, file_name, content):
        self.messages[file_name] = {'content': content, 'frequency': 1, 'last_used': time.time()}
        self._check_size(self.messages)
        logger.debug(f"Cached message from file: {file_name}")

    def get_message(self, file_name):
        if file_name in self.messages:
            self.messages[file_name]['frequency'] += 1
            self.messages[file_name]['last_used'] = time.time()
            logger.debug(f"Cache hit for message file: {file_name}")
            return self.messages[file_name]['content']
        logger.debug(f"Cache miss for message file: {file_name}")
        return None

    def set_groups(self, groups):
        self.groups = OrderedDict.fromkeys(groups)
        logger.info(f"Updated cached groups. Total groups: {len(self.groups)}")

    def get_groups(self):
        logger.debug(f"Retrieving {len(self.groups)} groups from cache")
        return list(self.groups.keys())

    def set_blacklist(self, blacklist):
        self.blacklist = set(blacklist)
        logger.info(f"Updated cached blacklist. Total blacklisted: {len(self.blacklist)}")

    def get_blacklist(self):
        logger.debug(f"Retrieving {len(self.blacklist)} blacklisted items from cache")
        return list(self.blacklist)

    def update_message_rotation(self, group, message_index):
        self.message_rotation[group] = message_index
        self._check_size(self.message_rotation)
        logger.debug(f"Updated message rotation for group {group}: index {message_index}")

    def get_message_rotation(self, group):
        return self.message_rotation.get(group, -1)

    def update_group_performance(self, group, send_time, success):
        if group not in self.group_performance:
            self.group_performance[group] = {"total_time": 0, "count": 0, "success_count": 0}
        self.group_performance[group]["total_time"] += send_time
        self.group_performance[group]["count"] += 1
        if success:
            self.group_performance[group]["success_count"] += 1
        self._check_size(self.group_performance)
        logger.debug(f"Updated performance for group {group}: time {send_time:.2f}s, success: {success}")

    def get_group_performance(self, group):
        return self.group_performance.get(group, {"total_time": 0, "count": 0, "success_count": 0})
