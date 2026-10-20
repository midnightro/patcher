#!/usr/bin/env python3
"""Build a local trial for the ten Majestic Goat wing color effects.

Each wing aliases verified stock aura and footprint effects. The black wing
uses its original black aura and purple Nyar footprint; no custom trail assets
are added.

The builder writes an offline work directory only. It does not alter the
Client master, DATA.INI, Patch_Test, or any player data.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
WORKSPACE = TOOLS.parents[2]
sys.path.insert(0, str(TOOLS))

from grf import Grf  # noqa: E402
from lua51_inspect import Reader, parse_proto  # noqa: E402
from make_grf import build  # noqa: E402


MASTER = WORKSPACE / "Client-master-pc"
MIDNIGHT_GRF = MASTER / "midnight.grf"
DATA_GRF = MASTER / "data.grf"
ITEMINFO = MASTER / "SystemEN" / "itemInfo_C.lua"

HAT_IDS = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffectids.lub"
HAT_INFO = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffectinfo.lub"
HAT_EFFECT_F = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lub"
HAT_EFFECT_F_LUA = b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lua"
FOOTPRINT_INFO = b"data\\luafiles514\\lua files\\hateffectinfo\\footprinteffectinfo.lub"
FOOTPRINT_INFO_LUA = b"data\\luafiles514\\lua files\\hateffectinfo\\footprinteffectinfo.lua"
ITEMINFO_MEMBER = b"SystemEN\\itemInfo_C.lua"

OBSOLETE_SHADOW_RIFT_MEMBERS = {
    b"data\\texture\\effect\\midnight_shadow_rift\\shadow_rift_bottom\\midnight_shadow_rift.str",
    b"data\\texture\\effect\\midnight_shadow_rift\\shadow_rift_bottom\\midnight_shadow_rift.bmp",
}

PRIVATE_EFFECT_BASE = 4000

# Aura styles and footprint motifs are intentionally different by color.
# Item IDs are the ten paired wings already registered by the PC Client.
WINGS = [
    ("Red", 480055, "HAT_EF_SUBJECT_AURA_RED", "FOOTPRINT_EF_phoenix"),
    ("Gold", 480058, "HAT_EF_SUBJECT_AURA_GOLD", "FOOTPRINT_EF_butterfly_yellow"),
    ("Black", 480056, "HAT_EF_LEVEL99_BLACK", "FOOTPRINT_EF_nyar_purple"),
    ("Green", 480060, "HAT_EF_LEVEL160_LIME", "FOOTPRINT_EF_divine_blue"),
    ("White", 480057, "HAT_EF_SUBJECT_AURA_WHITE", "FOOTPRINT_EF_divine"),
    ("Graphite", 480070, "HAT_EF_SUBJECT_AURA_NAVY", "FOOTPRINT_EF_bluestar"),
    ("Dawn", 480072, "HAT_EF_LEVEL160_SUN_ORANGE", "FOOTPRINT_EF_yellowstar"),
    ("Amethyst", 480073, "HAT_EF_C_Fluttering_Haze", "FOOTPRINT_EF_purplestar"),
    ("Sapphire", 480074, "HAT_EF_ROS_BlueSpirit", "FOOTPRINT_EF_butterfly_blue"),
    ("Rose", 480078, "HAT_EF_C_Romance_Rose_TW", "FOOTPRINT_EF_butterfly_purple"),
]


OP_MOVE = 0
OP_LOADK = 1
OP_GETGLOBAL = 5
OP_GETTABLE = 6
OP_SETTABLE = 9
OP_NEWTABLE = 10
OP_CALL = 28
OP_RETURN = 30


def encode_abc(op: int, a: int, b: int, c: int) -> int:
    return (op & 0x3F) | ((a & 0xFF) << 6) | ((c & 0x1FF) << 14) | ((b & 0x1FF) << 23)


def encode_abx(op: int, a: int, bx: int) -> int:
    return (op & 0x3F) | ((a & 0xFF) << 6) | ((bx & 0x3FFFF) << 14)


def encode_rk(index: int) -> int:
    if not 0 <= index < 256:
        raise ValueError(f"constant index is outside Lua 5.1 RK range: {index}")
    return 256 + index


def write_string(value: bytes | None) -> bytes:
    if value is None:
        return struct.pack("<I", 0)
    raw = value + b"\x00"
    return struct.pack("<I", len(raw)) + raw


def write_proto(proto: dict) -> bytes:
    result = bytearray()
    result += write_string(proto["source"])
    result += struct.pack(
        "<IIBBBB",
        proto["line_start"], proto["line_end"], proto["nups"],
        proto["params"], proto["vararg"], proto["stack"],
    )
    result += struct.pack("<I", len(proto["code"]))
    for instruction in proto["code"]:
        result += struct.pack("<I", instruction)
    result += struct.pack("<I", len(proto["constants"]))
    for constant in proto["constants"]:
        if constant is None:
            result += b"\x00"
        elif isinstance(constant, bool):
            result += b"\x01" + (b"\x01" if constant else b"\x00")
        elif isinstance(constant, (int, float)):
            result += b"\x03" + struct.pack("<d", float(constant))
        elif isinstance(constant, bytes):
            result += b"\x04" + write_string(constant)
        else:
            raise TypeError(f"unsupported Lua constant: {constant!r}")
    result += struct.pack("<I", len(proto["children"]))
    for child in proto["children"]:
        result += write_proto(child)
    result += struct.pack("<I", len(proto["lineinfo"]))
    for line in proto["lineinfo"]:
        result += struct.pack("<I", line)
    result += struct.pack("<I", len(proto["locals"]))
    for name, start, end in proto["locals"]:
        result += write_string(name)
        result += struct.pack("<II", start, end)
    result += struct.pack("<I", len(proto["upvalues"]))
    for name in proto["upvalues"]:
        result += write_string(name)
    return bytes(result)


def make_alias_chunk(stock: bytes, table_name: bytes, aliases: list[tuple[int, int]], source: bytes) -> bytes:
    constants: list[object] = []

    def add(value):
        for index, present in enumerate(constants):
            if type(present) is type(value) and present == value:
                return index
        constants.append(value)
        return len(constants) - 1

    k_assert = add(b"assert")
    k_loadstring = add(b"loadstring")
    k_stock = add(stock)
    k_stock_name = add(source)
    k_table = add(table_name)
    code = [
        encode_abx(OP_GETGLOBAL, 0, k_assert),
        encode_abx(OP_GETGLOBAL, 1, k_loadstring),
        encode_abx(OP_LOADK, 2, k_stock),
        encode_abx(OP_LOADK, 3, k_stock_name),
        encode_abc(OP_CALL, 1, 3, 0),
        encode_abc(OP_CALL, 0, 0, 2),
        encode_abc(OP_MOVE, 1, 0, 0),
        encode_abc(OP_CALL, 1, 1, 1),
    ]

    for target_id, source_id in aliases:
        k_target = add(float(target_id))
        k_source = add(float(source_id))
        code.extend([
            encode_abx(OP_LOADK, 1, k_target),
            encode_abx(OP_GETGLOBAL, 2, k_table),
            encode_abx(OP_LOADK, 3, k_source),
            encode_abc(OP_GETTABLE, 3, 2, encode_rk(k_source)),
            encode_abc(OP_SETTABLE, 2, encode_rk(k_target), 3),
        ])

    code.append(encode_abc(OP_RETURN, 0, 1, 0))
    proto = {
        "source": source,
        "line_start": 1,
        "line_end": 1,
        "nups": 0,
        "params": 0,
        "vararg": 0,
        "stack": 4,
        "code": code,
        "constants": constants,
        "children": [],
        "lineinfo": [1] * len(code),
        "locals": [],
        "upvalues": [],
    }
    return b"\x1bLua\x51\x00\x01\x04\x04\x04\x08\x00" + write_proto(proto)


def string_number_map(chunk: bytes) -> dict[str, int]:
    constants = parse_proto(Reader(chunk))["constants"]
    result: dict[str, int] = {}
    for index in range(1, len(constants) - 1):
        name, number = constants[index], constants[index + 1]
        if isinstance(name, bytes) and isinstance(number, (int, float)):
            result[name.decode("ascii")] = int(number)
    return result


def unwrap_stock_chunk(chunk: bytes, label: str) -> bytes:
    """Return the original stock chunk embedded by an earlier generated wrapper."""
    proto = parse_proto(Reader(chunk))
    embedded = [
        value for value in proto["constants"]
        if isinstance(value, bytes) and value.startswith(b"\x1bLua")
    ]
    if not embedded:
        return chunk
    if len(embedded) != 1:
        raise RuntimeError(f"expected one embedded stock Lua chunk in {label}, found {len(embedded)}")
    parse_proto(Reader(embedded[0]))
    return embedded[0]


def get_member(archive: Grf, name: bytes) -> bytes:
    if name not in archive.entries:
        raise RuntimeError(f"missing GRF member {name!r} in {archive.path}")
    return archive.read(name)


def str_texture_names(data: bytes) -> list[bytes]:
    if not data.startswith(b"STRM") or len(data) < 44:
        raise RuntimeError("invalid STRM header")
    stored_layer_count = struct.unpack_from("<I", data, 16)[0]
    if stored_layer_count < 1:
        raise RuntimeError("invalid STRM stored layer count")
    # Ragnarok STRM stores one more than the number of serialized layers.
    layer_count = stored_layer_count - 1
    position = 44
    keyframe_size = struct.calcsize("<II2f8f8ffIff4fIII")
    textures: list[bytes] = []
    for _ in range(layer_count):
        if position + 4 > len(data):
            raise RuntimeError("truncated STRM texture count")
        texture_count = struct.unpack_from("<I", data, position)[0]
        position += 4
        for _ in range(texture_count):
            if position + 128 > len(data):
                raise RuntimeError("truncated STRM texture name")
            name = data[position:position + 128].split(b"\x00", 1)[0]
            position += 128
            if name:
                textures.append(name)
        if position + 4 > len(data):
            raise RuntimeError("truncated STRM key count")
        key_count = struct.unpack_from("<I", data, position)[0]
        position += 4 + key_count * keyframe_size
        if position > len(data):
            raise RuntimeError("truncated STRM keyframes")
    if position != len(data):
        raise RuntimeError(f"parsed {position} of {len(data)} STRM bytes")
    return textures


def validate_str_textures(data: Grf, str_path: bytes, str_bytes: bytes) -> None:
    members = {name.lower() for name in data.entries}
    parent = str_path.replace(b"/", b"\\").rsplit(b"\\", 1)[0]
    root = b"data\\texture\\effect\\" + parent + b"\\"
    for texture in str_texture_names(str_bytes):
        full = root + texture.replace(b"/", b"\\")
        if full.lower() not in members:
            raise RuntimeError(f"missing STR texture {full!r} referenced by {str_path!r}")


def iteminfo_with_effects() -> bytes:
    raw = ITEMINFO.read_bytes()
    text = raw.decode("cp874")
    marker = "-- Midnight RO wing color effects (private IDs 4000-4009)"
    newline = "\r\n" if b"\r\n" in raw else "\n"
    rows = []
    for index, (color, item_id, _aura, _foot) in enumerate(WINGS):
        rows.append((item_id, PRIVATE_EFFECT_BASE + index, color))
    pairs = "\n".join(f"\t[{item_id}] = {effect_id}, -- {label}" for item_id, effect_id, label in rows)
    block = f'''-- Midnight RO wing color effects (private IDs 4000-4009)
local midnightWingColorEffectByItem = {{
{pairs}
}}
for itemId, effectId in pairs(midnightWingColorEffectByItem) do
\tlocal item = tbl_custom[itemId] or tbl[itemId]
\tif not item then error("Midnight RO wing effect item is missing: " .. itemId) end
\titem.EffectID = effectId
end
midnightWingColorEffectByItem = nil'''
    rendered = block.replace("\n", newline)
    if marker in text:
        start = text.index(marker)
        end_token = "midnightWingColorEffectByItem = nil"
        end = text.index(end_token, start) + len(end_token)
        text = text[:start] + rendered + text[end:]
    else:
        text = text.rstrip("\r\n") + newline + rendered + newline
    return text.encode("cp874")


def validate_footprint_assets(data: Grf, footprint_chunk: bytes, names: list[str]) -> None:
    constants = parse_proto(Reader(footprint_chunk))["constants"]
    member_names = {name.lower() for name in data.entries}
    prefix = b"data\\texture\\effect\\"
    for effect_name in names:
        key = effect_name.encode("ascii")
        if key not in constants:
            raise RuntimeError(f"footprint definition is missing {effect_name}")
        index = constants.index(key) + 1
        paths = []
        while index < len(constants):
            value = constants[index]
            if isinstance(value, bytes) and value.startswith((b"FOOTPRINT_EF_", b"HAT_EF_")):
                break
            if isinstance(value, bytes) and value.lower().endswith(b".str"):
                paths.append(value.replace(b"/", b"\\"))
            index += 1
        if not paths:
            raise RuntimeError(f"no STR path found for {effect_name}")
        for relative in paths:
            full = (prefix + relative).lower()
            if full not in member_names:
                raise RuntimeError(f"missing stock footprint STR: {full!r}")
            str_path = next(name for name in data.entries if name.lower() == full)
            str_bytes = data.read(str_path)
            validate_str_textures(data, str_path[len(prefix):], str_bytes)


def validate_hat_assets(data: Grf, hat_info_chunk: bytes, names: list[str]) -> None:
    constants = parse_proto(Reader(hat_info_chunk))["constants"]
    members = {name.lower() for name in data.entries}
    prefix = b"data\\texture\\effect\\"
    for effect_name in names:
        key = effect_name.encode("ascii")
        if key not in constants:
            raise RuntimeError(f"HatEffect definition is missing {effect_name}")
        index = constants.index(key) + 1
        paths = []
        while index < len(constants):
            value = constants[index]
            if isinstance(value, bytes) and value.startswith((b"HAT_EF_", b"FOOTPRINT_EF_")):
                break
            if isinstance(value, bytes) and value.lower().endswith(b".str"):
                paths.append(value.replace(b"/", b"\\"))
            index += 1
        for relative in paths:
            full = prefix + relative
            if full.lower() not in members:
                raise RuntimeError(f"missing stock HatEffect STR: {full!r}")
            str_path = next(name for name in data.entries if name.lower() == full.lower())
            validate_str_textures(data, relative, data.read(str_path))


def validate_alias_assignments(
    chunk: bytes, table_name: bytes, aliases: list[tuple[int, int]], label: str
) -> None:
    """Verify the generated Lua bytecode actually assigns every alias."""
    proto = parse_proto(Reader(chunk))
    constants = proto["constants"]
    code = proto["code"]

    def abx(raw: int) -> tuple[int, int, int]:
        return raw & 0x3F, (raw >> 6) & 0xFF, (raw >> 14) & 0x3FFFF

    def abc(raw: int) -> tuple[int, int, int, int]:
        return raw & 0x3F, (raw >> 6) & 0xFF, (raw >> 23) & 0x1FF, (raw >> 14) & 0x1FF

    for target, source in aliases:
        target_indexes = [i for i, value in enumerate(constants) if value == float(target)]
        source_indexes = [i for i, value in enumerate(constants) if value == float(source)]
        table_indexes = [i for i, value in enumerate(constants) if value == table_name]
        found = False
        for index in range(max(0, len(code) - 4)):
            first, second, third, fourth, fifth = code[index:index + 5]
            op, register, constant_index = abx(first)
            if op != OP_LOADK or register != 1 or constant_index not in target_indexes:
                continue
            op, register, constant_index = abx(second)
            if op != OP_GETGLOBAL or register != 2 or constant_index not in table_indexes:
                continue
            op, register, constant_index = abx(third)
            if op != OP_LOADK or register != 3 or constant_index not in source_indexes:
                continue
            op, register, b, c = abc(fourth)
            if op != OP_GETTABLE or register != 3 or b != 2 or c != 256 + constant_index:
                continue
            op, register, b, c = abc(fifth)
            if op == OP_SETTABLE and register == 2 and b == 256 + target_indexes[0] and c == 3:
                found = True
                break
        if not found:
            raise RuntimeError(f"{label} omitted actual table assignment {target} -> {source}")


def build_work(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    iteminfo = iteminfo_with_effects()
    master = Grf(MIDNIGHT_GRF)
    data = Grf(DATA_GRF)
    try:
        hat_ids_chunk = get_member(master, HAT_IDS)
        hat_info_chunk = get_member(master, HAT_INFO)
        hat_effect_chunk = unwrap_stock_chunk(get_member(master, HAT_EFFECT_F), "hateffect_f.lub")
        footprint_chunk = unwrap_stock_chunk(get_member(master, FOOTPRINT_INFO), "footprinteffectinfo.lub")
        ids = string_number_map(hat_ids_chunk)
        hat_constants = parse_proto(Reader(hat_info_chunk))["constants"]
        footprint_constants = parse_proto(Reader(footprint_chunk))["constants"]

        aura_aliases = []
        footprint_aliases = []
        for index, (color, item_id, aura_name, footprint_name) in enumerate(WINGS):
            private_id = PRIVATE_EFFECT_BASE + index
            if private_id in ids.values():
                raise RuntimeError(f"private effect ID collides with HatEFID: {private_id}")
            if aura_name.encode("ascii") not in hat_constants:
                raise RuntimeError(f"aura effect is missing from HatEffectInfo: {aura_name}")
            if aura_name not in ids:
                raise RuntimeError(f"HatEFID lookup is missing a mapping for {color}")
            aura_aliases.append((private_id, ids[aura_name]))
            if footprint_name.encode("ascii") not in footprint_constants:
                raise RuntimeError(f"footprint effect is missing from FootPrintEffectInfo: {footprint_name}")
            if footprint_name not in ids:
                raise RuntimeError(f"HatEFID lookup is missing a footprint mapping for {color}")
            footprint_aliases.append((private_id, ids[footprint_name]))

        validate_footprint_assets(data, footprint_chunk, [entry[3] for entry in WINGS])
        validate_hat_assets(data, hat_info_chunk, [entry[2] for entry in WINGS])
        new_hat_effects = make_alias_chunk(
            hat_effect_chunk, b"hatEffectTable", aura_aliases, b"@WingColorEffects.HatEffect"
        )
        new_footprints = make_alias_chunk(
            footprint_chunk,
            b"FootPrintEffectTable",
            footprint_aliases,
            b"@WingColorEffects.FootPrintEffectInfo",
        )

        # Check generated Lua 5.1 chunks and keep the existing custom HatEffect
        # registrations untouched inside the embedded base chunk.
        validate_alias_assignments(new_hat_effects, b"hatEffectTable", aura_aliases, "HatEffect")
        validate_alias_assignments(
            new_footprints, b"FootPrintEffectTable", footprint_aliases, "FootPrintEffectInfo"
        )
        for label, chunk in (("HatEffect", new_hat_effects), ("FootPrintEffectInfo", new_footprints)):
            if parse_proto(Reader(chunk))["children"]:
                raise RuntimeError(f"{label} wrapper unexpectedly has child prototypes")
        footprint_constants_out = parse_proto(Reader(new_footprints))["constants"]
        if any(
            isinstance(value, bytes) and b"midnight_shadow_rift" in value.lower()
            for value in footprint_constants_out
        ):
            raise RuntimeError("obsolete custom shadow-rift footprint is still registered")

        replacements = {
            HAT_EFFECT_F: new_hat_effects,
            # Keep .lua and .lub byte-identical. The prior text .lua wrapper
            # used loadstring("..."), which is invalid Lua and can prevent the
            # aura table from loading when the client selects the source path.
            HAT_EFFECT_F_LUA: new_hat_effects,
            FOOTPRINT_INFO: new_footprints,
            FOOTPRINT_INFO_LUA: new_footprints,
            ITEMINFO_MEMBER: iteminfo,
        }
        files = [
            (name, replacements.get(name, master.read(name)))
            for name in master.entries
            if name.lower() not in {member.lower() for member in OBSOLETE_SHADOW_RIFT_MEMBERS}
        ]
    finally:
        data.close()
        master.close()

    grf_out = output_dir / "midnight.grf"
    temp_out = output_dir / "midnight.grf.building"
    build(temp_out, files, verbose=False)
    check = Grf(temp_out)
    try:
        if len(check.entries) != len(files):
            raise RuntimeError("member count changed during GRF build")
        for name, expected in files:
            if check.read(name) != expected:
                raise RuntimeError(f"GRF verification mismatch: {name!r}")
    finally:
        check.close()
    temp_out.replace(grf_out)

    iteminfo_out = output_dir / "SystemEN" / "itemInfo_C.lua"
    iteminfo_out.parent.mkdir(parents=True, exist_ok=True)
    iteminfo_out.write_bytes(iteminfo)
    digest_lines = []
    for path in (grf_out, iteminfo_out):
        relative = path.relative_to(output_dir).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        digest_lines.append(f"{digest}  {relative}")
    (output_dir / "SHA256SUMS.prep.txt").write_text("\n".join(digest_lines) + "\n", encoding="ascii")

    print(f"output={output_dir}")
    print(f"members={len(files)}")
    for index, (color, item_id, aura_name, footprint_name) in enumerate(WINGS):
        private_id = PRIVATE_EFFECT_BASE + index
        print(f"{color}: item={item_id} effect={private_id} aura={aura_name} footprint={footprint_name}")
    for line in digest_lines:
        print(line)


def main() -> None:
    default = Path(tempfile.gettempdir()) / "midnightro_wing_effects_20261020"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=default)
    args = parser.parse_args()
    build_work(args.output_dir.resolve())


if __name__ == "__main__":
    main()
