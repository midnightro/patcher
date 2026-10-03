#!/usr/bin/env python3
"""Build and install dedicated 3D map 'midnight_gate' (The Shadow Colosseum) for Midnight RO.

Layout (100x100 GAT / 50x50 GND):
- South Entrance & Corridor (The Hall of Gate):
  - Entrance spawn: (50, 15)
  - Exit Keeper NPC: (50, 12)
  - Corridor walk area: X=[44..56], Y=[12..44]
  - Corridor Guardian monster spawn zones: (50, 24) and (50, 36)
- Gateway Chokepoint:
  - X=[46..54], Y=[44..48]
- Grand Colosseum (The Shadow Arena):
  - Centered at (50, 70), radius 20 cells
  - Wave monster battle center: (50, 70)
  - North Boss Throne / Altar: (50, 86)
- Void Abyss Boundary:
  - Non-walkable void surrounding corridor and colosseum.

Files generated:
- data/midnight_gate.gat
- data/midnight_gate.gnd
- data/midnight_gate.rsw
- data/texture/유저인터페이스/map/midnight_gate.bmp
- data/mapnametable.txt (entry added)
- data/mp3nametable.txt (entry added)

Packages into MidnightROClient/midnight.grf cleanly.
Also updates server map_index.txt, maps_athena.conf, map_cache.dat, and instance_db.yml.
"""

from __future__ import annotations

import io
import math
import os
import shutil
import struct
import sys
import zlib
from pathlib import Path
from PIL import Image

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
SERVER = ROOT / "server"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
UI_SOURCES = TOOLS / "ui_sources" / "midnight_gate"
MAP_SOURCES = UI_SOURCES / "map"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build


def is_walkable_gat(x: int, y: int) -> tuple[bool, int, float]:
    """Returns (is_walkable, cell_type, height) for GAT cell (x, y)."""
    # 1. Entrance & Corridor
    if 44 <= x <= 56 and 12 <= y <= 44:
        return True, 0, 0.0

    # 2. Gateway Chokepoint
    if 46 <= x <= 54 and 44 <= y <= 48:
        return True, 0, 0.0

    # 3. North Boss Altar (Elevated slightly)
    if 45 <= x <= 55 and 82 <= y <= 89:
        return True, 0, 4.0

    # 4. Grand Colosseum (Octagonal / Circular Arena)
    dx = x - 50
    dy = y - 70
    dist2 = dx * dx + dy * dy
    if dist2 <= 20 * 20:
        return True, 0, 0.0

    # Outer Void Abyss: non-walkable wall (type 1)
    return False, 1, -80.0


def build_gat(w: int = 100, h: int = 100) -> bytes:
    """Build binary .gat file."""
    buf = bytearray()
    buf += b"GRAT"
    buf += struct.pack("<H", 0x0201) # ver 1.2
    buf += struct.pack("<II", w, h)

    for y in range(h):
        for x in range(w):
            walkable, ctype, height = is_walkable_gat(x, y)
            # 4 corner heights (bl, br, tl, tr)
            h_bl = height
            h_br = height
            h_tl = height
            h_tr = height
            buf += struct.pack("<ffffI", h_bl, h_br, h_tl, h_tr, ctype)

    return bytes(buf)


def is_tile_walkable_gnd(tx: int, ty: int) -> tuple[bool, int, float]:
    """GND tile (tx, ty) corresponds to 2x2 GAT cells:
    x in [2*tx, 2*tx+1], y in [2*ty, 2*ty+1].
    Returns (is_walkable, floor_tile_type, height).
    """
    gx = 2 * tx + 1
    gy = 2 * ty + 1
    walkable, ctype, h = is_walkable_gat(gx, gy)
    if not walkable:
        return False, 0, -80.0

    # Determine surface texture style
    # Boss Altar: Tile 3 (Altar stone)
    if 45 <= gx <= 55 and 82 <= gy <= 89:
        return True, 3, 4.0

    # Colosseum Center Emblem: Tile 2 (Magic circle/emblem)
    dx = gx - 50
    dy = gy - 70
    if dx * dx + dy * dy <= 8 * 8:
        return True, 2, 0.0

    # Normal Corridor / Colosseum: Tile 1 (Dark obsidian stone)
    return True, 1, 0.0


