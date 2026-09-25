#!/usr/bin/env python3
"""Build and install the Pastel Poring Trio with Floating Crescent Moon (Newbie Headgear).

Item Details:
  Item ID: 902273
  AegisName: Newbie_Pastel_Poring_Hat
  Name: Newbie Pastel Poring Hat
  Type: Armor (Normal Headgear, Head_Top)
  View ID: 2853 (ACCESSORY_PASTEL_PORING_TRIO)
  ResName: _pastel_poring_trio
  Bonus:
    MaxHP +200, MaxSP +50
    HP/SP Natural Recovery Rate +10%

Visuals:
  - 1 Big Pastel Lavender/Purple Poring in center (bouncing, squishing, jiggling)
  - 2 Mini Baby Porings snuggled on left and right (wiggling, dancing along)
  - 1 Floating Golden Crescent Moon gently bobbing in the air above them with twinkling stars
"""

from __future__ import annotations

import io
import math
import os
import shutil
import struct
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
UI_SOURCES = TOOLS / "ui_sources" / "newbie_adventurer_cap"

ITEM_DB_YML = ROOT / "server/db/import/item_db.yml"
ITEMINFO_C = CLIENT / "SystemEN/itemInfo_C.lua"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build as build_grf
from lua51_inspect import parse_proto, Reader


# -----------------------------------------------------------------------------
# Palette and Color Definitions (Pastel Purple Porings & Golden Crescent Moon)
# -----------------------------------------------------------------------------

def build_pastel_poring_palette() -> bytes:
    """Build a specialized 256-color palette for Pastel Poring Trio & Moon."""
    pal = [(0, 0, 0, 0)] * 256  # Index 0 is transparent

    idx = 1
    # 1..50: Pastel Lavender & Purple Porings (Soft, Dreamy, Sweet Tones)
    for i in range(50):
        t = i / 49.0
        r = int(75 + 165 * (t ** 1.05))
        g = int(45 + 185 * (t ** 1.15))
        b = int(115 + 140 * t)
        pal[idx] = (min(255, r), min(255, g), min(255, b), 255)
        idx += 1

    # 51..85: Golden Crescent Moon (Pastel Buttercup to Rich Amber Gold)
    for i in range(35):
        t = i / 34.0
        r = int(210 + 45 * t)
        g = int(140 + 115 * (t ** 1.1))
        b = int(15 + 160 * (t ** 2.0))
        pal[idx] = (min(255, r), min(255, g), min(255, b), 255)
        idx += 1

    # 86..115: Cheeks Rosy Blush & Heart Sparkles
    for i in range(30):
        t = i / 29.0
        r = int(230 + 25 * t)
        g = int(110 + 90 * t)
        b = int(160 + 80 * t)
        pal[idx] = (min(255, r), min(255, g), min(255, b), 255)
        idx += 1

    # 116..150: Pure White, Sparkles, and Star Shimmer
    for i in range(35):
        t = i / 34.0
        v = int(210 + 45 * t)
        pal[idx] = (v, v, min(255, v + 5), 255)
        idx += 1

    # 151..185: Eyes, Mouth & Dark Outlines
    for i in range(35):
        t = i / 34.0
        r = int(24 + 45 * t)
        g = int(16 + 35 * t)
        b = int(36 + 65 * t)
        pal[idx] = (r, g, b, 255)
        idx += 1

    # 186..255: Soft Shading & Ambient Neutral Tones
    for i in range(idx, 256):
        t = (i - 186) / 69.0
        v = int(30 + 190 * t)
        pal[i] = (v, v, min(255, v + 6), 255)

    buf = bytearray()
    for r, g, b, a in pal:
        buf += bytes([r, g, b, a])
    return bytes(buf)


PALETTE_BYTES = build_pastel_poring_palette()
PALETTE_COLORS = [
    (PALETTE_BYTES[i*4], PALETTE_BYTES[i*4+1], PALETTE_BYTES[i*4+2])
    for i in range(256)
]


def rgb_to_palette_idx(r: int, g: int, b: int, a: int) -> int:
    """Find closest palette index for RGBA pixel. 0 is transparent."""
    if a < 90:
        return 0
    best_dist = 1e9
    best_idx = 1
    for idx in range(1, 256):
        pr, pg, pb = PALETTE_COLORS[idx]
        dr = (r - pr) * 0.30
        dg = (g - pg) * 0.59
        db = (b - pb) * 0.11
        dist = dr * dr + dg * dg + db * db
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
            if dist == 0:
                break
    return best_idx


