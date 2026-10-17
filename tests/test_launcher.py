"""First-run setup must use local packages and the selected interpreter."""
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import launcher


class LauncherTests(unittest.TestCase):
    def test_environment_does_not_borrow_another_project_dependencies(self):
        with TemporaryDirectory() as folder, patch.dict(os.environ, {"PYTHONPATH": "other-project", "PYTHONHOME": "other-python"}):
            root = Path(folder)
            environment = launcher.runtime_environment(root)
            self.assertNotIn("PYTHONPATH", environment)
            self.assertNotIn("PYTHONHOME", environment)
            (root / ".deps").mkdir()
            self.assertEqual(launcher.runtime_environment(root)["PYTHONPATH"], str(root / ".deps"))

    def test_ready_runtime_launches_without_installing_again(self):
        with TemporaryDirectory() as folder, patch.object(launcher, "ROOT", Path(folder)), \
                patch.object(launcher, "has_dependencies", return_value=True), \
                patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            self.assertEqual(launcher.main([]), 0)
            self.assertEqual(len(run.call_args_list), 1)
            self.assertEqual(run.call_args.args[0][-1], str(Path(folder) / "main.py"))

    def test_first_run_installs_into_local_venv_and_verifies_imports(self):
        with TemporaryDirectory() as folder, patch.object(launcher, "has_dependencies", side_effect=[False, True]) as check, \
                patch.object(launcher.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run, \
                redirect_stdout(io.StringIO()):
            root = Path(folder)
            python, _ = launcher.prepare_runtime(root)
            self.assertTrue(python.is_relative_to(root / ".venv"))
            pip_calls = [call.args[0] for call in run.call_args_list if "pip" in call.args[0]]
            self.assertEqual(len(pip_calls), 1)
            self.assertEqual(pip_calls[0][0], str(python))
            self.assertIn(str(root / "requirements.txt"), pip_calls[0])
            self.assertEqual(check.call_args.args[0], python)

    def test_failed_install_does_not_start_the_application(self):
        with TemporaryDirectory() as folder, patch.object(launcher, "ROOT", Path(folder)), \
                patch.object(launcher, "has_dependencies", return_value=False), \
                patch.object(launcher.subprocess, "run", side_effect=subprocess.CalledProcessError(1, ["pip"])) as run, \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(launcher.main([]), 1)
            self.assertIn("run.bat again", errors.getvalue())
            self.assertTrue(all("main.py" not in str(call.args[0]) for call in run.call_args_list))
