#!/usr/bin/env python3
"""Build the Midnight RO Auto Hunt Option 8 Tactical Ground Reticle texture and STR effect."""

from __future__ import annotations

import hashlib
import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


TOOLS = Path(__file__).resolve().parent
ASSETS = TOOLS / "ui_sources/auto_hunt_overhead"
MASTER = ASSETS / "midnight_auto_hunt_master.png"
PREVIEW = ASSETS / "midnight_auto_hunt.png"
TEXTURE = ASSETS / "midnight_auto_hunt.tga"
EFFECT = ASSETS / "midnight_auto_hunt.str"

CANVAS_SIZE = (256, 256)
ART_WIDTH = 106.0   # Tightly fitted to inner edge of yellow ring
ART_HEIGHT = 53.0   # 2:1 isometric ground ellipse
FPS = 12
MAX_KEY = 72
TEXTURE_NAME = b"midnight_auto_hunt.tga"
KEYFRAME = struct.Struct("<II2f8f8ffIff4fIII")


def build_texture() -> None:
    """Generate high-resolution tactical radar compass reticle with Theme 1 Midnight Violet & Cyber Cyan."""
    size = 1024
    cx, cy = size // 2, size // 2

    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)

    # Theme 1: Midnight Violet & Cyber Cyan palette
    c_violet_bright = (235, 150, 255, 255)  # Vivid neon violet
    c_violet_deep = (175, 55, 245, 255)    # Rich midnight violet
    c_cyan = (0, 225, 255, 255)            # Electric cyber cyan
    c_cyan_bright = (160, 250, 255, 255)   # Starlight ice cyan
    c_white = (255, 255, 255, 255)

    r_out = 430
    r_out_inner = 405
    # Thicker outer rings: Midnight Violet
    draw.ellipse((cx - r_out, cy - r_out, cx + r_out, cy + r_out), outline=c_violet_bright, width=16)
    draw.ellipse((cx - r_out_inner, cy - r_out_inner, cx + r_out_inner, cy + r_out_inner), outline=c_violet_deep, width=10)

    # Thicker middle cyan ring
    r_mid = 330
    draw.ellipse((cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid), outline=c_cyan, width=14)

    # Thicker inner ring
    r_in = 240
    draw.ellipse((cx - r_in, cy - r_in, cx + r_in, cy + r_in), outline=c_cyan_bright, width=8)

    # Bolder compass ticks
    for deg in range(0, 360, 5):
        rad = math.radians(deg)
        is_cardinal = (deg % 90 == 0)
        is_major = (deg % 30 == 0)
        is_sub = (deg % 10 == 0)

        if is_cardinal:
            l_len = 38
            color = c_white
            w = 12
        elif is_major:
            l_len = 26
            color = c_violet_bright
            w = 10
        elif is_sub:
            l_len = 18
            color = c_cyan
            w = 7
        else:
            l_len = 10
            color = c_cyan
            w = 5

        x1 = cx + (r_out - l_len) * math.cos(rad)
        y1 = cy + (r_out - l_len) * math.sin(rad)
        x2 = cx + (r_out + 4) * math.cos(rad)
        y2 = cy + (r_out + 4) * math.sin(rad)
        draw.line((x1, y1, x2, y2), fill=color, width=w)

    # Bolder crosshairs: Cyber Cyan with pure white core
    for deg in (0, 90, 180, 270):
        rad = math.radians(deg)
        draw.line((
            cx + (r_in - 30) * math.cos(rad), cy + (r_in - 30) * math.sin(rad),
            cx + (r_out + 26) * math.cos(rad), cy + (r_out + 26) * math.sin(rad)
        ), fill=c_cyan, width=12)
        draw.line((
            cx + (r_in - 28) * math.cos(rad), cy + (r_in - 28) * math.sin(rad),
            cx + (r_out + 24) * math.cos(rad), cy + (r_out + 24) * math.sin(rad)
        ), fill=c_white, width=4)

    # Bolder diamonds at 45-degree angles: Violet with White core
    for deg in (45, 135, 225, 315):
        rad = math.radians(deg)
        d_r = (r_out + r_mid) / 2
        dx = cx + d_r * math.cos(rad)
        dy = cy + d_r * math.sin(rad)
        d = 24
        draw.polygon([(dx, dy - d), (dx + d, dy), (dx, dy + d), (dx - d, dy)], fill=c_violet_deep)
        d2 = 12
        draw.polygon([(dx, dy - d2), (dx + d2, dy), (dx, dy + d2), (dx - d2, dy)], fill=c_white)

    # Cardinal letters N, E, S, W
    cardinals = [
        ("N", 270),
        ("E", 0),
        ("S", 90),
        ("W", 180),
    ]
    try:
        font = ImageFont.truetype("arialbd.ttf", 56)
    except Exception:
        font = ImageFont.load_default()

    for letter, deg in cardinals:
        rad = math.radians(deg)
        dist = r_out + 28
        tx = cx + dist * math.cos(rad)
        ty = cy + dist * math.sin(rad)
        bbox = draw.textbbox((0, 0), letter, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((tx - tw / 2, ty - th / 2 - 5), letter, fill=c_violet_bright, font=font)

    # Multi-layer radiant colored bloom (wide soft violet aura + medium cyan halo)
    r_ch, g_ch, b_ch, a_ch = base.split()
    a_wide = a_ch.filter(ImageFilter.GaussianBlur(24))
    a_mid = a_ch.filter(ImageFilter.GaussianBlur(10))
    glow_a = Image.blend(a_wide, a_mid, 0.6)
    glow_img = Image.merge("RGBA", (r_ch, g_ch, b_ch, glow_a))

    # Composite: colored glow behind crisp base
    final_1024 = Image.alpha_composite(glow_img, base)

    # Downsample to 256x256 using Lanczos for clean anti-aliasing
    final_256 = final_1024.resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    final_256.save(PREVIEW, "PNG")
    final_256.save(TEXTURE, "TGA")
    final_1024.save(MASTER, "PNG")


def keyframe(frame: int, y: float = 240.0, opacity: float = 230.0) -> bytes:
    half_width = ART_WIDTH / 2.0
    half_height = ART_HEIGHT / 2.0
    return KEYFRAME.pack(
        frame,
        0,
        320.0,
        y,
        0.0,
        0.0,
        1.0,
        1.0,
        0.0,
        0.0,
        1.0,
        1.0,
        -half_width,
        half_width,
        half_width,
        -half_width,
        -half_height,
        -half_height,
        half_height,
        half_height,
        0.0,
        0,
        0.0,
        0.0,
        255.0,
        255.0,
        255.0,
        opacity,
        5,
        6,
        0,
    )


def interpolation(
    frame: int,
    next_frame: int,
    y: float,
    next_y: float,
    opacity: float,
    next_opacity: float,
) -> bytes:
    duration = next_frame - frame
    if duration <= 0:
        raise ValueError("STR interpolation requires increasing frame numbers")

    floats_before_anim = [0.0] * 19
    floats_before_anim[1] = (next_y - y) / duration
    floats_after_anim = [0.0] * 6
    floats_after_anim[5] = (next_opacity - opacity) / duration
    return KEYFRAME.pack(
        frame,
        1,
        *floats_before_anim,
        0,
        *floats_after_anim,
        0,
        0,
        0,
    )


def build_str() -> None:
    texture_field = TEXTURE_NAME + bytes(128 - len(TEXTURE_NAME))
    # Ultra-smooth, slow breathing glow (วูบวาบ ช้าลงอีกนิด):
    # Constant grounded Y=240.0, smooth sinusoidal opacity pulse (95.0 <-> 255.0) over 6.0 seconds
    states = (
        (0, 240.0, 95.0),
        (12, 240.0, 130.0),
        (24, 240.0, 195.0),
        (36, 240.0, 255.0),
        (48, 240.0, 195.0),
        (60, 240.0, 130.0),
        (72, 240.0, 95.0),
    )
    frames = []
    for index, (frame, y, opacity) in enumerate(states):
        frames.append(keyframe(frame, y, opacity))
        if index + 1 < len(states):
            next_frame, next_y, next_opacity = states[index + 1]
            frames.append(
                interpolation(
                    frame,
                    next_frame,
                    y,
                    next_y,
                    opacity,
                    next_opacity,
                )
            )

    payload = bytearray()
    payload += b"STRM"
    payload += struct.pack("<IIII", 0x94, FPS, MAX_KEY, 2)
    payload += bytes(24)
    payload += struct.pack("<I", 1)
    payload += texture_field
    payload += struct.pack("<I", len(frames))
    payload += b"".join(frames)
    EFFECT.write_bytes(payload)


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    build_texture()
    build_str()

    tga_hash = hashlib.sha256(TEXTURE.read_bytes()).hexdigest()[:12]
    str_hash = hashlib.sha256(EFFECT.read_bytes()).hexdigest()[:12]
    print(f"Option 8 (Theme 1: Midnight Violet & Cyber Cyan + Animated Pulse) built successfully:")
    print(f"  TGA: {TEXTURE} ({tga_hash})")
    print(f"  STR: {EFFECT} ({str_hash})")
    print(f"  Size: {ART_WIDTH}x{ART_HEIGHT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
