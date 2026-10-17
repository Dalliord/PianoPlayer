"""Export the exact five-minute piano score at its 32nd-note grid.

The app's 75 ms grid is one eighth of a quarter note at 100 BPM. Both files
preserve the player's pitch, onset, hold and physical-key retrigger rules.
The WAV uses the same offline piano approximation as the earlier originals;
the score leaves enough silence for its final release to finish before 5:00.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from player.song_library import SongPreset, load_song_library
from tools.render_song import Note, collect_notes, write_midi, write_wav


SONG_ID = "wolf-last-dawn"
DURATION_MS = 300_000
NOTES_PER_BEAT = 8


def write_exact_wav(path: Path, notes: list[Note], duration_ms: int,
                    sample_rate: int = 24000) -> tuple[float, float]:
    """Remove only the renderer's silent padding, never an audible release."""
    write_wav(path, notes, duration_ms, sample_rate)
    frame_count = round(duration_ms * sample_rate / 1000)
    with wave.open(str(path), "rb") as reader:
        params = reader.getparams()
        pcm = reader.readframes(frame_count)
        padding = reader.readframes(reader.getnframes())
    if len(pcm) != frame_count * params.sampwidth * params.nchannels:
        raise ValueError("The renderer produced less audio than the written score")
    if any(padding):
        raise ValueError("The score needs more final silence before an exact-duration export")
    with wave.open(str(path), "wb") as writer:
        writer.setparams(params)
        writer.writeframes(pcm)
    samples = np.frombuffer(pcm, dtype="<i2").astype(np.float64) / 32767
    peak = float(np.max(np.abs(samples)))
    rms = float(np.sqrt(np.mean(samples ** 2)))
    if not np.isfinite(peak) or not 0 < peak < 1 or rms <= 0:
        raise ValueError("The exported WAV is silent, invalid or clipped")
    return peak, rms


def render(song: SongPreset, output_dir: Path,
           sample_rate: int = 24000, *, humanize: bool = False,
           seed: int | None = None) -> tuple[Path, Path, int, float, float]:
    if song.id != SONG_ID:
        raise ValueError(f"This renderer is for {SONG_ID}")
    if song.note_delay_ms != 75:
        raise ValueError("The written 100 BPM score requires a 75 ms 32nd-note grid")
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
    print(f"{song.title}: {attacks} note attacks, 100 BPM, exactly {DURATION_MS / 1000:.3f} s")
    print(f"MIDI: {midi.resolve()}")
    print(f"WAV: {audio.resolve()} ({args.sample_rate} Hz, mono 16-bit, "
          f"peak {peak:.3f}, RMS {rms:.3f})")


if __name__ == "__main__":
    main()
