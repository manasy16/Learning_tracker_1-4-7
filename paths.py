from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "LearningTracker147"

DATA_DIR = Path(user_data_dir(APP_NAME, appauthor=False))
DB_PATH = DATA_DIR / "learning.db"
CONFIG_PATH = DATA_DIR / "config.json"
LOG_DIR = DATA_DIR / "logs"


def ensure_data_dirs():
    if DATA_DIR.exists() and not DATA_DIR.is_dir():
        raise RuntimeError(f"Data path exists but is not a folder: {DATA_DIR}")
    if LOG_DIR.exists() and not LOG_DIR.is_dir():
        raise RuntimeError(f"Log path exists but is not a folder: {LOG_DIR}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
