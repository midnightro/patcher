#!/usr/bin/env python3
"""Safely update Midnight Gate scripts to use the new 'midnight_gate' map."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SERVER = ROOT / "server"
NPC_DIR = SERVER / "npc" / "custom" / "midnight"

def patch_cp874_file(path: Path, replacements: list[tuple[str, str]]):
    if not path.exists():
        print(f"File not found: {path}")
        return
    raw = path.read_bytes()
    # Decode with cp874
    text = raw.decode("cp874", errors="replace")
    for old_s, new_s in replacements:
        if old_s in text:
            text = text.replace(old_s, new_s)
            print(f"[{path.name}] Replaced: {old_s[:30]}... -> {new_s[:30]}...")
        else:
            print(f"[{path.name}] NOT FOUND: {old_s[:40]}")
    # Write back CRLF cp874
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    path.write_bytes(text.encode("cp874"))

def patch_utf8_file(path: Path, replacements: list[tuple[str, str]]):
    if not path.exists():
        return
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except Exception:
        text = raw.decode("cp874", errors="replace")
    for old_s, new_s in replacements:
        if old_s in text:
            text = text.replace(old_s, new_s)
    text = text.replace("\r\n", "\n").replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))

def main():
    print("=== Updating Midnight Gate Scripts ===")

    # 1. midnight_core.txt
    core_replacements = [
        ('mapwarp "guild_vs2-2","morocc",160,100;', 'mapwarp "midnight_gate","morocc",160,100;'),
    ]
    patch_cp874_file(NPC_DIR / "midnight_core.txt", core_replacements)
    patch_utf8_file(NPC_DIR / "midnight_core.utf8.txt", core_replacements)

    # 2. midnight_gate.txt
    gate_replacements = [
        ('mapwarp "guild_vs2-2","morocc",160,100;', 'mapwarp "midnight_gate","morocc",160,100;'),
        ('warp "guild_vs2-2",.@entry_x[.@entry],.@entry_y[.@entry];', 'warp "midnight_gate",50,15;'),
        ('strcharinfo(3) == "guild_vs2-2"', 'strcharinfo(3) == "midnight_gate"'),
    ]
    patch_cp874_file(NPC_DIR / "midnight_gate.txt", gate_replacements)
    patch_utf8_file(NPC_DIR / "midnight_gate.utf8.txt", gate_replacements)

    # 3. midnight_gate_wave.txt
    wave_replacements = [
        ('.battle_map$ = "guild_vs2-2";', '.battle_map$ = "midnight_gate";'),
        ('.battle_y = 55;', '.battle_y = 70;'),
        ('guild_vs2-2\tmapflag', 'midnight_gate\tmapflag'),
        ('guild_vs2-2,50,50,4\tscript\tGate Exit Keeper', 'midnight_gate,50,14,4\tscript\tGate Exit Keeper'),
        ('(50,50)', '(50,14)'),
        ('mapwarp .battle_map$,"morocc",160,100;', 'mapwarp .battle_map$,"morocc",160,100;'),
    ]
    patch_cp874_file(NPC_DIR / "midnight_gate_wave.txt", wave_replacements)
    patch_utf8_file(NPC_DIR / "midnight_gate_wave.utf8.txt", wave_replacements)

    print("=== Update Completed! ===")

if __name__ == "__main__":
    main()
