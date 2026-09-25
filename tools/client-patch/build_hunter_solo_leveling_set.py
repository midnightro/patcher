#!/usr/bin/env python3
"""Build and install the Solo Leveling Shadow Monarch 4-Piece Hunter Rank Costume Set (v3).

Items:
  902269: [Hunter C] Kasaka's Shadow Fang (Costume Lower - Mouth Dagger, View 2850)
  902270: [Hunter B] Obsidian Crown of the Monarch (Costume Upper - Dark Crown, View 2851)
  902271: [Hunter A] Monarch's Shadow Gaze (Costume Middle - Animated Flame Eyes, View 2852)
  902272: [Hunter S] Monarch's Shadow Aura (Costume Garment - Animated Shadow Mist Aura & Soul Fire, Robe View 164)
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
UI_SOURCES = TOOLS / "ui_sources" / "solo_leveling_hunter_set"

ITEM_DB_YML = ROOT / "server/db/import/item_db.yml"
ITEMINFO_C = CLIENT / "SystemEN/itemInfo_C.lua"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build as build_grf
from lua51_inspect import parse_proto, Reader


# -----------------------------------------------------------------------------
# Palette and Color Definitions (Solo Leveling Shadow Monarch Aesthetic)
# -----------------------------------------------------------------------------

def build_shadow_monarch_palette() -> bytes:
    """Build a specialized 256-color palette for Solo Leveling pixel art."""
    pal = [(0, 0, 0, 0)] * 256  # Index 0 is transparent

    idx = 1
    # 1..32: Obsidian / Deep Dark Shades (near-black to cool charcoal slate)
    for i in range(32):
        t = i / 31.0
        r = int(8 + 32 * (t ** 1.3))
        g = int(10 + 36 * (t ** 1.3))
        b = int(18 + 52 * (t ** 1.3))
        pal[idx] = (r, g, b, 255)
        idx += 1

    # 33..80: Luminescent Cyan / Azure / Shadow Electric Blue Glow
    for i in range(48):
        t = i / 47.0
        if t < 0.5:
            st = t / 0.5
            r = int(0 + 10 * st)
            g = int(80 + 120 * st)
            b = int(160 + 95 * st)
        else:
            st = (t - 0.5) / 0.5
            r = int(10 + 245 * (st ** 1.5))
            g = int(200 + 55 * st)
            b = 255
        pal[idx] = (r, g, b, 255)
        idx += 1

    # 81..120: Violet / Purple Shadow Monarch Runes & Accents
    for i in range(40):
        t = i / 39.0
        r = int(70 + 170 * (t ** 1.2))
        g = int(20 + 80 * (t ** 1.5))
        b = int(130 + 125 * t)
        pal[idx] = (r, g, b, 255)
        idx += 1

    # 121..160: Metallic Silver / Dragon Fang Highlights & Steel Greys
    for i in range(40):
        t = i / 39.0
        val = int(50 + 205 * t)
        pal[idx] = (val, min(255, val + 5), min(255, val + 15), 255)
        idx += 1

    # 161..200: Toxic Poison Highlights (Teal/Emerald venom sheen)
    for i in range(40):
        t = i / 39.0
        r = int(0 + 60 * t)
        g = int(160 + 95 * t)
        b = int(180 + 75 * (1.0 - t))
        pal[idx] = (r, g, b, 255)
        idx += 1

    # 201..255: Soft Shadow mist / blended gradients
    for i in range(idx, 256):
        t = (i - 201) / 54.0
        r = int(15 + 40 * t)
        g = int(25 + 60 * t)
        b = int(60 + 120 * t)
        pal[i] = (r, g, b, 255)

    buf = bytearray()
    for r, g, b, a in pal:
        buf += bytes([r, g, b, a])
    return bytes(buf)


PALETTE_BYTES = build_shadow_monarch_palette()
PALETTE_COLORS = [
    (PALETTE_BYTES[i*4], PALETTE_BYTES[i*4+1], PALETTE_BYTES[i*4+2])
    for i in range(256)
]


def rgb_to_palette_idx(r: int, g: int, b: int, a: int) -> int:
    """Find closest palette index for RGBA pixel. 0 is transparent."""
    if a < 110:
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


# -----------------------------------------------------------------------------
# SPR Encoding Helpers
# -----------------------------------------------------------------------------

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


def encode_spr_rgba(frames: list[Image.Image], donor_palette: bytes) -> bytes:
    """Encode RGBA frames into Ragnarok Online SPR v2.1 format (ABGR, vertically flipped)."""
    buf = bytearray()
    buf += b"SP"
    buf += struct.pack("<BB", 0x01, 0x02)  # v2.1
    buf += struct.pack("<HH", 0, len(frames))  # 0 indexed, N rgba frames

    for frame in frames:
        flipped_frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
        w, h = flipped_frame.size
        raw_rgba = flipped_frame.tobytes("raw", "RGBA")
        abgr = bytearray(w * h * 4)
        for i in range(0, len(raw_rgba), 4):
            r, g, b, a = raw_rgba[i], raw_rgba[i + 1], raw_rgba[i + 2], raw_rgba[i + 3]
            abgr[i] = a
            abgr[i + 1] = b
            abgr[i + 2] = g
            abgr[i + 3] = r
        buf += struct.pack("<HH", w, h)
        buf += abgr

    buf += donor_palette if len(donor_palette) == 1024 else bytearray(1024)
    return bytes(buf)


# -----------------------------------------------------------------------------
# 1. Kasaka's Shadow Fang Artwork (Mouth Dagger, View 2850)
# -----------------------------------------------------------------------------

def render_kasaka_dagger_frames() -> list[Image.Image]:
    """Render 9 directional frames for Kasaka's Poison Fang held in mouth.
    
    Solo Leveling Dragon Fang aesthetic matching illustrated card:
    - Sleek curved dragon fang blade in dark bone and obsidian charcoal
    - Razor-thin 1-pixel cyan cutting edge with white-hot glint
    - Dripping venom tip and hooked needle point
    - Wrapped black leather grip with silver serpent wire wrap and bone serpent crossguard
    """
    dims = [
        (25, 8), (21, 8), (14, 8), (8, 6), (5, 3),
        (18, 6), (5, 3), (8, 6), (6, 5)
    ]
    frames = []

    for idx, (w, h) in enumerate(dims):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)

        if idx == 0:
            # Frame 0 (25x8): Front View
            # 1. Wrapped dark leather hilt with engraved silver serpent wire (x=0..6, y=2..4)
            d.point([(0, 3), (0, 4)], fill=(16, 20, 26, 255))
            d.point([(1, 3)], fill=(170, 195, 225, 255))  # Silver claw pommel
            for x in range(2, 7):
                d.point([(x, 3)], fill=(22, 26, 34, 255))
                d.point([(x, 4)], fill=(14, 18, 24, 255))
            d.point([(3, 3), (5, 3)], fill=(160, 185, 215, 255))  # Silver wire wrap

            # 2. Bone serpent crossguard (x=6..8, y=1..5)
            d.line([(7, 1), (7, 5)], fill=(45, 54, 70, 255), width=1)
            d.point([(7, 1), (7, 5)], fill=(160, 185, 215, 255))
            d.point([(6, 2), (8, 2), (6, 4), (8, 4)], fill=(85, 100, 128, 255))
            d.point([(8, 3)], fill=(0, 245, 255, 255))  # Cyan viper eye glint

            # 3. Curved dragon fang body (dark bone / charcoal)
            d.line([(8, 2), (18, 2)], fill=(42, 50, 65, 255), width=1)
            d.line([(19, 3), (22, 3)], fill=(32, 40, 52, 255), width=1)
            d.point([(11, 1), (15, 1), (18, 1)], fill=(75, 90, 115, 255))
            d.point([(12, 1), (16, 1)], fill=(170, 195, 225, 255))  # Razor spine highlight
            d.line([(8, 3), (18, 3)], fill=(24, 28, 38, 255), width=1)

            # 4. Razor-thin 1-pixel cyan cutting edge (lower edge)
            d.line([(8, 4), (20, 4)], fill=(0, 245, 255, 255), width=1)
            d.line([(12, 4), (16, 4)], fill=(240, 255, 255, 255), width=1)  # White-hot glint

            # Hooked fang tip & dripping venom
            d.point([(21, 4), (22, 4)], fill=(0, 245, 255, 255))
            d.point([(23, 4)], fill=(255, 255, 255, 255))
            d.point([(23, 5)], fill=(0, 245, 255, 255))  # Downward hooked tip
            d.point([(22, 6)], fill=(0, 210, 255, 200))  # Venom drop
            d.point([(22, 7)], fill=(0, 180, 255, 140))

        elif idx in (1, 7):
            # South-West / South-East (21x8)
            d.line([(1, 2), (5, 3)], fill=(20, 24, 32, 255), width=2)
            d.point([(3, 2)], fill=(160, 185, 215, 255))
            d.line([(5, 1), (7, 5)], fill=(45, 54, 70, 255), width=1)
            d.line([(7, 3), (16, 5)], fill=(32, 40, 54, 255), width=1)
            d.point([(10, 2), (13, 3)], fill=(60, 72, 95, 255))
            d.line([(7, 4), (17, 5)], fill=(22, 26, 36, 255), width=1)
            d.line([(8, 5), (19, 6)], fill=(0, 245, 255, 255), width=1)
            d.point([(13, 5)], fill=(240, 255, 255, 255))
            d.point([(20, 6)], fill=(245, 255, 255, 255))
            d.point([(19, 7)], fill=(0, 210, 255, 180))

        elif idx in (2, 6):
            # West / East (14x8)
            d.line([(7, 1), (12, 5)], fill=(20, 24, 32, 255), width=2)
            d.point([(6, 2), (7, 3)], fill=(65, 80, 105, 255))
            d.line([(1, 0), (6, 3)], fill=(32, 40, 54, 255), width=1)
            d.line([(0, 1), (5, 4)], fill=(0, 245, 255, 255), width=1)
            d.point([(0, 1)], fill=(240, 255, 255, 255))
            d.point([(0, 2)], fill=(0, 210, 255, 180))

        elif idx in (3, 5):
            # North-West / North-East (8x6)
            d.line([(1, 1), (5, 3)], fill=(20, 24, 32, 255), width=2)
            d.point([(0, 0)], fill=(0, 245, 255, 255))
            d.point([(6, 3)], fill=(160, 185, 220, 255))

        else:
            # North / Back (5x3)
            d.line([(0, 1), (4, 1)], fill=(20, 24, 32, 255), width=1)
            d.point([(2, 1)], fill=(160, 185, 215, 255))

        frames.append(im)

    return frames


# -----------------------------------------------------------------------------
# 2. Obsidian Crown of the Monarch (View 2851) - Realistic High-End Circlet
# -----------------------------------------------------------------------------

def shift_act_clips(raw_act: bytes, dx: int = 0, dy: int = -14) -> bytes:
    """Shift all sprite clips in an ACT v0x0205 archive by (dx, dy)."""
    act = bytearray(raw_act)
    action_count = struct.unpack_from('<H', act, 4)[0]
    pos = 16
    for a in range(action_count):
        f_count = struct.unpack_from('<I', act, pos)[0]
        pos += 4
        for f in range(f_count):
            pos += 32
            c_count = struct.unpack_from('<I', act, pos)[0]
            pos += 4
            for c in range(c_count):
                x, y = struct.unpack_from('<ii', act, pos)
                struct.pack_into('<ii', act, pos, x + dx, y + dy)
                pos += 44
            pos += 4  # sound_index
            att = struct.unpack_from('<I', act, pos)[0]
            pos += 4 + att * 16
    return bytes(act)


def build_obsidian_crown_assets(data_grf: Grf) -> tuple[bytes, bytes, bytes, bytes, bytes]:
    """Build authentic Obsidian Monarch Crown matching the masterpiece illustrated card.
    
    Transforms the official 11-frame 3D circlet geometry into:
    - Elevated by 14 pixels (dy = -14) onto the top hair crest to completely clear the eyes
    - 85-90% Obsidian Black / Blackened Gothic Silver metal
    - Central radiant cyan diamond gem with pure white-hot flare
    """
    raw_circlet_spr = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_s_circlet_of_time.spr")
    pal_circlet = raw_circlet_spr[-1024:]
    offset = 8
    num_indexed = struct.unpack('<H', raw_circlet_spr[4:6])[0]

    frames = []
    for f in range(num_indexed):
        w, h = struct.unpack('<HH', raw_circlet_spr[offset:offset+4])
        offset += 4
        size = struct.unpack('<H', raw_circlet_spr[offset:offset+2])[0]
        offset += 2
        rle = raw_circlet_spr[offset:offset+size]
        offset += size
        pix = bytearray()
        idx = 0
        while idx < len(rle):
            b = rle[idx]; idx += 1
            if b == 0:
                c = rle[idx]; idx += 1
                pix.extend([0]*c)
            else:
                pix.append(b)

        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        cx = w // 2
        for y in range(h):
            for x in range(w):
                pi = pix[y*w + x]
                if pi != 0:
                    r, gc, bc = pal_circlet[pi*4], pal_circlet[pi*4+1], pal_circlet[pi*4+2]
                    # Identify center jewel (red/pink in original circlet)
                    is_center_gem = (r > 140 and gc < 120 and r > gc * 1.3)
                    if is_center_gem:
                        if abs(x - cx) <= 0 and y in (7, 8):
                            im.putpixel((x, y), (240, 255, 255, 255))
                        elif abs(x - cx) <= 1 and 6 <= y <= 10:
                            im.putpixel((x, y), (0, 245, 255, 255))
                        else:
                            im.putpixel((x, y), (0, 160, 230, 255))
                    else:
                        # 85-90% Obsidian Black / Blackened Gothic Silver metal
                        lum = 0.299 * r + 0.587 * gc + 0.114 * bc
                        t = min(1.0, max(0.0, (lum - 35.0) / 200.0))
                        if t < 0.35:
                            k = t / 0.35
                            nr = int(14 * (1 - k) + 26 * k)
                            ng = int(16 * (1 - k) + 30 * k)
                            nb = int(22 * (1 - k) + 40 * k)
                        elif t < 0.75:
                            k = (t - 0.35) / 0.40
                            nr = int(26 * (1 - k) + 55 * k)
                            ng = int(30 * (1 - k) + 64 * k)
                            nb = int(40 * (1 - k) + 82 * k)
                        else:
                            k = (t - 0.75) / 0.25
                            nr = int(55 * (1 - k) + 140 * k)
                            ng = int(64 * (1 - k) + 160 * k)
                            nb = int(82 * (1 - k) + 195 * k)
                        im.putpixel((x, y), (nr, ng, nb, 255))

        frames.append(im)

    spr_crown = encode_spr_indexed(frames, PALETTE_BYTES)
    raw_crown_m = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_s_circlet_of_time.act")
    raw_crown_f = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9_s_circlet_of_time.act")
    act_crown_m = shift_act_clips(raw_crown_m, 0, -6)
    act_crown_f = shift_act_clips(raw_crown_f, 0, -6)
    spr_crown_drop = spr_crown
    act_crown_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\s_circlet_of_time.act")

    return spr_crown, act_crown_m, act_crown_f, spr_crown_drop, act_crown_drop


# -----------------------------------------------------------------------------
# 3. Monarch's Shadow Gaze Artwork (Animated Flame Eyes, View 2852)
# -----------------------------------------------------------------------------

def render_monarch_gaze_frames() -> list[Image.Image]:
    """Render 9 RGBA frames (25x25 each) of Monarch's Shadow Gaze.
    
    Flowing soft spirit flame tails trailing horizontally out to the sides (temples/ears):
    - Dark brow shadow contour above the eyes
    - Intensely radiant cyan-white iris core (opaque & vivid on all skin tones)
    - Positioned at cy=11 to comfortably clear mouth dagger
    - Ethereal, wavy fluttering flame tails sweeping sideways with vibrant saturation
    """
    frames = [Image.new("RGBA", (25, 25), (0, 0, 0, 0)) for _ in range(9)]

    def draw_flowing_eye(im: Image.Image, cx: int, cy: int, stage: int, sdir: int, length_scale: float = 1.0) -> None:
        # 1. Dark Shadow Brow Contour above eye (sharp contrast accentuating the gaze)
        brow_span = 3 if length_scale > 0.8 else 2
        for bx in range(-brow_span, brow_span + 1):
            px = cx + bx
            py = cy - 2
            a = 210 if abs(bx) <= 1 else 110
            if 0 <= px < 25 and 0 <= py < 25:
                im.putpixel((px, py), (14, 10, 22, a))

        # 2. Eye Core (intense, vivid cyan-white flare)
        for dy_c in (-1, 0, 1):
            for dx_c in (-1, 0, 1):
                px = cx + dx_c
                py = cy + dy_c
                if 0 <= px < 25 and 0 <= py < 25:
                    dist = abs(dx_c) + abs(dy_c)
                    if dist == 2:
                        im.putpixel((px, py), (0, 180, 255, 230))
                    elif dist == 1:
                        im.putpixel((px, py), (0, 225, 255, 255))

        # Inner bright halo
        if 0 <= cx + sdir < 25:
            im.putpixel((cx + sdir, cy), (130, 245, 255, 255))
        if 0 <= cy - 1 < 25:
            im.putpixel((cx, cy - 1), (150, 245, 255, 255))

        # Center pure white flare
        im.putpixel((cx, cy), (255, 255, 255, 255))
        if 0 <= cx - sdir < 25:
            im.putpixel((cx - sdir, cy), (240, 255, 255, 255))

        # 3. Soft Flowing Sideways Tail (ออกด้านข้าง พริ้วๆ นุ่มนวล เข้ม คมชัด)
        max_dist = int(round(7.5 * length_scale))
        if stage == 1:
            max_dist = min(8, max_dist + 1)

        # 3 animation stages for undulating silk/spirit tail:
        for d in range(1, max_dist + 1):
            x = cx + sdir * d
            if not (0 <= x < 25):
                continue

            t = d / max_dist  # 0.0 near eye, 1.0 at tail tip
            base_elevation = - (d * 0.15)

            # Flutter wave (undulating silk ribbon):
            if stage == 0:
                wave = math.sin(d * 0.8) * 0.6
            elif stage == 1:
                wave = math.sin(d * 0.8 - 1.2) * 0.75 - (0.4 * (t**1.8))
            else:  # stage 2
                wave = math.sin(d * 0.8 - 2.4) * 0.65

            y_center = cy + base_elevation + wave

            # Opacity gradients (higher minimum alpha for high visibility):
            core_alpha = int(255 * (1.0 - t * 0.35))
            mist_alpha = int(180 * (1.0 - t * 0.55))

            # Evaluate continuous soft profile along Y around y_center:
            for y_cand in range(int(math.floor(y_center - 1.8)), int(math.ceil(y_center + 1.8)) + 1):
                if not (0 <= y_cand < 25):
                    continue
                dist_y = abs(y_cand - y_center)
                if dist_y > 1.5:
                    continue

                thickness = 1.0 - 0.35 * t
                scaled_dist = dist_y / thickness

                if scaled_dist <= 0.7:
                    cr = int(30 * (1 - t) + 80 * t)
                    cg = int(245 * (1 - t * 0.20))
                    cb = 255
                    a = core_alpha
                elif scaled_dist <= 1.4:
                    cr = int(50 * (1 - t) + 140 * t)
                    cg = int(190 * (1 - t) + 80 * t)
                    cb = 255
                    a = mist_alpha
                else:
                    continue

                old = im.getpixel((x, y_cand))
                if a > old[3]:
                    im.putpixel((x, y_cand), (cr, cg, cb, a))
                elif a > 30 and old[3] < 255:
                    na = min(255, old[3] + int(a * 0.4))
                    im.putpixel((x, y_cand), (cr, cg, cb, na))

        # 4. Spirit ember spark at the tail tip (fluttering in the wind)
        tip_d = max_dist
        if stage == 1 and length_scale > 0.8:
            ex = cx + sdir * (tip_d + 1)
            ey = int(round(cy - (tip_d * 0.15) + (math.sin(tip_d * 0.8 - 1.2) * 0.75 - 0.4)))
            if 0 <= ex < 25 and 0 <= ey < 25:
                im.putpixel((ex, ey), (160, 220, 255, 140))
        elif stage == 2 and length_scale > 0.8:
            ex = cx + sdir * (tip_d + 1)
            ey = int(round(cy - (tip_d * 0.15) + (math.sin(tip_d * 0.8 - 2.4) * 0.65)))
            if 0 <= ex < 25 and 0 <= ey < 25:
                im.putpixel((ex, ey), (140, 200, 255, 120))

    # Front facing frames (0, 1, 2) - cy=11 leaves clear space above dagger
    for stage in (0, 1, 2):
        draw_flowing_eye(frames[stage], 8, 11, stage, sdir=-1, length_scale=1.0)
        draw_flowing_eye(frames[stage], 16, 11, stage, sdir=1, length_scale=1.0)

    # 3/4 facing frames (3, 4, 5) - cy=11
    for stage in (0, 1, 2):
        draw_flowing_eye(frames[3 + stage], 8, 11, stage, sdir=-1, length_scale=1.0)
        draw_flowing_eye(frames[3 + stage], 15, 11, stage, sdir=-1, length_scale=0.6)

    # Profile facing frames (6, 7, 8) - cy=11
    for stage in (0, 1, 2):
        draw_flowing_eye(frames[6 + stage], 11, 11, stage, sdir=1, length_scale=1.0)

    return frames


# -----------------------------------------------------------------------------
# 4. Monarch's Shadow Aura (Robe View 164) - Animated Ground Shadow Mist & Soul Fire
# -----------------------------------------------------------------------------

def build_transparent_spr_from_donor(raw_spr: bytes) -> bytes:
    """Build a completely transparent SPR matching the donor's exact frame count and dimensions.
    
    CRITICAL: RO client crashes if an ACT file asks for a frame index that does not exist in SPR.
    Robes have 9 frames (frame indices 0..8). Every frame must exist with its original dimensions!
    """
    num_indexed = struct.unpack('<H', raw_spr[4:6])[0]
    out_buf = bytearray(raw_spr[:8])
    offset = 8
    for f in range(num_indexed):
        w, h = struct.unpack('<HH', raw_spr[offset:offset+4])
        offset += 4
        size = struct.unpack('<H', raw_spr[offset:offset+2])[0]
        offset += 2 + size
        rle = bytearray()
        remaining = w * h
        while remaining > 0:
            count = min(255, remaining)
            rle.append(0)
            rle.append(count)
            remaining -= count
        out_buf.extend(struct.pack('<HHH', w, h, len(rle)))
        out_buf.extend(rle)
    out_buf.extend(raw_spr[-1024:])
    return bytes(out_buf)


def build_monarch_aura_assets(data_grf: Grf) -> tuple[bytes, bytes, bytes]:
    raw_cloak = data_grf.read(b"data\\sprite\\\xb7\xce\xba\xea\\c_dark_lord_cloak\\c_dark_lord_cloak.spr")
    raw_doram = data_grf.read(b"data\\sprite\\\xb7\xce\xba\xea\\c_dark_lord_cloak\\c_dark_lord_cloak_doram.spr")
    drop_spr_data = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\c_dark_lord_cloak.spr")

    cloak_spr_data = build_transparent_spr_from_donor(raw_cloak)
    doram_spr_data = build_transparent_spr_from_donor(raw_doram)

    return cloak_spr_data, doram_spr_data, drop_spr_data


build_monarch_cloak_assets = build_monarch_aura_assets


# -----------------------------------------------------------------------------
# 5. Icons & Collection Artworks (Refined Solo Leveling Designs)
# -----------------------------------------------------------------------------

def create_kasaka_icons() -> tuple[Image.Image, Image.Image]:
    """Generate 24x24 icon and 75x100 collection for Kasaka's Poison Fang."""
    icon = Image.new("RGB", (24, 24), (255, 0, 255))
    d = ImageDraw.Draw(icon)
    # Hilt
    d.line([(3, 21), (8, 16)], fill=(16, 20, 28), width=3)
    d.line([(2, 22), (3, 21)], fill=(60, 75, 95), width=2)
    d.point([(4, 20), (6, 18)], fill=(130, 150, 180))
    # Bone serpent guard
    d.line([(6, 14), (10, 18)], fill=(35, 42, 58), width=2)
    d.point([(6, 14), (10, 18)], fill=(100, 120, 155))
    # Curved blade
    blade_pts = [(9, 15), (12, 11), (16, 6), (20, 3), (22, 2), (21, 5), (18, 9), (15, 13), (11, 16)]
    d.polygon(blade_pts, fill=(0, 175, 235))
    d.line([(9, 15), (12, 11), (16, 6), (20, 3), (22, 2)], fill=(240, 255, 255), width=1)
    d.polygon([(11, 14), (14, 11), (17, 7), (19, 5), (17, 8), (14, 12)], fill=(0, 95, 160))
    d.point([(14, 14), (17, 10)], fill=(0, 245, 255))
    d.point([(23, 1), (21, 4), (18, 10)], fill=(0, 255, 255))
    d.point([(22, 2)], fill=(255, 255, 255))

    col = Image.new("RGB", (75, 100), (255, 0, 255))
    d_col = ImageDraw.Draw(col)
    cx, cy = 37, 50
    for r in range(32, 0, -2):
        t = r / 32.0
        val = int(140 * (1.0 - t))
        d_col.ellipse([(cx - r - 6, cy - r), (cx + r + 6, cy + r)], fill=(0, int(val * 0.7), val))

    d_col.line([(12, 86), (32, 66)], fill=(16, 20, 28), width=7)
    d_col.line([(11, 87), (31, 67)], fill=(45, 55, 75), width=2)
    d_col.ellipse([(8, 85), (15, 92)], fill=(28, 34, 48))
    d_col.point([(11, 88), (12, 89)], fill=(130, 150, 185))
    d_col.polygon([(29, 72), (37, 63), (33, 58), (25, 67)], fill=(14, 18, 26))
    d_col.line([(29, 72), (37, 63)], fill=(80, 95, 125), width=1)

    blade = [(34, 62), (50, 38), (62, 20), (68, 14), (64, 22), (54, 38), (44, 52), (35, 63)]
    d_col.polygon(blade, fill=(0, 175, 235))
    d_col.line([(34, 62), (50, 38), (62, 20), (68, 14)], fill=(240, 255, 255), width=2)
    d_col.polygon([(38, 59), (48, 41), (56, 28), (52, 38), (42, 54)], fill=(0, 95, 160))
    d_col.polygon([(46, 48), (48, 51), (43, 52)], fill=(0, 240, 255))
    d_col.polygon([(54, 36), (56, 39), (51, 40)], fill=(0, 240, 255))
    for px, py in [(70, 12), (64, 20), (54, 30), (44, 42), (48, 50), (58, 36)]:
        d_col.point([(px, py), (px + 1, py), (px, py + 1)], fill=(0, 255, 255))
        d_col.point([(px, py)], fill=(255, 255, 255))

    return icon, col


