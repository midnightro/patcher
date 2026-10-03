#!/usr/bin/env python3
"""Build and install authentic 3D maps for Midnight RO:
1. 'mid_redgate' (The Crimson Snow Realm / Red Gate) -> derived from guild_vs4 (100x100)
2. 'mid_double'  (The Cartenon Temple / Double Gate) -> derived from guild_vs3 (100x100)

Features:
- Guaranteed authentic Ragexe 3D QuadTree & bounding hierarchy (ZERO black void, perfect collision & rendering)
- Custom themed texture re-mapping:
  - Red Gate: authentic ice cave ground, frost walls, and frozen ice pillars
  - Double Gate: authentic sandstone temple colonnades and sacred sanctuary walls
- Custom thematic directional & ambient lighting:
  - Red Gate: Crimson blood-snow blizzard (diff: 0.85, 0.20, 0.20 / amb: 0.35, 0.10, 0.15)
  - Double Gate: Ancient Cartenon Sanctuary (diff: 0.80, 0.65, 0.40 / amb: 0.28, 0.15, 0.38)
- Themed custom minimaps (.bmp)
- Updates:
  1. MidnightROClient/midnight.grf (.gat, .gnd, .rsw, minimap .bmp)
  2. server/db/import/map_cache.dat (synchronized genuine GAT cells)
"""

from __future__ import annotations

import io
import os
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
UI_SOURCES = TOOLS / "ui_sources" / "midnight_special_maps"
MAP_SOURCES = UI_SOURCES / "maps"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build


def pad40(s: bytes) -> bytes:
    return s + b"\x00" * (40 - len(s))


def pad_slot(s: bytes, length: int = 80) -> bytes:
    return s + b"\x00" * (length - len(s))


def tint_minimap(bmp_data: bytes, r_mult: float, g_mult: float, b_mult: float) -> bytes:
    """Tints a 512x512 minimap BMP and exports as uncompressed BMP."""
    im = Image.open(io.BytesIO(bmp_data)).convert("RGB")
    pixels = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            # Keep pure black backgrounds intact
            if r <= 5 and g <= 5 and b <= 5:
                continue
            nr = min(255, int(r * r_mult))
            ng = min(255, int(g * g_mult))
            nb = min(255, int(b * b_mult))
            pixels[x, y] = (nr, ng, nb)
    buf = io.BytesIO()
    im.save(buf, format="BMP")
    return buf.getvalue()


def patch_gnd_textures(gnd_bytes: bytes, replacements: dict[int, bytes]) -> bytes:
    """Replaces texture paths in GND texture slot table without altering offsets or length."""
    gnd_raw = bytearray(gnd_bytes)
    tex_count, tex_len = struct.unpack_from("<II", gnd_raw, 18)
    pos = 26
    for i in range(tex_count):
        if i in replacements:
            new_tex = replacements[i]
            if len(new_tex) > tex_len - 1:
                new_tex = new_tex[: tex_len - 1]
            gnd_raw[pos : pos + tex_len] = pad_slot(new_tex, tex_len)
        pos += tex_len
    return bytes(gnd_raw)


def patch_rsw(rsw_bytes: bytes, gnd_name: str, gat_name: str,
              diff: tuple[float, float, float],
              amb: tuple[float, float, float],
              light_dir: tuple[int, int] = (45, 45)) -> bytes:
    """Repoints internal GND/GAT pointers and modifies light parameters at offset 190."""
    rsw_raw = bytearray(rsw_bytes)
    # Header pointers (offsets 6, 46, 86, 126)
    rsw_raw[6:46] = pad40(b"")
    rsw_raw[46:86] = pad40(gnd_name.encode("ascii"))
    rsw_raw[86:126] = pad40(gat_name.encode("ascii"))
    rsw_raw[126:166] = pad40(b"")

    # Light parameters at offset 190:
    # int light_longitude, int light_latitude,
    # float diff_r, float diff_g, float diff_b,
    # float amb_r, float amb_g, float amb_b
    struct.pack_into(
        "<iiffffff",
        rsw_raw,
        190,
        light_dir[0],
        light_dir[1],
        diff[0],
        diff[1],
        diff[2],
        amb[0],
        amb[1],
        amb[2],
    )
    return bytes(rsw_raw)


