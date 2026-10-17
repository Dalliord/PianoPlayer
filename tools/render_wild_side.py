"""Render the video-derived Wild Side arrangement using the player's timings."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player.song_library import load_song_library
from tools.build_wild_side import DURATION_MS, NOTE_DELAY_MS, SONG_ID, SOURCE_START_FRAME
from tools.render_song import collect_notes, write_midi
from tools.render_wolf_last_dawn import write_exact_wav


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--humanize", action="store_true")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    song = next(s for s in load_song_library() if s.id == SONG_ID)
    if song.note_delay_ms != NOTE_DELAY_MS:
        parser.error("Restore the written 20 ms timing grid before exporting")
    notes, duration = collect_notes(song, humanize=args.humanize, seed=args.seed)
    if duration != DURATION_MS:
        parser.error(f"Unexpected duration: {duration}")
    out = ROOT / "assets/arrangements"
    out.mkdir(parents=True, exist_ok=True)
    midi = out / f"{SONG_ID}.mid"
    wav = out / f"{SONG_ID}.wav"
    # A neutral 120 BPM MIDI clock; all recorded timings remain absolute.
    write_midi(midi, song, notes, duration, notes_per_beat=25)
    peak, rms = write_exact_wav(wav, notes, duration)
    # Include the lead-in and response around the user's favourite transition.
    # Reference 0:50 becomes 0:46.567 after removing the empty video lead-in.
    clip_start = round((46_000 - SOURCE_START_FRAME * 1000 / 30) * 24)
    clip_end = round((57_000 - SOURCE_START_FRAME * 1000 / 30) * 24)
    with wave.open(str(wav), "rb") as source:
        params = source.getparams()
        source.setpos(clip_start)
        frames = source.readframes(clip_end - clip_start)
    preview = out / "wild-side-transition.wav"
    with wave.open(str(preview), "wb") as target:
        target.setparams(params)
        target.writeframes(frames)
    print(f"Wild Side: {len(notes)} attacks, {duration / 1000:.3f} s, peak {peak:.3f}, RMS {rms:.3f}")
    print(midi)
    print(wav)
    print(preview)


if __name__ == "__main__":
    main()