def create_crown_icons() -> tuple[Image.Image, Image.Image]:
    """Generate 24x24 icon and 75x100 collection for Obsidian Crown."""
    icon = Image.new("RGB", (24, 24), (255, 0, 255))
    d = ImageDraw.Draw(icon)
    d.line([(2, 18), (21, 18)], fill=(14, 18, 26), width=2)
    d.line([(3, 17), (20, 17)], fill=(48, 60, 82), width=1)
    d.polygon([(11, 2), (14, 9), (13, 17), (10, 17), (9, 9)], fill=(26, 32, 46))
    d.line([(11, 2), (11, 17)], fill=(90, 110, 148), width=1)
    d.point([(11, 2)], fill=(255, 255, 255))
    d.polygon([(6, 6), (9, 17), (5, 17)], fill=(18, 22, 32))
    d.line([(6, 6), (6, 17)], fill=(65, 80, 110), width=1)
    d.polygon([(17, 6), (18, 17), (14, 17)], fill=(18, 22, 32))
    d.line([(17, 6), (17, 17)], fill=(65, 80, 110), width=1)
    d.polygon([(2, 10), (4, 17), (1, 17)], fill=(12, 15, 22))
    d.polygon([(21, 10), (22, 17), (19, 17)], fill=(12, 15, 22))
    d.line([(11, 7), (11, 13)], fill=(0, 245, 255), width=1)
    d.line([(10, 9), (12, 9)], fill=(185, 80, 255), width=1)
    d.point([(6, 11), (17, 11)], fill=(0, 220, 255))

    col = Image.new("RGB", (75, 100), (255, 0, 255))
    d_col = ImageDraw.Draw(col)
    cx, cy = 37, 52
    for r in range(32, 0, -2):
        t = r / 32.0
        val = int(120 * (1.0 - t))
        d_col.ellipse([(cx - r - 6, cy - r + 4), (cx + r + 6, cy + r + 4)], fill=(int(val * 0.8), int(val * 0.1), int(val * 1.3)))
    by = 70
    d_col.line([(12, by), (62, by)], fill=(16, 20, 28), width=6)
    d_col.line([(14, by - 2), (60, by - 2)], fill=(48, 60, 82), width=2)
    d_col.polygon([(cx, 20), (cx + 9, 44), (cx + 7, by), (cx - 7, by), (cx - 9, 44)], fill=(24, 30, 42))
    d_col.line([(cx, 20), (cx, by)], fill=(100, 120, 160), width=2)
    d_col.point([(cx, 20), (cx, 21)], fill=(255, 255, 255))
    d_col.polygon([(cx - 17, 30), (cx - 10, by), (cx - 22, by)], fill=(18, 22, 32))
    d_col.line([(cx - 17, 30), (cx - 17, by)], fill=(75, 90, 125), width=1)
    d_col.polygon([(cx + 17, 30), (cx + 22, by), (cx + 10, by)], fill=(18, 22, 32))
    d_col.line([(cx + 17, 30), (cx + 17, by)], fill=(75, 90, 125), width=1)
    d_col.polygon([(cx - 26, 40), (cx - 20, by), (cx - 28, by)], fill=(12, 15, 22))
    d_col.polygon([(cx + 26, 40), (cx + 28, by), (cx + 20, by)], fill=(12, 15, 22))
    d_col.line([(cx, 34), (cx, 56)], fill=(0, 245, 255), width=2)
    d_col.line([(cx - 5, 42), (cx + 5, 42)], fill=(195, 90, 255), width=2)
    d_col.line([(cx - 4, 50), (cx + 4, 50)], fill=(0, 230, 255), width=1)
    d_col.point([(cx - 17, 46), (cx + 17, 46)], fill=(0, 240, 255))
    d_col.point([(cx - 17, 52), (cx + 17, 52)], fill=(190, 80, 255))

    return icon, col


