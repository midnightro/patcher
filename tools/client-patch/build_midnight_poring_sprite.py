#!/usr/bin/env python3
"""Build and install Midnight Poring (25000) client sprite and action assets.

- Generates a Cosmic Midnight Violet palette with golden moon highlights and starry accents.
- Enhances all 49 Poring frames with the Golden Crescent Moon motif on front-facing angles.
- Encodes a valid Ragnarok SPR 2.1 archive with custom 1024-byte palette.
- Reuses calibrated donor ACT for flawless animations across all 8 directions.
- Patches jobname_f.lub bytecode to map ID 25000 -> "midnight_poring".
- Stages and updates MidnightROClient/midnight.grf cleanly.
"""

from __future__ import annotations

import os
import shutil
import struct
import sys
from pathlib import Path
from PIL import Image

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
UI_SOURCES = TOOLS / "ui_sources" / "midnight_poring"

sys.path.insert(0, str(TOOLS))
from grf import Grf  # noqa: E402
from lua51_inspect import Reader, parse_proto  # noqa: E402
from make_grf import build  # noqa: E402

MONSTER_DIR = b"data\\sprite\\\xb8\xf3\xbd\xba\xc5\xcd\\"
JOBNAME_KEY = b"data\\luafiles514\\lua files\\datainfo\\jobname.lub"
JOBNAME_F_KEY = b"data\\luafiles514\\lua files\\datainfo\\jobname_f.lub"
JOBNAME_F_LUA_KEY = b"data\\luafiles514\\lua files\\datainfo\\jobname_f.lua"

COLOR_MAP = {
    # Highlights: Soft celestial lilac / starlight glow
    64: (218, 198, 255),
    65: (185, 150, 252),
    66: (146,  98, 235),
    67: (112,  64, 202),
    68: ( 84,  42, 168),
    69: ( 60,  26, 132),
    70: ( 40,  15,  98),
    71: ( 24,   8,  65),

    # Secondary gradient / curves
    82: (195, 162, 255),
    83: (152, 105, 225),
    84: (108,  62, 178),
    85: ( 72,  34, 135),
    86: ( 45,  18,  92),

    # Blush & interior mouth tones: Mystical twilight lavender
    16: (160, 136, 228),
    17: (140, 112, 205),
    18: (118,  86, 178),
    19: ( 98,  66, 152),
    20: ( 78,  48, 126),
    21: ( 58,  32, 100),
    22: ( 40,  20,  75),
    26: (205, 185, 255),
    27: (175, 148, 235),
    29: (128, 100, 188),
    33: (228, 210, 255),

    # Shading / Ambience
    140: (105, 110, 190),
    142: ( 55,  52, 115),
    173: ( 85,  42, 118),

    # Gold / Star Accents
    40: (255, 240, 130),
    41: (248, 208,  80),
    42: (225, 172,  48),
    43: (188, 135,  32),
    88: (255, 252, 200),
    144: (255, 242, 155),
    145: (238, 190,  70),
    146: (205, 150,  42),
    147: (165, 115,  32),
    148: (128,  82,  22),
    149: ( 92,  52, 135),
    150: ( 68,  32, 105),
    151: ( 48,  20,  78),
}

MOON_COLORS = {
    240: (255, 255, 215),  # Bright Moon Highlight
    241: (255, 228,  70),  # Pure Golden Moon Core
    242: (238, 188,  35),  # Golden Amber Shade
    243: (185, 130,  18),  # Deep Bronze Outline
    244: (180, 245, 255),  # Luminous Cyan Stardust
    245: (255, 255, 255),  # Pure Starlight
}

# Crescent moon pattern relative to center (dx, dy, color_index)
MOON_PATTERN = [
    (0, -2, 240), (1, -2, 241),
    (-1, -1, 240), (0, -1, 241),
    (-1, 0, 241), (0, 0, 241),
    (-1, 1, 241), (0, 1, 241),
    (0, 2, 242), (1, 2, 243)
]


def rle_encode(indices: bytes) -> bytes:
    """Encode indexed pixel buffer using SPR 2.1 RLE algorithm."""
    out = bytearray()
    idx = 0
    n = len(indices)
    while idx < n:
        v = indices[idx]
        idx += 1
        out.append(v)
        if v == 0:
            count = 1
            while idx < n and indices[idx] == 0 and count < 255:
                count += 1
                idx += 1
            out.append(count)
    return bytes(out)


