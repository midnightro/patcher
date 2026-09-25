#!/usr/bin/env python3
"""Build authentic Realistic Hunter Rank Wings (Rank B, A, S) from master PNGs.

Tiers:
  B: Elegant Celestial (Golden plumage, 2 wings, compact & refined)
  A: Twilight Archangel (Violet & platinum blades, 4 wings, runic glow)
  S: Sovereign of Cosmos (Midnight nebula, 6 wings, constellation stars, cosmic halo)

Generates:
  - 32-bit RGBA TGA textures
  - Multi-frame breathing & fluttering .str 3D effect binaries
"""

from __future__ import annotations

import math
import struct
import sys
from pathlib import Path
import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parent
ASSETS = TOOLS / "ui_sources/hunter_rank_wings"
TEXTURE_DIR = ASSETS / "textures"
EFFECT_DIR = ASSETS / "effects"

TIERS = {
    "b": {
        "master": "wings_b_master.png",
        "tex_name": "hunter_wings_b.tga",
        "str_name": "midnight_hunter_wings_b.str",
        "effect_id": 214,
        "width": 54.0,
        "height": 54.0,
        "tex_size": 256,
        "fps": 15,
        "max_key": 60,
    },
    "a": {
        "master": "wings_a_master.png",
        "tex_name": "hunter_wings_a.tga",
        "str_name": "midnight_hunter_wings_a.str",
        "effect_id": 215,
        "width": 72.0,
        "height": 72.0,
        "tex_size": 256,
        "fps": 15,
        "max_key": 60,
    },
    "s": {
        "master": "wings_s_master.png",
        "tex_name": "hunter_wings_s.tga",
        "str_name": "midnight_hunter_wings_s.str",
        "effect_id": 216,
        "width": 96.0,
        "height": 96.0,
        "tex_size": 256,
        "fps": 15,
        "max_key": 60,
    },
}

KEYFRAME = struct.Struct("<II2f8f8ffIff4fIII")
Y_POS = 240.0


def extract_alpha(img: Image.Image) -> Image.Image:
    """Extract anti-aliased RGBA matte from pure black background."""
    img_rgba = img.convert("RGBA")
    arr = np.array(img_rgba).astype(np.float32)
    rgb = arr[:, :, :3]
    max_c = np.max(rgb, axis=2)
    # Smooth thresholding for crisp feather boundaries and soft starlight glow
    alpha = np.clip((max_c - 6.0) / (32.0 - 6.0), 0.0, 1.0)
    alpha = (alpha * 255.0).astype(np.uint8)
    res = img_rgba.copy()
    res.putalpha(Image.fromarray(alpha))
    return res


def keyframe(
    frame: int,
    w: float,
    h: float,
    y: float = 240.0,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
    opacity: float = 255.0,
) -> bytes:
    half_w = (w * scale_x) / 2.0
    half_h = (h * scale_y) / 2.0
    return KEYFRAME.pack(
        frame,
        0,       # 0 = keyframe
        320.0,
        y,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,  # uv
        -half_w, half_w, half_w, -half_w,         # x quad
        -half_h, -half_h, half_h, half_h,         # y quad
        0.0,     # angle
        0,       # tex_index
        0.0, 0.0,# anim
        255.0, 255.0, 255.0, opacity,             # rgba
        5, 6, 0  # blend: normal alpha (SRC_ALPHA, INV_SRC_ALPHA)
    )


def interpolation(
    frame: int,
    next_frame: int,
    w: float,
    h: float,
    scale_from: tuple[float, float],
    scale_to: tuple[float, float],
    opacity_from: float,
    opacity_to: float,
) -> bytes:
    dur = next_frame - frame
    if dur <= 0:
        raise ValueError("Interpolation duration must be > 0")

    half_w_from = (w * scale_from[0]) / 2.0
    half_w_to = (w * scale_to[0]) / 2.0
    half_h_from = (h * scale_from[1]) / 2.0
    half_h_to = (h * scale_to[1]) / 2.0

    floats_before = [0.0] * 19
    # quad vertex velocity
    dx = (half_w_to - half_w_from) / dur
    dy = (half_h_to - half_h_from) / dur
    floats_before[10] = -dx
    floats_before[11] = dx
    floats_before[12] = dx
    floats_before[13] = -dx
    floats_before[14] = -dy
    floats_before[15] = -dy
    floats_before[16] = dy
    floats_before[17] = dy

    floats_after = [0.0] * 6
    floats_after[5] = (opacity_to - opacity_from) / dur

    return KEYFRAME.pack(
        frame,
        1,  # 1 = interpolation
        *floats_before,
        0,
        *floats_after,
        0, 0, 0
    )