def build_gnd(w: int = 50, h: int = 50) -> bytes:
    """Build binary .gnd file (v1.7) matching RO engine specification."""
    buf = bytearray()
    buf += b"GRGN"
    buf += struct.pack("<H", 0x0701) # ver 1.7
    buf += struct.pack("<IIf", w, h, 10.0) # width, height, ratio

    textures = [
        b"BLACK.BMP",
        b"\xb1\xe2\xc5\xb8\xb8\xb6\xc0\xbb\xb3\xbb\xba\xce\\TN_in006.bmp", # Dark obsidian stone
        b"pe_kingch_02.bmp",                                               # Center emblem
        b"\xc7\xca\xb5\xe5\xb9\xd4\xb4\xd9\\gp-lostdun_g03.bmp",         # Altar & border stone
    ]
    tex_path_len = 80
    buf += struct.pack("<II", len(textures), tex_path_len)
    for tex in textures:
        padded = tex + b"\x00" * (tex_path_len - len(tex))
        buf += padded

    # Lightmaps: 1 ambient lightmap (8x8 RGBA)
    lm_count = 1
    lm_w = 8
    lm_h = 8
    lm_cell = 1
    buf += struct.pack("<IIII", lm_count, lm_w, lm_h, lm_cell)
    # 8x8 RGBA moonlight tone (B, G, R, A = 220, 190, 180, 255)
    lm_data = bytes([180, 190, 220, 255] * (lm_w * lm_h))
    buf += lm_data

    # Tiles:
    # Tile 0: Void floor (BLACK.BMP)
    # Tile 1: Dark Obsidian Stone floor
    # Tile 2: Center Emblem floor
    # Tile 3: Altar Stone floor
    # Tile 4: Wall / Border side texture
    tile_defs = [
        (0, 0), # tex 0, lm 0
        (1, 0), # tex 1, lm 0
        (2, 0), # tex 2, lm 0
        (3, 0), # tex 3, lm 0
        (3, 0), # tex 3, lm 0 for walls
    ]
    buf += struct.pack("<I", len(tile_defs))
    for tex_idx, lm_idx in tile_defs:
        # u1, u2, u3, u4, v1, v2, v3, v4 (8 floats)
        # In GND tile: u1=0, u2=1, u3=0, u4=1; v1=0, v2=0, v3=1, v4=1
        u = (0.0, 1.0, 0.0, 1.0)
        v = (0.0, 0.0, 1.0, 1.0)
        buf += struct.pack("<4f4f", *u, *v)
        buf += struct.pack("<HH", tex_idx, lm_idx)
        buf += bytes([255, 255, 255, 255]) # BGRA color tint

    # Cubes: w * h cubes (each 28 bytes: 4 heights + 3 tile indices)
    for ty in range(h):
        for tx in range(w):
            walkable, floor_tile, height = is_tile_walkable_gnd(tx, ty)
            if walkable:
                # 4 corner heights: top-left, top-right, bottom-left, bottom-right
                tl = height
                tr = height
                bl = height
                br = height
                top_tile = floor_tile

                # Check if neighboring tiles are void to place side walls
                has_side_wall = False
                if ty > 0 and not is_tile_walkable_gnd(tx, ty - 1)[0]:
                    has_side_wall = True
                if tx < w - 1 and not is_tile_walkable_gnd(tx + 1, ty)[0]:
                    has_side_wall = True

                side_tile = 4 if has_side_wall else -1
                front_tile = 4 if has_side_wall else -1
            else:
                tl = -80.0
                tr = -80.0
                bl = -80.0
                br = -80.0
                top_tile = 0 # BLACK.BMP void
                side_tile = -1
                front_tile = -1

            buf += struct.pack("<ffffiii", tl, tr, bl, br, top_tile, side_tile, front_tile)

    return bytes(buf)


