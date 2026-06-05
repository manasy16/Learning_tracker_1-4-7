# Read/write config.json
import json
import re

from paths import CONFIG_PATH, ensure_data_dirs

DEFAULTS = {
    "prompt_time": "21:00",
    "startup": True,
}

TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def load() -> dict:
    ensure_data_dirs()

    if not CONFIG_PATH.exists():
        save(DEFAULTS.copy())
        return DEFAULTS.copy()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = DEFAULTS.copy()
        save(data)
        return data

    # Fill in any missing keys from new versions
    for k, v in DEFAULTS.items():
        if k not in data:
            data[k] = v

    if not _valid_prompt_time(data.get("prompt_time")):
        data["prompt_time"] = DEFAULTS["prompt_time"]

    data["startup"] = bool(data.get("startup"))
    return data


def save(config: dict):
    ensure_data_dirs()
    data = DEFAULTS.copy()
    data.update(config or {})

    if not _valid_prompt_time(data.get("prompt_time")):
        data["prompt_time"] = DEFAULTS["prompt_time"]

    data["startup"] = bool(data.get("startup"))

    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get(key):
    return load().get(key, DEFAULTS.get(key))


def set_key(key, value):
    config = load()
    config[key] = value
    save(config)


def _valid_prompt_time(value) -> bool:
    if not isinstance(value, str) or not TIME_RE.match(value):
        return False
    hour, minute = value.split(":")
    return 0 <= int(hour) <= 23 and 0 <= int(minute) <= 59
