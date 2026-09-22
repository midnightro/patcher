#!/usr/bin/env python3
"""Render a review sheet of body sprites under each clothes-dye palette.

    py -3 render_clothes_palette_sheet.py OUT.png [--compare OLD.grf] [--slots 0,1,2,3,4,12,13,14,15]

One row per job/gender that has a palette 15, one column per slot.  With
``--compare`` the slots 12-15 are drawn twice: first from OLD.grf, then from the
current ``midnight.grf``, so a palette change can be judged by eye before release.
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clothes_palette_policy as policy  # noqa: E402
from grf import Grf  # noqa: E402

SPRITE_DIR = "data\\sprite\\인간족\\몸통\\".encode("cp949")
# sprite names that differ from the palette stem (same table as tools/palette-gen)
ALIAS = {"크루": "크루세이더", "페코페코_크루": "구페코크루세이더", "검사페코": "페코검사", "어새신": "어세신"}
SCALE = 2
CELL = (64, 104)
LABEL_W = 150
HEADER_H = 22


def read_spr_image(data: bytes, index: int) -> tuple[int, int, bytes]:
    if data[:2] != b"SP":
        raise ValueError("not an SPR file")
    minor, major = data[2], data[3]
    version = major * 10 + minor
    pal_count = struct.unpack_from("<H", data, 4)[0]
    pos = 8 if version >= 20 else 6
    for current in range(pal_count):
        width, height = struct.unpack_from("<HH", data, pos)
        pos += 4
        if version >= 21:
            size = struct.unpack_from("<H", data, pos)[0]
            pos += 2
            raw = data[pos : pos + size]
            pos += size
            if current == index:
                pixels = bytearray()
                i = 0
                while i < len(raw):
                    value = raw[i]
                    if value == 0:
                        pixels.extend(b"\x00" * raw[i + 1])
                        i += 2
                    else:
                        pixels.append(value)
                        i += 1
                return width, height, bytes(pixels[: width * height])
        else:
            if current == index:
                return width, height, data[pos : pos + width * height]
            pos += width * height
    raise IndexError(index)


def sprite_for(stem: bytes, sprites: Grf) -> bytes | None:
    label = policy.stem_label(stem)
    name, _, gender = label.rpartition("_")
    for candidate in (name, ALIAS.get(name)):
        if not candidate:
            continue
        path = SPRITE_DIR + f"{gender}\\{candidate}_{gender}.spr".encode("cp949")
        if path in sprites.entries:
            return sprites.read(path)
    return None


def draw(width: int, height: int, pixels: bytes, palette: bytes) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    image.putdata(
        [
            (0, 0, 0, 0) if p == 0 else (palette[p * 4], palette[p * 4 + 1], palette[p * 4 + 2], 255)
            for p in pixels
        ]
    )
    return image.resize((width * SCALE, height * SCALE), Image.NEAREST)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out")
    parser.add_argument("--compare", help="older midnight.grf to show beside the current one")
    parser.add_argument("--slots", default="0,1,2,3,4,12,13,14,15")
    parser.add_argument("--target", type=Path, default=policy.TARGET, help="archive to render (default midnight.grf)")
    parser.add_argument("--only", help="comma-separated stems to include, e.g. 검사_남,어세신_여")
    args = parser.parse_args()
    slots = [int(s) for s in args.slots.split(",")]

    current = policy.read_members(args.target)
    older = policy.read_members(Path(args.compare)) if args.compare else None
    base = Grf(policy.BASE)

    def palette(members: dict[bytes, bytes], stem: bytes, slot: int) -> bytes | None:
        name = policy.key(stem, slot)
        if name in members:
            return members[name]
        return base.read(name) if name in base.entries else None

    columns: list[tuple[str, dict[bytes, bytes], int]] = []
    for slot in slots:
        if older is not None and slot >= 12:
            columns.append((f"{slot} old", older, slot))
            columns.append((f"{slot} new", current, slot))
        else:
            columns.append((str(slot), current, slot))

    stems = sorted(s for s, sl in policy.custom_stems(current).items() if policy.SIGNATURE_SLOT in sl)
    if args.only:
        wanted = set(args.only.split(","))
        stems = [s for s in stems if policy.stem_label(s) in wanted]
    sheet = Image.new("RGB", (LABEL_W + CELL[0] * len(columns), HEADER_H + CELL[1] * len(stems)), (58, 60, 66))
    pen = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("malgun.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
    for col, (title, _members, _slot) in enumerate(columns):
        pen.text((LABEL_W + col * CELL[0] + 4, 4), title, fill=(230, 230, 230), font=font)
    missing = []
    for row, stem in enumerate(stems):
        top = HEADER_H + row * CELL[1]
        pen.text((6, top + CELL[1] // 2 - 8), policy.stem_label(stem), fill=(230, 230, 230), font=font)
        spr = sprite_for(stem, base)
        if spr is None:
            missing.append(policy.stem_label(stem))
            continue
        width, height, pixels = read_spr_image(spr, 0)
        for col, (_title, members, slot) in enumerate(columns):
            pal = palette(members, stem, slot)
            if pal is None:
                continue
            tile = draw(width, height, pixels, pal)
            tile.thumbnail(CELL)
            x = LABEL_W + col * CELL[0] + (CELL[0] - tile.width) // 2
            y = top + (CELL[1] - tile.height) // 2
            sheet.paste(tile, (x, y), tile)
    base.close()
    sheet.save(args.out)
    print(f"wrote {args.out}: {len(stems)} rows x {len(columns)} columns")
    if missing:
        print("no sprite for:", ", ".join(missing))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(main())