def build_rsw(map_name: str = "midnight_gate") -> bytes:
    """Build binary .rsw file (v2.1) linking GND, GAT, lighting, and pillar models."""
    buf = bytearray()
    buf += b"GRSW"
    buf += struct.pack("<H", 0x0102) # ver 2.1

    def pad40(s: bytes) -> bytes:
        return s + b"\x00" * (40 - len(s))

    buf += pad40(b"") # ini
    buf += pad40(f"{map_name}.gnd".encode("latin-1"))
    buf += pad40(f"{map_name}.gat".encode("latin-1"))
    buf += pad40(b"") # src

    # Water: level, type, wave_h, wave_spd, wave_pitch, anim_spd
    buf += struct.pack("<fifffi", -200.0, 0, 1.0, 2.0, 50.0, 3)

    # Light:
    # longitude, latitude, diff_r, diff_g, diff_b, amb_r, amb_g, amb_b, shadow_intensity
    # Cool moonlit blue directional (0.50, 0.55, 0.80), Deep Shadow Monarch ambient (0.28, 0.22, 0.42)
    buf += struct.pack(
        "<iifffffff",
        45, 45,
        0.50, 0.55, 0.80,
        0.28, 0.22, 0.42,
        0.55
    )

    # Ground margins: top, bottom, left, right
    buf += struct.pack("<iiii", 0, 0, 0, 0)

    # Objects: Place Stone Pillars along corridor and colosseum perimeter
    # Object structure in RSW 2.1 (type 1 = Model):
    # type (4), name (40), anim_type (4), anim_spd (4), block_type (4),
    # rsm_name (80), node_name (80),
    # pos_x, pos_y, pos_z (3f),
    # rot_x, rot_y, rot_z (3f),
    # scale_x, scale_y, scale_z (3f)
    pillar_rsm = b"\xb0\xc5\xba\xce\xc0\xcc\xbc\xbd\\\xb0\xc5\xba\xce_\xbf\xeb\xb1\xe2\xb5\xd5.rsm" # Turtle dragon stone pillar
    pillars = []

    # Corridor pillars left & right (in world units: 1 gat cell = 5 units, origin at center 50,50 = 0,0)
    # Center is (50, 50). Cell (gx, gy) -> World X = (gx - 50) * 5.0, World Z = (50 - gy) * 5.0
    for y_gate in [16, 24, 32, 40]:
        wz = (50 - y_gate) * 5.0
        # Left pillar at x = 42
        pillars.append(((42 - 50) * 5.0, 0.0, wz))
        # Right pillar at x = 58
        pillars.append(((58 - 50) * 5.0, 0.0, wz))

    # Colosseum perimeter pillars (8 pillars around radius 21 at y=70)
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        px = 50 + int(math.cos(rad) * 21)
        py = 70 + int(math.sin(rad) * 21)
        pillars.append(((px - 50) * 5.0, 0.0, (50 - py) * 5.0))

    obj_count = len(pillars)
    buf += struct.pack("<I", obj_count)

    for i, (wx, wy, wz) in enumerate(pillars):
        buf += struct.pack("<I", 1) # type 1 = Model
        pname = f"pillar_{i}".encode("latin-1")
        buf += pname + b"\x00" * (40 - len(pname))
        buf += struct.pack("<iii", 0, 0, 0) # anim_type, anim_speed, block_type
        buf += pillar_rsm + b"\x00" * (80 - len(pillar_rsm))
        buf += b"\x00" * 80 # node_name
        buf += struct.pack("<fff", wx, wy, wz) # pos (X, Y, Z)
        buf += struct.pack("<fff", 0.0, 0.0, 0.0) # rot
        buf += struct.pack("<fff", 1.0, 1.0, 1.0) # scale

    return bytes(buf)


def update_server_files(gat_bytes: bytes):
    """Update server/db/import/map_index.txt, maps_athena.conf, map_cache.dat, and instance_db.yml."""
    print("Updating server database and configs...")

    # 1. server/db/import/map_index.txt
    map_index_path = SERVER / "db" / "import" / "map_index.txt"
    content = map_index_path.read_text(encoding="latin-1", errors="replace")
    if "mid_gate" not in content:
        content += "\nmid_gate\n"
        map_index_path.write_text(content, encoding="latin-1")
        print("   Added mid_gate to db/import/map_index.txt")

    # 2. server/conf/maps_athena.conf
    maps_conf_path = SERVER / "conf" / "maps_athena.conf"
    conf_content = maps_conf_path.read_text(encoding="utf-8-sig")
    if "map: mid_gate" not in conf_content:
        conf_content += "\nmap: mid_gate\n"
        maps_conf_path.write_text(conf_content, encoding="utf-8-sig")
        print("   Added map: mid_gate to conf/maps_athena.conf")

    # 3. server/db/import/map_cache.dat
    cache_path = SERVER / "db" / "import" / "map_cache.dat"
    if cache_path.exists():
        raw_cache = cache_path.read_bytes()
        declared, count = struct.unpack_from("<IH", raw_cache, 0)
        pos = 8
        cache_entries = []
        already_has_gate = False
        for _ in range(count):
            nr, w, h, clen = struct.unpack_from("<12shhi", raw_cache, pos)
            pos += 20
            cdata = raw_cache[pos:pos+clen]
            pos += clen
            name = nr.split(b"\0", 1)[0].decode("ascii", "replace").lower()
            if name == "mid_gate":
                already_has_gate = True
            elif name == "midnight_gat":
                # Remove obsolete truncated entry
                continue
            cache_entries.append((nr, w, h, cdata))

        if not already_has_gate:
            # Build cell byte array from GAT
            w = 100
            h = 100
            cell_types = bytearray(w * h)
            for i in range(w * h):
                off = 14 + i * 20 + 16
                ctype = struct.unpack_from("<I", gat_bytes, off)[0]
                cell_types[i] = ctype & 0xFF

            comp_cells = zlib.compress(bytes(cell_types), 9)
            gate_name_raw = b"mid_gate"[:12].ljust(12, b"\x00")
            cache_entries.append((gate_name_raw, w, h, comp_cells))

            # Pack back into binary
            new_body = bytearray()
            for nr, ew, eh, edata in cache_entries:
                new_body += struct.pack("<12shhi", nr, ew, eh, len(edata))
                new_body += edata

            total_bytes = 8 + len(new_body)
            new_header = struct.pack("<IHH", total_bytes, len(cache_entries), 0)
            cache_path.write_bytes(new_header + new_body)
            print(f"   Injected mid_gate into db/import/map_cache.dat (total maps: {len(cache_entries)})")
        else:
            print("   mid_gate already in map_cache.dat")

    # 4. server/db/import/instance_db.yml
    inst_db_path = SERVER / "db" / "import" / "instance_db.yml"
    inst_content = inst_db_path.read_text(encoding="utf-8")
    if "mid_gate" not in inst_content:
        inst_entry = """
Body:
  - Id: 100
    Name: Midnight Gate
    TimeLimit: 3600
    Enter:
      Map: mid_gate
      X: 50
      Y: 15
"""
        inst_content += inst_entry
        inst_db_path.write_text(inst_content, encoding="utf-8")
        print("   Added Midnight Gate instance definition to db/import/instance_db.yml")


