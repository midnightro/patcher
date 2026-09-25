#!/usr/bin/env python3
"""Patch Hunter Rank HatEffects into lua_compat_ui.grf and MidnightROClient/midnight.grf.

HatEffect IDs:
  1:   Auto Hunt Ground Reticle (midnight_auto_hunt.str)
  289: Midnight RO Aura (midnight_ro_aura.str)
  208: Hunter Rank E (midnight_hunter_rank_e.str)
  209: Hunter Rank D (midnight_hunter_rank_d.str)
  210: Hunter Rank C (midnight_hunter_rank_c.str)
  211: Hunter Rank B (midnight_hunter_rank_b.str)
  212: Hunter Rank A (midnight_hunter_rank_a.str)
  213: Hunter Rank S (midnight_hunter_rank_s.str)

Placement: Right of HP/SP bar without overlapping (hatEffectPosX = 6.2, hatEffectPos = -13.0, Static)
"""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
sys.path.insert(0, str(TOOLS))

from grf import Grf
from lua51_inspect import Reader, parse_proto
from make_grf import build

ASSETS = TOOLS / "ui_sources/hunter_rank_badges"
TEXTURE_DIR = ASSETS / "textures"
EFFECT_DIR = ASSETS / "effects"

WINGS_ASSETS = TOOLS / "ui_sources/hunter_rank_wings"
WINGS_TEXTURE_DIR = WINGS_ASSETS / "textures"
WINGS_EFFECT_DIR = WINGS_ASSETS / "effects"

BACKUP_COMPAT = TOOLS / "runtime_grf_sources/lua_compat_ui.grf.before_hunter_badges"
COMPAT_GRF = TOOLS / "runtime_grf_sources/lua_compat_ui.grf"
LOCAL_CLIENT_GRF = ROOT / "MidnightROClient/midnight.grf"

MEMBER_LUB = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lub"
MEMBER_LUA = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lua"
MEMBER_INFO_LUB = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffectinfo.lub"
MEMBER_INFO_LUA = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffectinfo.lua"

TIERS = [
    ("e", 208),
    ("d", 209),
    ("c", 210),
    ("b", 211),
    ("a", 212),
    ("s", 213),
]

WINGS_TIERS = [
    ("b", 214),
    ("a", 215),
    ("s", 216),
]

OP_MOVE = 0
OP_LOADK = 1
OP_GETGLOBAL = 5
OP_SETTABLE = 9
OP_NEWTABLE = 10
OP_CALL = 28
OP_RETURN = 30


def encode_abc(op: int, a: int, b: int, c: int) -> int:
    return (op & 0x3F) | ((a & 0xFF) << 6) | ((c & 0x1FF) << 14) | ((b & 0x1FF) << 23)


def encode_abx(op: int, a: int, bx: int) -> int:
    return (op & 0x3F) | ((a & 0xFF) << 6) | ((bx & 0x3FFFF) << 14)


def encode_rk(idx: int) -> int:
    return 256 + idx


def write_string(s: bytes | None) -> bytes:
    if s is None:
        return struct.pack("<I", 0)
    raw = s + b"\x00"
    return struct.pack("<I", len(raw)) + raw


def write_proto(p: dict) -> bytes:
    out = bytearray()
    out += write_string(p["source"])
    out += struct.pack("<IIBBBB", p["line_start"], p["line_end"], p["nups"], p["params"], p["vararg"], p["stack"])
    out += struct.pack("<I", len(p["code"]))
    for ins in p["code"]:
        out += struct.pack("<I", ins)
    out += struct.pack("<I", len(p["constants"]))
    for c in p["constants"]:
        if c is None:
            out += b"\x00"
        elif isinstance(c, bool):
            out += b"\x01" + (b"\x01" if c else b"\x00")
        elif isinstance(c, (int, float)):
            out += b"\x03" + struct.pack("<d", float(c))
        elif isinstance(c, bytes):
            out += b"\x04" + write_string(c)
        else:
            raise ValueError(f"Unknown constant: {c}")
    out += struct.pack("<I", len(p["children"]))
    for ch in p["children"]:
        out += write_proto(ch)
    out += struct.pack("<I", len(p["lineinfo"]))
    for line in p["lineinfo"]:
        out += struct.pack("<I", line)
    out += struct.pack("<I", len(p["locals"]))
    for name, s, e in p["locals"]:
        out += write_string(name)
        out += struct.pack("<II", s, e)
    out += struct.pack("<I", len(p["upvalues"]))
    for up in p["upvalues"]:
        out += write_string(up)
    return bytes(out)


