import logging
import os
import sys

import db
import settings as cfg

logger = logging.getLogger(__name__)

# ─── Input API ────────────────────────────────────────────────────────────────

class InputApi:
    def __init__(self):
        self.window = None

    def save_topic(self, topic: str) -> dict:
        topic = (topic or "").strip()
        if not topic:
            return {"status": "error", "message": "Empty"}
        try:
            db.add_topic(topic)
            return {"status": "ok", "count": db.get_topics_logged_today()}
        except Exception as e:
            logger.exception("Failed to save topic")
            return {"status": "error", "message": str(e)}

    def get_today_count(self) -> int:
        try:
            return db.get_topics_logged_today()
        except Exception:
            logger.exception("Failed to read today's topic count")
            return 0

    def close(self):
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                logger.exception("Failed to close input window")

# ─── Revision API ─────────────────────────────────────────────────────────────

class RevisionApi:
    def __init__(self, due=None):
        self.window = None
        self._due   = due or []   # pre-loaded so no DB call from JS thread

    def get_due(self) -> list:
        return self._due

    def mark_done(self, topic_id: int, rev_num: int) -> dict:
        try:
            db.mark_revised(int(topic_id), int(rev_num))
            return {"status": "ok"}
        except Exception as e:
            logger.exception("Failed to mark revision done")
            return {"status": "error", "message": str(e)}

    def close(self):
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                logger.exception("Failed to close revision window")

# ─── Settings API ─────────────────────────────────────────────────────────────

class SettingsApi:
    def __init__(self, on_settings_saved=None):
        self.window = None
        self.on_settings_saved = on_settings_saved

    def get_settings(self) -> dict:
        try:
            return cfg.load()
        except Exception:
            logger.exception("Failed to load settings")
            return cfg.DEFAULTS.copy()

    def save_settings(self, data: dict) -> dict:
        try:
            cfg.save(data)
            if self.on_settings_saved:
                self.on_settings_saved()
            return {"status": "ok"}
        except Exception as e:
            logger.exception("Failed to save settings")
            return {"status": "error", "message": str(e)}

    def set_startup(self, enabled: bool) -> dict:
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            name = "LearningTracker147"
            if enabled:
                exe    = sys.executable.replace("python.exe", "pythonw.exe")
                script = os.path.abspath(sys.argv[0])
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{exe}" "{script}"')
            else:
                try:
                    winreg.DeleteValue(key, name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return {"status": "ok"}
        except Exception as e:
            logger.exception("Failed to update Windows startup setting")
            return {"status": "error", "message": str(e)}

    def close(self):
        if self.window:
            try:
                self.window.destroy()
            except Exception:
                logger.exception("Failed to close settings window")
