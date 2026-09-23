#!/usr/bin/env python3
"""Build authentic Realistic Hunter Rank Badges from realistic_master.png (Static display, no artificial font overlays).

Ranks:
  E: Weathered Antique Bronze Shield with hunter markings (ID 208)
  D: Reinforced Iron Steel Shield with rivets & scratches (ID 209)
  C: Polished Silver with Starlight Cyan Gem & wings (ID 210)
  B: Royal 24k Gold with Midnight Sapphire Gems & wings (ID 211)
  A: Lustrous Platinum with Cyber Violet Amethyst & dual wings (ID 212)
  S: Sovereign Radiant Gold Crown with Starlight Diamonds & wings (ID 213)
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path
import numpy as np
from PIL import Image

TOOLS = Path(__file__).resolve().parent
ASSETS = TOOLS / "ui_sources/hunter_rank_badges"
TEXTURE_DIR = ASSETS / "textures"
EFFECT_DIR = ASSETS / "effects"
MASTER_SOURCE = ASSETS / "realistic_master.png"

TIERS = ("e", "d", "c", "b", "a", "s")
BASE_EFFECT_ID = 208

# In-game display dimensions: 24x24 pixels (authentic name-tag badge scale)
ART_WIDTH = 24.0
ART_HEIGHT = 24.0
FPS = 12
MAX_KEY = 24
KEYFRAME = struct.Struct("<II2f8f8ffIff4fIII")

# Offset for Option B (Right-side of Character Name)
Y_POS = 240.0

# Bounding boxes for each badge in realistic_master.png (1376 x 768)
BOUNDS = {
    "e": (30, 240, 235, 535),
    "d": (250, 240, 460, 535),
    "c": (470, 240, 685, 535),
    "b": (690, 240, 910, 535),
    "a": (912, 220, 1125, 535),
    "s": (1125, 200, 1365, 535),
}


def extract_alpha(crop: Image.Image) -> Image.Image:
    """Perform clean, anti-aliased alpha matting against pure pitch-black background."""
    arr = np.array(crop).astype(np.float32)
    rgb = arr[:, :, :3]
    max_c = np.max(rgb, axis=2)
    alpha = np.clip((max_c - 8.0) / (38.0 - 8.0), 0.0, 1.0)
    alpha = (alpha * 255.0).astype(np.uint8)
    res = crop.copy()
    res.putalpha(Image.fromarray(alpha))
    return res


def keyframe(frame: int, y: float = 240.0, opacity: float = 255.0) -> bytes:
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


def build_str(tier: str) -> bytes:
    """Generate a clean, static (no floating/bobbing) .str effect binary."""
    texture_name = f"hunter_rank_{tier}.tga".encode("ascii")
    texture_field = texture_name + bytes(128 - len(texture_name))

    # Static: constant Y position, constant 255.0 opacity (zero bobbing)
    frames = [
        keyframe(0, Y_POS, 255.0),
        interpolation(0, MAX_KEY, Y_POS, Y_POS, 255.0, 255.0),
        keyframe(MAX_KEY, Y_POS, 255.0),
    ]

    payload = bytearray(b"STRM")
    payload += struct.pack("<IIII", 0x94, FPS, MAX_KEY, 2)
    payload += bytes(24)
    payload += struct.pack("<I", 1)  # 1 texture layer
    payload += texture_field
    payload += struct.pack("<I", len(frames))
    payload += b"".join(frames)
    return bytes(payload)


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    TEXTURE_DIR.mkdir(parents=True, exist_ok=True)
    EFFECT_DIR.mkdir(parents=True, exist_ok=True)

    if not MASTER_SOURCE.is_file():
        print(f"Error: Missing master source at {MASTER_SOURCE}")
        return 1

    print("Building Authentic Realistic Hunter Rank Badges directly from realistic_master.png...")
    master_img = Image.open(MASTER_SOURCE).convert("RGBA")

    crops: dict[str, Image.Image] = {}
    for tier in TIERS:
        box = BOUNDS[tier]
        cropped = master_img.crop(box)
        badge_rgba = extract_alpha(cropped)

        # Pad to square canvas preserving aspect ratio
        bw, bh = badge_rgba.size
        dim = max(bw, bh) + 16
        canvas = Image.new("RGBA", (dim, dim), (0, 0, 0, 0))
        canvas.alpha_composite(badge_rgba, ((dim - bw) // 2, (dim - bh) // 2))

        # Save high-resolution master
        master_path = ASSETS / f"hunter_rank_{tier}_master.png"
        canvas.save(master_path, "PNG")

        # Downsample to 64x64 using Lanczos for clean in-game mip/resolution
        game_img = canvas.resize((64, 64), Image.Resampling.LANCZOS)
        tga_path = TEXTURE_DIR / f"hunter_rank_{tier}.tga"
        png_path = TEXTURE_DIR / f"hunter_rank_{tier}.png"
        game_img.save(png_path, "PNG")
        game_img.save(tga_path, "TGA")

        # Build static STR effect (no bobbing animation)
        str_data = build_str(tier)
        str_path = EFFECT_DIR / f"midnight_hunter_rank_{tier}.str"
        str_path.write_bytes(str_data)

        crops[tier] = game_img
        tga_hash = hashlib.sha256(tga_path.read_bytes()).hexdigest()[:10]
        str_hash = hashlib.sha256(str_data).hexdigest()[:10]
        print(f"  Rank {tier.upper()}: TGA={tga_path.name} ({tga_hash}) | STR={str_path.name} ({str_hash})")

    # Build updated combined preview sheet
    sheet = Image.new("RGBA", (64 * 6 + 12 * 7, 64 + 20), (22, 24, 30, 255))
    for i, tier in enumerate(TIERS):
        sheet.alpha_composite(crops[tier], (12 + i * 76, 10))
    sheet_path = ASSETS / "hunter_rank_badges_sheet.png"
    sheet.save(sheet_path, "PNG")
    print(f"\nAll 6 realistic badges built directly from master art. Sheet saved at {sheet_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
