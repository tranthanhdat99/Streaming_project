# utils/logging_utils.py

import os
import logging
from logging.handlers import RotatingFileHandler
import config

def get_logger(name: str, dir_key: str, file_key: str) -> logging.Logger:
    """
    Returns a logger configured with a RotatingFileHandler.
    
    - name: logger name (e.g. "Producer", "Consumer2")
    - dir_key: one of config.LOG_DIRS keys ("consumer_1", "producer", "consumer_2")
    - file_key: one of config.LOG_FILES keys ("consumer_1", "producer", "consumer_2")
    """
    log_dir  = config.LOG_DIRS[dir_key]
    log_file = config.LOG_FILES[file_key]
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    # Avoid adding duplicate handlers if called multiple times
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = RotatingFileHandler(
            filename=os.path.join(log_dir, log_file),
            maxBytes=config.MAX_LOG_BYTES,
            backupCount=config.BACKUP_COUNT
        )
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(handler)
    return logger
