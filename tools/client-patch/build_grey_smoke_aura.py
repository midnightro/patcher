#!/usr/bin/env python3
"""Build dense organic dark obsidian smoke mist aura for [Hunter Rank S] Monarch's Shadow Aura.

Solves user request:
- 100% Organic volumetric billowing dark smoke plumes (NO geometric shapes, NO fake polygons)
- Intermittent thin electric cyan lightning threads crackling through the smoke
- True 360-degree surrounding depth (back + front layers)
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path
from PIL import Image
import numpy as np

TOOLS = Path(__file__).resolve().parent
SOURCES = TOOLS / "ui_sources/solo_leveling_hunter_set"
KEYFRAME = struct.Struct("<II2f8f8ffIff4fIII")


def write_tga_32(img: Image.Image, out_path: Path) -> None:
    """Write uncompressed 32-bit RGBA TGA file (bottom-left origin)."""
    w, h = img.size
    rgba = img.convert("RGBA")
    r, g, b, a = rgba.split()
    bgra = Image.merge("RGBA", (b, g, r, a))

    header = bytearray(18)
    header[2] = 2  # uncompressed true-color
    struct.pack_into("<HHBB", header, 12, w, h, 32, 8)
    flipped = bgra.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    out_path.write_bytes(bytes(header) + flipped.tobytes())


def make_static_layer(
    textures: list[str],
    max_key: int,
    half_w: float,
    half_h: float,
    pos_x: float,
    pos_y: float,
    anim_type: int,
    anim_speed: float,
    color: tuple[float, float, float, float],
    blend: tuple[int, int, int],
    angle: float = 0.0,
) -> bytes:
    tex_data = bytearray()
    tex_data += struct.pack("<I", len(textures))
    for t in textures:
        raw_t = t.encode("latin-1")
        tex_data += raw_t + bytes(128 - len(raw_t))

    r, g, b, a = color
    b1, b2, b3 = blend

    k0 = KEYFRAME.pack(
        0, 0,
        pos_x, pos_y,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
        -half_w, half_w, half_w, -half_w,
        -half_h, -half_h, half_h, half_h,
        angle,
        anim_type, anim_speed, angle,
        r, g, b, a,
        b1, b2, b3
    )

    k1 = KEYFRAME.pack(
        0, 1,
        0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0,
        anim_type, anim_speed, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0, 0, 0
    )

    k_end = KEYFRAME.pack(
        max_key, 0,
        pos_x, pos_y,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
        -half_w, half_w, half_w, -half_w,
        -half_h, -half_h, half_h, half_h,
        angle,
        anim_type, anim_speed, angle,
        r, g, b, a,
        b1, b2, b3
    )

    keys_data = struct.pack("<I", 3) + k0 + k1 + k_end
    return bytes(tex_data + keys_data)


def make_timeline_layer(
    textures: list[str],
    max_key: int,
    half_w: float,
    half_h: float,
    pos_x: float,
    pos_y: float,
    anim_type: int,
    anim_speed: float,
    rgb: tuple[float, float, float],
    blend: tuple[int, int, int],
    timeline: list[tuple[int, float]],
    angle: float = 0.0,
) -> bytes:
    """Build multi-keyframe animated layer for intermittent timed lightning."""
    tex_data = bytearray()
    tex_data += struct.pack("<I", len(textures))
    for t in textures:
        raw_t = t.encode("latin-1")
        tex_data += raw_t + bytes(128 - len(raw_t))

    r, g, b = rgb
    b1, b2, b3 = blend
    keys_buf = bytearray()

    for i in range(len(timeline) - 1):
        f_curr, op_curr = timeline[i]
        f_next, op_next = timeline[i + 1]
        dur = max(1, f_next - f_curr)
        d_op = (op_next - op_curr) / dur

        k0 = KEYFRAME.pack(
            f_curr, 0,
            pos_x, pos_y,
            0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
            -half_w, half_w, half_w, -half_w,
            -half_h, -half_h, half_h, half_h,
            angle,
            anim_type, anim_speed, angle,
            r, g, b, op_curr,
            b1, b2, b3
        )
        keys_buf += k0

        k1 = KEYFRAME.pack(
            f_curr, 1,
            0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
            0.0,
            anim_type, anim_speed, 0.0,
            0.0, 0.0, 0.0, d_op,
            0, 0, 0
        )
        keys_buf += k1

    f_end, op_end = timeline[-1]
    k_end = KEYFRAME.pack(
        f_end, 0,
        pos_x, pos_y,
        0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0,
        -half_w, half_w, half_w, -half_w,
        -half_h, -half_h, half_h, half_h,
        angle,
        anim_type, anim_speed, angle,
        r, g, b, op_end,
        b1, b2, b3
    )
    keys_buf += k_end

    total_keys = (len(timeline) - 1) * 2 + 1
    return bytes(tex_data + struct.pack("<I", total_keys) + keys_buf)


def build_str(layers: list[bytes], max_key: int = 60, fps: int = 60) -> bytes:
    payload = bytearray(b"STRM")
    stored_layers = len(layers) + 1
    payload += struct.pack("<IIII", 0x94, fps, max_key, stored_layers)
    payload += bytes(24)  # 6 reserved ints
    for l in layers:
        payload += l
    return bytes(payload)


def generate_smoke_textures() -> list[Path]:
    """Generate 12 seamless frames of dense, majestic dark obsidian smoke plumes."""
    print("Generating 12 frames of dense dark obsidian smoke plumes for Rank S...")
    raw_frames = [Image.open(SOURCES / f"sha_smk_{i:02d}.png") for i in range(6)]

    enhanced = []
    for f in raw_frames:
        arr = np.array(f, dtype=np.float32)
        gray = arr[..., 0]
        # Deep dark obsidian charcoal [22..58]
        new_gray = 22.0 + (gray / 175.0) * 36.0
        arr[..., 0] = new_gray
        arr[..., 1] = new_gray * 1.02
        arr[..., 2] = new_gray * 1.08
        # High-density alpha curve: solid opaque core, beautifully feathered wispy tips
        alpha = arr[..., 3]
        alpha_norm = alpha / 255.0
        alpha_dense = np.clip((alpha_norm ** 0.52) * 255.0, 0.0, 255.0)
        arr[..., 3] = alpha_dense
        enhanced.append(Image.fromarray(arr.astype(np.uint8), "RGBA"))

    W, H = 140, 180
    smoke_paths = []

    for k in range(12):
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))

        # Plume 1: Left surging smoke pillar
        p1 = enhanced[k % 6].resize((88, 140), Image.Resampling.BILINEAR)
        canvas.paste(p1, (6, 18), p1)

        # Plume 2: Right surging smoke pillar (time-shifted by 3 frames, flipped)
        p2 = enhanced[(k + 3) % 6].resize((88, 140), Image.Resampling.BILINEAR).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        canvas.paste(p2, (46, 12), p2)

        # Plume 3: Center rising plume
        p3 = enhanced[(k + 1) % 6].resize((82, 145), Image.Resampling.BILINEAR)
        canvas.paste(p3, (28, 20), p3)

        # Plume 4: Ground/waist billow
        p4 = enhanced[(k + 4) % 6].resize((90, 110), Image.Resampling.BILINEAR)
        canvas.paste(p4, (25, 60), p4)

        out_tga = SOURCES / f"midnight_monarch_mist_{k:02d}.tga"
        write_tga_32(canvas, out_tga)
        smoke_paths.append(out_tga)

    print(f"  Saved 12 dense smoke textures: midnight_monarch_mist_00.tga .. 11.tga ({W}x{H})")
    return smoke_paths


def build_str_effects() -> None:
    """Build back and front STR files with dense volumetric depth and intermittent lightning."""
    print("\nBuilding Rank S dense volumetric STR effect files...")

    smoke_tex_names = [f"midnight_monarch_mist_{i:02d}.tga" for i in range(12)]
    bolt_tex_names = [f"midnight_monarch_bolt_{i:02d}.tga" for i in range(4)]

    # -------------------------------------------------------------------------
    # 1. Back STR (HatEffect 217, rendered behind character)
    # -------------------------------------------------------------------------
    # Layer 0: Dense surging dark shadow smoke pillar (Rank S Majesty!)
    back_smoke_core = make_static_layer(
        textures=smoke_tex_names,
        max_key=60,
        half_w=54.0,
        half_h=68.0,
        pos_x=320.0,
        pos_y=236.0,
        anim_type=2,
        anim_speed=0.22,
        color=(255.0, 255.0, 255.0, 235.0),
        blend=(5, 6, 0),  # Alpha blend
        angle=0.0,
    )

    # Layer 1: Wider volumetric outer smoke layer (asymmetric billowing)
    back_smoke_outer = make_static_layer(
        textures=smoke_tex_names,
        max_key=60,
        half_w=62.0,
        half_h=74.0,
        pos_x=320.0,
        pos_y=234.0,
        anim_type=2,
        anim_speed=0.26,
        color=(255.0, 255.0, 255.0, 160.0),
        blend=(5, 6, 0),
        angle=0.0,
    )

    # Layer 2: Intermittent thin electric cyan lightning crackles behind shoulders
    timeline_back_bolt = [
        (0, 0.0),       # silent / hidden
        (13, 0.0),      # dormant
        (16, 190.0),    # spark flickers on
        (20, 255.0),    # peak lightning flare
        (25, 0.0),      # extinguish
        (40, 0.0),      # dormant
        (43, 210.0),    # second electrical zap
        (48, 0.0),      # extinguish
        (60, 0.0),      # silent until loop restart
    ]
    back_bolt = make_timeline_layer(
        textures=bolt_tex_names,
        max_key=60,
        half_w=40.0,
        half_h=42.0,
        pos_x=318.0,
        pos_y=232.0,
        anim_type=3,
        anim_speed=0.30,
        rgb=(0.0, 235.0, 255.0),
        blend=(5, 7, 0),  # Additive glow
        timeline=timeline_back_bolt,
        angle=0.0,
    )

    back_str_bytes = build_str([back_smoke_core, back_smoke_outer, back_bolt], max_key=60, fps=60)
    back_str_path = SOURCES / "midnight_monarch_shadow_back.str"
    back_str_path.write_bytes(back_str_bytes)
    print(f"  Saved {back_str_path.name} ({len(back_str_bytes)} bytes)")

    # -------------------------------------------------------------------------
    # 2. Front STR (HatEffect 218, rendered in front of character)
    # -------------------------------------------------------------------------
    # Layer 0: Front shadow smoke billow curling across waist/lower body (dense enough to be clearly seen!)
    front_smoke = make_static_layer(
        textures=smoke_tex_names,
        max_key=60,
        half_w=42.0,
        half_h=48.0,
        pos_x=320.0,
        pos_y=256.0,
        anim_type=2,
        anim_speed=0.22,
        color=(255.0, 255.0, 255.0, 150.0),
        blend=(5, 6, 0),
        angle=0.0,
    )

    # Layer 1: Front intermittent thin electric cyan lightning across lower body
    timeline_front_bolt = [
        (0, 0.0),       # silent
        (27, 0.0),      # dormant
        (30, 200.0),    # foreground crackle starts
        (34, 255.0),    # peak foreground spark
        (39, 0.0),      # extinguish
        (60, 0.0),      # dormant until loop restart
    ]
    front_bolt = make_timeline_layer(
        textures=bolt_tex_names,
        max_key=60,
        half_w=36.0,
        half_h=38.0,
        pos_x=322.0,
        pos_y=250.0,
        anim_type=3,
        anim_speed=0.32,
        rgb=(0.0, 235.0, 255.0),
        blend=(5, 7, 0),
        timeline=timeline_front_bolt,
        angle=0.0,
    )

    front_str_bytes = build_str([front_smoke, front_bolt], max_key=60, fps=60)
    front_str_path = SOURCES / "midnight_monarch_shadow_front.str"
    front_str_path.write_bytes(front_str_bytes)
    print(f"  Saved {front_str_path.name} ({len(front_str_bytes)} bytes)")


def main() -> int:
    generate_smoke_textures()
    build_str_effects()
    print("\nRank S dense dark smoke aura successfully built!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