def build_hateffect_chunk(stock_chunk: bytes, effects: list[dict]) -> bytes:
    constants = []

    def add_const(val):
        for i, c in enumerate(constants):
            if type(c) == type(val) and c == val:
                return i
        constants.append(val)
        return len(constants) - 1

    k_assert = add_const(b"assert")
    k_loadstring = add_const(b"loadstring")
    k_stock_chunk = add_const(stock_chunk)
    k_stock_name = add_const(b"@HatEffect_F.stock")
    k_tbl_name = add_const(b"hatEffectTable")

    k_res = add_const(b"resourceFileName")
    k_eid = add_const(b"hatEffectID")
    k_pos = add_const(b"hatEffectPos")
    k_posx = add_const(b"hatEffectPosX")
    k_render_before = add_const(b"isRenderBeforeCharacter")
    k_ignore_riding = add_const(b"isIgnoreRiding")
    k_adj_pos = add_const(b"isAdjustPositionWhenShrinkState")
    k_adj_sz = add_const(b"isAdjustSizeWhenShrinkState")
    k_attached = add_const(b"isAttachedHead")
    k_pair = add_const(b"isEffectPair")

    k_neg1 = add_const(-1.0)
    k_false = add_const(False)
    k_true = add_const(True)

    code = [
        encode_abx(OP_GETGLOBAL, 0, k_assert),
        encode_abx(OP_GETGLOBAL, 1, k_loadstring),
        encode_abx(OP_LOADK, 2, k_stock_chunk),
        encode_abx(OP_LOADK, 3, k_stock_name),
        encode_abc(OP_CALL, 1, 3, 0),
        encode_abc(OP_CALL, 0, 0, 2),
        encode_abc(OP_MOVE, 1, 0, 0),
        encode_abc(OP_CALL, 1, 1, 1),
    ]

    for eff in effects:
        k_id = add_const(float(eff["id"]))
        k_res_val = add_const(eff["res"].encode("latin-1"))
        k_pos_val = add_const(float(eff.get("pos_y", -6.0)))
        k_posx_val = add_const(float(eff.get("pos_x", 35.0)))
        k_bef_val = k_true if eff.get("render_before", False) else k_false
        k_att_val = k_true if eff.get("attached_head", True) else k_false

        code.extend([
            encode_abx(OP_LOADK, 1, k_id),
            encode_abx(OP_GETGLOBAL, 2, k_tbl_name),
            encode_abc(OP_NEWTABLE, 3, 0, 10),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_res), encode_rk(k_res_val)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_eid), encode_rk(k_neg1)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_pos), encode_rk(k_pos_val)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_posx), encode_rk(k_posx_val)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_render_before), encode_rk(k_bef_val)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_ignore_riding), encode_rk(k_true)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_adj_pos), encode_rk(k_true)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_adj_sz), encode_rk(k_true)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_attached), encode_rk(k_att_val)),
            encode_abc(OP_SETTABLE, 3, encode_rk(k_pair), encode_rk(k_false)),
            encode_abc(OP_SETTABLE, 2, 1, 3),
        ])

    code.append(encode_abc(OP_RETURN, 0, 1, 0))

    proto = {
        "source": b"@HatEffect_F.midnight",
        "line_start": 1,
        "line_end": 1,
        "nups": 0,
        "params": 0,
        "vararg": 0,
        "stack": 10,
        "code": code,
        "constants": constants,
        "children": [],
        "lineinfo": [1] * len(code),
        "locals": [],
        "upvalues": [],
    }

    return b"\x1bLua\x51\x00\x01\x04\x04\x04\x08\x00" + write_proto(proto)