def update_server_map_cache(maps_to_add: list[tuple[str, bytes]]):
    """Updates server/db/import/map_cache.dat with genuine GAT cells."""
    cache_path = SERVER / "db" / "import" / "map_cache.dat"
    raw_cache = cache_path.read_bytes()
    declared, count = struct.unpack_from("<IH", raw_cache, 0)
    pos = 8
    cache_entries = []
    names_to_replace = {name.lower() for name, _ in maps_to_add}

    for _ in range(count):
        nr, ew, eh, clen = struct.unpack_from("<12shhi", raw_cache, pos)
        pos += 20
        cdata = raw_cache[pos : pos + clen]
        pos += clen
        name = nr.split(b"\0", 1)[0].decode("ascii", "replace").lower()
        if name in names_to_replace:
            continue
        cache_entries.append((nr, ew, eh, cdata))

    for name, gat_bytes in maps_to_add:
        w, h = struct.unpack_from("<II", gat_bytes, 6)
        cell_types = bytearray(w * h)
        for i in range(w * h):
            off = 14 + i * 20 + 16
            ctype = struct.unpack_from("<I", gat_bytes, off)[0]
            cell_types[i] = ctype & 0xFF
        comp_cells = zlib.compress(bytes(cell_types), 9)
        nr = name.encode("ascii")[:12].ljust(12, b"\x00")
        cache_entries.append((nr, w, h, comp_cells))
        print(f"  Added {name} ({w}x{h}, {len(comp_cells)} bytes compressed) to map_cache.dat")

    new_body = bytearray()
    for nr, ew, eh, edata in cache_entries:
        new_body += struct.pack("<12shhi", nr, ew, eh, len(edata))
        new_body += edata

    total_bytes = 8 + len(new_body)
    new_header = struct.pack("<IHH", total_bytes, len(cache_entries), 0)
    cache_path.write_bytes(new_header + new_body)
    print(f"Updated server map_cache.dat: {len(cache_entries)} maps total")