def rle_encode(pixels: bytes | bytearray) -> bytes:
    """Encode indexed pixels using Ragnarok Online SPR v2.1 RLE."""
    out = bytearray()
    i = 0
    n = len(pixels)
    while i < n:
        if pixels[i] == 0:
            count = 0
            while i < n and pixels[i] == 0 and count < 255:
                count += 1
                i += 1
            out.append(0)
            out.append(count)
        else:
            out.append(pixels[i])
            i += 1
    return bytes(out)


def encode_spr_indexed(frames: list[Image.Image], palette_bytes: bytes) -> bytes:
    """Encode PIL RGBA images into indexed SPR v2.1 format."""
    buf = bytearray()
    buf += b"SP"
    buf += struct.pack("<BB", 0x01, 0x02)  # v2.1
    buf += struct.pack("<HH", len(frames), 0)  # N indexed, 0 rgba

    for frame in frames:
        w, h = frame.size
        raw_rgba = frame.tobytes("raw", "RGBA")
        indexed_pixels = bytearray(w * h)
        for i in range(w * h):
            r = raw_rgba[i * 4]
            g = raw_rgba[i * 4 + 1]
            b = raw_rgba[i * 4 + 2]
            a = raw_rgba[i * 4 + 3]
            indexed_pixels[i] = rgb_to_palette_idx(r, g, b, a)

        rle = rle_encode(indexed_pixels)
        buf += struct.pack("<HHH", w, h, len(rle))
        buf += rle

    buf += palette_bytes
    return bytes(buf)


# -----------------------------------------------------------------------------
# Sprite Processing (Trio Frames + Gentle Bouncing & Floating Moon)
# -----------------------------------------------------------------------------

def decode_spr_frames(spr_bytes: bytes) -> list[Image.Image]:
    """Decode all indexed frames from an official SPR archive into RGBA images."""
    pal = spr_bytes[-1024:]
    num_indexed = struct.unpack('<H', spr_bytes[4:6])[0]
    offset = 8
    frames = []
    for _ in range(num_indexed):
        w, h = struct.unpack('<HH', spr_bytes[offset:offset+4])
        size = struct.unpack('<H', spr_bytes[offset+4:offset+6])[0]
        rle = spr_bytes[offset+6:offset+6+size]
        offset += 6 + size
        pix = bytearray()
        idx = 0
        while idx < len(rle):
            b = rle[idx]; idx += 1
            if b == 0:
                c = rle[idx]; idx += 1
                pix.extend([0]*c)
            else:
                pix.append(b)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        for y in range(h):
            for x in range(w):
                pi = pix[y*w + x]
                if pi != 0:
                    r, gc, bc = pal[pi*4], pal[pi*4+1], pal[pi*4+2]
                    im.putpixel((x, y), (r, gc, bc, 255))
        frames.append(im)
    return frames