def create_gaze_icons() -> tuple[Image.Image, Image.Image]:
    """Generate 24x24 icon and 75x100 collection for Monarch's Shadow Gaze."""
    icon = Image.new("RGB", (24, 24), (255, 0, 255))
    d = ImageDraw.Draw(icon)
    for cx, sdir in [(7, -1), (16, 1)]:
        d.ellipse([(cx - 2, 13), (cx + 2, 16)], fill=(0, 110, 210))
        d.ellipse([(cx - 1, 13), (cx + 1, 15)], fill=(0, 240, 255))
        d.point([(cx, 14)], fill=(255, 255, 255))
        d.line([(cx, 13), (cx + sdir * 3, 8), (cx + sdir * 5, 4)], fill=(0, 225, 255), width=2)
        d.line([(cx, 13), (cx + sdir * 2, 7), (cx + sdir * 4, 3)], fill=(240, 255, 255), width=1)
        d.point([(cx + sdir * 5, 3), (cx + sdir * 6, 2)], fill=(170, 245, 255))
        d.point([(cx + sdir * 6, 4), (cx + sdir * 7, 3)], fill=(160, 75, 255))

    col = Image.new("RGB", (75, 100), (255, 0, 255))
    d_col = ImageDraw.Draw(col)
    cx, cy = 37, 52
    d_col.polygon([(16, 28), (58, 28), (52, 76), (37, 86), (22, 76)], fill=(10, 14, 22))
    for ex, sdir in [(27, -1), (47, 1)]:
        for r in range(16, 0, -2):
            t = r / 16.0
            d_col.ellipse([(ex - r, cy - r), (ex + r, cy + r)], fill=(0, int(160 * (1 - t)), int(235 * (1 - t))))
        d_col.ellipse([(ex - 5, cy - 2), (ex + 5, cy + 2)], fill=(0, 235, 255))
        d_col.ellipse([(ex - 3, cy - 1), (ex + 3, cy + 1)], fill=(255, 255, 255))
        flame = [(ex, cy), (ex + sdir * 10, cy - 14), (ex + sdir * 20, cy - 28), (ex + sdir * 14, cy - 30), (ex + sdir * 5, cy - 12)]
        d_col.polygon(flame, fill=(0, 225, 255))
        d_col.line([(ex, cy), (ex + sdir * 20, cy - 28)], fill=(240, 255, 255), width=2)
        d_col.point([(ex + sdir * 21, cy - 30), (ex + sdir * 23, cy - 32)], fill=(170, 70, 255))
        d_col.point([(ex + sdir * 16, cy - 34)], fill=(0, 255, 255))

    return icon, col