def build_spr_and_act() -> tuple[bytes, bytes]:
    """Extract donor Poring SPR/ACT and build Midnight Poring assets."""
    data_grf = Grf(DATA_GRF)
    try:
        donor_spr_raw = data_grf.read(MONSTER_DIR + b"poring.spr")
        donor_act = data_grf.read(MONSTER_DIR + b"poring.act")
    finally:
        data_grf.close()

    # Build Palette
    palette_raw = bytearray(donor_spr_raw[-1024:])
    for idx, (r, g, b) in COLOR_MAP.items():
        palette_raw[idx * 4: (idx + 1) * 4] = bytes((r, g, b, 0))
    for idx, (r, g, b) in MOON_COLORS.items():
        palette_raw[idx * 4: (idx + 1) * 4] = bytes((r, g, b, 0))

    # Read 49 frames
    offset = 8
    frames = []
    for i in range(49):
        w, h = struct.unpack_from('<HH', donor_spr_raw, offset)
        offset += 4
        comp_len = struct.unpack_from('<H', donor_spr_raw, offset)[0]
        offset += 2
        raw = donor_spr_raw[offset: offset + comp_len]
        offset += comp_len

        decompressed = bytearray()
        idx = 0
        while idx < len(raw):
            v = raw[idx]
            idx += 1
            decompressed.append(v)
            if v == 0:
                count = raw[idx]
                idx += 1
                if count > 1:
                    decompressed.extend(b'\x00' * (count - 1))
        frames.append({'width': w, 'height': h, 'pixels': decompressed})

    # Apply moon emblem to front-facing / side-facing frames
    # Front-facing frames in Poring: South (0..7), South-West (8..15), South-East (40..48)
    front_frames = set(range(0, 8)) | set(range(8, 16)) | set(range(40, 48))

    spr_payload = bytearray(b"SP\x01\x02")
    spr_payload += struct.pack("<HH", len(frames), 0)

    for i, frame in enumerate(frames):
        w, h = frame['width'], frame['height']
        pixels = bytearray(frame['pixels'])

        if i in front_frames:
            cx = w // 2
            if i in range(8, 16):
                cx -= 2  # slight offset for SW angle
            elif i in range(40, 48):
                cx += 2  # slight offset for SE angle

            step = i % 8
            cy = 13
            if step in (1, 5):
                cy = 14
            elif step in (2, 6):
                cy = 15
            elif step in (3, 7):
                cy = 12

            for dx, dy, col in MOON_PATTERN:
                px, py = cx + dx, cy + dy
                if 0 <= px < w and 0 <= py < h:
                    pos = py * w + px
                    if pixels[pos] != 0:
                        pixels[pos] = col

            # Little sparkles
            s1_x, s1_y = cx - 7, cy + 5
            if 0 <= s1_x < w and 0 <= s1_y < h and pixels[s1_y * w + s1_x] != 0:
                pixels[s1_y * w + s1_x] = 244
            s2_x, s2_y = cx + 8, cy + 4
            if 0 <= s2_x < w and 0 <= s2_y < h and pixels[s2_y * w + s2_x] != 0:
                pixels[s2_y * w + s2_x] = 240

        encoded = rle_encode(bytes(pixels))
        spr_payload += struct.pack("<HHH", w, h, len(encoded))
        spr_payload += encoded

    spr_payload += bytes(palette_raw)
    return bytes(spr_payload), donor_act


