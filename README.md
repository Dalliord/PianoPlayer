**Piano Player** is a Windows desktop application that turns piano sheets into automated keyboard performances. It sends key presses to compatible virtual pianos, letting you play anything from simple melodies to dense arrangements with overlapping voices, sustained chords, and fast passages.

Create your own song library, import MIDI files, edit arrangements, and customize how each piece is played. The application combines a straightforward interface with detailed control over rhythm, note duration, and articulation.

- **Personal song library**  
  Add songs, give them custom names, and edit their sheets directly in the application. Remove songs you no longer need and undo the most recent deletion during the current session. Songs, edits, and individual playback settings are saved locally.

- **MIDI import**  
  Convert MIDI files into playable keyboard sheets. Select the tracks you want to include, preserve tempo changes and note durations, and account for sustain pedal events. Optional octave adaptation helps fit notes into the supported keyboard range.

- **Three main timing controls**  
  Adjust **Note Delay**, **Key Hold Time**, and **Start Delay**. Control the spacing between notes, how long keys remain pressed, and how much time you have to switch to your virtual piano before playback begins.

- **Independent notes and sustained chords**  
  Hold individual notes or entire chords while other parts of the arrangement continue playing. Different keys within the same chord can have different release times, allowing layered accompaniment and melody.

- **Advanced sheet notation**  
  Combine single notes, simultaneous chords, fast sequences, pauses, and explicit hold durations. Use BPM changes, triplet subdivisions, precise timing commands, and gradual tempo transitions to shape an arrangement.

- **Humanization**  
  Introduce subtle variations in note timing, hold duration, and chord articulation while maintaining the overall tempo. Disable humanization when you want playback to follow the written timing precisely.

- **Playback controls and progress tracking**  
  Play, pause, resume, and stop performances using the interface or customizable global hotkeys. Follow elapsed time, playback progress, and highlighting of the current section in the sheet editor.

- **Multilingual interface**  
  Available in **English, Spanish, Portuguese, Japanese, Korean, Chinese, French, German, and Russian**, with native language names and flag icons.

Built with **Python, PySide6, and AutoHotkey v2**, Piano Player features a dark interface and automatic dependency setup through `run.bat`.

Requires **Windows 10/11, Python 3.12 or later, and AutoHotkey v2**. An internet connection is needed for the initial dependency installation.