def main():
    print("=== Building Authentic 3D Maps: mid_redgate & mid_double ===")
    MAP_SOURCES.mkdir(parents=True, exist_ok=True)

    dg = Grf(DATA_GRF)

    # -----------------------------------------------------------------------
    # 1. Build 'mid_redgate' (from guild_vs4)
    # -----------------------------------------------------------------------
    print("\n[1/2] Processing 'mid_redgate' (base: guild_vs4 100x100)...")
    red_gat = dg.read(b"data\\guild_vs4.gat")
    red_gnd = dg.read(b"data\\guild_vs4.gnd")
    red_rsw = dg.read(b"data\\guild_vs4.rsw")
    red_bmp_key = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\guild_vs4.bmp"
    red_bmp_raw = dg.read(red_bmp_key)

    # Texture replacements for Crimson Ice Cave:
    # Slot 1: main floor -> ice cave floor 04
    # Slot 4: wall -> ice cave cliff 01
    # Slot 5, 6, 7: secondary floors -> ice cave floor 01, 02, 03
    red_tex_replacements = {
        1: b"\xc7\xca\xb5\xe5\xb9\xd9\xb4\xda\\\xbe\xf3\xc0\xbd\xb5\xbf\xb1\xbc_\xbe\xf3\xc0\xbd04.bmp",
        4: b"\xc7\xca\xb5\xe5\xb9\xd9\xb4\xda\\\xbe\xf3\xc0\xbd\xb5\xbf\xb1\xbc_\xc0\xfd\xba\xae01.bmp",
        5: b"\xc7\xca\xb5\xe5\xb9\xd9\xb4\xda\\\xbe\xf3\xc0\xbd\xb5\xbf\xb1\xbc_\xbe\xf3\xc0\xbd01.bmp",
        6: b"\xc7\xca\xb5\xe5\xb9\xd9\xb4\xda\\\xbe\xf3\xc0\xbd\xb5\xbf\xb1\xbc_\xbe\xf3\xc0\xbd02.bmp",
        7: b"\xc7\xca\xb5\xe5\xb9\xd9\xb4\xda\\\xbe\xf3\xc0\xbd\xb5\xbf\xb1\xbc_\xbe\xf3\xc0\xbd03.bmp",
    }
    red_gnd_patched = patch_gnd_textures(red_gnd, red_tex_replacements)

    # RSW with Crimson Blood-Snow Lighting
    red_rsw_patched = patch_rsw(
        red_rsw,
        gnd_name="mid_redgate.gnd",
        gat_name="mid_redgate.gat",
        diff=(0.85, 0.20, 0.20),  # Intense blood-red sunlight
        amb=(0.35, 0.10, 0.15),   # Deep crimson ambient shadow
        light_dir=(45, 45),
    )

    # Tint minimap to blood-snow crimson
    red_bmp_tinted = tint_minimap(red_bmp_raw, r_mult=1.35, g_mult=0.45, b_mult=0.55)

    # Save local copies in ui_sources
    (MAP_SOURCES / "mid_redgate.gat").write_bytes(red_gat)
    (MAP_SOURCES / "mid_redgate.gnd").write_bytes(red_gnd_patched)
    (MAP_SOURCES / "mid_redgate.rsw").write_bytes(red_rsw_patched)
    (MAP_SOURCES / "mid_redgate.bmp").write_bytes(red_bmp_tinted)
    print("  Saved mid_redgate files in ui_sources/midnight_special_maps/maps/")

    # -----------------------------------------------------------------------
    # 2. Build 'mid_double' (from guild_vs3)
    # -----------------------------------------------------------------------
    print("\n[2/2] Processing 'mid_double' (base: guild_vs3 100x100)...")
    dbl_gat = dg.read(b"data\\guild_vs3.gat")
    dbl_gnd = dg.read(b"data\\guild_vs3.gnd")
    dbl_rsw = dg.read(b"data\\guild_vs3.rsw")
    dbl_bmp_key = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\guild_vs3.bmp"
    dbl_bmp_raw = dg.read(dbl_bmp_key)
    dg.close()

    # guild_vs3 already has authentic sandstone temple architecture.
    # Keep its textures and apply golden-amber & mystic violet Cartenon Sanctuary lighting:
    dbl_gnd_patched = dbl_gnd  # keep intact for pristine stone details
    dbl_rsw_patched = patch_rsw(
        dbl_rsw,
        gnd_name="mid_double.gnd",
        gat_name="mid_double.gat",
        diff=(0.80, 0.65, 0.40),  # Golden holy amber illumination
        amb=(0.28, 0.15, 0.38),   # Ancient violet mystical shadows
        light_dir=(45, 45),
    )

    # Tint minimap to sacred amber/violet
    dbl_bmp_tinted = tint_minimap(dbl_bmp_raw, r_mult=1.15, g_mult=0.90, b_mult=1.20)

    # Save local copies in ui_sources
    (MAP_SOURCES / "mid_double.gat").write_bytes(dbl_gat)
    (MAP_SOURCES / "mid_double.gnd").write_bytes(dbl_gnd_patched)
    (MAP_SOURCES / "mid_double.rsw").write_bytes(dbl_rsw_patched)
    (MAP_SOURCES / "mid_double.bmp").write_bytes(dbl_bmp_tinted)
    print("  Saved mid_double files in ui_sources/midnight_special_maps/maps/")

    # -----------------------------------------------------------------------
    # 3. Update server map_cache.dat
    # -----------------------------------------------------------------------
    print("\n[3/4] Updating server map_cache.dat with authentic GAT cells...")
    update_server_map_cache([
        ("mid_redgate", red_gat),
        ("mid_double", dbl_gat),
    ])

    # -----------------------------------------------------------------------
    # 4. Package into MidnightROClient/midnight.grf
    # -----------------------------------------------------------------------
    print("\n[4/4] Packing into MidnightROClient/midnight.grf...")
    tg = Grf(TARGET_GRF)
    all_files = {}
    for entry in tg.entries:
        all_files[entry] = tg.read(entry)
    tg.close()

    # Map files dictionary
    new_entries = {
        b"data\\mid_redgate.gat": red_gat,
        b"data\\mid_redgate.gnd": red_gnd_patched,
        b"data\\mid_redgate.rsw": red_rsw_patched,
        b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\mid_redgate.bmp": red_bmp_tinted,
        b"data\\mid_double.gat": dbl_gat,
        b"data\\mid_double.gnd": dbl_gnd_patched,
        b"data\\mid_double.rsw": dbl_rsw_patched,
        b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\mid_double.bmp": dbl_bmp_tinted,
    }

    all_files.update(new_entries)

    # Update mp3nametable.txt to map mid_redgate to 125.mp3 (Forbidden Anguish)
    mp3_key = b"data\\mp3nametable.txt"
    if mp3_key in all_files:
        mp3_str = all_files[mp3_key].decode("latin1", "ignore")
        mp3_str = mp3_str.replace("mid_redgate.rsw#bgm\\108.mp3#", "mid_redgate.rsw#bgm\\125.mp3#")
        mp3_str = mp3_str.replace("mid_redgate.rsw#bgm\\124.mp3#", "mid_redgate.rsw#bgm\\125.mp3#")
        if "mid_redgate.rsw#bgm\\125.mp3#" not in mp3_str:
            mp3_str += "\r\nmid_redgate.rsw#bgm\\125.mp3#\r\n"
        all_files[mp3_key] = mp3_str.encode("latin1")
        print("  Updated mp3nametable.txt: mid_redgate -> bgm\\125.mp3 (Forbidden Anguish)")

    print(f"Total entries to pack in midnight.grf: {len(all_files)}")

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"Staged GRF built: {staged_grf.stat().st_size} bytes")

    try:
        staged_grf.replace(TARGET_GRF)
        print("Successfully updated MidnightROClient/midnight.grf!")
    except Exception as e:
        print(f"Notice: Could not replace directly (Client might be open): {e}")
        print(f"Staged file saved at: {staged_grf}")


if __name__ == "__main__":
    main()
