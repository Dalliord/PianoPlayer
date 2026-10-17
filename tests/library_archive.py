"""Historical scores remain testable without appearing in the app library."""
import json
from pathlib import Path
from player.song_library import SongPreset, load_song_library


def load_historical_library():
    directory = Path(__file__).resolve().parents[1] / "assets/songs"
    songs = list(load_song_library())
    for entry in json.loads((directory / "archive/catalog.json").read_text(encoding="utf-8")):
        data = dict(entry)
        sheet = (directory / data.pop("sheet_file")).read_text(encoding="utf-8")
        songs.append(SongPreset(sheet=sheet, **data))
    return tuple(songs)
