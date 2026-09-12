#!/usr/bin/env python3
"""Build and install Midnight Monsters Suite (IDs: 25000–25006).

- Generates premium Cosmic Midnight palettes for all 6 remaining monsters:
  25001: Midnight Familiar (donor: farmiliar)
  25002: Midnight Skeleton (donor: skeleton)
  25003: Midnight Zombie   (donor: zombie)
  25004: Shadow Willow     (donor: elder_wilow)
  25005: Lost Soul         (donor: eggyra)
  25006: Dream Whisper     (donor: whisper)
- Preserves Midnight Poring (25000) with its custom Golden Crescent Moon emblem.
- Patches jobname.lub to register JobNameTable[25000..25006].
- Patches System/monster_size_effect_new.lub to attach thematic visual particle effects to all 7 monsters.
- Packages everything cleanly into MidnightROClient/midnight.grf and disk files.
- Updates web database assets and APNG previews.
"""

from __future__ import annotations

import colorsys
import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
UI_SOURCES = TOOLS / "ui_sources" / "midnight_monsters"
PORING_SOURCES = TOOLS / "ui_sources" / "midnight_poring"

sys.path.insert(0, str(TOOLS))
from grf import Grf  # noqa: E402
from lua51_inspect import Reader, parse_proto  # noqa: E402
from make_grf import build  # noqa: E402

MONSTER_DIR = b"data\\sprite\\\xb8\xf3\xbd\xba\xc5\xcd\\"
JOBNAME_KEY = b"data\\luafiles514\\lua files\\datainfo\\jobname.lub"
MONSTER_SIZE_EFFECT_KEY = b"system\\monster_size_effect_new.lub"

# Monster metadata: (id, name, sprite_file_basename, donor_spr_name, donor_act_name)
MONSTERS = [
    (25000, "midnight_poring",   "midnight_poring",   "poring",      "poring"),
    (25001, "midnight_familiar", "midnight_familiar", "farmiliar",   "farmiliar"),
    (25002, "midnight_skeleton", "midnight_skeleton", "skeleton",    "skeleton"),
    (25003, "midnight_zombie",   "midnight_zombie",   "zombie",      "zombie"),
    (25004, "shadow_willow",     "shadow_willow",     "elder_wilow", "elder_wilow"),
    (25005, "midnight_demon",    "midnight_demon",    "mini_demon",  "mini_demon"),
    (25006, "midnight_hyegun",   "midnight_hyegun",   "hyegun",      "hyegun"),
]

# Visual effects to attach: monster_id -> list of effect names in EFFECT table
MONSTER_EFFECTS = {
    25000: ["EF_MOONSTAR", "EF_GLOW1"],        # Luminous stardust & moonlight glow
    25001: ["EF_TORCH_PURPLE"],                # Purple night mist
    25002: ["EF_BLUELIGHTBODY"],               # Pale moonlight spectral glow
    25003: ["EF_POISONSMOKE"],                 # Dark noxious night miasma
    25004: ["EF_GLOW2"],                       # Subtle sparkling moonlight shimmer
    25005: ["EF_TORCH_PURPLE"],                # Flying night imp purple flame aura
    25006: ["EF_GHOST", "EF_SOULLIGHT"],       # Chinese vampire ghost spectral radiance
}