def build_str(tier_key: str, cfg: dict) -> bytes:
    """Build multi-frame organic fluttering/breathing STR binary."""
    tex_name = cfg["tex_name"].encode("ascii")
    tex_field = tex_name + bytes(128 - len(tex_name))

    fps = cfg["fps"]
    max_key = cfg["max_key"]
    w = cfg["width"]
    h = cfg["height"]

    # 4-stage smooth sinusoidal wing breathing cycle over 60 frames (4.0 seconds)
    # (frame, (scale_x, scale_y), opacity)
    timeline = [
        (0, (1.00, 1.00), 255.0),
        (15, (1.04, 0.98), 245.0),
        (30, (0.97, 1.03), 255.0),
        (45, (1.03, 0.99), 250.0),
        (60, (1.00, 1.00), 255.0),
    ]

    frames = []
    for i in range(len(timeline) - 1):
        f1, s1, op1 = timeline[i]
        f2, s2, op2 = timeline[i + 1]
        frames.append(keyframe(f1, w, h, Y_POS, s1[0], s1[1], op1))
        frames.append(interpolation(f1, f2, w, h, s1, s2, op1, op2))
    # Final keyframe at max_key
    f_end, s_end, op_end = timeline[-1]
    frames.append(keyframe(f_end, w, h, Y_POS, s_end[0], s_end[1], op_end))

    payload = bytearray(b"STRM")
    payload += struct.pack("<IIII", 0x94, fps, max_key, 2)  # 2 = 1 layer + 1
    payload += bytes(24)
    payload += struct.pack("<I", 1)  # 1 texture
    payload += tex_field
    payload += struct.pack("<I", len(frames))
    payload += b"".join(frames)
    return bytes(payload)


def write_tga_32(img: Image.Image, out_path: Path) -> None:
    """Write uncompressed true-color 32-bit RGBA Targa (.tga) file."""
    w, h = img.size
    rgba = img.convert("RGBA")
    r, g, b, a = rgba.split()
    bgra = Image.merge("RGBA", (b, g, r, a))

    # TGA header for 32-bit uncompressed true color, bottom-left origin
    # Bytes 12-15: width, height. Byte 16: 32 bits. Byte 17: 8 alpha bits
    header = bytearray(18)
    header[2] = 2  # uncompressed true-color
    struct.pack_into("<HHBB", header, 12, w, h, 32, 8)

    # Flip vertically because TGA bottom-left origin
    flipped = bgra.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    out_path.write_bytes(bytes(header) + flipped.tobytes())


def main() -> int:
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    EFFECT_DIR.mkdir(parents=True, exist_ok=True)

    print("Building Realistic Hunter Rank Wings (Rank B, A, S)...")

    for tier_key, cfg in TIERS.items():
        master_file = ASSETS / cfg["master"]
        if not master_file.is_file():
            print(f"Error: Missing master file {master_file}")
            return 1

        print(f"\nProcessing Tier {tier_key.upper()} ({cfg['tex_name']})...")
        raw_img = Image.open(master_file)
        clean_rgba = extract_alpha(raw_img)

        # Scale cleanly to target texture dimension with Lanczos filter
        target_size = (cfg["tex_size"], cfg["tex_size"])
        resized_tex = clean_rgba.resize(target_size, Image.Resampling.LANCZOS)

        # Save texture as .tga (32-bit RGBA)
        tga_out = TEXTURE_DIR / cfg["tex_name"]
        write_tga_32(resized_tex, tga_out)
        print(f"  Saved TGA: {tga_out.name} ({target_size[0]}x{target_size[1]}, {tga_out.stat().st_size} bytes)")

        # Save transparent PNG copy for inspect/preview
        png_preview = TEXTURE_DIR / f"{Path(cfg['tex_name']).stem}.png"
        resized_tex.save(png_preview, "PNG")

        # Build STR binary effect
        str_bytes = build_str(tier_key, cfg)
        str_out = EFFECT_DIR / cfg["str_name"]
        str_out.write_bytes(str_bytes)
        print(f"  Saved STR: {str_out.name} ({len(str_bytes)} bytes)")

    print("\nAll Hunter Rank Wings assets built successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