def patch_jobname() -> bytes:
    """Patch jobname.lub bytecode to map ID 25000 -> 'midnight_poring'."""
    data_grf = Grf(DATA_GRF)
    try:
        raw = data_grf.read(JOBNAME_KEY)
    finally:
        data_grf.close()

    p = parse_proto(Reader(raw))

    def encode_abx(op, a, bx):
        return (bx << 14) | (a << 6) | op

    def encode_abc(op, a, b, c):
        return (b << 23) | (c << 14) | (a << 6) | op

    idx_mob_id = len(p['constants'])
    p['constants'].append(25000)
    idx_mob_name = len(p['constants'])
    p['constants'].append(b'midnight_poring')

    # In jobname.lub, R(0) is the JobNameTable right before SETGLOBAL / RETURN
    inst1 = encode_abx(1, 1, idx_mob_id)
    inst2 = encode_abx(1, 2, idx_mob_name)
    inst3 = encode_abc(9, 0, 1, 2)

    p['code'].insert(-2, inst1)
    p['code'].insert(-2, inst2)
    p['code'].insert(-2, inst3)
    if p['lineinfo']:
        p['lineinfo'].insert(-2, 0)
        p['lineinfo'].insert(-2, 0)
        p['lineinfo'].insert(-2, 0)

    def pack_proto_chunk(proto, is_top=False):
        buf = bytearray()
        src = proto['source'] if is_top else None
        if src is None:
            buf += struct.pack('<I', 0)
        else:
            buf += struct.pack('<I', len(src) + 1) + src + b'\x00'
        buf += struct.pack('<II', proto['line_start'], proto['line_end'])
        buf += bytes([proto['nups'], proto['params'], proto['vararg'], proto['stack']])
        buf += struct.pack('<I', len(proto['code']))
        for inst in proto['code']:
            buf += struct.pack('<I', inst)
        buf += struct.pack('<I', len(proto['constants']))
        for c in proto['constants']:
            if c is None:
                buf += b'\x00'
            elif isinstance(c, bool):
                buf += b'\x01' + bytes([1 if c else 0])
            elif isinstance(c, (int, float)):
                buf += b'\x03' + struct.pack('<d', float(c))
            elif isinstance(c, bytes):
                buf += b'\x04' + struct.pack('<I', len(c) + 1) + c + b'\x00'
        buf += struct.pack('<I', len(proto['children']))
        for ch in proto['children']:
            buf += pack_proto_chunk(ch, False)
        buf += struct.pack('<I', len(proto['lineinfo']))
        for line in proto['lineinfo']:
            buf += struct.pack('<I', line)
        buf += struct.pack('<I', len(proto['locals']))
        for name, start, end in proto['locals']:
            buf += struct.pack('<I', len(name) + 1) + name + b'\x00' + struct.pack('<II', start, end)
        buf += struct.pack('<I', len(proto['upvalues']))
        for upval in proto['upvalues']:
            buf += struct.pack('<I', len(upval) + 1) + upval + b'\x00'
        return bytes(buf)

    patched = raw[:12] + pack_proto_chunk(p, True)
    # verify
    _ = parse_proto(Reader(patched))
    return patched


def main():
    UI_SOURCES.mkdir(parents=True, exist_ok=True)
    print("1. Generating Midnight Poring SPR & ACT...")
    spr_bytes, act_bytes = build_spr_and_act()

    spr_file = UI_SOURCES / "midnight_poring.spr"
    act_file = UI_SOURCES / "midnight_poring.act"
    spr_file.write_bytes(spr_bytes)
    act_file.write_bytes(act_bytes)
    print(f"   Saved {spr_file.name} ({len(spr_bytes)} bytes)")
    print(f"   Saved {act_file.name} ({len(act_bytes)} bytes)")

    print("2. Patching jobname.lub...")
    lub_bytes = patch_jobname()
    lub_file = UI_SOURCES / "jobname.lub"
    lub_file.write_bytes(lub_bytes)
    print(f"   Saved {lub_file.name} ({len(lub_bytes)} bytes)")

    # Read current live midnight.grf
    print("3. Updating MidnightROClient/midnight.grf...")
    current_grf = Grf(TARGET_GRF)
    all_files = {}
    try:
        for entry in current_grf.entries:
            all_files[entry] = current_grf.read(entry)
    finally:
        current_grf.close()

    # Ensure broken jobname_f.lub is completely purged from midnight.grf
    all_files.pop(JOBNAME_F_KEY, None)
    all_files.pop(JOBNAME_F_LUA_KEY, None)

    # Add the new members
    all_files[MONSTER_DIR + b"midnight_poring.spr"] = spr_bytes
    all_files[MONSTER_DIR + b"midnight_poring.act"] = act_bytes
    all_files[JOBNAME_KEY] = lub_bytes

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"   Built staged GRF: {staged_grf}")

    # Try applying immediately
    try:
        staged_grf.replace(TARGET_GRF)
        print("   Applied staged GRF -> midnight.grf successfully!")
    except PermissionError:
        print("   WARNING: midnight.grf is locked by game client. Staged as midnight.grf.staged")

    # Also update web public assets for ID 25000 so web matches game client!
    print("4. Updating Web assets...")
    web_dir = ROOT / "web" / "public" / "assets" / "monsters" / "25000"
    web_dir.mkdir(parents=True, exist_ok=True)
    (web_dir / "sprite.spr").write_bytes(spr_bytes)
    (web_dir / "action.act").write_bytes(act_bytes)
    print("   Web assets updated in web/public/assets/monsters/25000/")


if __name__ == "__main__":
    main()
