"""Optional real-AHK IPC tests: never send note key-down events."""
import os
from pathlib import Path
import queue
import subprocess
from tempfile import TemporaryDirectory
import threading
import time
import unittest

from player.parser import SheetParser
from player.plan_writer import build_plan, write_plan

ROOT = Path(__file__).resolve().parents[1]
AHK = Path(os.environ.get("AHK_EXECUTABLE", "C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe"))


@unittest.skipUnless(os.environ.get("RUN_AHK_TESTS") == "1" and AHK.is_file(), "Set RUN_AHK_TESTS=1 with AHK v2 installed")
class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.messages = queue.Queue()
        self.process = subprocess.Popen(
            [str(AHK), "/ErrorStdOut=UTF-8", str(ROOT / "ahk/player.ahk"),
             "Event", "F21", "F22", "F23"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
        threading.Thread(target=self._reader, daemon=True).start()
        try:
            self.wait_for("READY")
        except Exception:
            self.tearDown()
            raise

    def _reader(self):
        for line in self.process.stdout:
            self.messages.put(line.strip())

    def send(self, command):
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

    def wait_for(self, prefix, timeout=4):
        deadline = time.monotonic() + timeout
        seen = []
        while time.monotonic() < deadline:
            try:
                line = self.messages.get(timeout=0.05)
                seen.append(line)
                if line.startswith(prefix):
                    return line
                if line.startswith("ERROR"):
                    self.fail(line)
            except queue.Empty:
                if self.process.poll() is not None:
                    self.fail(f"Worker exited with {self.process.returncode}; messages: {seen}")
        self.fail(f"No {prefix!r}; messages: {seen}")

    def play(self, source):
        path = Path(self.folder.name) / "plan.tsv"
        write_plan(build_plan(SheetParser().parse(source)), path, 35)
        self.send("PLAY\t" + str(path))

    def test_pause_only_plan_finishes_and_reports_time(self):
        start = time.monotonic()
        self.play("---")
        self.wait_for("STATE\tPLAYING")
        self.wait_for("STATE\tFINISHED")
        self.assertGreaterEqual(time.monotonic() - start, 0.28)

    def test_version_two_pause_only_plan_finishes_without_key_downs(self):
        path = Path(self.folder.name) / "pause-v2.tsv"
        path.write_text("ROBLOXSHEETS\t2\t35\t300.000\n"
                        "0.000\tPAUSE\t0\t0\t3\t0.000\n", encoding="utf-8")
        self.send("PLAY\t" + str(path))
        self.wait_for("STATE\tPLAYING")
        self.wait_for("STATE\tFINISHED")

    def test_numeric_reader_supports_legacy_and_per_event_holds(self):
        # Valid sounding plans only reach the pure reader. They never reach
        # the worker's Play command, timers or any physical keyboard emitter.
        v1 = "ROBLOXSHEETS\t1\t35\t300.000\n"
        v2 = "ROBLOXSHEETS\t2\t35\t300.000\n"
        v3 = "ROBLOXSHEETS\t3\t35\t60000.000\n"
        fixtures = [
            ("legacy", v1 + "0.000\tCHORD\t97,65\t0\t4\n"
             "100.000\tPAUSE\t0\t4\t5\n", "1", "35,0"),
            ("variable-holds", v2 + "0.000\tNOTE\t97\t0\t1\t31.250\n"
             "1.750\tCHORD\t65,83\t1\t5\t39.125\n"
             "100.000\tPAUSE\t0\t5\t6\t0.000\n", "2", "31.25,39.125,0"),
            ("negative-onset", v2 + "-0.001\tNOTE\t97\t0\t1\t35\n", "INVALID", ""),
            ("unordered-onsets", v2 + "20\tNOTE\t97\t0\t1\t35\n"
             "19\tNOTE\t97\t1\t2\t35\n", "INVALID", ""),
            ("short-hold", v2 + "0\tNOTE\t97\t0\t1\t4.999\n", "INVALID", ""),
            ("long-hold", v2 + "0\tNOTE\t97\t0\t1\t200.001\n", "INVALID", ""),
            ("sustained-chord", v3 + "0\tCHORD\t97,115,100\t0\t11\t1000\n"
             "100\tNOTE\t102\t12\t13\t35\n", "3", "1000,35"),
            ("maximum-sustain", v3 + "0\tNOTE\t97\t0\t1\t60000\n", "3", "60000"),
            ("excessive-sustain", v3 + "0\tNOTE\t97\t0\t1\t60000.001\n", "INVALID", ""),
            ("sustain-beyond-duration", v3 + "1\tNOTE\t97\t0\t1\t60000\n", "INVALID", ""),
            ("sustain-pause", v3 + "0\tPAUSE\t0\t0\t1\t1\n", "INVALID", ""),
            ("release-beyond-duration", v2 + "299\tNOTE\t97\t0\t1\t5\n", "INVALID", ""),
            ("pause-hold", v2 + "0\tPAUSE\t0\t0\t1\t35\n", "INVALID", ""),
            ("pause-keys", v2 + "0\tPAUSE\t97\t0\t1\t0\n", "INVALID", ""),
            ("missing-hold", v2 + "0\tNOTE\t97\t0\t1\n", "INVALID", ""),
            ("non-finite-onset", v2 + "NaN\tNOTE\t97\t0\t1\t35\n", "INVALID", ""),
            ("invalid-key", v2 + "0\tNOTE\t127\t0\t1\t35\n", "INVALID", ""),
            ("backwards-span", v2 + "0\tNOTE\t97\t2\t1\t35\n", "INVALID", ""),
            ("rounding-tolerance", "ROBLOXSHEETS\t2\t35\t300.000\n"
             "294.668\tNOTE\t97\t0\t1\t5.333\n", "2", "5.333"),
        ]
        rows = []
        for name, content, version, holds in fixtures:
            path = Path(self.folder.name) / f"{name}.tsv"
            path.write_text(content, encoding="utf-8")
            rows.append(f"{name}\t{path}\t{version}\t{holds}\n")
        manifest = Path(self.folder.name) / "reader-manifest.tsv"
        manifest.write_text("".join(rows), encoding="utf-8")
        result = subprocess.run(
            [str(AHK), "/ErrorStdOut=UTF-8", str(ROOT / "tests/plan_reader_contract.ahk"),
             str(manifest)], capture_output=True, text=True, encoding="utf-8",
            timeout=4, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"OK\tplan reader\t{len(fixtures)} plans", result.stdout)

    def test_keyboard_contract_with_recorded_events(self):
        result = subprocess.run([str(AHK), "/ErrorStdOut=UTF-8", str(ROOT / "tests/keyboard_contract.ahk")],
                                capture_output=True, text=True, encoding="utf-8", timeout=4,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK\tkeyboard contract", result.stdout)

    def test_pause_resume_and_stop(self):
        self.play("-" * 30)
        self.wait_for("STATE\tPLAYING")
        self.send("PAUSE")
        self.wait_for("STATE\tPAUSED")
        self.send("RESUME")
        self.wait_for("STATE\tPLAYING")
        self.send("STOP")
        self.wait_for("STATE\tSTOPPED")

    def test_runs_without_roblox_and_emergency_stop(self):
        self.play("-" * 30)
        self.wait_for("STATE\tPLAYING")
        self.send("EMERGENCY")
        self.wait_for("STATE\tSTOPPED")

    def test_plan_validation_error_does_not_crash_worker(self):
        path = Path(self.folder.name) / "bad.tsv"
        path.write_text("bad header\n")
        self.send("PLAY\t" + str(path))
        self.wait_for("STATE\tERROR")
        # Drain expected diagnostic so wait_for can continue.
        self.assertTrue(self.messages.get(timeout=2).startswith("ERROR\t"))
        self.send("STOP")
        self.wait_for("STATE\tSTOPPED")

    def tearDown(self):
        if self.process.poll() is None:
            self.send("EXIT")
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        self.process.stdin.close()
        self.process.stdout.close()
        self.folder.cleanup()


if __name__ == "__main__":
    unittest.main()
