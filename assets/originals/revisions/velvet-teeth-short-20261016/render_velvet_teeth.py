"""Export Velvet Teeth's short sextuplet-grid piano performance.

Each 4/4 measure contains 24 slots: six 80 ms slots per quarter note at
125 BPM. MIDI and WAV share the player's pitch, onset, hold and physical-key
retrigger rules. The WAV is an offline piano approximation.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player.song_library import SongPreset, load_song_library
from tools.render_song import collect_notes, write_midi
from tools.render_wolf_last_dawn import write_exact_wav


SONG_ID = "velvet-teeth"
DURATION_MS = 92_160
NOTES_PER_BEAT = 6


def render(song: SongPreset, output_dir: Path,
           sample_rate: int = 24000, *, humanize: bool = False,
           seed: int | None = None) -> tuple[Path, Path, int, float, float]:
    if song.id != SONG_ID:
        raise ValueError(f"This renderer is for {SONG_ID}")
    if song.note_delay_ms != 80:
        raise ValueError("The written 125 BPM score requires an 80 ms sextuplet grid")
    if not 8000 <= sample_rate <= 96000:
        raise ValueError("Sample rate must be between 8000 and 96000 Hz")
    notes, duration_ms = collect_notes(song, humanize=humanize, seed=seed)
    if duration_ms != DURATION_MS:
        raise ValueError(f"Expected exactly {DURATION_MS} ms, received {duration_ms}")
    if not notes:
        raise ValueError("The score contains no notes")
    if max(note.end_ms for note in notes) + 750 > DURATION_MS:
        raise ValueError("Final notes leave insufficient room for the piano release")
    output_dir.mkdir(parents=True, exist_ok=True)
    midi_path = output_dir / f"{song.id}.mid"
    wav_path = output_dir / f"{song.id}.wav"
    write_midi(midi_path, song, notes, duration_ms, notes_per_beat=NOTES_PER_BEAT)
    peak, rms = write_exact_wav(wav_path, notes, DURATION_MS, sample_rate)
    return midi_path, wav_path, len(notes), peak, rms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets/originals")
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--humanize", action="store_true", help="Render one humanized performance")
    parser.add_argument("--seed", type=int, help="Repeat the same humanized performance")
    args = parser.parse_args()
    if not 8000 <= args.sample_rate <= 96000:
        parser.error("Sample rate must be between 8000 and 96000 Hz")
    song = next((song for song in load_song_library() if song.id == SONG_ID), None)
    if song is None:
        parser.error(f"Song not yet installed in the catalog: {SONG_ID}")
    midi, audio, attacks, peak, rms = render(song, args.output_dir, args.sample_rate,
                                          humanize=args.humanize, seed=args.seed)
    print(f"{song.title}: {attacks} note attacks, 125 BPM, exactly {DURATION_MS / 1000:.3f} s")
    print(f"MIDI: {midi.resolve()}")
    print(f"WAV: {audio.resolve()} ({args.sample_rate} Hz, mono 16-bit, "
          f"peak {peak:.3f}, RMS {rms:.3f})")


if __name__ == "__main__":
    main()
