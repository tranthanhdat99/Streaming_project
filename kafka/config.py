# config.py

import os
from configparser import ConfigParser

DEFAULT_CONF_PATH = os.path.join(
    os.path.dirname(__file__),
    'config', 'kafka', 'settings.conf'
)

# 1) Load defaults from settings.conf
conf = ConfigParser()
conf.read(os.getenv('APP_CONF', DEFAULT_CONF_PATH))

def get(section: str, key: str, *, fallback=None):
    """First try ENV VAR override, then settings.conf, then fallback."""
    env_key = f"{section.upper()}_{key.upper()}"
    if env_key in os.environ:
        return os.environ[env_key]
    if conf.has_option(section, key):
        return conf.get(section, key)
    return fallback

def get_int(section: str, key: str, *, fallback=None):
    val = get(section, key, fallback=None)
    try:
        return int(val)
    except (TypeError, ValueError):
        return fallback

# Build each config dict:
SOURCE_KAFKA = {
    'bootstrap.servers': get('kafka_source', 'bootstrap.servers'),
    'security.protocol':  get('kafka_source', 'security.protocol'),
    'sasl.mechanism':     get('kafka_source', 'sasl.mechanism'),
    'sasl.username':      get('kafka_source', 'sasl.username'),
    'sasl.password':      get('kafka_source', 'sasl.password'),
    'group.id':           get('kafka_source', 'group.id'),
    'auto.offset.reset':  get('kafka_source', 'auto.offset.reset'),
}

DEST_KAFKA = {
    'bootstrap.servers': get('kafka_dest', 'bootstrap.servers'),
    'security.protocol': get('kafka_dest', 'security.protocol'),
    'sasl.mechanism':    get('kafka_dest', 'sasl.mechanism'),
    'sasl.username':     get('kafka_dest', 'sasl.username'),
    'sasl.password':     get('kafka_dest', 'sasl.password'),
}

LOCAL_KAFKA = {
    'bootstrap.servers': get('kafka_local', 'bootstrap.servers'),
    'group.id':           get('kafka_local', 'group.id'),
    'auto.offset.reset':  get('kafka_local', 'auto.offset.reset'),
    'security.protocol':  get('kafka_local', 'security.protocol'),
    'sasl.mechanism':     get('kafka_local', 'sasl.mechanism'),
    'sasl.username':      get('kafka_local', 'sasl.username'),
    'sasl.password':      get('kafka_local', 'sasl.password'),
}

TOPICS = {
    'source':       get('topics', 'source'),
    'intermediate': get('topics', 'intermediate'),
}

MONGODB = {
    'uri':                    get('mongodb', 'uri'),
    'database':               get('mongodb', 'database'),
    'collection':             get('mongodb', 'collection'),
    'serverSelectionTimeoutMS': get_int('mongodb', 'serverSelectionTimeoutMS'),
}

LOG_DIRS = {
    'consumer_1': get('logging', 'consumer_1_dir'),
    'producer':   get('logging', 'producer_dir'),
    'consumer_2': get('logging', 'consumer_2_dir'),
}

LOG_FILES = {
    'consumer_1': get('logging', 'consumer_1_file'),
    'producer':   get('logging', 'producer_file'),
    'consumer_2': get('logging', 'consumer_2_file'),
}

MAX_LOG_BYTES = get_int('logging', 'max_bytes', fallback=5 * 1024 * 1024)
BACKUP_COUNT  = get_int('logging', 'backup_count', fallback=10)
