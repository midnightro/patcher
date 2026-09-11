#!/usr/bin/env python3
"""Apply Option 8 Tactical Ground Reticle to lua_compat_ui.grf and midnight.grf."""

from __future__ import annotations

import os
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from grf import Grf
from lua51_inspect import Reader, parse_proto
from make_grf import build

ASSETS = TOOLS / "ui_sources/auto_hunt_overhead"
TGA_FILE = ASSETS / "midnight_auto_hunt.tga"
STR_FILE = ASSETS / "midnight_auto_hunt.str"

MEMBER_STR = b"data\\texture\\effect\\midnight_auto_hunt\\midnight_auto_hunt.str"
MEMBER_TGA = b"data\\texture\\effect\\midnight_auto_hunt\\midnight_auto_hunt.tga"
MEMBER_LUB = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lub"
MEMBER_LUA = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lua"


def patch_hateffect_bytecode(original_lub: bytes) -> bytes:
    raw = bytearray(original_lub)
    p = parse_proto(Reader(bytes(raw)))

    code = p["code"]
    code0_bytes = struct.pack("<I", code[0])
    code_offset = raw.find(code0_bytes)
    if code_offset == -1:
        raise RuntimeError("cannot find code offset in hateffect_f.lub")

    def encode_inst(op: int, a: int, b: int, c: int) -> int:
        return (b << 23) | (c << 14) | (a << 6) | op

    def decode_inst(val: int) -> tuple[int, int, int, int]:
        op = val & 0x3F
        a = (val >> 6) & 0xFF
        c = (val >> 14) & 0x1FF
        b = (val >> 23) & 0x1FF
        return op, a, b, c

    # 1. Update inst 15: SETTABLE A=3, B=256+14 (isRenderBeforeCharacter), C=256+17 (K[17]=True)
    op, a, b, c = decode_inst(code[15])
    new_inst15 = encode_inst(op, a, b, 256 + 17)
    raw[code_offset + 15 * 4 : code_offset + 16 * 4] = struct.pack("<I", new_inst15)

    # 2. Update inst 19: SETTABLE A=3, B=256+20 (isAttachedHead), C=256+15 (K[15]=False)
    op, a, b, c = decode_inst(code[19])
    new_inst19 = encode_inst(op, a, b, 256 + 15)
    raw[code_offset + 19 * 4 : code_offset + 20 * 4] = struct.pack("<I", new_inst19)

    # 3. Update inst 42: LOADBOOL A=5, bool=1, c=0 (IsRenderBeforeCharacter -> true)
    new_inst42 = encode_inst(2, 5, 1, 0)
    raw[code_offset + 42 * 4 : code_offset + 43 * 4] = struct.pack("<I", new_inst42)

    # 4. Update inst 58: LOADBOOL A=5, bool=0, c=0 (IsAttachedToHead -> false)
    new_inst58 = encode_inst(2, 5, 0, 0)
    raw[code_offset + 58 * 4 : code_offset + 59 * 4] = struct.pack("<I", new_inst58)

    # 5. Update inst 62: LOADBOOL A=5, bool=0, c=0 (IsIgnoredRidingState_Include_AttachedToHead -> false)
    new_inst62 = encode_inst(2, 5, 0, 0)
    raw[code_offset + 62 * 4 : code_offset + 63 * 4] = struct.pack("<I", new_inst62)

    # 6. Change K[11] -6.0 to -11.0:
    minus_6 = struct.pack("<d", -6.0)
    minus_11 = struct.pack("<d", -11.0)
    idx = raw.find(minus_6)
    if idx != -1:
        raw[idx : idx + 8] = minus_11
    elif minus_11 not in raw:
        raise RuntimeError("cannot find -6.0 or -11.0 constant in hateffect_f.lub")

    # Verify that the modified bytecode parses without errors
    p2 = parse_proto(Reader(bytes(raw)))
    return bytes(raw)