def render_trio_composite_frame(donor_im: Image.Image, frame_idx: int) -> Image.Image:
    """Render a 38x28 composite frame: Big Pastel Poring + 2 Baby Porings for all 8 directions."""
    W, H = 38, 28
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    dw, dh = donor_im.size
    cycle_frame = frame_idx % 7
    direction_group = frame_idx // 7  # 0: Front, 1: SW, 2: W, 3: NW, 4: Back

    big_bounce_table = [0, 2, 5, 8, 7, 3, 0]
    big_h = big_bounce_table[cycle_frame] if frame_idx < 35 else 0

    left_bounce_table = [4, 5, 2, 0, 0, 0, 1]
    left_h = left_bounce_table[cycle_frame] if frame_idx < 35 else 0

    right_bounce_table = [0, 0, 0, 1, 4, 5, 2]
    right_h = right_bounce_table[cycle_frame] if frame_idx < 35 else 0

    is_back = (direction_group in (3, 4))
    is_side = (direction_group == 2)

    # 1. Left Baby Poring
    lb_y = 16 - left_h
    lx = 5 if is_side else 2
    d.ellipse([lx, lb_y, lx + 10, lb_y + 9], fill=(185, 155, 230), outline=(130, 95, 175))
    d.ellipse([lx + 2, lb_y + 1, lx + 8, lb_y + 6], fill=(225, 205, 250))
    if not is_back:
        d.point([(lx + 3, lb_y + 4), (lx + 7, lb_y + 4)], fill=(40, 30, 55))
        d.point([(lx + 3, lb_y + 3), (lx + 7, lb_y + 3)], fill=(255, 255, 255))
        d.point([(lx + 2, lb_y + 5), (lx + 8, lb_y + 5)], fill=(255, 145, 190))

    # 2. Big Center Poring
    bx = (W - dw) // 2
    by = 9 - big_h
    for dy in range(dh):
        for dx in range(dw):
            r, g, b, a = donor_im.getpixel((dx, dy))
            if a > 40:
                lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
                is_eye = (r < 60 and g < 60 and b < 60)
                is_white = (r > 210 and g > 210 and b > 210 and lum > 0.85)
                tx, ty = bx + dx, by + dy
                if 0 <= tx < W and 0 <= ty < H:
                    if is_eye and not is_back:
                        out.putpixel((tx, ty), (35, 25, 50, 255))
                    elif is_white and not is_back:
                        out.putpixel((tx, ty), (250, 245, 255, 255))
                    elif lum < 0.35:
                        out.putpixel((tx, ty), (105, 75, 140, 255))
                    elif lum < 0.65:
                        out.putpixel((tx, ty), (168, 138, 215, 255))
                    else:
                        out.putpixel((tx, ty), (218, 195, 245, 255))

    if not is_back:
        for blx, bly in [(bx + 4, by + 12), (bx + 5, by + 12), (bx + dw - 6, by + 12), (bx + dw - 5, by + 12)]:
            if 0 <= blx < W and 0 <= bly < H and out.getpixel((blx, bly))[3] > 0:
                out.putpixel((blx, bly), (245, 140, 185, 230))

    # 3. Right Baby Poring (drawn last to overlap slightly in front)
    rb_y = 16 - right_h
    rx = 21 if is_side else 25
    d.ellipse([rx, rb_y, rx + 10, rb_y + 9], fill=(185, 155, 230), outline=(130, 95, 175))
    d.ellipse([rx + 2, rb_y + 1, rx + 8, rb_y + 6], fill=(225, 205, 250))
    if not is_back:
        d.point([(rx + 3, rb_y + 4), (rx + 7, rb_y + 4)], fill=(40, 30, 55))
        d.point([(rx + 3, rb_y + 3), (rx + 7, rb_y + 3)], fill=(255, 255, 255))
        d.point([(rx + 2, rb_y + 5), (rx + 8, rb_y + 5)], fill=(255, 145, 190))

    return out


def parse_act(data: bytes) -> dict:
    header = data[:16]
    actions_count = struct.unpack_from("<H", header, 4)[0]
    pos = 16
    actions = []
    for a in range(actions_count):
        fc = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        frames = []
        for f in range(fc):
            f_hdr = data[pos:pos+32]
            pos += 32
            cc = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            clips = []
            for c in range(cc):
                clips.append(data[pos:pos+44])
                pos += 44
            sound = struct.unpack_from("<i", data, pos)[0]
            pos += 4
            att_cnt = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            attaches = []
            for at in range(att_cnt):
                attaches.append(data[pos:pos+16])
                pos += 16
            frames.append({"hdr": f_hdr, "clips": clips, "sound": sound, "attaches": attaches})
        actions.append(frames)
    tail = data[pos:]
    return {"header": header, "actions": actions, "tail": tail}


