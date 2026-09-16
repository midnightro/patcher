#!/usr/bin/env python3
"""Build and install all Midnight Gacha Egg client artwork."""

from __future__ import annotations

import shutil
import struct
import sys
from pathlib import Path

from PIL import Image, ImageFilter

WORKSPACE = Path(__file__).resolve().parents[3]
PATCHER_TOOLS = WORKSPACE / "patcher" / "tools" / "client-patch"
sys.path.insert(0, str(PATCHER_TOOLS))
from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402

CLIENT = WORKSPACE / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
LOCAL_ENDPOINT_GRF = CLIENT / "server_Local_endpoint.grf"
UI = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\"
DROP = b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\"
# Use the verified existing Costume 1 egg animation as a compatible 1-frame
# donor; legacy clients require an ACT even though the item icon is static.
DONOR_ACT = DROP + b"mid_gacha1_egg.act"
EGGS = (
    ("costume_1_gacha_egg", "costume_1_gacha_egg_master.png", b"mid_gacha1_egg"),
    ("costume_2_gacha_egg", "costume_2_gacha_egg_master.png", b"mid_gacha2_egg"),
    ("shadow_gacha_egg", "shadow_gacha_egg_master.png", b"mid_shadow_egg"),
)


def artwork(path: Path) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    alpha = source.getchannel("A").point(lambda value: 255 if value >= 140 else 0)
    bbox = alpha.getbbox()
    if bbox is None:
        raise RuntimeError(f"no opaque artwork in {path}")
    return source.crop(bbox)


def indexed_asset(art: Image.Image) -> Image.Image:
    size, inset = (24, 24), 1
    canvas = Image.new("RGBA", size, (255, 0, 255, 0))
    scale = min((size[0] - inset * 2) / art.width, (size[1] - inset * 2) / art.height)
    fitted = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS)
    alpha = fitted.getchannel("A")
    crisp = fitted.convert("RGB").filter(ImageFilter.UnsharpMask(radius=0.7, percent=150, threshold=2)).convert("RGBA")
    crisp.putalpha(alpha)
    canvas.alpha_composite(crisp, ((size[0] - crisp.width) // 2, (size[1] - crisp.height) // 2))
    rgb = Image.new("RGB", size, (255, 0, 255))
    rgb.paste(canvas.convert("RGB"))
    quantized = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    indexed = Image.new("P", size)
    indexed.putpalette([255, 0, 255] + quantized.getpalette()[:255 * 3])
    indexed.putdata([0 if opacity < 150 else color + 1 for color, opacity in zip(quantized.get_flattened_data(), canvas.getchannel("A").get_flattened_data())])
    return indexed


def sprite(image: Image.Image) -> bytes:
    raw, encoded, cursor = list(image.get_flattened_data()), bytearray(), 0
    while cursor < len(raw):
        if raw[cursor]:
            encoded.append(raw[cursor]); cursor += 1; continue
        run = 1
        while cursor + run < len(raw) and raw[cursor + run] == 0 and run < 255:
            run += 1
        encoded.extend((0, run)); cursor += run
    palette = image.getpalette()[:768] + [0] * (768 - len(image.getpalette()[:768]))
    payload = bytearray(b"SP\x01\x02") + struct.pack("<HHHHH", 1, 0, image.width, image.height, len(encoded)) + encoded
    for index in range(256):
        payload += bytes((*palette[index * 3:index * 3 + 3], 0))
    return bytes(payload)


def files() -> dict[bytes, bytes]:
    added: dict[bytes, bytes] = {}
    root = Path(__file__).parent / "ui_sources"
    for folder, master, resource in EGGS:
        directory = root / folder
        art = artwork(directory / master)
        icon = indexed_asset(art)
        item_bmp = directory / f"{folder}_item.bmp"
        icon.save(item_bmp, "BMP", bits=8)
        check = Image.open(item_bmp)
        if check.mode != "P" or check.size != (24, 24) or check.getpalette()[:3] != [255, 0, 255]:
            raise RuntimeError(f"invalid RO indexed BMP: {item_bmp}")
        icon.resize((192, 192), Image.Resampling.NEAREST).save(directory / f"{folder}_item_preview.png")
        collection = Image.new("RGBA", (75, 100), (255, 255, 255, 255))
        scale = min(69 / art.width, 94 / art.height)
        fitted = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.Resampling.LANCZOS)
        collection.alpha_composite(fitted, ((75 - fitted.width) // 2, (100 - fitted.height) // 2))
        collection_bmp = directory / f"{folder}_collection.bmp"
        collection.convert("RGB").save(collection_bmp, "BMP")
        collection.save(directory / f"{folder}_collection_preview.png", "PNG")
        spr = sprite(icon)
        (directory / f"{folder}.spr").write_bytes(spr)
        added[UI + b"item\\" + resource + b".bmp"] = item_bmp.read_bytes()
        added[UI + b"collection\\" + resource + b".bmp"] = collection_bmp.read_bytes()
        added[DROP + resource + b".spr"] = spr
    return added


def rebuild(target: Path, members: dict[bytes, bytes]) -> None:
    staged = target.with_suffix(target.suffix + ".staged")
    build(staged, list(members.items()), verbose=False)
    verify = Grf(staged)
    try:
        for name, content in members.items():
            if verify.read(name) != content:
                raise RuntimeError(f"GRF verification failed: {name!r}")
    finally:
        verify.close()
    staged.replace(target)


def main() -> None:
    if not TARGET_GRF.exists() or not LOCAL_ENDPOINT_GRF.exists():
        raise FileNotFoundError("missing midnight.grf or server_Local_endpoint.grf")
    added = files()
    for target in (TARGET_GRF, LOCAL_ENDPOINT_GRF):
        current = Grf(target)
        try:
            members = {entry: current.read(entry) for entry in current.entries}
            donor = current.read(DONOR_ACT)
        finally:
            current.close()
        for _, _, resource in EGGS:
            added[DROP + resource + b".act"] = donor
        members.update(added)
        backup = target.with_name(target.name + ".before_all_gacha_eggs")
        if not backup.exists():
            shutil.copy2(target, backup)
        rebuild(target, members)
    print("Installed all three Gacha Egg assets in midnight.grf and server_Local_endpoint.grf.")


if __name__ == "__main__":
    main()
