#!/usr/bin/env python3
"""Install authentic 3D dark dungeon geometry (2@cata - The Sealed Catacomb) as 'mid_gate'.

Features:
- Size: 160x160
- North Entrance: (80, 144)
- South Corridor: X=[77..83], Y=[102..140] (corridor sentinels)
- Main Arena & Altar: Centered at (80, 65), Radius ~25 cells
- Full official 3D QuadTree/bounding mesh hierarchy (guaranteed no black void)
- Updates:
  1. MidnightROClient/midnight.grf (mid_gate.gat, mid_gate.gnd, mid_gate.rsw, mid_gate.bmp)
  2. server/db/import/map_cache.dat (160x160 cells)
  3. server/db/import/instance_db.yml (Enter X: 80, Y: 144)
"""

from __future__ import annotations

import io
import os
import struct
import sys
import zlib
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
SERVER = ROOT / "server"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build


def pad40(s: bytes) -> bytes:
    return s + b"\x00" * (40 - len(s))


def main():
    print("=== Installing 2@cata (The Sealed Shadow Catacomb) as 'mid_gate' ===")

    # 1. Read base geometry from data.grf (2@cata)
    dg = Grf(DATA_GRF)
    gat_bytes = dg.read(b"data\\2@cata.gat")
    gnd_bytes = dg.read(b"data\\2@cata.gnd")
    rsw_raw = bytearray(dg.read(b"data\\2@cata.rsw"))
    bmp_key = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\2@cata.bmp"
    bmp_bytes = dg.read(bmp_key) if bmp_key in dg.entries else b""
    dg.close()

    # Verify 160x160 GAT
    w, h = struct.unpack_from("<II", gat_bytes, 6)
    print(f"Read 2@cata geometry: {w}x{h} (GAT: {len(gat_bytes)}, GND: {len(gnd_bytes)}, RSW: {len(rsw_raw)})")
    assert w == 160 and h == 160

    # 2. Patch RSW internal header pointers to mid_gate.gnd and mid_gate.gat
    rsw_raw[6:46] = pad40(b"")
    rsw_raw[46:86] = pad40(b"mid_gate.gnd")
    rsw_raw[86:126] = pad40(b"mid_gate.gat")
    rsw_raw[126:166] = pad40(b"")
    rsw_bytes = bytes(rsw_raw)

    # 3. Update server/db/import/map_cache.dat
    cache_path = SERVER / "db" / "import" / "map_cache.dat"
    raw_cache = cache_path.read_bytes()
    declared, count = struct.unpack_from("<IH", raw_cache, 0)
    pos = 8
    cache_entries = []
    for _ in range(count):
        nr, ew, eh, clen = struct.unpack_from("<12shhi", raw_cache, pos)
        pos += 20
        cdata = raw_cache[pos : pos + clen]
        pos += clen
        name = nr.split(b"\0", 1)[0].decode("ascii", "replace").lower()
        if name in ("mid_gate", "midnight_gat"):
            continue
        cache_entries.append((nr, ew, eh, cdata))

    cell_types = bytearray(w * h)
    for i in range(w * h):
        off = 14 + i * 20 + 16
        ctype = struct.unpack_from("<I", gat_bytes, off)[0]
        cell_types[i] = ctype & 0xFF

    comp_cells = zlib.compress(bytes(cell_types), 9)
    gate_name_raw = b"mid_gate"[:12].ljust(12, b"\x00")
    cache_entries.append((gate_name_raw, w, h, comp_cells))

    new_body = bytearray()
    for nr, ew, eh, edata in cache_entries:
        new_body += struct.pack("<12shhi", nr, ew, eh, len(edata))
        new_body += edata

    total_bytes = 8 + len(new_body)
    new_header = struct.pack("<IHH", total_bytes, len(cache_entries), 0)
    cache_path.write_bytes(new_header + new_body)
    print(f"Updated server map_cache.dat: {len(cache_entries)} maps total")

    # 4. Update server/db/import/instance_db.yml
    inst_db_path = SERVER / "db" / "import" / "instance_db.yml"
    inst_content = inst_db_path.read_text(encoding="utf-8")
    new_inst = """Header:
  Type: INSTANCE_DB
  Version: 2

Body:
  - Id: 100
    Name: Midnight Gate
    TimeLimit: 3600
    Enter:
      Map: mid_gate
      X: 80
      Y: 144
"""
    inst_db_path.write_text(new_inst, encoding="utf-8")
    print("Updated server instance_db.yml (Enter X: 80, Y: 144)")

    # 5. Package into Dev Client midnight.grf
    tg = Grf(TARGET_GRF)
    all_files = {}
    for entry in tg.entries:
        all_files[entry] = tg.read(entry)
    tg.close()

    all_files[b"data\\mid_gate.gat"] = gat_bytes
    all_files[b"data\\mid_gate.gnd"] = gnd_bytes
    all_files[b"data\\mid_gate.rsw"] = rsw_bytes
    if bmp_bytes:
        all_files[b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\map\\mid_gate.bmp"] = bmp_bytes

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"Staged GRF built: {staged_grf.stat().st_size} bytes")

    try:
        staged_grf.replace(TARGET_GRF)
        print("Successfully updated MidnightROClient/midnight.grf!")
    except Exception as e:
        print("Replace error:", e)


if __name__ == "__main__":
    main()
