#!/usr/bin/env python3
"""Build shaded Majestic Goat costume colorways from the master item.

The source item's horn palette is remapped; its gold center ornament, outlines,
shape, ACT animation, and item stats are preserved. By default, generated
Client files are staged as a copyable Patch_Test candidate. Pass --apply-master
to also update Client master after checking that the game and launcher are
closed. Add --master-only to skip candidate staging until preliminary live tests
are complete.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
sys.path.insert(0, str(TOOLS))
from grf import Grf  # noqa: E402
from lua51_inspect import Reader, parse_proto  # noqa: E402
from make_grf import build as build_grf  # noqa: E402

CLIENT = ROOT / "Client-master-pc"
DATA_GRF = CLIENT / "data.grf"
MASTER_GRF = CLIENT / "midnight.grf"
ITEMINFO = CLIENT / "SystemEN" / "itemInfo_C.lua"
BASELINE_ITEMINFO = CLIENT / "SystemEN" / "itemInfo_ProjectRO_Costume.lua"
BASELINE_BUILDER = ROOT / "server" / "tools" / "client-patch" / "build_costume_baseline_tooltip.py"
ITEM_DB = ROOT / "server" / "db" / "import" / "item_db.yml"
PATCH = ROOT / "Patch_Test" / "majestic_goat_colorways"
SOURCE = TOOLS / "ui_sources" / "majestic_goat_colorways"
BUILD = ROOT / "tmp" / "majestic_goat_colorways"

BASE_ID = 19549
FIRST_ID = 902275
FIRST_VIEW = 2854
SPRITE_ROOT = b"data\\sprite\\"
LUA_ROOT = b"data\\luafiles514\\lua files\\datainfo\\"
UI_ROOT = b"data\\texture\\" + bytes.fromhex("c0afc0fac0cec5cdc6e4c0ccbdba") + b"\\"
ACCESSORY = bytes.fromhex("bec7bcbcbbe7b8ae")  # 악세사리 (CP949)
MALE = bytes.fromhex("b3b2")                 # 남
FEMALE = bytes.fromhex("bfa9")               # 여
ITEM = bytes.fromhex("bec6c0ccc5db")          # 아이템
MASTER_STEM = bytes.fromhex("b8b6c1a6bdbac6bdb0edbfecc6ae")  # 마제스틱고우트
DAWN_ICON_STEM = bytes.fromhex("b4ebc7fcb8b6c1a6bdbac6bdb0edbfecc6ae32")  # ID 400124 icon
HORN_RAMP = (112, 113, 114, 115, 116, 117, 118, 119)
COLORWAYS = (
    {
        "id": 902275, "view": 2854, "aegis": "C_Majestic_Goat_Sapphire",
        "name": "Costume Majestic Goat (Sapphire)", "resource": "maj_goat_sapphire",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_SAPPHIRE", "label": "Sapphire",
        "ramp": ((118,194,255),(92,162,245),(74,137,222),(58,113,197),(43,89,165),(31,67,133),(23,47,96),(15,29,61)),
    },
    {
        "id": 902276, "view": 2855, "aegis": "C_Majestic_Goat_Emerald",
        "name": "Costume Majestic Goat (Emerald)", "resource": "maj_goat_emerald",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_EMERALD", "label": "Emerald",
        "ramp": ((136,226,173),(102,200,145),(76,174,122),(56,148,100),(41,121,81),(30,93,62),(22,67,44),(14,43,29)),
    },
    {
        "id": 902277, "view": 2856, "aegis": "C_Majestic_Goat_Ruby",
        "name": "Costume Majestic Goat (Ruby)", "resource": "maj_goat_ruby",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_RUBY", "label": "Ruby",
        "ramp": ((255,156,170),(235,110,135),(209,77,106),(183,54,82),(154,37,63),(122,26,49),(87,17,35),(52,9,21)),
    },
    {
        "id": 902278, "view": 2857, "aegis": "C_Majestic_Goat_Pearl",
        "name": "Costume Majestic Goat (Pearl)", "resource": "maj_goat_pearl",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_PEARL", "label": "Warm Ivory test",
        "ramp": ((255,252,247),(245,241,235),(226,220,211),(201,193,181),(170,160,147),(136,126,115),(100,91,83),(63,56,51)),
    },
    {
        "id": 902279, "view": 2858, "aegis": "C_Majestic_Goat_Amethyst",
        "name": "Costume Majestic Goat (Amethyst)", "resource": "maj_goat_amethyst",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_AMETHYST", "label": "Amethyst",
        "ramp": ((229,183,255),(199,141,245),(170,106,226),(143,79,204),(116,57,177),(88,40,143),(62,26,104),(37,14,68)),
    },
    {
        "id": 902280, "view": 2859, "aegis": "C_Majestic_Goat_Rose",
        "name": "Costume Majestic Goat (Rose)", "resource": "maj_goat_rose",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_ROSE", "label": "Rose",
        "ramp": ((255,195,228),(246,151,204),(222,116,179),(197,85,152),(166,61,127),(132,40,99),(96,25,70),(58,14,43)),
    },
    {
        "id": 902281, "view": 2860, "aegis": "C_Majestic_Goat_Graphite",
        "name": "Costume Majestic Goat (Graphite Gray)", "resource": "maj_goat_graphite",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_GRAPHITE", "label": "Graphite Gray",
        "ramp": ((228,231,237),(199,203,211),(170,175,185),(141,147,159),(112,119,132),(83,91,105),(57,64,78),(32,37,49)),
    },
    {
        "id": 902282, "view": 2861, "aegis": "C_Majestic_Goat_Onyx",
        "name": "Costume Majestic Goat (Onyx Black)", "resource": "maj_goat_onyx",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_ONYX", "label": "Onyx Black",
        "ramp": ((157,164,177),(120,127,141),(87,94,108),(62,69,82),(43,49,62),(29,34,45),(18,22,32),(8,11,19)),
    },
    {
        "id": 902283, "view": 2862, "aegis": "C_Majestic_Goat_Fallen_Shade",
        "name": "Costume Majestic Goat (Fallen Shade)", "resource": "maj_goat_fallen_shade",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_FALLEN_SHADE", "label": "Fallen Shade",
        "ramp": ((157,151,166),(128,122,139),(101,95,112),(76,70,87),(55,49,66),(37,32,49),(24,19,35),(13,9,22)),
    },
    {
        "id": 902284, "view": 2863, "aegis": "C_Majestic_Goat_Fallen_Dusk",
        "name": "Costume Majestic Goat (Fallen Dusk)", "resource": "maj_goat_fallen_dusk",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_FALLEN_DUSK", "label": "Fallen Dusk",
        "ramp": ((170,157,180),(139,126,151),(109,97,122),(83,72,99),(61,51,76),(43,35,57),(28,22,40),(16,11,25)),
    },
    {
        "id": 902285, "view": 2864, "aegis": "C_Majestic_Goat_Feather_White",
        "name": "Costume Majestic Goat (Feather White)", "resource": "maj_goat_feather_white",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_FEATHER_WHITE", "label": "Feather White",
        "ramp": ((255,255,255),(245,245,244),(224,224,222),(198,198,195),(168,168,164),(133,133,128),(96,96,92),(60,60,57)),
    },
    {
        "id": 902286, "view": 2865, "aegis": "C_Majestic_Goat_Silver_Smoke",
        "name": "Costume Majestic Goat (Silver Smoke)", "resource": "maj_goat_silver_smoke",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_SILVER_SMOKE", "label": "Silver Smoke",
        "ramp": ((248,248,248),(230,230,230),(208,208,208),(184,184,184),(156,156,156),(124,124,124),(88,88,88),(52,52,52)),
    },
    {
        "id": 902287, "view": 2866, "aegis": "C_Majestic_Goat_Rose_Silver",
        "name": "Costume Majestic Goat (Rose Silver)", "resource": "maj_goat_rose_silver",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_ROSE_SILVER", "label": "Rose Silver",
        "ramp": ((255,249,251),(247,234,239),(232,213,223),(209,188,203),(181,158,177),(148,125,146),(110,88,109),(70,52,72)),
    },
    {
        "id": 902288, "view": 2867, "aegis": "C_Majestic_Goat_Archangel_Match",
        "name": "Costume Majestic Goat (Archangel Match)", "resource": "maj_goat_archangel_match",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_ARCHANGEL_MATCH", "label": "Archangel Match",
        # Sampled from the white-to-shadow colors in the official Archangel Wings (2573) icon.
        "ramp": ((255,255,255),(255,243,235),(238,223,215),(220,203,195),(185,163,155),(153,123,123),(131,94,95),(84,54,64)),
    },
    {
        "id": 902289, "view": 2868, "aegis": "C_Majestic_Goat_Warm_Feather",
        "name": "Costume Majestic Goat (Warm Feather)", "resource": "maj_goat_warm_feather",
        "accessory": "ACCESSORY_MAJESTIC_GOAT_WARM_FEATHER", "label": "Warm Feather",
        "ramp": ((255,255,255),(255,248,244),(244,236,231),(228,217,210),(207,192,185),(181,161,155),(149,127,125),(111,92,96)),
    },
)


def src_paths() -> dict[str, bytes]:
    base = SPRITE_ROOT
    male_path = base + ACCESSORY + b"\\" + MALE + b"\\" + MALE + b"_" + MASTER_STEM
    female_path = base + ACCESSORY + b"\\" + FEMALE + b"\\" + FEMALE + b"_" + MASTER_STEM
    drop_path = base + ITEM + b"\\" + MASTER_STEM
    texture = UI_ROOT
    return {
        "male_spr": male_path + b".spr", "male_act": male_path + b".act",
        "female_spr": female_path + b".spr", "female_act": female_path + b".act",
        "drop_spr": drop_path + b".spr", "drop_act": drop_path + b".act",
        # Use the official front-facing inventory icon and detailed collection
        # artwork from costume item 400124, keeping both views visually matched.
        "icon": texture + b"item\\" + DAWN_ICON_STEM + b".bmp",
        "collection": texture + b"collection\\" + DAWN_ICON_STEM + b".bmp",
    }


def get_sources() -> dict[str, bytes]:
    if not DATA_GRF.exists() or not MASTER_GRF.exists():
        raise FileNotFoundError("Client master must contain data.grf and midnight.grf")
    archive = Grf(str(DATA_GRF))
    try:
        result = {key: archive.read(path) for key, path in src_paths().items()}
    finally:
        archive.close()
    SOURCE.mkdir(parents=True, exist_ok=True)
    for key, payload in result.items():
        (SOURCE / f"master_{key}{'.bmp' if key in ('icon','collection') else '.spr' if key.endswith('_spr') else '.act'}").write_bytes(payload)
    archive = Grf(str(MASTER_GRF))
    try:
        for key in ("accessoryid.lub", "accname.lub"):
            snapshot = SOURCE / f"master_{key}"
            if not snapshot.exists():
                snapshot.write_bytes(archive.read(LUA_ROOT + key.encode("ascii")))
    finally:
        archive.close()
    iteminfo_snapshot = SOURCE / "master_itemInfo_C.lua"
    if not iteminfo_snapshot.exists():
        iteminfo_snapshot.write_bytes(ITEMINFO.read_bytes())
    return result


def map_spr_palette(spr: bytes, ramp: tuple[tuple[int, int, int], ...]) -> bytes:
    if spr[:4] != b"SP\x01\x02" or len(spr) < 1032:
        raise ValueError("Expected indexed SPR 1.2 with a 1024-byte palette")
    out = bytearray(spr)
    palette_start = len(out) - 1024
    for index, color in zip(HORN_RAMP, ramp, strict=True):
        pos = palette_start + index * 4
        alpha = out[pos + 3]
        out[pos:pos + 4] = bytes((*color, alpha))
    return bytes(out)


def icon_variant(payload: bytes, ramp: tuple[tuple[int, int, int], ...]) -> tuple[bytes, Image.Image]:
    import io
    image = Image.open(io.BytesIO(payload))
    if image.mode != "P" or image.size != (24, 24):
        raise ValueError("Item 400124 source icon must be an indexed 24x24 BMP")
    palette = list(image.getpalette() or [])
    palette += [0] * (768 - len(palette))
    pixels = list(image.get_flattened_data())
    magenta_indices = {
        index for index in range(256)
        if palette[index * 3:index * 3 + 3] == [255, 0, 255]
    }
    if not magenta_indices:
        raise ValueError("Item 400124 source icon is missing its magenta transparency color")
    if 0 not in magenta_indices and 0 in pixels:
        raise ValueError("Item 400124 uses palette index 0 for visible artwork")
    pixels = [0 if index in magenta_indices else index for index in pixels]
    palette[:3] = [255, 0, 255]
    for index, color in zip(HORN_RAMP, ramp, strict=True):
        palette[index * 3:index * 3 + 3] = color
    image.putdata(pixels)
    image.putpalette(palette[:768])
    output = io.BytesIO()
    image.save(output, format="BMP")
    check = Image.open(io.BytesIO(output.getvalue()))
    if check.mode != "P" or check.size != (24, 24) or check.getpalette()[:3] != [255, 0, 255]:
        raise ValueError("Recolored item 400124 icon lost indexed magenta transparency")
    return output.getvalue(), check


def collection_variant(
    payload: bytes,
    icon_payload: bytes,
    ramp: tuple[tuple[int, int, int], ...],
) -> tuple[bytes, Image.Image, Image.Image]:
    import colorsys
    import io
    original = Image.open(io.BytesIO(payload)).convert("RGB")
    output = original.copy()
    mask = Image.new("L", original.size, 0)
    original_pixels, output_pixels, mask_pixels = original.load(), output.load(), mask.load()
    icon = Image.open(io.BytesIO(icon_payload))
    if icon.mode != "P" or icon.size != (24, 24):
        raise ValueError("Collection recolor needs item 400124's indexed inventory icon")
    icon_palette = icon.getpalette() or []
    source_ramp = [
        tuple(icon_palette[index * 3:index * 3 + 3])
        for index in HORN_RAMP
    ]
    source_hsv = [colorsys.rgb_to_hsv(*(component / 255 for component in color)) for color in source_ramp]
    target_hsv = [colorsys.rgb_to_hsv(*(component / 255 for component in color)) for color in ramp]
    changed = 0
    for y in range(original.height):
        for x in range(original.width):
            rgb = original_pixels[x, y]
            hue, saturation, value = colorsys.rgb_to_hsv(*(component / 255 for component in rgb))
            # The item 400124 horns are pink/magenta. The hue mask excludes the
            # warm brown side/ear tips and gold bridge; upper-horn bounds exclude
            # the cast shadow. Pixel positions stay fixed; source brightness
            # maps continuously to the selected ramp to retain detail without
            # flattening dark gray and black colorways.
            if y < 64 and hue >= 0.78 and saturation > 0.02 and value > 0.12:
                # Interpolate between adjacent 400124 horn shades by source
                # brightness; nearest-shade mapping creates visible bands on
                # the tight left curl and its dark interior.
                segment = len(source_hsv) - 2
                blend = 1.0
                if value >= source_hsv[0][2]:
                    segment, blend = 0, 0.0
                elif value > source_hsv[-1][2]:
                    for index in range(len(source_hsv) - 1):
                        bright, dark = source_hsv[index][2], source_hsv[index + 1][2]
                        if bright >= value >= dark:
                            segment = index
                            blend = (bright - value) / (bright - dark)
                            break
                source_bright = source_hsv[segment]
                source_dark = source_hsv[segment + 1]
                target_bright = target_hsv[segment]
                target_dark = target_hsv[segment + 1]
                hue_delta = ((target_dark[0] - target_bright[0] + 0.5) % 1.0) - 0.5
                target_hue = (target_bright[0] + hue_delta * blend) % 1.0
                target_saturation = target_bright[1] + (target_dark[1] - target_bright[1]) * blend
                target_value = target_bright[2] + (target_dark[2] - target_bright[2]) * blend
                source_saturation = source_bright[1] + (source_dark[1] - source_bright[1]) * blend
                saturation_scale = saturation / source_saturation if source_saturation else 1.0
                recolored = colorsys.hsv_to_rgb(
                    target_hue,
                    min(1.0, target_saturation * saturation_scale),
                    target_value,
                )
                output_pixels[x, y] = tuple(round(component * 255) for component in recolored)
                mask_pixels[x, y] = 255
                changed += 1
    if changed < 500:
        raise ValueError(f"Collection recolor selected too few horn pixels ({changed})")
    output_bmp = io.BytesIO()
    output.save(output_bmp, format="BMP")
    return output_bmp.getvalue(), output, mask


def decode_first_indexed_frame(spr: bytes) -> Image.Image:
    indexed_count, rgba_count = struct.unpack_from("<HH", spr, 4)
    if indexed_count < 1 or rgba_count != 0:
        raise ValueError("Expected indexed master accessory sprite")
    width, height, size = struct.unpack_from("<HHH", spr, 8)
    encoded = spr[14:14 + size]
    pixels = bytearray()
    cursor = 0
    while cursor < len(encoded):
        value = encoded[cursor]
        cursor += 1
        if value == 0:
            run = encoded[cursor]
            cursor += 1
            pixels.extend(b"\0" * run)
        else:
            pixels.append(value)
    if len(pixels) != width * height:
        raise ValueError("SPR RLE did not decode to the declared frame dimensions")
    palette = spr[-1024:]
    image = Image.new("RGBA", (width, height))
    image.putdata([
        (palette[index * 4], palette[index * 4 + 1], palette[index * 4 + 2], 0 if index == 0 else 255)
        for index in pixels
    ])
    return image


def add_sprite_files(files: dict[bytes, bytes], source: dict[str, bytes], item: dict) -> tuple[bytes, bytes]:
    resource = item["resource"].encode("ascii")
    male = map_spr_palette(source["male_spr"], item["ramp"])
    female = map_spr_palette(source["female_spr"], item["ramp"])
    drop = map_spr_palette(source["drop_spr"], item["ramp"])
    for directory, prefix, payload, act in (
        (ACCESSORY + b"\\" + MALE, MALE, male, source["male_act"]),
        (ACCESSORY + b"\\" + FEMALE, FEMALE, female, source["female_act"]),
    ):
        for underscore in (b"_", b"__"):
            stem = prefix + underscore + resource
            files[SPRITE_ROOT + directory + b"\\" + stem + b".spr"] = payload
            files[SPRITE_ROOT + directory + b"\\" + stem + b".act"] = act
    for underscore in (b"", b"_"):
        files[SPRITE_ROOT + ITEM + b"\\" + underscore + resource + b".spr"] = drop
        files[SPRITE_ROOT + ITEM + b"\\" + underscore + resource + b".act"] = source["drop_act"]
    icon, icon_preview = icon_variant(source["icon"], item["ramp"])
    collection, collection_preview, collection_mask = collection_variant(
        source["collection"], source["icon"], item["ramp"]
    )
    for stem in (resource, b"_" + resource):
        files[UI_ROOT + b"item\\" + stem + b".bmp"] = icon
        files[UI_ROOT + b"collection\\" + stem + b".bmp"] = collection
    item_dir = SOURCE / item["resource"]
    item_dir.mkdir(parents=True, exist_ok=True)
    icon_preview_rgba = icon_preview.convert("RGBA")
    icon_alpha = Image.new("L", icon_preview.size)
    icon_alpha.putdata([0 if index == 0 else 255 for index in icon_preview.get_flattened_data()])
    icon_preview_rgba.putalpha(icon_alpha)
    icon_preview_rgba.resize((192, 192), Image.Resampling.NEAREST).save(item_dir / "inventory_preview.png")
    collection_preview.save(item_dir / "collection_preview.png")
    if item["label"] == "Sapphire":
        collection_mask.save(SOURCE / "collection_recolor_mask.png")
    decode_first_indexed_frame(male).resize((192, 192), Image.Resampling.NEAREST).save(item_dir / "male_sprite_preview.png")
    return male, icon


def encode_lua(proto: dict) -> bytes:
    import struct as st
    def chunk(current: dict, top: bool = False) -> bytes:
        body = bytearray()
        src = current["source"] if top else None
        body += st.pack("<I", len(src) + 1) + src + b"\0" if src is not None else st.pack("<I", 0)
        body += st.pack("<II", current["line_start"], current["line_end"])
        body += bytes((current["nups"], current["params"], current["vararg"], current["stack"]))
        body += st.pack("<I", len(current["code"]))
        body += b"".join(st.pack("<I", instruction) for instruction in current["code"])
        body += st.pack("<I", len(current["constants"]))
        for value in current["constants"]:
            if value is None:
                body += b"\0"
            elif isinstance(value, bool):
                body += b"\1" + bytes((int(value),))
            elif isinstance(value, (int, float)):
                body += b"\3" + st.pack("<d", float(value))
            elif isinstance(value, bytes):
                body += b"\4" + st.pack("<I", len(value) + 1) + value + b"\0"
            else:
                raise TypeError(f"Unsupported Lua constant: {type(value)!r}")
        body += st.pack("<I", len(current["children"]))
        for child in current["children"]:
            body += chunk(child)
        body += st.pack("<I", len(current["lineinfo"]))
        body += b"".join(st.pack("<I", line) for line in current["lineinfo"])
        body += st.pack("<I", len(current["locals"]))
        for name, start, end in current["locals"]:
            body += st.pack("<I", len(name) + 1) + name + b"\0" + st.pack("<II", start, end)
        body += st.pack("<I", len(current["upvalues"]))
        for name in current["upvalues"]:
            body += st.pack("<I", len(name) + 1) + name + b"\0"
        return bytes(body)
    return chunk(proto, True)


def encode_abx(op: int, a: int, bx: int) -> int:
    return (bx << 14) | (a << 6) | op


def encode_abc(op: int, a: int, b: int, c: int) -> int:
    return (b << 23) | (c << 14) | (a << 6) | op


def patch_lua_member(raw: bytes, entries: list[tuple[str, int | str]]) -> bytes:
    proto = parse_proto(Reader(raw))
    present_numbers = {int(value) for value in proto["constants"] if isinstance(value, float) and value.is_integer()}
    present_strings = {value.decode("latin-1") for value in proto["constants"] if isinstance(value, bytes)}
    for key, value in entries:
        if isinstance(value, int):
            if value in present_numbers or key in present_strings:
                raise ValueError(f"Lua mapping collision: {key} -> {value}")
        elif key in present_numbers or value in present_strings:
            raise ValueError(f"Lua mapping collision: {key} -> {value}")
    for key, value in entries:
        key_const = len(proto["constants"])
        proto["constants"].append(key.encode("ascii") if isinstance(key, str) else key)
        value_const = len(proto["constants"])
        proto["constants"].append(float(value) if isinstance(value, int) else value.encode("ascii"))
        proto["code"].insert(-2, encode_abx(1, 1, key_const))
        proto["code"].insert(-2, encode_abx(1, 2, value_const))
        proto["code"].insert(-2, encode_abc(9, 0, 1, 2))
        if proto["lineinfo"]:
            proto["lineinfo"].extend((0, 0, 0))
    return raw[:12] + encode_lua(proto)


def patch_grf(source: dict[str, bytes]) -> tuple[Path, dict[bytes, bytes]]:
    archive = Grf(str(MASTER_GRF))
    try:
        files = {name: archive.read(name) for name in archive.entries}
    finally:
        archive.close()
    accessory_id_path = LUA_ROOT + b"accessoryid.lub"
    accessory_name_path = LUA_ROOT + b"accname.lub"
    base_accessory_id = (SOURCE / "master_accessoryid.lub").read_bytes()
    base_accessory_name = (SOURCE / "master_accname.lub").read_bytes()
    id_proto = parse_proto(Reader(base_accessory_id))
    used_views = {int(value) for value in id_proto["constants"] if isinstance(value, float) and value.is_integer()}
    expected_ids = {2850, 2851, 2852, 2853}
    if not expected_ids.issubset(used_views):
        raise ValueError("Current midnight.grf is missing the expected custom View IDs 2850-2853")
    for item in COLORWAYS:
        if item["view"] in used_views:
            raise ValueError(f"Accessory View ID {item['view']} is already used")
    additions: dict[bytes, bytes] = {}
    for item in COLORWAYS:
        add_sprite_files(additions, source, item)
    # Rebuildable if this batch was already installed: replace only our named
    # members and rebuild the two Lua maps from their captured master versions.
    for name in additions:
        files.pop(name, None)
    id_entries = [(item["accessory"], item["view"]) for item in COLORWAYS]
    name_entries = [(item["view"], "_" + item["resource"]) for item in COLORWAYS]
    files[accessory_id_path] = patch_lua_member(base_accessory_id, id_entries)
    files[accessory_name_path] = patch_lua_member(base_accessory_name, name_entries)
    for item in COLORWAYS:
        male = map_spr_palette(source["male_spr"], item["ramp"])
        # Female and item sprites must have the same palette-only transformation.
        if male[-1024:] != map_spr_palette(source["male_spr"], item["ramp"])[-1024:]:
            raise ValueError("Male SPR palette verification failed")
    overlap = set(files).intersection(additions)
    if overlap:
        raise ValueError(f"New resource paths already exist in midnight.grf: {next(iter(overlap))!r}")
    files.update(additions)
    staged = BUILD / "midnight.grf"
    staged.parent.mkdir(parents=True, exist_ok=True)
    build_grf(staged, list(files.items()), verbose=False)
    rebuilt = Grf(str(staged))
    try:
        if rebuilt.version != 0x200 or len(rebuilt.entries) != len(files):
            raise ValueError("Rebuilt midnight.grf did not retain v0x200 or every archive member")
        for name, content in additions.items():
            if rebuilt.read(name) != content:
                raise ValueError(f"GRF roundtrip verification failed for {name!r}")
        for name in (accessory_id_path, accessory_name_path):
            if rebuilt.read(name) != files[name]:
                raise ValueError(f"GRF Lua member verification failed for {name!r}")
    finally:
        rebuilt.close()
    return staged, additions


def iteminfo_payload() -> bytes:
    raw = (SOURCE / "master_itemInfo_C.lua").read_bytes()
    text = raw.decode("cp874")
    if "tbl_custom[902275]" in text:
        raise ValueError("Client itemInfo_C.lua already contains this batch")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    lines = [
        "-- Midnight RO - Costume Majestic Goat colorways, cloned from item 19549.",
        "local function cloneMajesticGoatColorway(itemId, displayName, resourceName, viewId)",
        "\tlocal source = tbl[19549]",
        "\tif not source then error(\"Costume Majestic Goat master item 19549 is missing\") end",
        "\tlocal item = {}",
        "\tfor key, value in pairs(source) do item[key] = value end",
        "\tlocal description = {}",
        "\tfor index, line in ipairs(source.identifiedDescriptionName or {}) do description[index] = line end",
        "\tlocal positionAndWeight, weightChanges = string.gsub(description[3] or \"\", \" : 10$\", \" : 0\")",
        "\tlocal requiredLevel, levelChanges = string.gsub(description[4] or \"\", \" : 100$\", \" : 1\")",
        "\tif weightChanges ~= 1 or levelChanges ~= 1 then error(\"Unexpected Costume Majestic Goat description format\") end",
        "\tdescription[3] = positionAndWeight",
        "\tdescription[4] = requiredLevel",
        "\titem.identifiedDescriptionName = description",
        "\titem.unidentifiedDisplayName = displayName",
        "\titem.identifiedDisplayName = displayName",
        "\titem.unidentifiedResourceName = resourceName",
        "\titem.identifiedResourceName = resourceName",
        "\titem.ClassNum = viewId",
        "\titem.costume = true",
        "\ttbl_custom[itemId] = item",
        "end",
    ]
    for item in COLORWAYS:
        lines.append(f'cloneMajesticGoatColorway({item["id"]}, "{item["name"]}", "{item["resource"]}", {item["view"]})')
    marker = "-- Table for Official Overrides"
    if marker not in text:
        raise ValueError("Could not find itemInfo_C.lua insertion point")
    block = eol.join(lines) + eol + eol
    text = text.replace(marker, block + marker, 1)
    return text.encode("cp874", errors="strict")


def costume_baseline_payload() -> bytes:
    spec = importlib.util.spec_from_file_location("costume_baseline_tooltip", BASELINE_BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load Costume baseline generator: {BASELINE_BUILDER}")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    records: dict[int, dict] = {}
    builder.load_item_db(builder.ITEM_DB, records)
    costume_ids = sorted(item_id for item_id, item in records.items() if builder.is_costume(item))
    missing = [item["id"] for item in COLORWAYS if item["id"] not in costume_ids]
    if missing:
        raise ValueError(f"Costume baseline source is missing colorway IDs: {missing}")
    payload = builder.render(costume_ids).encode("ascii", errors="strict")
    if "{ 902275, 902289 }," not in payload.decode("ascii"):
        raise ValueError("Generated Costume baseline does not cover all fifteen Majestic Goat colorways")
    return payload


def server_item_entries(items: tuple[dict, ...] | None = None) -> str:
    lines: list[str] = []
    for item in COLORWAYS if items is None else items:
        lines.extend((
            "  # Costume Majestic Goat recolor, cloned from official item 19549.",
            f'  - Id: {item["id"]}',
            f'    AegisName: "{item["aegis"]}"',
            f'    Name: "{item["name"]}"',
            "    Type: Armor",
            "    Buy: 20",
            "    Weight: 0",
            "    Locations:",
            "      Costume_Head_Top: true",
            "    ArmorLevel: 1",
            "    EquipLevelMin: 1",
            f'    View: {item["view"]}',
            "    Script: |",
            "      bonus bUnbreakableHelm;",
            "",
        ))
    return "\n".join(lines)


def update_server_db() -> None:
    raw = ITEM_DB.read_bytes()
    lines = raw.decode("utf-8").splitlines(keepends=True)
    bodies = [line.rstrip("\r\n") for line in lines]
    entry_starts = [index for index, line in enumerate(bodies) if re.fullmatch(r"  - Id: \d+", line)]
    entry_by_id: dict[int, tuple[int, int]] = {}
    for position, start in enumerate(entry_starts):
        end = entry_starts[position + 1] if position + 1 < len(entry_starts) else len(lines)
        item_id = int(bodies[start].split(":", 1)[1].strip())
        entry_by_id[item_id] = (start, end)
    missing: list[dict] = []
    changed = False
    for item in COLORWAYS:
        entry = entry_by_id.get(item["id"])
        if entry is None:
            id_pattern = rf"^[ \t]*- Id:[ \t]*{item['id']}[ \t]*$"
            aegis_pattern = rf'^[ \t]*AegisName:[ \t]*"{re.escape(item["aegis"])}"[ \t]*$'
            all_text = "".join(lines)
            if re.search(id_pattern, all_text, re.MULTILINE) or re.search(aegis_pattern, all_text, re.MULTILINE):
                raise ValueError(f"Server item ID or AegisName exists with different data: {item['id']}")
            view_pattern = rf"^[ \t]*View:[ \t]*{item['view']}[ \t]*$"
            if re.search(view_pattern, all_text, re.MULTILINE):
                raise ValueError(f"Server import already uses costume View ID {item['view']}")
            missing.append(item)
            continue
        start, end = entry
        block = bodies[start:end]
        if f'    AegisName: "{item["aegis"]}"' not in block or f'    View: {item["view"]}' not in block:
            raise ValueError(f"Server item ID {item['id']} exists with conflicting AegisName or View")
        for field, value in (("Weight", 0), ("EquipLevelMin", 1)):
            matches = [index for index, line in enumerate(block) if re.match(rf"^    {field}:", line)]
            if len(matches) != 1:
                raise ValueError(f"Expected one {field} field for item {item['id']}")
            target = matches[0]
            if not re.fullmatch(rf"    {field}: \d+", block[target]):
                raise ValueError(f"Unexpected {field} value format for item {item['id']}")
            replacement = f"    {field}: {value}"
            if block[target] != replacement:
                original = lines[start + target]
                ending = original[len(original.rstrip("\r\n")):]
                lines[start + target] = replacement + ending
                block[target] = replacement
                changed = True
    if not missing and not changed:
        return
    output = "".join(lines)
    if missing:
        eol = b"\r\n" if b"\r\n" in raw else b"\n"
        addition = server_item_entries(tuple(missing)).strip("\n")
        output_bytes = output.encode("utf-8").rstrip(b"\r\n") + eol + eol + addition.encode("utf-8").replace(b"\n", eol) + eol
    else:
        output_bytes = output.encode("utf-8")
    ITEM_DB.write_bytes(output_bytes)


def write_sources_and_previews(source: dict[str, bytes]) -> None:
    (SOURCE / "colorways.json").write_text(json.dumps([
        {key: value for key, value in item.items() if key != "ramp"} | {"ramp": item["ramp"]}
        for item in COLORWAYS
    ], indent=2) + "\n", encoding="utf-8")
    original_male = decode_first_indexed_frame(source["male_spr"])
    cell_w, cell_h = 220, 245
    sheet = Image.new("RGB", (cell_w * len(COLORWAYS), cell_h), (239, 241, 246))
    draw = ImageDraw.Draw(sheet)
    for index, item in enumerate(COLORWAYS):
        preview = original_male.copy()
        pixels = list(preview.get_flattened_data())
        palette = source["male_spr"][-1024:]
        rgb_lookup = {tuple(palette[i * 4:i * 4 + 3]): color for i, color in zip(HORN_RAMP, item["ramp"], strict=True)}
        preview.putdata([(*rgb_lookup.get(pixel[:3], pixel[:3]), pixel[3]) for pixel in pixels])
        preview.thumbnail((180, 140), Image.Resampling.NEAREST)
        preview_canvas = Image.new("RGBA", (cell_w - 24, 155), (255, 255, 255, 255))
        preview_canvas.alpha_composite(preview, ((preview_canvas.width - preview.width) // 2, (preview_canvas.height - preview.height) // 2))
        x = index * cell_w
        sheet.paste(preview_canvas.convert("RGB"), (x + 12, 12))
        draw.text((x + 14, 176), f"{item['label']} | ID {item['id']}", fill=(32, 38, 51))
        draw.text((x + 14, 197), f"View {item['view']}  /  {item['resource']}", fill=(71, 78, 91))
        draw.text((x + 14, 219), "Gold center ornament preserved", fill=(112, 101, 70))
        folder = SOURCE / item["resource"]
        folder.mkdir(parents=True, exist_ok=True)
        preview.save(folder / "male_sprite_preview.png")
    sheet.save(SOURCE / "colorways_contact_sheet.png")


def write_candidate(grf_path: Path, iteminfo: bytes, baseline_iteminfo: bytes) -> None:
    PATCH.mkdir(parents=True, exist_ok=True)
    shutil.copy2(grf_path, PATCH / "midnight.grf")
    (PATCH / "SystemEN").mkdir(exist_ok=True)
    (PATCH / "SystemEN" / "itemInfo_C.lua").write_bytes(iteminfo)
    (PATCH / "SystemEN" / "itemInfo_ProjectRO_Costume.lua").write_bytes(baseline_iteminfo)
    instructions = """# Costume Majestic Goat colorways candidate