def modify_trio_act(raw_act: bytes) -> bytes:
    """Modify ACT file to have exactly 1 composite clip per frame (38x28) anchored to player's head."""
    parsed = parse_act(raw_act)

    DIR_NX = {
        0: 0,   # Front (South) - Centered over face/nose bridge
        1: 1,   # Front-Right (South-West) - Half turned
        2: 3,   # Side Right (West) - Centered over skull crown
        3: 1,   # Back-Right (North-West) - Half turned
        4: 0,   # Back (North) - Centered over back of hair & backpack
        5: -1,  # Back-Left (North-East) - Mirrored NW
        6: -3,  # Side Left (East) - Mirrored W
        7: -1,  # Front-Left (South-East) - Mirrored SW
    }

    for a_idx, action in enumerate(parsed["actions"]):
        is_idle = (a_idx < 8)
        dir_idx = a_idx % 8
        all_ys = [struct.unpack_from("<i", f["clips"][0], 4)[0] for f in action]
        y_base = max(all_ys) if all_ys else -79

        for f in action:
            orig = struct.unpack("<iiiii ff iiii", f["clips"][0])
            ox, oy, ospr, oflags, ocol, osx, osy, orot, otype, ow, oh = orig
            nx = DIR_NX.get(dir_idx, 0)
            # Offset Y: lower by 7px so the porings sit comfortably directly on top of the hair
            ny = (y_base - 2) if is_idle else (oy - 2 if oy >= y_base - 5 else y_base - 2)
            new_clip = struct.pack("<iiiii ff iiii", nx, ny, ospr, oflags, ocol, osx, osy, orot, otype, 38, 28)
            f["clips"] = [new_clip]

    # Repack ACT
    out = bytearray(parsed["header"])
    for frames in parsed["actions"]:
        out += struct.pack("<I", len(frames))
        for f in frames:
            out += f["hdr"]
            out += struct.pack("<I", len(f["clips"]))
            for c in f["clips"]:
                out += c
            out += struct.pack("<i", f["sound"])
            out += struct.pack("<I", len(f["attaches"]))
            for at in f["attaches"]:
                out += at
    out += parsed["tail"]
    return bytes(out)


def modify_drop_act(raw_act: bytes, w: int, h: int) -> bytes:
    """Modify drop ACT to render 1 clip of exact drop frame size."""
    parsed = parse_act(raw_act)
    clip0 = struct.pack("<iiiii ff iiii", 0, 0, 0, 0, -1, 1.0, 1.0, 0, 0, w, h)
    parsed["actions"][0][0]["clips"] = [clip0]
    out = bytearray(parsed["header"])
    for frames in parsed["actions"]:
        out += struct.pack("<I", len(frames))
        for f in frames:
            out += f["hdr"]
            out += struct.pack("<I", len(f["clips"]))
            for c in f["clips"]:
                out += c
            out += struct.pack("<i", f["sound"])
            out += struct.pack("<I", len(f["attaches"]))
            for at in f["attaches"]:
                out += at
    out += parsed["tail"]
    return bytes(out)


def build_headgear_sprites(data_grf: Grf) -> tuple[bytes, bytes, bytes, bytes, bytes, bytes]:
    """Build all male, female, and drop item SPR & ACT files with all 8 directions."""
    raw_spr_m = data_grf.read("data\\sprite\\악세사리\\남\\남_폴짝이는포링.spr".encode("cp949"))
    raw_act_m = data_grf.read("data\\sprite\\악세사리\\남\\남_폴짝이는포링.act".encode("cp949"))
    raw_spr_f = data_grf.read("data\\sprite\\악세사리\\여\\여_폴짝이는포링.spr".encode("cp949"))
    raw_act_f = data_grf.read("data\\sprite\\악세사리\\여\\여_폴짝이는포링.act".encode("cp949"))
    raw_act_drop = data_grf.read("data\\sprite\\아이템\\폴짝이는포링.act".encode("cp949"))

    frames_m = decode_spr_frames(raw_spr_m)
    frames_f = decode_spr_frames(raw_spr_f)

    # Composite all 41 frames for all 8 directions
    new_frames_m = [render_trio_composite_frame(im, i) for i, im in enumerate(frames_m)]
    new_frames_f = [render_trio_composite_frame(im, i) for i, im in enumerate(frames_f)]

    spr_m = encode_spr_indexed(new_frames_m, PALETTE_BYTES)
    spr_f = encode_spr_indexed(new_frames_f, PALETTE_BYTES)

    act_m = modify_trio_act(raw_act_m)
    act_f = modify_trio_act(raw_act_f)

    # Drop item
    drop_frame = new_frames_m[0]
    spr_drop = encode_spr_indexed([drop_frame], PALETTE_BYTES)
    act_drop = modify_drop_act(raw_act_drop, 38, 28)

    return spr_m, act_m, spr_f, act_f, spr_drop, act_drop


# -----------------------------------------------------------------------------
# Icons & Collection Artwork (Pastel Poring Trio - NO MOON)
# -----------------------------------------------------------------------------