def recolor_familiar_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Bright red/crimson eyes & fangs
    if s > 0.45 and (h < 0.06 or h > 0.94) and v > 0.5:
        nr, ng, nb = colorsys.hsv_to_rgb(0.98, 0.95, min(1.0, v * 1.1))
    else:
        # Body/wings: deep midnight indigo / violet
        new_h = 0.74 + (h - 0.05) * 0.1
        new_s = min(1.0, s * 1.25 + 0.18)
        new_v = v * 0.82
        nr, ng, nb = colorsys.hsv_to_rgb(new_h % 1.0, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


def recolor_skeleton_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Bones: lunar silver-blue moonlight
    if v > 0.32:
        new_h = 0.60
        new_s = min(0.38, s * 0.4 + 0.14)
        new_v = min(1.0, v * 1.12)
    else:
        # Deep shadows / metal: dark midnight navy
        new_h = 0.68
        new_s = 0.55
        new_v = v * 0.88
    nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


def recolor_zombie_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Clothes (brownish tan): deep twilight purple robes
    if 0.05 <= h <= 0.19:
        new_h = 0.75
        new_s = min(0.85, s * 1.25 + 0.22)
        new_v = v * 0.84
    else:
        # Flesh: ashen phantom twilight gray-violet
        new_h = 0.66
        new_s = min(0.32, s * 0.5 + 0.12)
        new_v = v * 0.90
    nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


def recolor_willow_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    if 0.11 <= h <= 0.19 and v > 0.68:
        # Eyes / core glow: glowing golden moon amber
        nr, ng, nb = colorsys.hsv_to_rgb(0.12, 0.95, v)
    elif 0.20 <= h <= 0.48:
        # Leaves: glowing celestial astral sapphire & violet crystal foliage
        new_h = 0.61 + (h - 0.20) * 0.45
        new_s = min(1.0, s * 1.15 + 0.15)
        new_v = min(1.0, v * 1.2)
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    else:
        # Bark: dark obsidian charcoal with subtle violet sheen
        new_h = 0.76
        new_s = min(0.38, s * 0.5 + 0.12)
        new_v = v * 0.72
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


def recolor_mini_demon_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Eyes / golden accents (yellows: 0.08 <= h <= 0.18 and v > 0.5)
    if 0.08 <= h <= 0.18 and v > 0.5:
        nr, ng, nb = colorsys.hsv_to_rgb(0.13, 0.95, min(1.0, v * 1.1))
    elif s > 0.3 and (h < 0.08 or h > 0.92):
        # Red imp skin -> deep midnight violet / cosmic indigo
        new_h = 0.74 + (h % 1.0) * 0.1
        new_s = min(1.0, s * 1.25 + 0.15)
        new_v = v * 0.85
        nr, ng, nb = colorsys.hsv_to_rgb(new_h % 1.0, new_s, new_v)
    elif s < 0.25 and v > 0.7:
        # White teeth / highlights -> celestial lilac
        nr, ng, nb = colorsys.hsv_to_rgb(0.72, 0.25, v)
    else:
        # Dark horns / wings / shadow
        new_h = 0.70
        new_s = min(0.6, s + 0.1)
        new_v = v * 0.8
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


def recolor_hyegun_color(r: int, g: int, b: int) -> tuple[int, int, int]:
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Talisman / yellow embroidery / golden hat ornament
    if 0.10 <= h <= 0.18 and s > 0.4:
        nr, ng, nb = colorsys.hsv_to_rgb(0.13, 0.95, min(1.0, v * 1.1))
    elif (h < 0.08 or h > 0.92) and s > 0.4:
        # Red rune on talisman or red prayer beads -> glowing crimson ruby
        nr, ng, nb = colorsys.hsv_to_rgb(0.98, 0.9, v)
    elif 0.50 <= h <= 0.65 and s > 0.3:
        # Blue robe -> deep imperial midnight violet / indigo robe
        new_h = 0.74
        new_s = min(0.9, s * 1.2 + 0.15)
        new_v = v * 0.88
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    elif s < 0.3 and v > 0.4:
        # Pale ghost skin -> lunar moonlight silver-blue
        new_h = 0.60
        new_s = min(0.35, s + 0.12)
        new_v = min(1.0, v * 1.08)
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    else:
        # Dark outlines
        new_h = 0.72
        new_s = 0.45
        new_v = v * 0.82
        nr, ng, nb = colorsys.hsv_to_rgb(new_h, new_s, new_v)
    return int(nr * 255), int(ng * 255), int(nb * 255)


RECOLOR_FUNCS = {
    "farmiliar":   recolor_familiar_color,
    "skeleton":    recolor_skeleton_color,
    "zombie":      recolor_zombie_color,
    "elder_wilow": recolor_willow_color,
    "mini_demon":  recolor_mini_demon_color,
    "hyegun":      recolor_hyegun_color,
}


def build_recolored_spr(donor_spr_bytes: bytes, donor_name: str) -> bytes:
    """Recolor palette and any RGBA frames of donor SPR 2.1 archive."""
    fn = RECOLOR_FUNCS[donor_name]
    raw = bytearray(donor_spr_bytes)
    magic, ver, indexed_count, rgba_count = struct.unpack_from('<2sHHH', raw, 0)

    # Recolor RGBA frames if present (e.g. farmiliar preview frames)
    if rgba_count > 0:
        offset = 8
        for _ in range(indexed_count):
            if ver >= 0x201:
                sz = struct.unpack_from('<H', raw, offset + 4)[0]
                offset += 6 + sz
            else:
                w, h = struct.unpack_from('<HH', raw, offset)
                offset += 4 + w * h
        for _ in range(rgba_count):
            w, h = struct.unpack_from('<HH', raw, offset)
            offset += 4
            pixel_bytes = w * h * 4
            for p in range(0, pixel_bytes, 4):
                a, b, g, r = raw[offset + p], raw[offset + p + 1], raw[offset + p + 2], raw[offset + p + 3]
                if a != 0:
                    nr, ng, nb = fn(r, g, b)
                    raw[offset + p + 1] = nb
                    raw[offset + p + 2] = ng
                    raw[offset + p + 3] = nr
            offset += pixel_bytes

    # Recolor 1024-byte palette at end of file
    pal = raw[-1024:]
    new_pal = bytearray(pal)
    for i in range(1, 256):
        r, g, b, a = pal[i * 4], pal[i * 4 + 1], pal[i * 4 + 2], pal[i * 4 + 3]
        if (r, g, b) != (0, 0, 0):
            nr, ng, nb = fn(r, g, b)
            new_pal[i * 4] = nr
            new_pal[i * 4 + 1] = ng
            new_pal[i * 4 + 2] = nb
    raw[-1024:] = new_pal
    return bytes(raw)


def pack_proto_chunk(proto, is_top=False) -> bytes:
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


def patch_jobname_lub() -> bytes:
    """Patch jobname.lub to register JobNameTable[25000..25006]."""
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

    # Insert instructions before SETGLOBAL JobNameTable (index -2)
    for mob_id, _, sprite_basename, _, _ in MONSTERS:
        idx_mob_id = len(p['constants'])
        p['constants'].append(mob_id)
        idx_mob_name = len(p['constants'])
        p['constants'].append(sprite_basename.encode('latin-1'))

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

    patched = raw[:12] + pack_proto_chunk(p, True)
    _ = parse_proto(Reader(patched))
    return patched


def patch_monster_size_effect_new() -> bytes:
    """Patch System/monster_size_effect_new.lub to attach visual effects to 25000..25006."""
    disk_path = CLIENT / "System" / "monster_size_effect_new.lub"
    raw = disk_path.read_bytes()
    p = parse_proto(Reader(raw))

    def encode_abx(op, a, bx):
        return (bx << 14) | (a << 6) | op

    def encode_abc(op, a, b, c):
        return (b << 23) | (c << 14) | (a << 6) | op

    idx_size_key = 2271  # 'MonsterSize'
    idx_eff_key = 2273   # 'MonsterEff'
    idx_1_0 = 6          # 1.0
    idx_effect_global = 0  # 'EFFECT'

    # Map effect name to its constant index in p['constants']
    eff_indices = {}
    for i, c in enumerate(p['constants']):
        if isinstance(c, bytes) and c.startswith(b'EF_'):
            eff_indices[c.decode('latin-1')] = i

    # Right before line 14706 (SETGLOBAL tbl), R(0) is tbl.
    # We insert our entries right before index -4 (before SETGLOBAL tbl, CLOSURE, SETGLOBAL main, RETURN)
    insert_pos = len(p['code']) - 4

    new_insts = []
    for mob_id, eff_list in MONSTER_EFFECTS.items():
        idx_id = len(p['constants'])
        p['constants'].append(float(mob_id))

        # LOADK R(1) mob_id
        new_insts.append(encode_abx(1, 1, idx_id))
        # NEWTABLE R(2) 0 2
        new_insts.append(encode_abc(10, 2, 0, 2))
        # LOADK R(3) 'MonsterSize'
        new_insts.append(encode_abx(1, 3, idx_size_key))
        # LOADK R(4) 1.0
        new_insts.append(encode_abx(1, 4, idx_1_0))
        # SETTABLE R(2) R(3) R(4)
        new_insts.append(encode_abc(9, 2, 3, 4))
        # LOADK R(3) 'MonsterEff'
        new_insts.append(encode_abx(1, 3, idx_eff_key))

        if len(eff_list) == 1:
            eff_name = eff_list[0]
            idx_eff_name = eff_indices[eff_name]
            # GETGLOBAL R(4) EFFECT
            new_insts.append(encode_abx(5, 4, idx_effect_global))
            # LOADK R(5) eff_name
            new_insts.append(encode_abx(1, 5, idx_eff_name))
            # GETTABLE R(4) R(4) R(5)
            new_insts.append(encode_abc(6, 4, 4, 5))
            # SETTABLE R(2) R(3) R(4)
            new_insts.append(encode_abc(9, 2, 3, 4))
        else:
            # Table of effects: NEWTABLE R(4) len 0
            new_insts.append(encode_abc(10, 4, len(eff_list), 0))
            for slot, eff_name in enumerate(eff_list):
                idx_eff_name = eff_indices[eff_name]
                # GETGLOBAL R(5 + slot) EFFECT
                new_insts.append(encode_abx(5, 5 + slot, idx_effect_global))
                # LOADK R(6 + slot) eff_name
                # Note: temporary register
                new_insts.append(encode_abx(1, 8, idx_eff_name))
                # GETTABLE R(5 + slot) R(5 + slot) R(8)
                new_insts.append(encode_abc(6, 5 + slot, 5 + slot, 8))
            # SETLIST R(4) len 1
            new_insts.append(encode_abc(34, 4, len(eff_list), 1))
            # SETTABLE R(2) R(3) R(4)
            new_insts.append(encode_abc(9, 2, 3, 4))

        # SETTABLE R(0) R(1) R(2)
        new_insts.append(encode_abc(9, 0, 1, 2))

    for inst in new_insts:
        p['code'].insert(insert_pos, inst)
        if p['lineinfo']:
            p['lineinfo'].insert(insert_pos, 0)
        insert_pos += 1

    patched = raw[:12] + pack_proto_chunk(p, True)
    _ = parse_proto(Reader(patched))
    return patched


def main():
    print("=== Midnight Monsters Suite Builder (25000–25006) ===")
    UI_SOURCES.mkdir(parents=True, exist_ok=True)
    data_grf = Grf(DATA_GRF)

    monster_assets = {}

    # 1. 25000 Midnight Poring (existing custom sprite)
    poring_spr = PORING_SOURCES / "midnight_poring.spr"
    poring_act = PORING_SOURCES / "midnight_poring.act"
    monster_assets[25000] = (poring_spr.read_bytes(), poring_act.read_bytes())
    print("1. Loaded Midnight Poring custom SPR & ACT (25000)")

    # 2. Recolor 25001..25006
    for mob_id, name, sprite_basename, donor_spr, donor_act in MONSTERS[1:]:
        print(f"   Building {name} ({mob_id}) from donor {donor_spr}...")
        donor_spr_raw = data_grf.read(MONSTER_DIR + donor_spr.encode('cp949') + b".spr")
        donor_act_raw = data_grf.read(MONSTER_DIR + donor_act.encode('cp949') + b".act")

        recolored_spr = build_recolored_spr(donor_spr_raw, donor_spr)
        monster_assets[mob_id] = (recolored_spr, donor_act_raw)

        # Save to ui_sources
        dst_dir = UI_SOURCES / sprite_basename
        dst_dir.mkdir(parents=True, exist_ok=True)
        (dst_dir / f"{sprite_basename}.spr").write_bytes(recolored_spr)
        (dst_dir / f"{sprite_basename}.act").write_bytes(donor_act_raw)
        print(f"      Saved {sprite_basename}.spr ({len(recolored_spr)} bytes)")

    data_grf.close()

    # 3. Patch jobname.lub
    print("2. Patching jobname.lub (IDs 25000..25006)...")
    jobname_bytes = patch_jobname_lub()
    (UI_SOURCES / "jobname.lub").write_bytes(jobname_bytes)
    print("   Patched jobname.lub successfully!")

    # 4. Patch monster_size_effect_new.lub
    print("3. Patching System/monster_size_effect_new.lub (thematic visual particle effects)...")
    eff_bytes = patch_monster_size_effect_new()
    (UI_SOURCES / "monster_size_effect_new.lub").write_bytes(eff_bytes)
    # Write to live client System folder on disk
    (CLIENT / "System" / "monster_size_effect_new.lub").write_bytes(eff_bytes)
    print("   Updated MidnightROClient/System/monster_size_effect_new.lub on disk!")

    # 5. Build midnight.grf
    print("4. Updating MidnightROClient/midnight.grf...")
    current_grf = Grf(TARGET_GRF)
    all_files = {}
    try:
        for entry in current_grf.entries:
            all_files[entry] = current_grf.read(entry)
    finally:
        current_grf.close()

    # Ensure stale jobname_f is purged
    all_files.pop(b"data\\luafiles514\\lua files\\datainfo\\jobname_f.lub", None)
    all_files.pop(b"data\\luafiles514\\lua files\\datainfo\\jobname_f.lua", None)
    all_files.pop(MONSTER_DIR + b"lost_soul.spr", None)
    all_files.pop(MONSTER_DIR + b"lost_soul.act", None)
    all_files.pop(MONSTER_DIR + b"dream_whisper.spr", None)
    all_files.pop(MONSTER_DIR + b"dream_whisper.act", None)

    # Add all 7 monster sprites & acts
    for mob_id, name, sprite_basename, _, _ in MONSTERS:
        spr_bytes, act_bytes = monster_assets[mob_id]
        all_files[MONSTER_DIR + sprite_basename.encode('cp949') + b".spr"] = spr_bytes
        all_files[MONSTER_DIR + sprite_basename.encode('cp949') + b".act"] = act_bytes

    all_files[JOBNAME_KEY] = jobname_bytes
    all_files[MONSTER_SIZE_EFFECT_KEY] = eff_bytes

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"   Built staged GRF: {staged_grf}")

    try:
        staged_grf.replace(TARGET_GRF)
        print("   Successfully updated midnight.grf!")
    except PermissionError:
        print("   WARNING: midnight.grf is locked. Staged at midnight.grf.staged")

    # 6. Update Web Assets
    print("5. Syncing assets to web/public/assets/monsters/...")
    web_base = ROOT / "web" / "public" / "assets" / "monsters"
    for mob_id, _, _, _, _ in MONSTERS:
        spr_bytes, act_bytes = monster_assets[mob_id]
        mob_web_dir = web_base / str(mob_id)
        mob_web_dir.mkdir(parents=True, exist_ok=True)
        (mob_web_dir / "sprite.spr").write_bytes(spr_bytes)
        (mob_web_dir / "action.act").write_bytes(act_bytes)
    print("   Web sprite.spr and action.act updated for all 7 monsters!")


if __name__ == "__main__":
    main()
