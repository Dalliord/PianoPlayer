"""Check local dependencies, install missing ones in .venv, then start the UI."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
DEPENDENCY_CHECK = (
    "import sys; assert sys.version_info >= (3, 12); "
    "from PySide6.QtWidgets import QApplication; "
    "from PySide6.QtSvg import QSvgRenderer; "
    "from mido import MidiFile"
)


def runtime_environment(root: Path) -> dict[str, str]:
    environment = os.environ.copy()
    # A package checkout must not depend on another project's Python environment.
    environment.pop("PYTHONHOME", None)
    environment.pop("PYTHONPATH", None)
    if (root / ".deps").is_dir():
        environment["PYTHONPATH"] = str(root / ".deps")
    return environment


def has_dependencies(python: Path, environment: dict[str, str]) -> bool:
    try:
        return subprocess.run([str(python), "-c", DEPENDENCY_CHECK], env=environment,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=30).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def prepare_runtime(root: Path) -> tuple[Path, dict[str, str]]:
    environment = runtime_environment(root)
    virtual_python = root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    python = virtual_python if virtual_python.is_file() else Path(sys.executable)
    if has_dependencies(python, environment):
        return python, environment

    print("First-run setup: installing the required libraries into .venv.", flush=True)
    print("An internet connection is required. This may take a few minutes.", flush=True)
    if not virtual_python.is_file():
        subprocess.run([sys.executable, "-m", "venv", str(root / ".venv")],
                       env=environment, cwd=root, check=True)
    # Repair interrupted installations without replacing the existing environment.
    subprocess.run([str(virtual_python), "-m", "ensurepip", "--upgrade"],
                   env=environment, cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run([str(virtual_python), "-m", "pip", "install", "--disable-pip-version-check",
                    "-r", str(root / "requirements.txt")], env=environment, cwd=root, check=True)
    if not has_dependencies(virtual_python, environment):
        raise RuntimeError("The required libraries could not be loaded after installation.")
    print("Setup complete.", flush=True)
    return virtual_python, environment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--setup-only", action="store_true", help="Install/check dependencies without opening the app")
    args = parser.parse_args(argv)
    if sys.version_info < (3, 12):
        print("Python 3.12 or later is required.", file=sys.stderr)
        return 1
    try:
        python, environment = prepare_runtime(ROOT)
        if args.setup_only:
            print("Piano Player is ready to start.")
            return 0
        return subprocess.run([str(python), str(ROOT / "main.py")], cwd=ROOT, env=environment).returncode
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Setup or launch failed: {error}", file=sys.stderr)
        print("Check your internet connection and run run.bat again.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
