import logging

from paths import LOG_DIR, ensure_data_dirs


def setup_logging():
    ensure_data_dirs()

    logging.basicConfig(
        filename=str(LOG_DIR / "app.log"),
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.getLogger("pywebview").setLevel(logging.WARNING)
