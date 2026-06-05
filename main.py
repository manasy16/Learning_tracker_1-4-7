import logging
import os
import queue
import sys
import threading
import time
from pathlib import Path

import schedule
import webview
from PIL import Image, ImageDraw
from pystray import Icon, Menu, MenuItem

import db
import settings as cfg
from api import InputApi, RevisionApi, SettingsApi
from logging_setup import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

BASE_DIR = Path(sys.argv[0]).resolve().parent


def ui(filename: str) -> str:
    return (BASE_DIR / "ui" / filename).as_uri()


def get_screen_size():
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return width, height


screen_w, screen_h = 1920, 1080

INPUT_W, INPUT_H = 520, 295
REVISION_W, REVISION_H = 420, 400
SETTINGS_W, SETTINGS_H = 400, 285

ui_queue = queue.Queue()
schedule_lock = threading.Lock()
tray_icon = None
tray_ready = threading.Event()


def request_ui(action: str):
    ui_queue.put(action)


def notify_user(message: str, title: str = "Learning Tracker"):
    if not tray_ready.wait(timeout=5):
        logger.warning("Tray was not ready; skipped notification: %s", message)
        return

    try:
        tray_icon.notify(message, title)
    except Exception:
        logger.exception("Failed to show notification: %s", message)


def notify_due_revisions():
    try:
        due = db.get_due_today()
    except Exception:
        logger.exception("Failed to check due revisions for notification")
        return

    if not due:
        logger.info("No due revisions for startup notification")
        return

    count = len(due)
    topic_word = "topic" if count == 1 else "topics"
    notify_user(f"{count} revision {topic_word} due today.", "Revision Due")


def process_ui_queue():
    while True:
        try:
            action = ui_queue.get_nowait()
        except queue.Empty:
            return

        try:
            if action == "input":
                open_input()
            elif action == "revision":
                open_revision()
            elif action == "revision_check":
                open_revision(show_empty=True)
            elif action == "settings":
                open_settings()
            else:
                logger.warning("Unknown UI action requested: %s", action)
        except Exception:
            logger.exception("Failed to process UI action: %s", action)


def run_ui_dispatcher():
    while True:
        process_ui_queue()
        time.sleep(0.2)


def open_input():
    logger.info("Opening input window")
    api = InputApi()
    win = webview.create_window(
        "Log Today's Topic",
        ui("tray_input.html"),
        width=INPUT_W,
        height=INPUT_H,
        x=(screen_w - INPUT_W) // 2,
        y=(screen_h - INPUT_H) // 2,
        frameless=True,
        easy_drag=True,
        on_top=True,
        js_api=api,
    )
    api.window = win


def open_revision(show_empty: bool = False):
    due = db.get_due_today()
    if not due and not show_empty:
        logger.info("No revisions due today")
        return

    logger.info("Opening revision window with %s due item(s)", len(due))
    api = RevisionApi(due)
    win = webview.create_window(
        "Revision Due",
        ui("revision.html"),
        width=REVISION_W,
        height=REVISION_H,
        x=screen_w - REVISION_W - 24,
        y=screen_h - REVISION_H - 60,
        frameless=True,
        easy_drag=True,
        on_top=True,
        js_api=api,
    )
    api.window = win


def open_settings():
    logger.info("Opening settings window")
    api = SettingsApi(on_settings_saved=schedule_prompt)
    win = webview.create_window(
        "Settings",
        ui("settings.html"),
        width=SETTINGS_W,
        height=SETTINGS_H,
        x=(screen_w - SETTINGS_W) // 2,
        y=(screen_h - SETTINGS_H) // 2,
        frameless=True,
        easy_drag=True,
        on_top=True,
        js_api=api,
    )
    api.window = win


def _make_icon():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, 62, 62], fill="#f59e0b")
    draw.rectangle([18, 20, 28, 44], fill="black")
    draw.rectangle([28, 20, 46, 44], fill="#333")
    draw.line([28, 20, 28, 44], fill="#f59e0b", width=2)
    return img


def _t(action: str):
    def handler(icon, item):
        request_ui(action)

    return handler


def _exit(icon, item):
    logger.info("Exit requested from tray")
    icon.stop()
    os._exit(0)


def run_tray():
    global tray_icon

    icon = Icon(
        "LearningTracker147",
        _make_icon(),
        "Learning Tracker - 1-4-7",
        Menu(
            MenuItem("Log Today's Topic", _t("input")),
            MenuItem("Check Revisions", _t("revision_check")),
            MenuItem("Settings", _t("settings")),
            Menu.SEPARATOR,
            MenuItem("Exit", _exit),
        ),
    )
    tray_icon = icon

    def setup(icon):
        icon.visible = True
        tray_ready.set()

        def delayed_start_notification():
            time.sleep(0.5)
            notify_user("App is running in the background.", "Learning Tracker")

        threading.Thread(target=delayed_start_notification, daemon=True).start()

    icon.run(setup=setup)


def schedule_prompt():
    with schedule_lock:
        schedule.clear("daily_prompt")
        prompt_time = cfg.get("prompt_time")
        schedule.every().day.at(prompt_time).do(
            lambda: request_ui("input")
        ).tag("daily_prompt")
        logger.info("Scheduled daily prompt at %s", prompt_time)


def run_scheduler():
    schedule_prompt()
    while True:
        with schedule_lock:
            schedule.run_pending()
        time.sleep(30)


def on_started():
    threading.Thread(target=run_tray, daemon=False).start()
    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=run_ui_dispatcher, daemon=True).start()
    print("Learning Tracker is running in the background. Use the tray icon to open it.")

    def startup_revision_check():
        time.sleep(3)
        notify_due_revisions()

    threading.Thread(target=startup_revision_check, daemon=True).start()


if __name__ == "__main__":
    try:
        db.init_db()
        screen_w, screen_h = get_screen_size()

        webview.create_window(
            "",
            html="<body style='margin:0;background:#000'></body>",
            width=1,
            height=1,
            hidden=True,
            frameless=True,
            focus=False,
            x=0,
            y=0,
        )

        webview.start(on_started, private_mode=False, debug=False)
    except Exception:
        logger.exception("Failed to start Learning Tracker")
        raise
