#!/usr/bin/env python3
"""Apply staged midnight.grf once client is closed."""

import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "MidnightROClient"
STAGED = CLIENT / "midnight.grf.staged"
TARGET = CLIENT / "midnight.grf"

def main():
    if not STAGED.exists():
        print("No staged file found at:", STAGED)
        return

    print("Attempting to apply staged midnight.grf...")
    for attempt in range(1, 6):
        try:
            STAGED.replace(TARGET)
            print("Successfully updated MidnightROClient/midnight.grf!")
            return
        except PermissionError:
            print(f"[{attempt}/5] midnight.grf is currently locked by game client. Retrying in 2 seconds (please exit game)...")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            return

    print("\nPlease close MidnightRO-Ragexe.exe first, then re-run this script.")

if __name__ == "__main__":
    main()
