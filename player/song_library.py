"""Bundled songs and their playback presets; independent of user settings."""
from dataclasses import dataclass
import json
from pathlib import Path
import logging
import re
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SongPreset:
    id: str
    title: str
    artist: str
    difficulty: str
    sheet: str
    source_url: str
    practice_url: str
    note_delay_ms: int
    key_hold_ms: int
    start_delay_s: float
    timing_basis: str = "Тайминг ещё не проверен."
    practice_transpose: int = 0
    imported: bool = False
    custom: bool = False


def load_song_library(custom_directory: Path | None = None, excluded_ids=()) -> tuple[SongPreset, ...]:
    """Load bundled songs and optional local manual/MIDI library entries."""
    directory = Path(__file__).resolve().parents[1] / "assets/songs"
    entries = json.loads((directory / "catalog.json").read_text(encoding="utf-8"))
    songs = []
    for entry in entries:
        data = dict(entry)
        filename = data.pop("sheet_file")
        if Path(filename).name != filename or not filename.endswith(".txt"):
            raise ValueError("Invalid bundled sheet path")
        song = SongPreset(sheet=(directory / filename).read_text(encoding="utf-8"), **data)
        if not (20 <= song.note_delay_ms <= 500 and 5 <= song.key_hold_ms <= 200 and 0 <= song.start_delay_s <= 10):
            raise ValueError(f"Invalid timing preset: {song.id}")
        songs.append(song)
    if not songs or len({song.id for song in songs}) != len(songs):
        raise ValueError("The song catalog must have unique, nonempty entries")
    if custom_directory is not None and custom_directory.exists():
        for path in sorted(custom_directory.glob("*.json")):
            try:
                if path.stat().st_size > 32 * 1024 * 1024:
                    raise ValueError("Imported song is too large")
                data = json.loads(path.read_text(encoding="utf-8"))
                if not re.fullmatch(r"(?:midi|custom)-[0-9a-f]{32}", path.stem) or data.get("id") != path.stem:
                    raise ValueError("Invalid imported song ID")
                song = SongPreset(**data)
                if (not (song.imported or song.custom) or not isinstance(song.sheet, str)
                        or not isinstance(song.title, str) or not song.title.strip()):
                    raise ValueError("Invalid imported song")
                if not (20 <= song.note_delay_ms <= 500 and 5 <= song.key_hold_ms <= 200 and 0 <= song.start_delay_s <= 10):
                    raise ValueError("Invalid imported preset")
                songs.append(song)
            except (OSError, ValueError, TypeError, KeyError):
                logging.warning("Cannot load imported song: %s", path, exc_info=True)
    excluded = set(excluded_ids)
    return tuple(song for song in songs if song.id not in excluded)


def save_imported_song(directory: Path, title: str, sheet: str, summary: str) -> SongPreset:
    from player.parser import SheetParser
    from player.plan_writer import build_plan
    plan = build_plan(SheetParser().parse(sheet), 100, 35)
    if not any(event.keys for event in plan.events):
        raise ValueError("Импортированная партитура не содержит нот.")
    song = SongPreset(id="midi-" + uuid4().hex, title=" ".join(title.split())[:120] or "Imported MIDI",
                      artist="MIDI", difficulty="MIDI", sheet=sheet, source_url="", practice_url="",
                      note_delay_ms=100, key_hold_ms=35, start_delay_s=3.0, imported=True,
                      timing_basis="Точный тайминг и удержания из MIDI записаны в sheet. Note Delay и базовый Hold "
                                   "не заменяют явные интервалы и удержания. " + summary)
    _save_song(directory, song)
    return song


def save_custom_song(directory: Path, title: str, sheet: str, note_delay_ms: int = 100,
                     key_hold_ms: int = 35, start_delay_s: float = 3.0) -> SongPreset:
    """Save a named, validated manual sheet as its own independent library entry."""
    from player.parser import SheetParser
    from player.plan_writer import build_plan
    title = " ".join(title.split())[:120]
    if not title:
        raise ValueError("Enter a song title.")
    if not (20 <= note_delay_ms <= 500 and 5 <= key_hold_ms <= 200 and 0 <= start_delay_s <= 10):
        raise ValueError("Invalid timing preset")
    plan = build_plan(SheetParser().parse(sheet), note_delay_ms, key_hold_ms)
    if not any(event.keys for event in plan.events):
        raise ValueError("The sheet has no notes.")
    song = SongPreset(id="custom-" + uuid4().hex, title=title, sheet=sheet, custom=True,
                      artist="", difficulty="", source_url="", practice_url="",
                      note_delay_ms=note_delay_ms, key_hold_ms=key_hold_ms, start_delay_s=start_delay_s)
    _save_song(directory, song)
    return song


def _save_song(directory: Path, song: SongPreset) -> None:
    from dataclasses import asdict
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / (song.id + ".json")
    temporary = directory / (song.id + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(asdict(song), stream, ensure_ascii=False, indent=2)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
