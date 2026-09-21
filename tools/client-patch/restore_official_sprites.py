#!/usr/bin/env python3
"""Restore official RO sprites by purging overrides from midnight.grf archives."""

from pathlib import Path
from grf import Grf
from make_grf import build

NPC_DIR = b"data\\sprite\\npc\\"
OFFICIAL_KEYS = [
    NPC_DIR + b"4_energy_blue.spr", NPC_DIR + b"4_energy_blue.act",
    NPC_DIR + b"4_energy_white.spr", NPC_DIR + b"4_energy_white.act",
    NPC_DIR + b"4_energy_yellow.spr", NPC_DIR + b"4_energy_yellow.act",
    NPC_DIR + b"4_energy_black.spr", NPC_DIR + b"4_energy_black.act",
    NPC_DIR + b"4_energy_red.spr", NPC_DIR + b"4_energy_red.act",
    NPC_DIR + b"4_m_death.spr", NPC_DIR + b"4_m_death.act",
    NPC_DIR + b"4_energy.spr", NPC_DIR + b"4_energy.act",
]


def purge_grf(grf_path: Path):
    if not grf_path.exists():
        print(f"Skipping {grf_path} (does not exist)")
        return

    print(f"Checking {grf_path}...")
    grf = Grf(str(grf_path))
    all_files = {}
    found = 0
    try:
        for entry in grf.entries:
            if entry in OFFICIAL_KEYS:
                found += 1
                print(f"  Found override: {entry.decode('latin-1', errors='ignore')}")
            else:
                all_files[entry] = grf.read(entry)
    finally:
        grf.close()

    if found == 0:
        print(f"  Clean: No official sprite overrides found in {grf_path}.")
        return

    staged = grf_path.with_suffix(".grf.cleanup_staged")
    build(staged, list(all_files.items()), verbose=False)
    try:
        staged.replace(grf_path)
        print(f"  Successfully purged {found} overrides from {grf_path}! Vanilla restored from data.grf.")
    except PermissionError:
        print(f"  WARNING: {grf_path} is locked. Please close client and run apply_staged.")


def main():
    repo_root = Path(__file__).resolve().parents[3]
    # 1. Dev Client
    purge_grf(repo_root / "MidnightROClient/midnight.grf")
    # 2. Prod Client
    purge_grf(Path("E:/MidnightROClient/midnight.grf"))


if __name__ == "__main__":
    main()
