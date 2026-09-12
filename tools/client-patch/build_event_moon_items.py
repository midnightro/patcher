#!/usr/bin/env python3
"""Build Moon Fragment (902247) and Moonlit Dust (902248) client assets.

Creates 24x24 item icons, 75x100 collection images, SPR 1.2 sprites,
copies donor ACT, writes preview images, updates MidnightROClient/midnight.grf,
and updates MidnightROClient/SystemEN/itemInfo_C.lua with CP874 encoding.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import struct
import sys
from pathlib import Path

from PIL import Image, ImageFilter

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402

ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
ITEMINFO_CUSTOM = CLIENT / "SystemEN" / "itemInfo_C.lua"

SOURCE_DIR = TOOLS / "ui_sources" / "event_moon_items"
ARTIFACTS_DIR = Path(r"C:\Users\Burin\.gemini\antigravity-ide\brain\02624681-4917-48c0-908d-f3a4bc96f4f4")

UI = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\"
DROP = b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\"

ITEMS = (
    {
        "id": 902247,
        "aegis": "Moon_Fragment",
        "name": "Moon Fragment",
        "resource": "moon_fragment",
        "master_filename": "moon_fragment_master.png",
        "raw_artifact": ARTIFACTS_DIR / "moon_fragment_master_1789230913222.jpg",
        "short_desc": "เศษเสี้ยวคริสตัลจันทราที่เปล่งประกายลึกลับ",
        "tooltip_lines": [
            "^FFD700Moon Fragment^000000",
            "^111111เศษเสี้ยวคริสตัลจันทราที่เปล่งประกายลึกลับ^000000",
            "^111111เป็นเศษแสงจากโลกที่ตื่นขึ้นหลังพระอาทิตย์ตกดิน^000000",
            "^111111พบได้จากสิ่งมีชีวิตพิเศษในยามค่ำคืนเท่านั้น^000000",
            "^B7DFE5====================^000000",
            "^00AAFFวัตถุดิบสำคัญสำหรับกิจกรรม Midnight Event^000000",
            "^111111สามารถใช้แลกเปลี่ยนของรางวัลกับ Midnight Keeper ได้^000000",
            "^B7DFE5====================^000000",
            "^111111ประเภท: ไอเทมเบ็ดเตล็ด | น้ำหนัก: 1^000000",
        ],
    },
    {
        "id": 902248,
        "aegis": "Moonlit_Dust",
        "name": "Moonlit Dust",
        "resource": "moonlit_dust",
        "master_filename": "moonlit_dust_master.png",
        "raw_artifact": ARTIFACTS_DIR / "moonlit_dust_master_1789230928528.jpg",
        "short_desc": "ผงละอองเรืองแสงระยิบระยับดั่งแสงดาวค่ำคืน",
        "tooltip_lines": [
            "^FFD700Moonlit Dust^000000",
            "^111111ผงละอองเรืองแสงระยิบระยับดั่งแสงดาวค่ำคืน^000000",
            "^111111ร่วงหล่นจากมอนสเตอร์พิเศษของ Midnight RO^000000",
            "^111111มีพลังงานมนตราแห่งราตรีกาลแฝงอยู่อย่างเข้มข้น^000000",
            "^B7DFE5====================^000000",
            "^00AAFFวัตถุดิบและของสะสมพิเศษสำหรับกิจกรรมในอนาคต^000000",
            "^111111สามารถเก็บสะสมไว้ในกระเป๋าหรือคลังได้^000000",
            "^B7DFE5====================^000000",
            "^111111ประเภท: ไอเทมเบ็ดเตล็ด | น้ำหนัก: 1^000000",
        ],
    },
)


def extract_art(image_path: Path, is_cyan_crystal: bool = False) -> Image.Image:
    """Remove flat magenta chroma key and halo glow, returning tightly cropped RGBA artwork."""
    source = Image.open(image_path).convert("RGB")
    rgba = Image.new("RGBA", source.size)
    pixels = []
    for pixel in source.get_flattened_data():
        r, g, b = pixel[:3]
        # Any pixel where red and blue dominate over green is part of the magenta backdrop or its halo glow
        is_bg = (r > g + 8 and b > g + 10) or (r > 120 and b > 120 and r > g + 5)
        if is_bg:
            pixels.append((r, g, b, 0))
        else:
            if is_cyan_crystal and r > g:
                r = g
            pixels.append((r, g, b, 255))
    rgba.putdata(pixels)
    bbox = rgba.getchannel("A").getbbox()
    if bbox is None:
        raise RuntimeError(f"no visible artwork extracted from {image_path}")
    return rgba.crop(bbox)


def indexed_asset(
    art: Image.Image,
    size: tuple[int, int],
    inset: int,
    *,
    sharpen: bool = True,
    alpha_threshold: int = 120,
) -> Image.Image:
    """Scale and quantize artwork into 8-bit indexed BMP with #FF00FF as index 0."""
    canvas = Image.new("RGBA", size, (255, 0, 255, 0))
    scale = min(
        (size[0] - inset * 2) / art.width,
        (size[1] - inset * 2) / art.height,
    )
    fitted = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    if sharpen:
        alpha = fitted.getchannel("A")
        crisp = fitted.convert("RGB").filter(
            ImageFilter.UnsharpMask(radius=0.7, percent=150, threshold=2)
        )
        fitted = crisp.convert("RGBA")
        fitted.putalpha(alpha)
    canvas.alpha_composite(
        fitted,
        ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2),
    )

    rgb = Image.new("RGB", size, (255, 0, 255))
    rgb.paste(canvas.convert("RGB"))
    quantized = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()[: 255 * 3]
    indexed = Image.new("P", size)
    indexed.putpalette([255, 0, 255] + palette)
    color_pixels = [value + 1 for value in quantized.get_flattened_data()]
    alpha_pixels = canvas.getchannel("A").get_flattened_data()
    indexed.putdata(
        [0 if opacity < alpha_threshold else value
         for opacity, value in zip(alpha_pixels, color_pixels)]
    )
    return indexed


