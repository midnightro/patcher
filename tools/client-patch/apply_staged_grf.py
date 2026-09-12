#!/usr/bin/env python3
"""Apply staged midnight.grf to live MidnightROClient/midnight.grf once client is closed."""

from pathlib import Path
import shutil
import sys

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
STAGED_GRF = CLIENT / "midnight.grf.staged"
BACKUP_GRF = CLIENT / "midnight.grf.before_event_moon_items"


def main():
    if not STAGED_GRF.exists():
        print(f"Staged file {STAGED_GRF} does not exist.")
        return 1

    if not BACKUP_GRF.exists() and TARGET_GRF.exists():
        shutil.copy2(TARGET_GRF, BACKUP_GRF)
        print(f"Created backup at {BACKUP_GRF}")

    try:
        STAGED_GRF.replace(TARGET_GRF)
        print(f"Successfully applied {STAGED_GRF.name} -> {TARGET_GRF}")
        return 0
    except PermissionError:
        print(f"ERROR: {TARGET_GRF} is locked. Please close MidnightRO-Ragexe and run again.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