This candidate adds fifteen shaded recolors of master costume item 19549. The brown
master remains unchanged; the gold center ornament remains gold in every recolor.
The indexed inventory icons and detailed collection previews come from item
400124. Their horn colors are recolored while preserving the original shading,
gold centerpiece, warm side/ear tips, and cast shadow. The preview recolor keeps
the original pixel placement and maps source shading continuously onto each
color ramp. Worn-sprite position follows the matching master assets.
The Costume baseline tooltip includes every new ID, showing Max HP +1%, Max SP
+1%, and weight limit +200.

| Name | Item ID | Accessory View |
|---|---:|---:|
| Sapphire | 902275 | 2854 |
| Emerald | 902276 | 2855 |
| Ruby | 902277 | 2856 |
| Warm Ivory test (display name remains Pearl) | 902278 | 2857 |
| Amethyst | 902279 | 2858 |
| Rose | 902280 | 2859 |
| Graphite Gray | 902281 | 2860 |
| Onyx Black | 902282 | 2861 |
| Fallen Shade | 902283 | 2862 |
| Fallen Dusk | 902284 | 2863 |
| Feather White | 902285 | 2864 |
| Silver Smoke | 902286 | 2865 |
| Rose Silver | 902287 | 2866 |
| Archangel Match (sampled from item 2573) | 902288 | 2867 |
| Warm Feather | 902289 | 2868 |

