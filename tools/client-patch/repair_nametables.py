#!/usr/bin/env python3
"""
Repair mp3nametable.txt and mapnametable.txt in MidnightROClient/midnight.grf
by pulling the complete base tables from data.grf and appending custom maps.
"""

import sys
import shutil
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
BACKUP_GRF = CLIENT / "midnight.grf.bak_before_nametables_repair"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build

def main():
    print(f"Reading base tables from {DATA_GRF}...")
    dg = Grf(DATA_GRF)
    
    mp3_base_raw = dg.read(b"data\\mp3nametable.txt")
    map_base_raw = dg.read(b"data\\mapnametable.txt")
    
    mp3_text = mp3_base_raw.decode("latin-1", "replace")
    map_text = map_base_raw.decode("latin-1", "replace")

    custom_bgms = [
        ("midnight_gate.rsw", "bgm\\18.mp3"),
        ("mid_gate.rsw", "bgm\\18.mp3"),
        ("mid_redgate.rsw", "bgm\\125.mp3"),
        ("mid_double.rsw", "bgm\\64.mp3"),
    ]

    custom_names = [
        ("midnight_gate.rsw", "Midnight Gate - The Shadow Realm"),
        ("mid_gate.rsw", "Midnight Gate - The Shadow Realm"),
        ("mid_redgate.rsw", "The Crimson Snow Realm (Red Gate)"),
        ("mid_double.rsw", "The Cartenon Temple (Double Gate)"),
    ]

    # Append custom BGMs
    for rsw, bgm in custom_bgms:
        entry = f"{rsw}#{bgm}#"
        if entry not in mp3_text:
            if not mp3_text.endswith("\r\n") and not mp3_text.endswith("\n"):
                mp3_text += "\r\n"
            mp3_text += f"{entry}\r\n"
            print(f"  Added BGM: {entry}")

    # Append custom map names
    for rsw, name in custom_names:
        entry = f"{rsw}#{name}#"
        if entry not in map_text:
            if not map_text.endswith("\r\n") and not map_text.endswith("\n"):
                map_text += "\r\n"
            map_text += f"{entry}\r\n"
            print(f"  Added Map Name: {entry}")

    print(f"\nFinal mp3nametable.txt lines: {len(mp3_text.splitlines())}")
    print(f"Final mapnametable.txt lines: {len(map_text.splitlines())}")

    # Read current midnight.grf
    print(f"\nReading target GRF {TARGET_GRF}...")
    mg = Grf(TARGET_GRF)
    all_files = {}
    for entry in mg.entries:
        all_files[entry] = mg.read(entry)

    # Backup midnight.grf if not already backed up
    if not BACKUP_GRF.exists():
        print(f"Creating backup: {BACKUP_GRF.name}")
        shutil.copy2(TARGET_GRF, BACKUP_GRF)

    # Update files in dict
    all_files[b"data\\mp3nametable.txt"] = mp3_text.encode("latin-1")
    all_files[b"data\\mapnametable.txt"] = map_text.encode("latin-1")

    mg.close()
    dg.close()

    # Build staged
    staged_grf = CLIENT / "midnight.grf.staged"
    print(f"Building staged GRF with {len(all_files)} entries...")
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"Staged GRF built: {staged_grf.stat().st_size} bytes")

    try:
        staged_grf.replace(TARGET_GRF)
        print("Successfully updated MidnightROClient/midnight.grf!")
    except PermissionError:
        print("ERROR: MidnightROClient/midnight.grf is locked by a running process. Please close the client.")
        sys.exit(1)

if __name__ == "__main__":
    main()