def main():
    print("=== Building 'mid_gate' 3D Map Assets (The Shadow Colosseum) ===")
    MAP_SOURCES.mkdir(parents=True, exist_ok=True)

    # 1. Generate GAT, GND, RSW
    print("1. Generating 3D map binaries (.gat, .gnd, .rsw)...")
    gat_bytes = build_gat(100, 100)
    gnd_bytes = build_gnd(50, 50)
    rsw_bytes = build_rsw("mid_gate")

    (MAP_SOURCES / "mid_gate.gat").write_bytes(gat_bytes)
    (MAP_SOURCES / "mid_gate.gnd").write_bytes(gnd_bytes)
    (MAP_SOURCES / "mid_gate.rsw").write_bytes(rsw_bytes)
    print(f"   GAT: {len(gat_bytes)} bytes | GND: {len(gnd_bytes)} bytes | RSW: {len(rsw_bytes)} bytes")

    # 2. Loading screen bitmap
    loading_bmp = MAP_SOURCES / "midnight_gate.bmp"
    if not loading_bmp.exists():
        print("   ERROR: missing midnight_gate.bmp in map sources!")
        return

    # 3. Update Server Files
    update_server_files(gat_bytes)

    # 4. Package into Dev Client midnight.grf
    print("2. Packaging map into Dev client midnight.grf...")
    target_grf = Grf(TARGET_GRF)
    all_files = {}
    for entry in target_grf.entries:
        all_files[entry] = target_grf.read(entry)

    # Insert map files
    all_files[b"data\\mid_gate.gat"] = gat_bytes
    all_files[b"data\\mid_gate.gnd"] = gnd_bytes
    all_files[b"data\\mid_gate.rsw"] = rsw_bytes
    all_files[b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\mid_gate.bmp"] = loading_bmp.read_bytes()

    # Update mapnametable.txt
    mapnametable_key = b"data\\mapnametable.txt"
    mnt_raw = all_files.get(mapnametable_key, b"").decode("latin-1", "replace")
    if "mid_gate.rsw#" not in mnt_raw:
        mnt_raw += "\r\nmid_gate.rsw#Midnight Gate - The Shadow Realm#\r\n"
        all_files[mapnametable_key] = mnt_raw.encode("latin-1")
        print("   Added mid_gate to mapnametable.txt")

    # Update mp3nametable.txt (BGM 18 - Theme of Boss / Dungeon)
    mp3nametable_key = b"data\\mp3nametable.txt"
    mp3_raw = all_files.get(mp3nametable_key, b"").decode("latin-1", "replace")
    if "mid_gate.rsw#" not in mp3_raw:
        mp3_raw += "\r\nmid_gate.rsw#bgm\\18.mp3#\r\n"
        all_files[mp3nametable_key] = mp3_raw.encode("latin-1")
        print("   Added mid_gate to mp3nametable.txt")

    # Build staged GRF and replace
    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"   Built staged GRF: {staged_grf} ({staged_grf.stat().st_size} bytes)")

    try:
        staged_grf.replace(TARGET_GRF)
        print("   Successfully updated Dev client midnight.grf (MidnightROClient/midnight.grf)!")
    except PermissionError:
        print("   WARNING: midnight.grf is locked by a running client process. Staged at midnight.grf.staged")

    print("\n=== 'mid_gate' Map Successfully Built & Installed! ===")


if __name__ == "__main__":
    main()