def generate_clean_lua_source(effects: list[dict]) -> str:
    lines = [
        'local stock = assert(loadstring("...", "@HatEffect_F.stock"))',
        "stock()",
        "",
        "-- Registered Custom HatEffects for Midnight RO",
    ]
    for eff in effects:
        res = eff["res"].replace("\\", "\\\\")
        lines.append(f"""hatEffectTable[{eff['id']}] = {{
    resourceFileName = "{res}",
    hatEffectID = -1,
    hatEffectPos = {eff.get('pos_y', -6.0)},
    hatEffectPosX = {eff.get('pos_x', 0.0)},
    isRenderBeforeCharacter = {'true' if eff.get('render_before', False) else 'false'},
    isIgnoreRiding = true,
    isAdjustPositionWhenShrinkState = true,
    isAdjustSizeWhenShrinkState = true,
    isAttachedHead = {'true' if eff.get('attached_head', True) else 'false'},
    isEffectPair = false
}}""")
    return "\n\n".join(lines)


def patch_hateffectinfo_chunk(raw_info: bytes, pos_y: float = -13.0, pos_x: float = 6.2) -> bytes:
    p = parse_proto(Reader(raw_info))
    constants = list(p["constants"])
    code = list(p["code"])

    def add_const(val):
        for i, c in enumerate(constants):
            if type(c) == type(val) and c == val:
                return i
        constants.append(val)
        return len(constants) - 1

    k_posx = add_const(pos_x)
    k_posy = add_const(pos_y)

    barrier_tiers = [
        ("e", 437),
        ("d", 439),
        ("c", 441),
        ("b", 443),
        ("a", 445),
        ("s", 447),
    ]

    for tier, str_const_idx in barrier_tiers:
        new_str = f"midnight_hunter_rank\\midnight_hunter_rank_{tier}.str".encode("latin-1")
        constants[str_const_idx] = new_str

        # find where str_const_idx is loaded
        inst_idx = None
        for i, ins in enumerate(code):
            if (ins & 0x3F) == 1 and ((ins >> 14) & 0x3FFFF) == str_const_idx:
                inst_idx = i
                break
        if inst_idx is not None:
            # inst_idx + 2 is hatEffectPos: change to pos_y
            code[inst_idx + 2] = encode_abx(1, 3, k_posy)
            # inst_idx + 4 is hatEffectPosX: change to pos_x
            code[inst_idx + 4] = encode_abx(1, 3, k_posx)

    p["constants"] = constants
    p["code"] = code
    return b"\x1bLuaQ\x00\x01\x04\x04\x04\x08\x00" + write_proto(p)


def update_grf(grf_path: Path, new_members: dict[bytes, bytes]) -> None:
    if not grf_path.is_file():
        print(f"Skipping non-existent GRF: {grf_path}")
        return

    print(f"Updating GRF: {grf_path.name}")
    src = Grf(str(grf_path))
    files = []
    try:
        for name in src.entries:
            if name in new_members:
                files.append((name, new_members[name]))
            else:
                files.append((name, src.read(name)))
    finally:
        src.close()

    existing_keys = {f[0] for f in files}
    for name, payload in new_members.items():
        if name not in existing_keys:
            files.append((name, payload))

    temp_path = grf_path.with_suffix(grf_path.suffix + ".tmp")
    build(temp_path, files, verbose=False)
    try:
        temp_path.replace(grf_path)
        print(f"  Successfully updated {grf_path.name} ({len(files)} entries)")
    except PermissionError:
        if temp_path.is_file():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise PermissionError(
            f"Cannot write to '{grf_path.name}' because it is currently locked by a running process "
            f"(e.g. MidnightRO-Ragexe.exe). Please exit the game client and rerun the patch."
        )