def patch_hateffect_lua(original_lua: bytes) -> bytes:
    text = original_lua.decode("latin-1")
    text = text.replace("hatEffectPos = -6", "hatEffectPos = -11")
    text = text.replace("isRenderBeforeCharacter = false", "isRenderBeforeCharacter = true")
    text = text.replace("isAttachedHead = true", "isAttachedHead = false")
    text = text.replace('wrap_value("GetHatEfPos", -6)', 'wrap_value("GetHatEfPos", -11)')
    text = text.replace('wrap_value("IsRenderBeforeCharacter", false)', 'wrap_value("IsRenderBeforeCharacter", true)')
    text = text.replace('wrap_value("IsAttachedToHead", true)', 'wrap_value("IsAttachedToHead", false)')
    text = text.replace('wrap_value("IsIgnoredRidingState_Include_AttachedToHead", true)', 'wrap_value("IsIgnoredRidingState_Include_AttachedToHead", false)')
    return text.encode("latin-1")


def update_grf(grf_path: Path, new_members: dict[bytes, bytes]) -> None:
    if not grf_path.is_file():
        print(f"Skipping non-existent GRF: {grf_path}")
        return

    print(f"Updating GRF: {grf_path}")
    backup = grf_path.with_suffix(grf_path.suffix + ".before_reticle_option8")
    if not backup.exists():
        shutil.copy2(grf_path, backup)

    src = Grf(str(grf_path))
    files = []
    try:
        for name in src.entries:
            if name in new_members:
                files.append((name, new_members[name]))
                print(f"  replaced {name.decode('latin-1', errors='replace')} ({len(new_members[name])} bytes)")
            else:
                files.append((name, src.read(name)))
    finally:
        src.close()

    # If any member in new_members was not in the archive and is required:
    existing_keys = {f[0] for f in files}
    for name, payload in new_members.items():
        if name not in existing_keys:
            files.append((name, payload))
            print(f"  added {name.decode('latin-1', errors='replace')} ({len(payload)} bytes)")

    temp_path = grf_path.with_suffix(grf_path.suffix + ".tmp")
    build(temp_path, files, verbose=False)
    try:
        temp_path.replace(grf_path)
        print(f"  Successfully updated {grf_path} ({len(files)} entries)")
    except PermissionError:
        print(f"  WARNING: {grf_path} is currently locked by a running client (e.g. MidnightRO-Ragexe).")
        print(f"  Saved as {temp_path}. Once the client is closed, it will replace {grf_path.name}.")


def main() -> None:
    tga_data = TGA_FILE.read_bytes()
    str_data = STR_FILE.read_bytes()

    # Get stock hateffect_f.lub and .lua from lua_compat_ui.grf
    compat_grf_path = TOOLS / "runtime_grf_sources/lua_compat_ui.grf"
    cg = Grf(str(compat_grf_path))
    try:
        orig_lub = cg.read(MEMBER_LUB)
        orig_lua = cg.read(MEMBER_LUA)
    finally:
        cg.close()

    patched_lub = patch_hateffect_bytecode(orig_lub)
    patched_lua = patch_hateffect_lua(orig_lua)

    members_full = {
        MEMBER_STR: str_data,
        MEMBER_TGA: tga_data,
        MEMBER_LUB: patched_lub,
        MEMBER_LUA: patched_lua,
    }

    members_assets_only = {
        MEMBER_STR: str_data,
        MEMBER_TGA: tga_data,
    }

    # 1. Update runtime_grf_sources/lua_compat_ui.grf
    update_grf(compat_grf_path, members_full)

    # 2. Update local client GRF for testing
    targets = [
        ROOT / "MidnightROClient/midnight.grf",
    ]

    for target in targets:
        if target.is_file():
            tg = Grf(str(target))
            has_lub = MEMBER_LUB in tg.entries
            tg.close()
            if has_lub:
                update_grf(target, members_full)
            else:
                update_grf(target, members_assets_only)

    print("\nPatch process finished.")


if __name__ == "__main__":
    main()

