"""Persist three timing settings and optional worker configuration."""
from dataclasses import asdict, dataclass, field
import json
import logging
from pathlib import Path
import math


@dataclass
class Settings:
    note_delay_ms: int = 100
    key_hold_ms: int = 35
    start_delay_s: float = 3.0
    humanize: bool = True
    language: str = "ru"
    ahk_executable_path: str = ""
    send_mode: str = "Event"
    selected_song_id: str = "beastars-pf-solo"
    deleted_song_ids: list[str] = field(default_factory=list)
    song_timings: dict[str, dict[str, int | float]] = field(default_factory=dict)
    sheet_overrides: dict[str, str] = field(default_factory=dict)
    hotkey_toggle: str = "F6"
    hotkey_stop: str = "F7"
    hotkey_emergency: str = "F8"


class SettingsStore:
    def __init__(self, path: Path):
        self.path = path

    def load(self) -> Settings:
        settings = Settings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Settings must be a JSON object")
            # Accept older field name without retaining obsolete speed/pause controls.
            settings.note_delay_ms = self._integer(data.get("note_delay_ms", data.get("base_interval_ms", 100)), 20, 500, 100)
            settings.key_hold_ms = self._integer(data.get("key_hold_ms", 35), 5, 200, 35)
            if isinstance(data.get("humanize"), bool):
                settings.humanize = data["humanize"]
            delay = data.get("start_delay_s", 3.0)
            if isinstance(delay, (int, float)) and not isinstance(delay, bool) and math.isfinite(delay):
                settings.start_delay_s = round(min(10.0, max(0.0, delay)), 1)
            for name in ("ahk_executable_path", "selected_song_id", "hotkey_toggle", "hotkey_stop", "hotkey_emergency"):
                value = data.get(name)
                if isinstance(value, str) and not any(char in value for char in "\t\r\n"):
                    setattr(settings, name, value)
            if data.get("send_mode") in ("Event", "Input"):
                settings.send_mode = data["send_mode"]
            from app.i18n import LANGUAGES
            if isinstance(data.get("language"), str) and data["language"] in {code for code, _, _ in LANGUAGES}:
                settings.language = data["language"]
            deleted = data.get("deleted_song_ids")
            if isinstance(deleted, list):
                settings.deleted_song_ids = list(dict.fromkeys(
                    value for value in deleted if isinstance(value, str) and value
                    and not any(char in value for char in "\t\r\n")))
            timings = data.get("song_timings")
            if isinstance(timings, dict):
                for song_id, values in timings.items():
                    if not isinstance(song_id, str) or not isinstance(values, dict):
                        continue
                    delay = values.get("start_delay_s", 3.0)
                    if not isinstance(delay, (int, float)) or isinstance(delay, bool) or not math.isfinite(delay):
                        delay = 3.0
                    settings.song_timings[song_id] = {
                        "note_delay_ms": self._integer(values.get("note_delay_ms"), 20, 500, settings.note_delay_ms),
                        "key_hold_ms": self._integer(values.get("key_hold_ms"), 5, 200, settings.key_hold_ms),
                        "start_delay_s": round(min(10.0, max(0.0, delay)), 1),
                    }
            overrides = data.get("sheet_overrides")
            if isinstance(overrides, dict):
                settings.sheet_overrides = {key: value for key, value in overrides.items() if isinstance(key, str) and isinstance(value, str)}
            # Old Roblox focus restrictions are intentionally discarded on migration.
        except (OSError, ValueError, TypeError):
            logging.info("Using default settings", exc_info=self.path.exists())
        self.save(settings)
        return settings

    @staticmethod
    def _integer(value: object, low: int, high: int, default: int) -> int:
        if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            return min(high, max(low, round(value)))
        return default

    def save(self, settings: Settings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(self.path)
