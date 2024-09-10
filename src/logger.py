import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import uuid
import time
import psutil
import socket
import colorlog
from pythonjsonlogger import jsonlogger

class SessionIdFilter(logging.Filter):
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id

    def filter(self, record):
        record.session_id = self.session_id
        return True

def setup_logger(config):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    session_id = str(uuid.uuid4())[:8]
    session_filter = SessionIdFilter(session_id)
    
    file_handler = RotatingFileHandler(
        'logs/bot.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(session_filter)
    
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(message)s %(session_id)s',
        timestamp=True
    )
    file_handler.setFormatter(json_formatter)
    
    logger.addHandler(file_handler)
    
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(session_filter)
    
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s.%(msecs)03d - %(levelname)s - [%(session_id)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    
    logger.addHandler(console_handler)
    
    logging.TRACE = 5
    logging.addLevelName(logging.TRACE, "TRACE")
    
    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(logging.TRACE):
            self._log(logging.TRACE, message, args, **kwargs)
    
    logging.Logger.trace = trace
    
    return logger

def get_logger():
    return logging.getLogger(__name__)

def rotate_logs():
    logger = get_logger()
    for handler in logger.handlers:
        if isinstance(handler, (RotatingFileHandler, TimedRotatingFileHandler)):
            handler.doRollover()
    logger.info("Log file rotated")

def generate_session_id():
    return str(uuid.uuid4())[:8]

def log_system_info():
    logger = get_logger()
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logger.info(f"System Info - CPU: {cpu_percent}%, "
                f"Memory: {memory.percent}% used, "
                f"Disk: {disk.percent}% used")

def log_network_info():
    logger = get_logger()
    try:
        start_time = time.time()
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        latency = (time.time() - start_time) * 1000
        logger.info(f"Network latency: {latency:.2f} ms")
    except socket.error:
        logger.warning("Network connectivity issue detected")

class PerformanceLogger:
    def __init__(self):
        self.start_time = time.time()
        self.message_count = 0
        self.total_send_time = 0

    def log_message_sent(self, send_time):
        self.message_count += 1
        self.total_send_time += send_time

    def log_session_performance(self):
        logger = get_logger()
        session_duration = time.time() - self.start_time
        avg_send_time = self.total_send_time / self.message_count if self.message_count > 0 else 0
        logger.info(f"Session Performance - Duration: {session_duration:.2f}s, "
                    f"Messages Sent: {self.message_count}, "
                    f"Avg Send Time: {avg_send_time:.2f}s")

performance_logger = PerformanceLogger()

def log_message_sent(send_time):
    performance_logger.log_message_sent(send_time)

def log_session_performance():
    performance_logger.log_session_performance()