def create_wings_icons() -> tuple[Image.Image, Image.Image]:
    """Generate 24x24 icon and 75x100 collection for 6 Sovereign Shadow Wings."""
    icon = Image.new("RGB", (24, 24), (255, 0, 255))
    d = ImageDraw.Draw(icon)
    cx, cy = 11, 14
    for sdir in (-1, 1):
        # Feather 1 (upper)
        d.polygon([(cx, cy), (cx + sdir * 8, cy - 9), (cx + sdir * 12, cy - 10), (cx + sdir * 7, cy - 3)], fill=(36, 44, 62))
        d.line([(cx + sdir * 8, cy - 9), (cx + sdir * 12, cy - 10)], fill=(0, 245, 255), width=1)
        d.point([(cx + sdir * 12, cy - 10)], fill=(255, 255, 255))
        d.line([(cx, cy), (cx + sdir * 10, cy - 7)], fill=(20, 24, 36), width=1)
        # Feather 2 (mid)
        d.polygon([(cx, cy), (cx + sdir * 10, cy - 2), (cx + sdir * 13, cy + 1), (cx + sdir * 7, cy + 3)], fill=(46, 56, 78))
        d.line([(cx + sdir * 10, cy - 2), (cx + sdir * 13, cy + 1)], fill=(0, 220, 255), width=1)
        d.point([(cx + sdir * 13, cy + 1)], fill=(200, 255, 255))
        d.line([(cx, cy), (cx + sdir * 11, cy)], fill=(24, 28, 42), width=1)
        # Feather 3 (lower)
        d.polygon([(cx, cy), (cx + sdir * 9, cy + 4), (cx + sdir * 10, cy + 8), (cx + sdir * 5, cy + 6)], fill=(28, 34, 48))
        d.line([(cx + sdir * 9, cy + 4), (cx + sdir * 10, cy + 8)], fill=(0, 190, 245), width=1)
        d.point([(cx + sdir * 2, cy - 1)], fill=(185, 80, 255))

    col = Image.new("RGB", (75, 100), (255, 0, 255))
    d_col = ImageDraw.Draw(col)
    cx, cy = 37, 50
    for r in range(32, 0, -2):
        t = r / 32.0
        d_col.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(int(12 * (1 - t)), int(40 * (1 - t)), int(80 * (1 - t))))
    for sdir in (-1, 1):
        # Feather 1
        p1 = [(cx, cy), (cx + sdir * 22, cy - 28), (cx + sdir * 35, cy - 38), (cx + sdir * 26, cy - 14)]
        d_col.polygon(p1, fill=(42, 50, 70))
        d_col.line([(cx + sdir * 22, cy - 28), (cx + sdir * 35, cy - 38)], fill=(0, 245, 255), width=2)
        d_col.line([(cx, cy), (cx + sdir * 30, cy - 28)], fill=(24, 28, 40), width=1)
        d_col.point([(cx + sdir * 35, cy - 38)], fill=(255, 255, 255))
        # Feather 2
        p2 = [(cx, cy), (cx + sdir * 28, cy - 6), (cx + sdir * 37, cy + 9), (cx + sdir * 24, cy + 17)]
        d_col.polygon(p2, fill=(52, 62, 86))
        d_col.line([(cx + sdir * 28, cy - 6), (cx + sdir * 37, cy + 9)], fill=(0, 225, 255), width=2)
        d_col.line([(cx, cy), (cx + sdir * 32, cy + 2)], fill=(28, 34, 48), width=1)
        # Feather 3
        p3 = [(cx, cy), (cx + sdir * 23, cy + 22), (cx + sdir * 29, cy + 33), (cx + sdir * 15, cy + 27)]
        d_col.polygon(p3, fill=(30, 36, 52))
        d_col.line([(cx + sdir * 23, cy + 22), (cx + sdir * 29, cy + 33)], fill=(0, 195, 245), width=2)
        d_col.line([(cx, cy), (cx + sdir * 24, cy + 26)], fill=(18, 22, 32), width=1)
        # Magic aura sparks
        d_col.point([(cx + sdir * 36, cy - 36), (cx + sdir * 38, cy - 34)], fill=(0, 255, 255))
        d_col.point([(cx + sdir * 38, cy + 11), (cx + sdir * 39, cy + 13)], fill=(0, 240, 255))
        d_col.point([(cx + sdir * 30, cy + 35)], fill=(0, 210, 255))
        d_col.point([(cx + sdir * 6, cy - 4), (cx + sdir * 8, cy + 2)], fill=(190, 80, 255))

    return icon, col


