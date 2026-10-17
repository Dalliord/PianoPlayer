"""Standard C2–C7 virtual-piano mapping shared by imports and audio export."""
WHITE_KEYS = "1234567890qwertyuiopasdfghjklzxcvbnm"
WHITE_PITCHES = tuple(12 * (octave + 1) + semitone
                     for octave in range(2, 8) for semitone in (0, 2, 4, 5, 7, 9, 11))[:len(WHITE_KEYS)]
KEY_TO_MIDI = dict(zip(WHITE_KEYS, WHITE_PITCHES))
SHARP_KEYS = {
    "!": "1", "@": "2", "$": "4", "%": "5", "^": "6", "*": "8", "(": "9",
    "Q": "q", "W": "w", "E": "e", "T": "t", "Y": "y", "I": "i", "O": "o", "P": "p",
    "S": "s", "D": "d", "G": "g", "H": "h", "J": "j", "L": "l", "Z": "z",
    "C": "c", "V": "v", "B": "b",
}
KEY_TO_MIDI.update({key: KEY_TO_MIDI[natural] + 1 for key, natural in SHARP_KEYS.items()})
MIDI_TO_KEY = {pitch: key for key, pitch in KEY_TO_MIDI.items()}
UNSHIFTED_SYMBOLS = dict(zip("!@#$%^&*()_+{}|:\"<>?~", "1234567890-=[]\\;',./`"))


def physical_key(character: str) -> str:
    return UNSHIFTED_SYMBOLS.get(character, character.lower())
