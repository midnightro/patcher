#!/usr/bin/env python3
"""Rename map from midnight_gate to mid_gate across all server configs and NPC scripts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SERVER = ROOT / "server"
NPC_DIR = SERVER / "npc" / "custom" / "midnight"

def patch_file(p: Path, is_cp874: bool = False):
    if not p.exists():
        return
    enc = "cp874" if is_cp874 else "utf-8"
    raw = p.read_bytes()
    try:
        text = raw.decode(enc)
    except Exception:
        text = raw.decode("latin-1")

    if "midnight_gate" in text:
        # Replace only map references, keep system name/script names
        text = text.replace('"midnight_gate"', '"mid_gate"')
        text = text.replace('.battle_map$ = "midnight_gate"', '.battle_map$ = "mid_gate"')
        text = text.replace('midnight_gate\tmapflag', 'mid_gate\tmapflag')
        text = text.replace('midnight_gate,50,', 'mid_gate,50,')
        text = text.replace('Map: midnight_gate', 'Map: mid_gate')
        text = text.replace('map: midnight_gate', 'map: mid_gate')
        text = text.replace('midnight_gate.rsw', 'mid_gate.rsw')
        text = text.replace('midnight_gate.gat', 'mid_gate.gat')
        text = text.replace('midnight_gate.gnd', 'mid_gate.gnd')
        p.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode(enc))
        print(f"Patched {p.name}")

def main():
    print("=== Renaming to mid_gate ===")
    # Configs
    patch_file(SERVER / "conf" / "maps_athena.conf", is_cp874=False)
    patch_file(SERVER / "db" / "import" / "instance_db.yml", is_cp874=False)

    # map_index.txt
    idx_path = SERVER / "db" / "import" / "map_index.txt"
    idx_txt = idx_path.read_text(encoding="latin-1")
    idx_txt = idx_txt.replace("midnight_gate", "mid_gate")
    idx_path.write_text(idx_txt, encoding="latin-1")
    print("Patched map_index.txt")

    # Scripts
    for name in ["midnight_core", "midnight_gate", "midnight_gate_wave", "midnight_gate_instance"]:
        patch_file(NPC_DIR / f"{name}.txt", is_cp874=True)
        patch_file(NPC_DIR / f"{name}.utf8.txt", is_cp874=False)

    print("=== Rename Complete ===")

if __name__ == "__main__":
    main()
