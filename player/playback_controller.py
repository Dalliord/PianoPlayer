"""Qt process bridge and interruptible monotonic countdown."""
import logging
import math
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import time

from PySide6.QtCore import QObject, QProcess, QTimer, Signal

from app.settings import Settings
from player.models import PlaybackPlan
from player.humanization import humanize_plan
from player.plan_writer import write_plan


class PlaybackController(QObject):
    state_changed = Signal(str, str)
    progress = Signal(int, int, float)
    toggle_requested = Signal()
    worker_ready = Signal(bool)
    error = Signal(str)

    ACTIVE = {"COUNTDOWN", "PLAYING", "PAUSED"}

    def __init__(self, root: Path, settings: Settings, parent: QObject | None = None):
        super().__init__(parent)
        self.root = root
        self.settings = settings
        self.state = "IDLE"
        self.ready = False
        self.stopping = False
        self._closing = False
        self._buffer = ""
        self._stderr = ""
        self._temporary: TemporaryDirectory | None = None
        self.plan: PlaybackPlan | None = None
        self._deadline = 0.0
        self._last_count = -1
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_error)
        self.process.errorOccurred.connect(self._process_error)
        self.process.finished.connect(self._finished)
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._countdown)

    def launch_worker(self) -> None:
        if self.process.state() != QProcess.ProcessState.NotRunning:
            return
        executable = self.settings.ahk_executable_path
        if not executable:
            candidates = [Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "AutoHotkey/v2/AutoHotkey64.exe",
                          Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/AutoHotkey/v2/AutoHotkey64.exe"]
            executable = next((str(path) for path in candidates if path.is_file()), "")
            executable = executable or shutil.which("AutoHotkey64.exe") or ""
        if not executable or not Path(executable).is_file():
            self._fail("AutoHotkey v2 не найден. Установите его или укажите путь в Advanced.")
            return
        self._buffer = ""
        self._stderr = ""
        self.process.setProgram(executable)
        self.process.setArguments(["/ErrorStdOut=UTF-8", str(self.root / "ahk/player.ahk"),
                                   self.settings.send_mode,
                                   self.settings.hotkey_toggle, self.settings.hotkey_stop,
                                   self.settings.hotkey_emergency])
        self.process.start()
        logging.info("Starting AHK worker: %s", executable)

    def play(self, plan: PlaybackPlan) -> None:
        if self.state == "PAUSED":
            self.resume()
            return
        if self.state in self.ACTIVE or not self.ready or self.stopping:
            return
        self._cleanup_plan()
        self.plan = (humanize_plan(plan, self.settings.note_delay_ms, self.settings.key_hold_ms)
                     if self.settings.humanize else plan)
        sessions = self.root / "data/sessions"
        sessions.mkdir(parents=True, exist_ok=True)
        self._temporary = TemporaryDirectory(prefix="robloxsheets-", dir=sessions)
        write_plan(self.plan, Path(self._temporary.name) / "plan.tsv", self.settings.key_hold_ms)
        self._deadline = time.monotonic() + self.settings.start_delay_s
        self._last_count = -1
        self.progress.emit(0, len(self.plan.events), 0.0)
        self._set_state("COUNTDOWN", "")
        self._countdown()
        if self.state == "COUNTDOWN":
            self.timer.start()
        logging.info("Play: %d plan events, humanize=%s", len(self.plan.events), self.settings.humanize)

    def _countdown(self) -> None:
        if self.state != "COUNTDOWN":
            self.timer.stop()
            return
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            self.timer.stop()
            if self._temporary:
                self._send("PLAY\t" + str(Path(self._temporary.name) / "plan.tsv"))
            self._set_state("PLAYING", "Playing")
            return
        count = math.ceil(remaining)
        if count != self._last_count:
            self._last_count = count
            self._set_state("COUNTDOWN", f"Starting in {count}...")

    def pause(self) -> None:
        if self.state == "PLAYING":
            self._send("PAUSE")

    def resume(self) -> None:
        if self.state == "PAUSED":
            self._send("RESUME")

    def stop(self, emergency: bool = False) -> None:
        self.timer.stop()
        self.stopping = self.process.state() == QProcess.ProcessState.Running
        self._send("EMERGENCY" if emergency else "STOP")
        self._set_state("STOPPED", "Emergency stopped" if emergency else "Stopped")
        self.progress.emit(0, len(self.plan.events) if self.plan else 0, 0.0)
        if not self.stopping:
            self._cleanup_plan()
        # AHK owns the file only until PLAY has been read; cleanup on its STOPPED acknowledgement.
        logging.info("%s", "Emergency stop" if emergency else "Stop")

    def _send(self, command: str) -> None:
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.write((command + "\n").encode("utf-8"))

    def _read_output(self) -> None:
        self._buffer += bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            fields = line.rstrip("\r").split("\t")
            try:
                self._handle_message(fields)
            except (ValueError, IndexError):
                logging.error("Malformed AHK message: %r", line)

    def _handle_message(self, fields: list[str]) -> None:
        if fields[0] == "READY":
            self.ready = True
            self.worker_ready.emit(True)
            self._set_state("IDLE", "Ready")
        elif fields[0] == "HOTKEY" and fields[1] == "TOGGLE":
            self.toggle_requested.emit()
        elif fields[0] == "HOTKEY" and fields[1] in {"STOP", "EMERGENCY"}:
            self.stop(fields[1] == "EMERGENCY")
        elif fields[0] == "STATE":
            state = fields[1]
            if state in {"STOPPED", "FINISHED", "ERROR"}:
                self.stopping = False
            labels = {"PAUSED": "Paused",
                      "PLAYING": "Playing", "FINISHED": "Finished", "STOPPED": "Stopped"}
            self._set_state(state, labels.get(state, state))
            if state in {"FINISHED", "STOPPED", "ERROR"}:
                self._cleanup_plan()
        elif fields[0] == "PROGRESS":
            self.progress.emit(int(fields[1]), int(fields[2]), float(fields[3]))
        elif fields[0] == "ERROR":
            self._fail("\t".join(fields[1:]))
        elif fields[0] != "":
            self._stderr += "\t".join(fields) + "\n"

    def _read_error(self) -> None:
        self._stderr += bytes(self.process.readAllStandardError()).decode("utf-8", errors="replace")

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if not self._closing:
            self._fail("Ошибка запуска AHK: " + self.process.errorString())

    def _finished(self, code: int, status: QProcess.ExitStatus) -> None:
        self.ready = False
        self.stopping = False
        self.worker_ready.emit(False)
        self.timer.stop()
        self._cleanup_plan()
        if not self._closing:
            self._fallback_release()
            self._fail((self._stderr or f"AHK завершился (код {code}).").strip())

    def _fail(self, message: str) -> None:
        self.timer.stop()
        self._cleanup_plan()
        self._set_state("ERROR", message)
        self.error.emit(message)
        logging.error("Playback error: %s", message)

    def _set_state(self, state: str, text: str) -> None:
        self.state = state
        self.state_changed.emit(state, text)

    def _cleanup_plan(self) -> None:
        if self._temporary:
            self._temporary.cleanup()
            self._temporary = None

    def shutdown(self) -> None:
        self._closing = True
        self.timer.stop()
        self._send("EXIT")
        self.process.waitForBytesWritten(200)
        if not self.process.waitForFinished(1500):
            self.process.kill()
            self.process.waitForFinished(1000)
            # Fallback for an unresponsive worker: send only key-up events via Win32.
            self._fallback_release()
        self.ready = False
        self.stopping = False
        self._cleanup_plan()

    def _fallback_release(self) -> None:
        if os.name != "nt":
            return
        import ctypes
        # Printable piano keys and modifiers. Never generate any new key-down here.
        for key in [*range(0x30, 0x5B), *range(0xBA, 0xC1), *range(0xDB, 0xDF),
                    0x10, 0x11, 0x12, 0x5B, 0x5C]:
            ctypes.windll.user32.keybd_event(key, 0, 2, 0)

    def restart_worker(self) -> None:
        self.shutdown()
        self._closing = False
        self.launch_worker()
