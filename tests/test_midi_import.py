from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mido

from player.midi_import import MidiImportError, convert_midi, read_midi
from player.parser import SheetParser
from player.plan_writer import build_plan
from player.piano_keys import KEY_TO_MIDI, physical_key
from player.song_library import load_song_library, save_imported_song


def make_midi(path, pitches=(60, 64)):
    mid = mido.MidiFile(type=1, ticks_per_beat=480)
    mid.tracks.append(mido.MidiTrack([
        mido.MetaMessage('track_name', name='Tempo'),
        mido.MetaMessage('set_tempo', tempo=500000),
        mido.MetaMessage('set_tempo', tempo=1000000, time=480),
        mido.MetaMessage('end_of_track', time=480),
    ]))
    mid.tracks.append(mido.MidiTrack([
        mido.MetaMessage('track_name', name='Melody'),
        mido.Message('note_on', note=pitches[0], velocity=80),
        mido.Message('note_off', note=pitches[0], time=240),
        mido.Message('note_on', note=pitches[1], velocity=80, time=240),
        mido.Message('note_on', note=pitches[1], velocity=0, time=480),
    ]))
    mid.tracks.append(mido.MidiTrack([
        mido.MetaMessage('track_name', name='Bass'),
        mido.Message('note_on', channel=1, note=36, velocity=60),
        mido.Message('note_off', channel=1, note=36, time=960),
    ]))
    mid.tracks.append(mido.MidiTrack([
        mido.Message('note_on', channel=9, note=42, velocity=90),
        mido.Message('note_off', channel=9, note=42, time=480),
    ]))
    mid.save(path)


class MidiImportTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.path = Path(self.folder.name) / 'Test.mid'

    def tearDown(self):
        self.folder.cleanup()

    def attacks(self, result):
        plan = build_plan(SheetParser().parse(result.sheet), 100, 35)
        return sorted((e.offset_ms, KEY_TO_MIDI[chr(k)], e.hold_ms) for e in plan.events for k in e.keys), plan

    def test_conductor_tempo_is_kept_when_only_one_music_track_is_selected(self):
        make_midi(self.path)
        doc = read_midi(self.path)
        result = convert_midi(doc, {1}, adapt=False)
        notes, plan = self.attacks(result)
        self.assertEqual(notes, [(0, 60, 250), (500, 64, 1000)])
        self.assertEqual(doc.duration_ms, 1500)
        self.assertEqual(plan.duration_ms, 2300)
        self.assertEqual(doc.tempo_changes, 1)
        self.assertEqual([t.notes for t in doc.tracks], [0, 2, 1, 0])
        self.assertEqual(doc.tracks[3].drums, 1)

    def test_pedal_support_and_vel_zero_note_off(self):
        mid = mido.MidiFile(type=0, ticks_per_beat=480)
        mid.tracks.append(mido.MidiTrack([
            mido.Message('control_change', control=64, value=127),
            mido.Message('note_on', note=60, velocity=80),
            mido.Message('note_on', note=60, velocity=0, time=240),
            mido.Message('note_on', note=64, velocity=80, time=240),
            mido.Message('note_off', note=64, time=240),
            mido.Message('control_change', control=64, value=0, time=240),
        ]))
        mid.save(self.path)
        doc = read_midi(self.path)
        held, _ = self.attacks(convert_midi(doc, sustain=True))
        plain, _ = self.attacks(convert_midi(doc, sustain=False))
        self.assertEqual(held, [(0, 60, 1000), (500, 64, 500)])
        self.assertEqual(plain, [(0, 60, 250), (500, 64, 250)])

    def test_range_adaptation_and_shift_conflicts_are_reported(self):
        mid = mido.MidiFile(type=0)
        mid.tracks.append(mido.MidiTrack(
            [mido.Message('note_on', note=n, velocity=64) for n in (24, 60, 61, 108)] +
            [mido.Message('note_off', note=n, time=480 if i == 0 else 0) for i,n in enumerate((24,60,61,108))]))
        mid.save(self.path)
        doc = read_midi(self.path)
        with self.assertRaises(MidiImportError):
            convert_midi(doc, adapt=False)
        result = convert_midi(doc)
        notes, plan = self.attacks(result)
        self.assertEqual(len(notes), 4)
        keys = [physical_key(chr(k)) for e in plan.events for k in e.keys]
        self.assertEqual(len(set(keys)), 4)
        self.assertEqual(result.changes['range'], 2)
        self.assertGreater(result.changes['revoiced'], 0)
        self.assertTrue(all(36 <= pitch <= 96 for _,pitch,_ in notes))

    def test_imported_song_is_persistent_separate_and_never_changes_bundled_songs(self):
        make_midi(self.path)
        result = convert_midi(read_midi(self.path))
        before = load_song_library()
        directory = Path(self.folder.name) / 'library'
        song = save_imported_song(directory, 'My MIDI', result.sheet, result.summary)
        other = save_imported_song(directory, 'My MIDI', result.sheet, result.summary)
        after = load_song_library(directory)
        self.assertEqual(after[:len(before)], before)
        self.assertEqual({s.id for s in after[len(before):]}, {song.id, other.id})
        self.assertTrue(song.imported)
        self.assertEqual(song.sheet, result.sheet)
        self.assertEqual(song.title, 'My MIDI')

    def test_bad_empty_and_asynchronous_files_do_not_produce_songs(self):
        self.path.write_bytes(b'not MIDI')
        with self.assertRaises(MidiImportError):
            read_midi(self.path)
        make_midi(self.path)
        with self.assertRaises(MidiImportError):
            convert_midi(read_midi(self.path), set())
        mid = mido.MidiFile(type=2)
        mid.tracks.append(mido.MidiTrack([mido.Message('note_on', note=60, velocity=60)]))
        mid.save(self.path)
        with self.assertRaises(MidiImportError):
            read_midi(self.path)

    def test_unclosed_short_and_overlapping_notes_are_reported(self):
        mid = mido.MidiFile(type=0, ticks_per_beat=480)
        mid.tracks.append(mido.MidiTrack([
            mido.Message('note_on', note=60, velocity=70),
            mido.Message('note_on', note=61, velocity=70, time=1),
            mido.Message('note_off', note=61, time=1),
            mido.MetaMessage('end_of_track', time=478),
        ]))
        mid.save(self.path)
        result = convert_midi(read_midi(self.path))
        notes, plan = self.attacks(result)
        self.assertEqual(len(notes), 2)
        self.assertEqual(result.changes['unclosed'], 1)
        self.assertEqual(result.changes['holds'], 1)
        self.assertEqual(result.changes['retriggered'], 1)

    def test_dense_chord_adaptation_never_silently_claims_to_play_all_61_notes(self):
        mid = mido.MidiFile(type=0)
        pitches = list(range(36, 97))
        mid.tracks.append(mido.MidiTrack([mido.Message('note_on', note=n, velocity=64) for n in pitches] +
                         [mido.Message('note_off', note=n, time=480 if i == 0 else 0) for i,n in enumerate(pitches)]))
        mid.save(self.path)
        result = convert_midi(read_midi(self.path))
        self.assertEqual(result.source_notes, 61)
        self.assertGreater(result.changes['omitted'], 0)
        self.assertEqual(result.played_notes + result.changes['omitted'], 61)
        notes, plan = self.attacks(result)
        keys = [physical_key(chr(k)) for e in plan.events for k in e.keys]
        self.assertEqual(len(set(keys)), len(keys))
        self.assertLessEqual(len(keys), 36)

    def test_low_bass_octaves_do_not_collapse_into_one_note_during_range_folding(self):
        mid = mido.MidiFile(type=0)
        mid.tracks.append(mido.MidiTrack([mido.Message('note_on', note=n, velocity=64) for n in (24,36,72)] +
                         [mido.Message('note_off', note=n, time=480 if i == 0 else 0) for i,n in enumerate((24,36,72))]))
        mid.save(self.path)
        result = convert_midi(read_midi(self.path))
        notes, _ = self.attacks(result)
        self.assertEqual({pitch for _,pitch,_ in notes}, {36,48,72})
        self.assertEqual(result.played_notes, 3)
        self.assertEqual(result.changes['merged'], 0)


if __name__ == '__main__':
    unittest.main()
