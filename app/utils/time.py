from datetime import datetime
from app.config import Config


def get_current_time():
    return datetime.now(Config.TIME_ZONE).isoformat()