## Copy and test

1. Reload the local Server item database (`@reloaditemdb` as GM, or restart the
   local Server when it is safe to do so).
2. Back up the three listed Client files, then copy `midnight.grf` to the Client root
   and both Lua files under `SystemEN` to the matching folder.
3. Connect to the local server and create each item from `@item 902275` through
   `@item 902289`, one at a time.
4. Check that each tooltip shows the baseline values and level/weight requirements,
   verify the inventory icon and male/female equipment appearance, and equip each
   item as Costume Head Top.

The server definitions are in `server/db/import/item_db.yml` on the developer
machine. This candidate is for live testing only; it is not a numbered patch.
"""
    (PATCH / "README.md").write_text(instructions, encoding="utf-8")
    manifest_files = [
        PATCH / "midnight.grf",
        PATCH / "SystemEN" / "itemInfo_C.lua",
        PATCH / "SystemEN" / "itemInfo_ProjectRO_Costume.lua",
    ]
    manifest = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(PATCH).as_posix()}\n" for path in manifest_files)
    (PATCH / "SHA256SUMS.txt").write_text(manifest, encoding="ascii")


def apply_master(grf_path: Path, iteminfo: bytes, baseline_iteminfo: bytes) -> None:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-Process | Where-Object {$_.ProcessName -match 'MidnightRO|Ragexe|ThorLauncher'} | Select-Object -ExpandProperty ProcessName) -join ','"],
            check=True, capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Could not check that the Client and Launcher are closed") from error
    if result.stdout.strip():
        raise RuntimeError(f"Close the Client and Launcher before applying files: {result.stdout.strip()}")
    shutil.copy2(grf_path, MASTER_GRF)
    ITEMINFO.write_bytes(iteminfo)
    BASELINE_ITEMINFO.write_bytes(baseline_iteminfo)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-master", action="store_true", help="copy built GRF and itemInfo_C.lua to Client master")
    parser.add_argument("--master-only", action="store_true", help="skip Patch_Test staging until preliminary live testing is complete")
    args = parser.parse_args()
    if args.master_only and not args.apply_master:
        parser.error("--master-only requires --apply-master")
    source = get_sources()
    grf_path, _ = patch_grf(source)
    iteminfo = iteminfo_payload()
    baseline_iteminfo = costume_baseline_payload()
    if not args.master_only:
        write_candidate(grf_path, iteminfo, baseline_iteminfo)
    write_sources_and_previews(source)
    if args.apply_master:
        apply_master(grf_path, iteminfo, baseline_iteminfo)
    update_server_db()
    if not args.master_only:
        print(f"Built candidate: {PATCH}")
    print(f"Source previews: {SOURCE / 'colorways_contact_sheet.png'}")
    print(f"Server database updated: {ITEM_DB}")
    if args.apply_master:
        print(f"Client master updated: {MASTER_GRF}, {ITEMINFO}, and {BASELINE_ITEMINFO}")


if __name__ == "__main__":
    main()