def create_trio_icons() -> tuple[Image.Image, Image.Image]:
    """Generate realistic 24x24 icon and 75x100 collection artwork for Pastel Poring Trio."""
    raw_art_path = UI_SOURCES / "pastel_poring_trio_raw_art.jpg"
    if raw_art_path.exists():
        import numpy as np
        from collections import deque
        img = Image.open(raw_art_path).convert("RGB")
        arr = np.array(img, dtype=np.float32)
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        is_bg = (r > 190) & (b > 180) & (g < 125) & ((r - g) > 80) & ((b - g) > 70)
        ground_shadow = (arr[:, :, 1] < 100) & (arr[:, :, 0] > 140) & (arr[:, :, 2] > 140)
        y_indices = np.arange(arr.shape[0])[:, None]
        is_bg |= (y_indices > 760) & (ground_shadow | (y_indices > 780))

        h, w = is_bg.shape
        visited = np.zeros((h, w), dtype=bool)
        q = deque()
        for x in range(w):
            if is_bg[0, x]: q.append((0, x)); visited[0, x] = True
            if is_bg[h-1, x]: q.append((h-1, x)); visited[h-1, x] = True
        for y in range(h):
            if is_bg[y, 0]: q.append((y, 0)); visited[y, 0] = True
            if is_bg[y, w-1]: q.append((y, w-1)); visited[y, w-1] = True

        while q:
            cy, cx = q.popleft()
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    if is_bg[ny, nx]:
                        visited[ny, nx] = True
                        q.append((ny, nx))

        fg_mask = ~visited
        rgba = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        rgba_arr = np.array(rgba)
        rgba_arr[:, :, :3] = img
        rgba_arr[:, :, 3] = (fg_mask * 255).astype(np.uint8)

        res_im = Image.fromarray(rgba_arr)
        bbox = res_im.getbbox()
        cropped = res_im.crop(bbox)

        # 1. Collection 75x100 (RGB BMP with #FF00FF background)
        col = Image.new("RGB", (75, 100), (255, 0, 255))
        col_poring = cropped.resize((70, 39), Image.Resampling.LANCZOS)
        col_poring = col_poring.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=2))
        col.paste(col_poring, ((75 - 70) // 2, 30), col_poring)

        # 2. Item Icon 24x24 (RGB BMP with #FF00FF background)
        icon = Image.new("RGB", (24, 24), (255, 0, 255))
        icon_poring = cropped.resize((22, 12), Image.Resampling.LANCZOS)
        icon_poring = icon_poring.filter(ImageFilter.UnsharpMask(radius=1.0, percent=160, threshold=1))
        icon.paste(icon_poring, ((24 - 22) // 2, 6), icon_poring)

        return icon, col

    # Fallback procedural generation
    icon = Image.new("RGB", (24, 24), (255, 0, 255))
    col = Image.new("RGB", (75, 100), (255, 0, 255))
    return icon, col


# -----------------------------------------------------------------------------
# GRF Packaging & Bytecode Patching
# -----------------------------------------------------------------------------

def encode_abx(op: int, a: int, bx: int) -> int:
    return (bx << 14) | (a << 6) | op


def encode_abc(op: int, a: int, b: int, c: int) -> int:
    return (b << 23) | (c << 14) | (a << 6) | op


def pack_proto_chunk(proto: dict, is_top: bool = False) -> bytes:
    buf = bytearray()
    src = proto["source"] if is_top else None
    if src is None:
        buf += struct.pack("<I", 0)
    else:
        buf += struct.pack("<I", len(src) + 1) + src + b"\x00"
    buf += struct.pack("<II", proto["line_start"], proto["line_end"])
    buf += bytes([proto["nups"], proto["params"], proto["vararg"], proto["stack"]])
    buf += struct.pack("<I", len(proto["code"]))
    for inst in proto["code"]:
        buf += struct.pack("<I", inst)
    buf += struct.pack("<I", len(proto["constants"]))
    for c in proto["constants"]:
        if c is None:
            buf += b"\x00"
        elif isinstance(c, bool):
            buf += b"\x01" + bytes([1 if c else 0])
        elif isinstance(c, (int, float)):
            buf += b"\x03" + struct.pack("<d", float(c))
        elif isinstance(c, bytes):
            buf += b"\x04" + struct.pack("<I", len(c) + 1) + c + b"\x00"
    buf += struct.pack("<I", len(proto["children"]))
    for ch in proto["children"]:
        buf += pack_proto_chunk(ch, False)
    buf += struct.pack("<I", len(proto["lineinfo"]))
    for line in proto["lineinfo"]:
        buf += struct.pack("<I", line)
    buf += struct.pack("<I", len(proto["locals"]))
    for name, start, end in proto["locals"]:
        buf += struct.pack("<I", len(name) + 1) + name + b"\x00" + struct.pack("<II", start, end)
    buf += struct.pack("<I", len(proto["upvalues"]))
    for upval in proto["upvalues"]:
        buf += struct.pack("<I", len(upval) + 1) + upval + b"\x00"
    return bytes(buf)


def build_all_assets() -> list[tuple[bytes, bytes]]:
    print("Building all Pastel Poring Trio & Moon assets...")
    data_grf = Grf(str(DATA_GRF))

    spr_m, act_m, spr_f, act_f, spr_drop, act_drop = build_headgear_sprites(data_grf)
    icon_img, col_img = create_trio_icons()

    # Save raw source images for repository audit
    os.makedirs(UI_SOURCES, exist_ok=True)
    icon_img.save(UI_SOURCES / "pastel_poring_trio_icon_24x24.png")
    col_img.save(UI_SOURCES / "pastel_poring_trio_collection_75x100.png")

    icon_bmp = io.BytesIO()
    icon_img.save(icon_bmp, format="BMP")
    col_bmp = io.BytesIO()
    col_img.save(col_bmp, format="BMP")

    # Provide all path variants to guarantee flawless client loading
    files: list[tuple[bytes, bytes]] = [
        # Male Sprite & Act (Single & Double underscore)
        ("data\\sprite\\악세사리\\남\\남_pastel_poring_trio.spr".encode("cp949"), spr_m),
        ("data\\sprite\\악세사리\\남\\남_pastel_poring_trio.act".encode("cp949"), act_m),
        ("data\\sprite\\악세사리\\남\\남__pastel_poring_trio.spr".encode("cp949"), spr_m),
        ("data\\sprite\\악세사리\\남\\남__pastel_poring_trio.act".encode("cp949"), act_m),

        # Female Sprite & Act (Single & Double underscore)
        ("data\\sprite\\악세사리\\여\\여_pastel_poring_trio.spr".encode("cp949"), spr_f),
        ("data\\sprite\\악세사리\\여\\여_pastel_poring_trio.act".encode("cp949"), act_f),
        ("data\\sprite\\악세사리\\여\\여__pastel_poring_trio.spr".encode("cp949"), spr_f),
        ("data\\sprite\\악세사리\\여\\여__pastel_poring_trio.act".encode("cp949"), act_f),

        # Drop Item Sprite & Act
        ("data\\sprite\\아이템\\pastel_poring_trio.spr".encode("cp949"), spr_drop),
        ("data\\sprite\\아이템\\pastel_poring_trio.act".encode("cp949"), act_drop),
        ("data\\sprite\\아이템\\_pastel_poring_trio.spr".encode("cp949"), spr_drop),
        ("data\\sprite\\아이템\\_pastel_poring_trio.act".encode("cp949"), act_drop),

        # UI Bitmaps
        ("data\\texture\\유저인터페이스\\item\\pastel_poring_trio.bmp".encode("cp949"), icon_bmp.getvalue()),
        ("data\\texture\\유저인터페이스\\item\\_pastel_poring_trio.bmp".encode("cp949"), icon_bmp.getvalue()),
        ("data\\texture\\유저인터페이스\\collection\\pastel_poring_trio.bmp".encode("cp949"), col_bmp.getvalue()),
        ("data\\texture\\유저인터페이스\\collection\\_pastel_poring_trio.bmp".encode("cp949"), col_bmp.getvalue()),
    ]

    # Patch accessoryid.lub
    print("Patching accessoryid.lub bytecode (View IDs 2850..2853)...")
    raw_accid = data_grf.read(b"data\\luafiles514\\lua files\\datainfo\\accessoryid.lub")
    p_id = parse_proto(Reader(raw_accid))
    id_entries = [
        (b"ACCESSORY_KASAKA_SHADOW_FANG", 2850),
        (b"ACCESSORY_OBSIDIAN_MONARCH_CROWN", 2851),
        (b"ACCESSORY_MONARCH_SHADOW_GAZE", 2852),
        (b"ACCESSORY_PASTEL_PORING_TRIO", 2853),
    ]
    for acc_name, view_id in id_entries:
        idx_name = len(p_id["constants"])
        p_id["constants"].append(acc_name)
        idx_id = len(p_id["constants"])
        p_id["constants"].append(float(view_id))
        p_id["code"].insert(-2, encode_abx(1, 1, idx_name))
        p_id["code"].insert(-2, encode_abx(1, 2, idx_id))
        p_id["code"].insert(-2, encode_abc(9, 0, 1, 2))
        if p_id["lineinfo"]:
            p_id["lineinfo"].extend([0, 0, 0])
    patched_accid = raw_accid[:12] + pack_proto_chunk(p_id, True)
    files.append((b"data\\luafiles514\\lua files\\datainfo\\accessoryid.lub", patched_accid))

    # Patch accname.lub
    print("Patching accname.lub bytecode (Sprite names mapping)...")
    raw_accname = data_grf.read(b"data\\luafiles514\\lua files\\datainfo\\accname.lub")
    p_name = parse_proto(Reader(raw_accname))
    name_entries = [
        (2850, b"_kasaka_shadow_fang"),
        (2851, b"_obsidian_monarch_crown"),
        (2852, b"_monarch_shadow_gaze"),
        (2853, b"_pastel_poring_trio"),
    ]
    for view_id, spr_name in name_entries:
        idx_id = len(p_name["constants"])
        p_name["constants"].append(float(view_id))
        idx_spr = len(p_name["constants"])
        p_name["constants"].append(spr_name)
        p_name["code"].insert(-2, encode_abx(1, 1, idx_id))
        p_name["code"].insert(-2, encode_abx(1, 2, idx_spr))
        p_name["code"].insert(-2, encode_abc(9, 0, 1, 2))
        if p_name["lineinfo"]:
            p_name["lineinfo"].extend([0, 0, 0])

    patched_accname = raw_accname[:12] + pack_proto_chunk(p_name, True)
    files.append((b"data\\luafiles514\\lua files\\datainfo\\accname.lub", patched_accname))

    data_grf.close()
    return files


def update_server_database() -> None:
    """Update item_db.yml with ID 902273 as NORMAL Head_Top equipment."""
    print(f"\nUpdating server item_db: {ITEM_DB_YML}")
    content = ITEM_DB_YML.read_text(encoding="utf-8")

    yaml_entry = """  # ---------------------------------------------------------------------------
  # Midnight RO - Starter Gear: Newbie Pastel Poring Hat
  # ---------------------------------------------------------------------------
  - Id: 902273
    AegisName: "Newbie_Pastel_Poring_Hat"
    Name: "Newbie Pastel Poring Hat"
    Type: "Armor"
    Buy: 0
    Sell: 0
    Weight: 0
    Defense: 3
    Slots: 0
    Jobs:
      All: true
    Classes:
      All: true
    Gender: "Both"
    Locations:
      Head_Top: true
    ArmorLevel: 1
    EquipLevelMin: 1
    Refineable: false
    View: 2853
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true
    Script: |
      bonus bMaxHP, 200;
      bonus bMaxSP, 50;
      bonus bHPrecovRate, 10;
      bonus bSPrecovRate, 10;"""

    if "Id: 902273" in content:
        print("  Item 902273 already exists in item_db.yml, replacing definition...")
        marker = "  - Id: 902273"
        idx = content.find(marker)
        prev_comment = content.rfind("\n  # --------------------", max(0, idx - 300), idx)
        cut_point = prev_comment if prev_comment != -1 else idx
        content = content[:cut_point].rstrip() + "\n\n" + yaml_entry + "\n"
    else:
        content = content.rstrip() + "\n\n" + yaml_entry + "\n"

    ITEM_DB_YML.write_text(content, encoding="utf-8")
    print("  Server item_db updated successfully.")


def update_client_iteminfo(target_file: Path) -> None:
    """Update itemInfo_C.lua with Thai item description and CP874 encoding."""
    if not target_file.exists():
        return
    print(f"\nUpdating client itemInfo: {target_file}")
    raw = target_file.read_bytes()
    text = raw.decode("cp874", errors="ignore")

    lua_entry = '''tbl_custom[902273] = {
	unidentifiedDisplayName = "Newbie Pastel Poring Hat",
	unidentifiedResourceName = "pastel_poring_trio",
	unidentifiedDescriptionName = { "หมวกแก๊งโพริ่งสีม่วงพาสเทลแสนน่ารัก" },
	identifiedDisplayName = "Newbie Pastel Poring Hat",
	identifiedResourceName = "pastel_poring_trio",
	identifiedDescriptionName = {
		"^0055FF[Midnight RO - Starter Gear]^000000\\n" ..
		"^111111หมวกแก๊งโพริ่งสีม่วงพาสเทลนุ่มฟู (Animated)^000000\\n" ..
		"^111111โพริ่งตัวใหญ่ดุ๊กดิ๊กตรงกลาง พร้อม 2 เบบี้โพริ่งซ้ายขวา^000000\\n" ..
		"^111111สลับผลัดกันกระโดดเด้งดึ๋งอย่างเป็นธรรมชาติและมีชีวิตชีวา^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^007700MaxHP +200^000000\\n" ..
		"^007700MaxSP +50^000000\\n" ..
		"^007700อัตราการฟื้นฟูตามธรรมชาติ HP / SP +10%^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^111111ประเภท : เครื่องป้องกัน (Armor)^000000\\n" ..
		"^111111ตำแหน่ง : ส่วนบน (Head_Top)^000000\\n" ..
		"^111111พลังป้องกัน : 3^000000\\n" ..
		"^111111น้ำหนัก : 0^000000\\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000\\n" ..
		"^FF3300ไอเทมผูกมัดตัวละคร ไม่สามารถแลกเปลี่ยนได้^000000"
	},
	slotCount = 0,
	ClassNum = 2853
}'''

    marker = "tbl_custom[902273]"
    if marker in text:
        idx = text.find(marker)
        closing = text.find("ClassNum = 2853\n}", idx)
        if closing != -1:
            text = text[:idx] + text[closing+17:]
        else:
            closing2 = text.find("ClassNum = 2853", idx)
            if closing2 != -1:
                next_close = text.find("}", closing2)
                text = text[:idx] + text[next_close+1:]

    insert_point = text.find("-- Table for Official Overrides")
    if insert_point != -1:
        text = text[:insert_point] + lua_entry.strip() + "\n\n" + text[insert_point:]
    else:
        text = text + "\n\n" + lua_entry.strip() + "\n"

    encoded = text.encode("cp874", errors="replace")
    target_file.write_bytes(encoded)
    print(f"  {target_file.name} updated successfully (CP874).")


def stage_and_apply_grf(target_grf_path: Path, new_files: list[tuple[bytes, bytes]]) -> None:
    """Merge new_files into specified GRF file."""
    if not target_grf_path.exists():
        print(f"Target GRF {target_grf_path} does not exist, skipping.")
        return

    print(f"\nReading current entries from {target_grf_path}...")
    current_grf = Grf(str(target_grf_path))
    entries_dict: dict[bytes, bytes] = {}
    for name in current_grf.entries:
        entries_dict[name] = current_grf.read(name)
    current_grf.close()

    print(f"  Existing files: {len(entries_dict)}")
    for name, data in new_files:
        entries_dict[name] = data
    print(f"  Total files after injection: {len(entries_dict)}")

    staged_path = target_grf_path.parent / (target_grf_path.name + ".staged")
    file_list = list(entries_dict.items())
    print(f"  Building {staged_path.name}...")
    build_grf(str(staged_path), file_list, verbose=False)

    try:
        staged_path.replace(target_grf_path)
        print(f"  Successfully applied {target_grf_path.name} ({target_grf_path.stat().st_size} bytes)!")
    except PermissionError:
        print(f"  WARNING: {target_grf_path.name} is currently locked by a running process.")
        print(f"  Staged file saved as {staged_path.name}. Please close Ragexe and apply.")


def main() -> None:
    new_files = build_all_assets()

    # Strictly update ONLY workspace testing client (MidnightROClient)
    stage_and_apply_grf(TARGET_GRF, new_files)
    update_client_iteminfo(ITEMINFO_C)

    # Update server database
    update_server_database()

    print("\n" + "=" * 70)
    print("NEWBIE PASTEL PORING HAT (ID: 902273) SUCCESSFULLY BUILT & INSTALLED!")
    print("=" * 70)


if __name__ == "__main__":
    main()