def collection_asset(
    art: Image.Image,
    size: tuple[int, int] = (75, 100),
    inset: int = 3,
    *,
    sharpen: bool = True,
) -> Image.Image:
    """Create 75x100 Collection image with a pure white background (255, 255, 255) like official RO collection images."""
    canvas = Image.new("RGBA", size, (255, 255, 255, 255))
    scale = min(
        (size[0] - inset * 2) / art.width,
        (size[1] - inset * 2) / art.height,
    )
    fitted = art.resize(
        (max(1, round(art.width * scale)), max(1, round(art.height * scale))),
        Image.Resampling.LANCZOS,
    )
    if sharpen:
        alpha = fitted.getchannel("A")
        crisp = fitted.convert("RGB").filter(
            ImageFilter.UnsharpMask(radius=0.7, percent=150, threshold=2)
        )
        fitted = crisp.convert("RGBA")
        fitted.putalpha(alpha)

    offset = ((size[0] - fitted.width) // 2, (size[1] - fitted.height) // 2)
    canvas.alpha_composite(fitted, offset)
    return canvas.convert("RGB")


def save_collection_asset(image: Image.Image, bmp_path: Path, preview_path: Path) -> None:
    """Save 24-bit RGB BMP with white background and PNG preview."""
    image.save(bmp_path, "BMP")
    check = Image.open(bmp_path)
    if check.size != (75, 100):
        raise RuntimeError(f"invalid collection size: {bmp_path}")
    image.save(preview_path, "PNG")


def save_asset(image: Image.Image, bmp_path: Path, preview_path: Path) -> None:
    """Save 8-bit indexed BMP and a nearest-neighbor scaled PNG preview."""
    image.save(bmp_path, "BMP", bits=8)
    check = Image.open(bmp_path)
    if check.mode != "P" or check.size != image.size:
        raise RuntimeError(f"invalid indexed BMP: {bmp_path}")
    if check.getpalette()[:3] != [255, 0, 255]:
        raise RuntimeError(f"palette index 0 is not transparent magenta: {bmp_path}")

    rgba = image.convert("RGBA")
    alpha = Image.new("L", image.size)
    alpha.putdata([0 if val == 0 else 255 for val in image.get_flattened_data()])
    rgba.putalpha(alpha)
    rgba.resize((image.width * 6, image.height * 6), Image.Resampling.NEAREST).save(preview_path)


def sprite_asset(image: Image.Image) -> bytes:
    """Encode 24x24 indexed frame as a Ragnarok SPR 1.2 item sprite."""
    raw = list(image.get_flattened_data())
    encoded = bytearray()
    cursor = 0
    while cursor < len(raw):
        if raw[cursor] != 0:
            encoded.append(raw[cursor])
            cursor += 1
            continue
        run = 1
        while cursor + run < len(raw) and raw[cursor + run] == 0 and run < 255:
            run += 1
        encoded.extend((0, run))
        cursor += run

    palette = image.getpalette()[:768]
    palette += [0] * (768 - len(palette))
    payload = bytearray(b"SP\x01\x02")
    payload += struct.pack("<HHHHH", 1, 0, image.width, image.height, len(encoded))
    payload += encoded
    for index in range(256):
        payload += bytes((palette[index * 3], palette[index * 3 + 1], palette[index * 3 + 2], 0))
    return bytes(payload)


def build_iteminfo_entry(item: dict) -> bytes:
    """Format single custom item entry encoded as strict CP874."""
    item_id = item["id"]
    name = item["name"]
    resource = item["resource"]
    short_desc = item["short_desc"]
    lines = item["tooltip_lines"]

    desc_lines = '\\n" ..\n\t\t\t"'.join(lines)
    text = f'''\t[{item_id}] = {{
\t\tunidentifiedDisplayName = "{name}",
\t\tunidentifiedResourceName = "{resource}",
\t\tunidentifiedDescriptionName = {{ "{short_desc}" }},
\t\tidentifiedDisplayName = "{name}",
\t\tidentifiedResourceName = "{resource}",
\t\tidentifiedDescriptionName = {{
\t\t\t"{desc_lines}"
\t\t}},
\t\tslotCount = 0,
\t\tClassNum = 0,
\t\tcostume = false
\t}},
'''
    return text.encode("cp874", errors="strict")


def update_iteminfo_file() -> None:
    """Update MidnightROClient/SystemEN/itemInfo_C.lua with CP874 encoding."""
    if not ITEMINFO_CUSTOM.exists():
        raise FileNotFoundError(f"not found: {ITEMINFO_CUSTOM}")

    data = ITEMINFO_CUSTOM.read_bytes()
    data.decode("cp874", errors="strict")

    marker = b"tbl_custom = {\r\n"
    if marker not in data:
        marker = b"tbl_custom = {\n"
    if data.count(marker) != 1:
        raise RuntimeError("could not locate unique tbl_custom marker")

    target_ids = {item["id"] for item in ITEMS}
    top_level = re.compile(rb"(?m)^\t\[(\d+)\]\s*=\s*\{")
    matches = list(top_level.finditer(data))
    removals = []
    for index, match in enumerate(matches):
        matched_id = int(match.group(1))
        if matched_id not in target_ids:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else data.find(b"\r\n}\r\n", match.end())
        if end < 0:
            end = data.find(b"\n}\n", match.end())
        if end < 0:
            raise RuntimeError(f"truncated ItemInfo entry {matched_id}")
        removals.append((match.start(), end))

    for start, end in reversed(removals):
        data = data[:start] + data[end:]

    entries_payload = b"".join(build_iteminfo_entry(item) for item in ITEMS)
    data = data.replace(marker, marker + entries_payload, 1)
    data.decode("cp874", errors="strict")
    ITEMINFO_CUSTOM.write_bytes(data)
    print(f"Updated {ITEMINFO_CUSTOM} with IDs: {[item['id'] for item in ITEMS]}")


def main() -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Prepare master artwork in ui_sources
    for item in ITEMS:
        dest = SOURCE_DIR / item["master_filename"]
        raw = item["raw_artifact"]
        if not dest.exists():
            shutil.copy2(raw, dest)
            print(f"Copied master art: {dest}")

    # 2. Extract donor act from current midnight.grf
    client_grf = Grf(TARGET_GRF)
    try:
        donor_act_member = DROP + b"midnight_vip_7.act"
        donor_act = client_grf.read(donor_act_member)
    finally:
        client_grf.close()

    new_members: list[tuple[bytes, bytes]] = []

    # 3. Generate BMPs, previews, and sprites
    for item in ITEMS:
        res = item["resource"]
        master_file = SOURCE_DIR / item["master_filename"]
        art = extract_art(master_file, is_cyan_crystal=(res == "moon_fragment"))

        item_bmp_path = SOURCE_DIR / f"{res}_item.bmp"
        col_bmp_path = SOURCE_DIR / f"{res}_collection.bmp"
        item_prev_path = SOURCE_DIR / f"{res}_item_preview.png"
        col_prev_path = SOURCE_DIR / f"{res}_collection_preview.png"
        spr_path = SOURCE_DIR / f"{res}.spr"
        act_path = SOURCE_DIR / f"{res}.act"

        # Item icon: 24x24 (1px inset)
        item_img = indexed_asset(art, (24, 24), inset=1, sharpen=True, alpha_threshold=120)
        save_asset(item_img, item_bmp_path, item_prev_path)

        # Collection: 75x100 (3px inset) on pure white background (255, 255, 255)
        col_img = collection_asset(art, (75, 100), inset=3, sharpen=True)
        save_collection_asset(col_img, col_bmp_path, col_prev_path)

        # SPR & ACT
        spr_data = sprite_asset(item_img)
        spr_path.write_bytes(spr_data)
        act_path.write_bytes(donor_act)

        encoded_res = res.encode("ascii")
        new_members.extend([
            (UI + b"item\\" + encoded_res + b".bmp", item_bmp_path.read_bytes()),
            (UI + b"collection\\" + encoded_res + b".bmp", col_bmp_path.read_bytes()),
            (DROP + encoded_res + b".spr", spr_data),
            (DROP + encoded_res + b".act", donor_act),
        ])
        print(f"Generated assets for {item['name']} ({res}): 24x24, 75x100, spr, act")

    # 4. Update MidnightROClient/midnight.grf
    backup_grf = CLIENT / "midnight.grf.before_event_moon_items"
    if not backup_grf.exists():
        shutil.copy2(TARGET_GRF, backup_grf)
        print(f"Created GRF backup at: {backup_grf}")

    current_grf = Grf(TARGET_GRF)
    all_files: dict[bytes, bytes] = {}
    try:
        for entry in current_grf.entries:
            all_files[entry] = current_grf.read(entry)
    finally:
        current_grf.close()

    for member_name, member_bytes in new_members:
        all_files[member_name] = member_bytes

    file_list = list(all_files.items())
    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, file_list, verbose=False)

    verify_grf = Grf(staged_grf)
    try:
        if verify_grf.version != 0x200:
            raise RuntimeError(f"expected GRF 0x200, got {verify_grf.version:#x}")
        for member_name, expected_data in new_members:
            if verify_grf.read(member_name) != expected_data:
                raise RuntimeError(f"round-trip failed for {member_name!r}")
    finally:
        verify_grf.close()

    print(f"Successfully packaged {len(new_members)} new members into {staged_grf}")
    print(f"Total GRF members: {len(file_list)}")

    try:
        staged_grf.replace(TARGET_GRF)
        print(f"Updated live {TARGET_GRF} successfully.")
    except PermissionError:
        print(f"NOTE: {TARGET_GRF} is currently locked (likely by running game client). Staged at {staged_grf}")

    # 5. Update itemInfo_C.lua
    update_iteminfo_file()

    # 6. Sync to web assets if web app exists
    web_assets = ROOT / "web" / "public" / "assets" / "items"
    if web_assets.exists():
        for item in ITEMS:
            res = item["resource"]
            item_id = str(item["id"])
            target_dir = web_assets / item_id
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(SOURCE_DIR / f"{res}_collection.bmp", target_dir / "collection.bmp")
            shutil.copy2(SOURCE_DIR / f"{res}_item.bmp", target_dir / "inventory.bmp")
        print(f"Synced updated assets to {web_assets}")


if __name__ == "__main__":
    main()