# -----------------------------------------------------------------------------
# Main Asset Assembler
# -----------------------------------------------------------------------------

def build_all_assets() -> list[tuple[bytes, bytes]]:
    """Assemble all sprites, icons, and client override files."""
    print("=" * 70)
    print("Building Solo Leveling Shadow Monarch 4-Piece Hunter Rank Costume Set (v3)")
    print("=" * 70)

    files: list[tuple[bytes, bytes]] = []

    def add_headgear_aliases(name_str: str, spr_data: bytes, act_m: bytes, act_f: bytes, spr_drop: bytes, act_drop: bytes) -> None:
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\{name_str}.act".encode("latin1"), act_m))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\_{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\_{name_str}.act".encode("latin1"), act_m))

        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_{name_str}.act".encode("latin1"), act_m))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2__{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2__{name_str}.act".encode("latin1"), act_m))

        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9_{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9_{name_str}.act".encode("latin1"), act_f))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9__{name_str}.spr".encode("latin1"), spr_data))
        files.append((f"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9__{name_str}.act".encode("latin1"), act_f))

        files.append((f"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\{name_str}.spr".encode("latin1"), spr_drop))
        files.append((f"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\{name_str}.act".encode("latin1"), act_drop))
        files.append((f"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_{name_str}.spr".encode("latin1"), spr_drop))
        files.append((f"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_{name_str}.act".encode("latin1"), act_drop))

    data_grf = Grf(str(DATA_GRF))
    ui_sources_dir = Path(r"E:\.midnight-ro\patcher\tools\client-patch\ui_sources\solo_leveling_hunter_set")
    ui_sources_dir.mkdir(parents=True, exist_ok=True)

    # 1. Kasaka's Shadow Fang (Rank C, View 2850)
    print("\n1. Rendering Kasaka's Shadow Fang (Rank C, View 2850)...")
    dagger_frames = render_kasaka_dagger_frames()
    spr_dagger = encode_spr_indexed(dagger_frames, PALETTE_BYTES)
    act_dagger_m = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_\xc7\xd8\xc0\xfb\xc0\xc7\xb4\xeb\xb0\xc5.act")
    act_dagger_f = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9_\xc7\xd8\xc0\xfb\xc0\xc7\xb4\xeb\xb0\xc5.act")
    act_dagger_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\\xc7\xd8\xc0\xfb\xc0\xc7\xb4\xeb\xb0\xc5.act")
    spr_dagger_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\\xc7\xd8\xc0\xfb\xc0\xc7\xb4\xeb\xb0\xc5.spr")
    spr_dagger_drop = spr_dagger_drop[:-1024] + PALETTE_BYTES

    add_headgear_aliases("kasaka_shadow_fang", spr_dagger, act_dagger_m, act_dagger_f, spr_dagger_drop, act_dagger_drop)

    icon_dagger_bytes = (ui_sources_dir / "kasaka_shadow_fang_icon_24.bmp").read_bytes()
    col_dagger_bytes = (ui_sources_dir / "kasaka_shadow_fang_collection_75x100.bmp").read_bytes()
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\kasaka_shadow_fang.bmp", icon_dagger_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\kasaka_shadow_fang.bmp", col_dagger_bytes))
    print("   Kasaka's Shadow Fang assets generated.")

    # 2. Obsidian Crown of the Monarch (Rank B, View 2851) - Realistic High-End Circlet
    print("\n2. Building Obsidian Crown of the Monarch (Rank B, View 2851)...")
    spr_crown, act_crown_m, act_crown_f, spr_crown_drop, act_crown_drop = build_obsidian_crown_assets(data_grf)

    add_headgear_aliases("obsidian_monarch_crown", spr_crown, act_crown_m, act_crown_f, spr_crown_drop, act_crown_drop)

    icon_crown_bytes = (ui_sources_dir / "obsidian_monarch_crown_icon_24.bmp").read_bytes()
    col_crown_bytes = (ui_sources_dir / "obsidian_monarch_crown_collection_75x100.bmp").read_bytes()
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\obsidian_monarch_crown.bmp", icon_crown_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\obsidian_monarch_crown.bmp", col_crown_bytes))
    print("   Obsidian Crown assets generated.")

    # 3. Monarch's Shadow Gaze (Rank A, View 2852) - ANIMATED
    print("\n3. Rendering Monarch's Shadow Gaze (Rank A, View 2852) [ANIMATED]...")
    gaze_frames = render_monarch_gaze_frames()
    orig_gaze_spr = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_c_blinking_eyes_bu.spr")
    donor_pal = orig_gaze_spr[-1024:]
    spr_gaze = encode_spr_rgba(gaze_frames, donor_pal)

    act_gaze_m = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xb3\xb2\\\xb3\xb2_c_blinking_eyes_bu.act")
    act_gaze_f = data_grf.read(b"data\\sprite\\\xbe\xc7\xbc\xbc\xbb\xe7\xb8\xae\\\xbf\xa9\\\xbf\xa9_c_blinking_eyes_bu.act")
    act_gaze_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\c_blinking_eyes_bu.act")
    spr_gaze_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\c_blinking_eyes_bu.spr")
    spr_gaze_drop = spr_gaze_drop[:-1024] + PALETTE_BYTES

    add_headgear_aliases("monarch_shadow_gaze", spr_gaze, act_gaze_m, act_gaze_f, spr_gaze_drop, act_gaze_drop)

    icon_gaze_bytes = (ui_sources_dir / "monarch_shadow_gaze_icon_24.bmp").read_bytes()
    col_gaze_bytes = (ui_sources_dir / "monarch_shadow_gaze_collection_75x100.bmp").read_bytes()
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\monarch_shadow_gaze.bmp", icon_gaze_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\monarch_shadow_gaze.bmp", col_gaze_bytes))
    print("   Monarch's Shadow Gaze (Animated RGBA 9-frame) generated.")

    # 4. Monarch's Shadow Aura (Rank S, View 164) - ANIMATED
    print("\n4. Building Monarch's Shadow Aura (Rank S, View 164) [ANIMATED]...")
    cloak_spr_data, doram_spr_data, drop_spr_data = build_monarch_aura_assets(data_grf)

    icon_aura_bytes = (ui_sources_dir / "monarch_shadow_aura_icon_24.bmp").read_bytes()
    col_aura_bytes = (ui_sources_dir / "monarch_shadow_aura_collection_75x100.bmp").read_bytes()

    # Main textures
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\monarch_shadow_aura.bmp", icon_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\monarch_shadow_aura.bmp", col_aura_bytes))

    # Compatibility texture aliases
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\monarch_sovereign_cloak.bmp", icon_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\monarch_sovereign_cloak.bmp", col_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\sovereign_shadow_wings.bmp", icon_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\sovereign_shadow_wings.bmp", col_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\item\\c_dark_lord_cloak.bmp", icon_aura_bytes))
    files.append((b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\collection\\c_dark_lord_cloak.bmp", col_aura_bytes))

    # Drop items for aura
    act_cloak_drop = data_grf.read(b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\c_dark_lord_cloak.act")

    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\monarch_shadow_aura.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\monarch_shadow_aura.act", act_cloak_drop))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_monarch_shadow_aura.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_monarch_shadow_aura.act", act_cloak_drop))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\monarch_sovereign_cloak.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\monarch_sovereign_cloak.act", act_cloak_drop))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_monarch_sovereign_cloak.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\_monarch_sovereign_cloak.act", act_cloak_drop))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\c_dark_lord_cloak.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\sovereign_shadow_wings.spr", drop_spr_data))
    files.append((b"data\\sprite\\\xbe\xc6\xc0\xcc\xc5\xdb\\sovereign_shadow_wings.act", act_cloak_drop))

    # Robe Sprites (C_Dark_Lord_Cloak / View 164)
    files.append((b"data\\sprite\\\xb7\xce\xba\xea\\c_dark_lord_cloak\\c_dark_lord_cloak.spr", cloak_spr_data))
    files.append((b"data\\sprite\\\xb7\xce\xba\xea\\C_Dark_Lord_Cloak\\c_dark_lord_cloak.spr", cloak_spr_data))
    files.append((b"data\\sprite\\\xb7\xce\xba\xea\\C_Dark_Lord_Cloak\\C_Dark_Lord_Cloak.spr", cloak_spr_data))
    files.append((b"data\\sprite\\\xb7\xce\xba\xea\\c_dark_lord_cloak\\c_dark_lord_cloak_doram.spr", doram_spr_data))
    files.append((b"data\\sprite\\\xb7\xce\xba\xea\\C_Dark_Lord_Cloak\\C_Dark_Lord_Cloak_doram.spr", doram_spr_data))

    # HatEffect 217 & 218 360-Degree Swirling Shadow Mist Aura assets
    for str_f in ui_sources_dir.glob("midnight_monarch_*.str"):
        s_bytes = str_f.read_bytes()
        files.append((f"data\\texture\\effect\\midnight_monarch_shadow\\{str_f.name}".encode("latin-1"), s_bytes))
        files.append((f"data\\texture\\effect\\{str_f.name}".encode("latin-1"), s_bytes))

    for tga_f in ui_sources_dir.glob("midnight_monarch_*.tga"):
        t_bytes = tga_f.read_bytes()
        files.append((f"data\\texture\\effect\\midnight_monarch_shadow\\{tga_f.name}".encode("latin-1"), t_bytes))
        files.append((f"data\\texture\\effect\\{tga_f.name}".encode("latin-1"), t_bytes))

    print("   Monarch's Shadow Aura (HatEffects 217 & 218, 360-Degree Swirling Shadow Mist & Thin Blue Lightning) generated.")

    # 5. Restore official accname_f.lub
    print("\n5. Restoring official bytecode accname_f.lub...")
    orig_accname_f = data_grf.read(b"data\\luafiles514\\lua files\\datainfo\\accname_f.lub")
    files.append((b"data\\luafiles514\\lua files\\datainfo\\accname_f.lub", orig_accname_f))

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

    # 6. Patch accessoryid.lub
    print("\n6. Patching accessoryid.lub bytecode (View IDs 2850..2852)...")
    raw_accid = data_grf.read(b"data\\luafiles514\\lua files\\datainfo\\accessoryid.lub")
    p_id = parse_proto(Reader(raw_accid))
    id_entries = [
        (b"ACCESSORY_KASAKA_SHADOW_FANG", 2850),
        (b"ACCESSORY_OBSIDIAN_MONARCH_CROWN", 2851),
        (b"ACCESSORY_MONARCH_SHADOW_GAZE", 2852),
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

    # 7. Patch accname.lub
    print("\n7. Patching accname.lub bytecode (Sprite names mapping)...")
    raw_accname = data_grf.read(b"data\\luafiles514\\lua files\\datainfo\\accname.lub")
    p_name = parse_proto(Reader(raw_accname))
    name_entries = [
        (2850, b"_kasaka_shadow_fang"),
        (2851, b"_obsidian_monarch_crown"),
        (2852, b"_monarch_shadow_gaze"),
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
    """Update item_db.yml with exact custom View IDs."""
    print(f"\nUpdating server item_db: {ITEM_DB_YML}")
    content = ITEM_DB_YML.read_text(encoding="utf-8")

    yaml_block = """  # ---------------------------------------------------------------------------
  # Midnight RO - Solo Leveling Shadow Monarch Hunter Rank Costumes (Rank C - S)
  # ---------------------------------------------------------------------------
  - Id: 902269
    AegisName: "NFS_Hunter_Dagger_C"
    Name: "[Hunter Rank C] Kasaka Shadow Fang"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Low: true
    View: 2850
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902270
    AegisName: "NFS_Hunter_Crown_B"
    Name: "[Hunter Rank B] Obsidian Crown of the Monarch"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Top: true
    View: 2851
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902271
    AegisName: "NFS_Hunter_Gaze_A"
    Name: "[Hunter Rank A] Monarch's Shadow Gaze"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Mid: true
    View: 2852
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902272
    AegisName: "NFS_Hunter_Aura_S"
    Name: "[Hunter Rank S] Monarch's Shadow Aura"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Garment: true
    View: 0
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
      hateffect 217, true;
      hateffect 218, true;
    UnEquipScript: |
      hateffect 217, false;
      hateffect 218, false;"""

    import re
    if "Id: 902269" in content:
        marker = "  - Id: 902269"
        idx = content.find(marker)
        prev_comment = content.rfind("\n  # --------------------", max(0, idx - 300), idx)
        if prev_comment == -1:
            prev_comment = content.rfind("\n# --------------------", max(0, idx - 300), idx)
        cut_point = prev_comment if prev_comment != -1 else idx
        content = content[:cut_point].rstrip() + "\n\n" + yaml_block + "\n"
    else:
        content = content.rstrip() + "\n\n" + yaml_block + "\n"

    ITEM_DB_YML.write_text(content, encoding="utf-8")
    print("  Server item_db updated successfully.")


def update_client_iteminfo(target_file: Path) -> None:
    """Update itemInfo_C.lua with clean ASCII resource names and Thai descriptions."""
    if not target_file.exists():
        return
    print(f"\nUpdating client itemInfo: {target_file}")
    raw = target_file.read_bytes()
    text = raw.decode("cp874", errors="ignore")

    lua_block = '''-- Solo Leveling Shadow Monarch Hunter Rank Costumes
tbl_custom[902269] = {
	unidentifiedDisplayName = "[Hunter C] Kasaka Shadow Fang",
	unidentifiedResourceName = "kasaka_shadow_fang",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank C" },
	identifiedDisplayName = "[Hunter C] Kasaka Shadow Fang",
	identifiedResourceName = "kasaka_shadow_fang",
	identifiedDescriptionName = {
		"^FF9900[Hunter C] Kasaka Shadow Fang^000000\\n" ..
		"^111111กริชเขี้ยวพิษคาซากะสีดำขลับ คมดาบอาบไอพิษสีฟ้าคราม^000000\\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank C^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^111111ประเภท : Costume^000000\\n" ..
		"^111111ตำแหน่ง : ส่วนล่าง (Lower)^000000\\n" ..
		"^111111น้ำหนัก : 0^000000\\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2850,
	costume = true
}

tbl_custom[902270] = {
	unidentifiedDisplayName = "[Hunter B] Obsidian Crown of the Monarch",
	unidentifiedResourceName = "obsidian_monarch_crown",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank B" },
	identifiedDisplayName = "[Hunter B] Obsidian Crown of the Monarch",
	identifiedResourceName = "obsidian_monarch_crown",
	identifiedDescriptionName = {
		"^FF9900[Hunter B] Obsidian Crown of the Monarch^000000\\n" ..
		"^111111มงกุฎผลึกหินสีดำออบซิเดียน สลักอักขระรูนโบราณเรืองแสงสีม่วง-คราม^000000\\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank B^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^111111ประเภท : Costume^000000\\n" ..
		"^111111ตำแหน่ง : ส่วนบน (Upper)^000000\\n" ..
		"^111111น้ำหนัก : 0^000000\\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2851,
	costume = true
}

tbl_custom[902271] = {
	unidentifiedDisplayName = "[Hunter A] Monarch\'s Shadow Gaze",
	unidentifiedResourceName = "monarch_shadow_gaze",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank A" },
	identifiedDisplayName = "[Hunter A] Monarch\'s Shadow Gaze",
	identifiedResourceName = "monarch_shadow_gaze",
	identifiedDescriptionName = {
		"^FF9900[Hunter A] Monarch\'s Shadow Gaze^000000\\n" ..
		"^111111ดวงตาเปลวไฟสีฟ้าครามสว่างวาบ พร้อมไอวิญญาณสีฟ้าลอยพริ้วจากหางตา (Animated)^000000\\n" ..
		"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank A^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^111111ประเภท : Costume^000000\\n" ..
		"^111111ตำแหน่ง : ส่วนกลาง (Middle)^000000\\n" ..
		"^111111น้ำหนัก : 0^000000\\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 2852,
	costume = true
}

tbl_custom[902272] = {
	unidentifiedDisplayName = "[Hunter S] Monarch's Shadow Aura",
	unidentifiedResourceName = "monarch_shadow_aura",
	unidentifiedDescriptionName = { "ไอเทมเกียรติยศ Hunter Rank S" },
	identifiedDisplayName = "[Hunter S] Monarch's Shadow Aura",
	identifiedResourceName = "monarch_shadow_aura",
	identifiedDescriptionName = {
		"^FF9900[Hunter S] Monarch's Shadow Aura^000000\\n" ..
		"^111111ออร่าหมอกเงาแห่งจักรพรรดิสีดำพวยพุ่งขึ้นจากใต้ฝ่าเท้าพร้อมประกายเพลิงวิญญาณสีฟ้าคราม (Animated)^000000\\n" ..
		"^111111รางวัลเกียรติยศสูงสุดสำหรับ Hunter ผู้ผ่านการประเมิน Rank S^000000\\n" ..
		"^B7DFE5====================^000000\\n" ..
		"^111111ประเภท : Costume^000000\\n" ..
		"^111111ตำแหน่ง : มัฟหลัง (Garment)^000000\\n" ..
		"^111111น้ำหนัก : 0^000000\\n" ..
		"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
		"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
	},
	slotCount = 0,
	ClassNum = 0,
	costume = true
}
'''

    marker = "-- Solo Leveling Shadow Monarch Hunter Rank Costumes"
    if marker in text:
        idx = text.find(marker)
        end_idx = text.find("tbl_custom[902272]", idx)
        if end_idx != -1:
            closing = text.find("costume = true\n}", end_idx)
            if closing != -1:
                text = text[:idx] + text[closing+16:]
            else:
                closing2 = text.find("})", end_idx)
                if closing2 != -1:
                    text = text[:idx] + text[closing2+2:]

    insert_point = text.find("-- Table for Official Overrides")
    if insert_point != -1:
        text = text[:insert_point] + lua_block.strip() + "\n\n" + text[insert_point:]
    else:
        text = text + "\n\n" + lua_block.strip() + "\n"

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
    print("ALL SOLO LEVELING HUNTER COSTUMES SUCCESSFULLY CREATED & INSTALLED (v3)!")
    print("=" * 70)


if __name__ == "__main__":
    main()