def main() -> int:
    print("Preparing clean, single-pass HatEffect patch...")

    # Load clean stock chunk from backup
    if BACKUP_COMPAT.is_file():
        clean_source = BACKUP_COMPAT
    else:
        clean_source = COMPAT_GRF

    gc = Grf(str(clean_source))
    try:
        raw_lub = gc.read(MEMBER_LUB)
        raw_info = gc.read(MEMBER_INFO_LUB)
    finally:
        gc.close()

    p = parse_proto(Reader(raw_lub))
    # Extract embedded stock chunk (found in constants)
    stock_chunk = None
    for c in p["constants"]:
        if isinstance(c, bytes) and c.startswith(b"\x1bLua"):
            # If inner also has embedded, find innermost
            inner = parse_proto(Reader(c))
            for ic in inner["constants"]:
                if isinstance(ic, bytes) and ic.startswith(b"\x1bLua"):
                    stock_chunk = ic
                    break
            if stock_chunk is None:
                stock_chunk = c
            break

    if stock_chunk is None:
        raise RuntimeError("Cannot find stock Lua chunk in hateffect_f.lub")

    print(f"Found stock chunk ({len(stock_chunk)} bytes).")

    # Define all custom effects for Midnight RO in one single table
    all_effects = [
        {"id": 1, "res": "midnight_auto_hunt\\midnight_auto_hunt.str", "pos_y": -11.0, "pos_x": 0.0, "render_before": True},
        {"id": 289, "res": "midnight_ro_aura\\midnight_ro_aura.str", "pos_y": -6.0, "pos_x": 0.0},
        {"id": 208, "res": "midnight_hunter_rank\\midnight_hunter_rank_e.str", "pos_y": -13.0, "pos_x": 6.2},
        {"id": 209, "res": "midnight_hunter_rank\\midnight_hunter_rank_d.str", "pos_y": -13.0, "pos_x": 6.2},
        {"id": 210, "res": "midnight_hunter_rank\\midnight_hunter_rank_c.str", "pos_y": -13.0, "pos_x": 6.2},
        {"id": 211, "res": "midnight_hunter_rank\\midnight_hunter_rank_b.str", "pos_y": -13.0, "pos_x": 6.2},
        {"id": 212, "res": "midnight_hunter_rank\\midnight_hunter_rank_a.str", "pos_y": -13.0, "pos_x": 6.2},
        {"id": 213, "res": "midnight_hunter_rank\\midnight_hunter_rank_s.str", "pos_y": -13.0, "pos_x": 6.2},
        # Hunter Rank Wings (Rank B, A, S):
        {"id": 214, "res": "midnight_hunter_wings\\midnight_hunter_wings_b.str", "pos_y": -7.0, "pos_x": 0.0, "render_before": True, "attached_head": False},
        {"id": 215, "res": "midnight_hunter_wings\\midnight_hunter_wings_a.str", "pos_y": -7.0, "pos_x": 0.0, "render_before": True, "attached_head": False},
        {"id": 216, "res": "midnight_hunter_wings\\midnight_hunter_wings_s.str", "pos_y": -7.0, "pos_x": 0.0, "render_before": True, "attached_head": False},
        # Solo Leveling Monarch's Shadow Aura (360-degree True Surrounding Aura: Back + Front Layers):
        {"id": 217, "res": "midnight_monarch_shadow\\midnight_monarch_shadow_back.str", "pos_y": -6.5, "pos_x": 0.0, "render_before": True, "attached_head": False},
        {"id": 218, "res": "midnight_monarch_shadow\\midnight_monarch_shadow_front.str", "pos_y": -6.5, "pos_x": 0.0, "render_before": False, "attached_head": False},
    ]

    single_pass_lub = build_hateffect_chunk(stock_chunk, all_effects)
    single_pass_lua = generate_clean_lua_source(all_effects).encode("latin-1")
    print(f"Built single-pass hateffect_f.lub ({len(single_pass_lub)} bytes).")

    # Verify that the generated bytecode parses cleanly
    parse_proto(Reader(single_pass_lub))
    print("Bytecode verification: PASSED (zero nesting, single clean chunk).")

    patched_info_lub = patch_hateffectinfo_chunk(raw_info)
    parse_proto(Reader(patched_info_lub))
    print("hateffectinfo bytecode verification: PASSED.")

    new_members: dict[bytes, bytes] = {
        MEMBER_LUB: single_pass_lub,
        MEMBER_LUA: single_pass_lua,
        MEMBER_INFO_LUB: patched_info_lub,
        MEMBER_INFO_LUA: patched_info_lub,
    }

    for tier, _ in TIERS:
        tga_file = TEXTURE_DIR / f"hunter_rank_{tier}.tga"
        str_file = EFFECT_DIR / f"midnight_hunter_rank_{tier}.str"

        if not tga_file.is_file() or not str_file.is_file():
            print(f"Error: Missing asset for tier {tier.upper()}!")
            return 1

        tga_bytes = tga_file.read_bytes()
        str_bytes = str_file.read_bytes()

        tga_entry = f"data\\texture\\effect\\midnight_hunter_rank\\hunter_rank_{tier}.tga".encode("latin-1")
        tga_fallback = f"data\\texture\\effect\\hunter_rank_{tier}.tga".encode("latin-1")
        str_entry = f"data\\texture\\effect\\midnight_hunter_rank\\midnight_hunter_rank_{tier}.str".encode("latin-1")

        new_members[tga_entry] = tga_bytes
        new_members[tga_fallback] = tga_bytes
        new_members[str_entry] = str_bytes

    for tier, _ in WINGS_TIERS:
        tga_file = WINGS_TEXTURE_DIR / f"hunter_wings_{tier}.tga"
        str_file = WINGS_EFFECT_DIR / f"midnight_hunter_wings_{tier}.str"

        if not tga_file.is_file() or not str_file.is_file():
            print(f"Error: Missing wings asset for tier {tier.upper()}!")
            return 1

        tga_bytes = tga_file.read_bytes()
        str_bytes = str_file.read_bytes()

        tga_entry = f"data\\texture\\effect\\midnight_hunter_wings\\hunter_wings_{tier}.tga".encode("latin-1")
        tga_fallback = f"data\\texture\\effect\\hunter_wings_{tier}.tga".encode("latin-1")
        str_entry = f"data\\texture\\effect\\midnight_hunter_wings\\midnight_hunter_wings_{tier}.str".encode("latin-1")

        new_members[tga_entry] = tga_bytes
        new_members[tga_fallback] = tga_bytes
        new_members[str_entry] = str_bytes

    # Solo Leveling Monarch's Shadow Aura assets (360-degree True Surrounding Aura)
    shadow_sources = TOOLS / "ui_sources/solo_leveling_hunter_set"
    for str_f in shadow_sources.glob("midnight_monarch_*.str"):
        s_bytes = str_f.read_bytes()
        new_members[f"data\\texture\\effect\\midnight_monarch_shadow\\{str_f.name}".encode("latin-1")] = s_bytes
        new_members[f"data\\texture\\effect\\{str_f.name}".encode("latin-1")] = s_bytes

    for tga_f in shadow_sources.glob("midnight_monarch_*.tga"):
        t_bytes = tga_f.read_bytes()
        new_members[f"data\\texture\\effect\\midnight_monarch_shadow\\{tga_f.name}".encode("latin-1")] = t_bytes
        new_members[f"data\\texture\\effect\\{tga_f.name}".encode("latin-1")] = t_bytes

    # 1. Update runtime_grf_sources/lua_compat_ui.grf
    update_grf(COMPAT_GRF, new_members)

    # 2. Update local workspace testing client ONLY (E:\.midnight-ro\MidnightROClient\midnight.grf)
    # Strictly respect user rule: DO NOT touch E:\MidnightROClient
    if LOCAL_CLIENT_GRF.is_file():
        update_grf(LOCAL_CLIENT_GRF, new_members)

    print("\nHunter Rank HatEffects cleanly deployed to client!")
    return 0



if __name__ == "__main__":
    sys.exit(main())
