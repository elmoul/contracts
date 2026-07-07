"""
Runs every tests/validate_*.py schema validator plus check_state_event_sync.py,
in a fixed order, and stops at the first failure (nonzero exit).

Each script is independently runnable (`python tests/validate_x.py`); this is
the single entry point that runs the full Python-side contract suite in one
command, e.g. from CI (see .github/workflows/verify.yml).

Run: python tests/run_all.py
"""
import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

VALIDATORS = [
    "validate_ai_request.py",
    "validate_control_plane.py",
    "validate_connector.py",
    "validate_dimension_event.py",
    "validate_state_event.py",
    "check_state_event_sync.py",
]


def main() -> int:
    for name in VALIDATORS:
        script = TESTS_DIR / name
        print(f"=== {name} ===")
        result = subprocess.run([sys.executable, str(script)])
        if result.returncode != 0:
            print(f"FAIL  {name} (exit {result.returncode})")
            return result.returncode
    print("All validators passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
