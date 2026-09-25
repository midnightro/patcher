#!/usr/bin/env python3
"""Build and install Solo Leveling Abyss Shadow Midnight Gate sprites (IDs 10701..10706).

Features:
- Uses the authentic 15-frame cyclic animation loop (128x173) from fro_shadow_loop.gif.
- Applies tailored 4-stage cinematic color ramps for each gate rank:
  - 10701: gate_rank_e (Pale Cyan / Ethereal Ice Mist)
  - 10702: gate_rank_d (Emerald Green / Toxic Jade Abyss)
  - 10703: gate_rank_c (Amber Gold / Solar Radiant Flame)
  - 10704: gate_rank_b (Mystic Purple / Royal Amethyst Rift)
  - 10705: gate_rank_a (Crimson Blaze / Hellfire Ruby Gate)
  - 10706: gate_rank_s (Shadow Monarch Void & Electric Blue Corona)
- Builds custom 15-frame client-compliant ACT 0x0205 archives with grounded target_y=-70.
- Calibrates animation delay=3.5 (~75ms per frame) matching the source GIF rhythm.
- Encodes 15-frame 32-bit RGBA SPR v2.1 files.
- Preserves jobname.lub and npcidentity.lub registrations for IDs 10701..10706.
- Stages and updates MidnightROClient/midnight.grf cleanly.
"""

from __future__ import annotations

import io
import math
import os
import shutil
import struct
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageSequence

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
UI_SOURCES = TOOLS / "ui_sources" / "midnight_gate"
RAW_GIF = TOOLS / "scratch" / "fro_shadow_loop.gif"

sys.path.insert(0, str(TOOLS))
from grf import Grf  # noqa: E402
from lua51_inspect import Reader, parse_proto  # noqa: E402
from make_grf import build  # noqa: E402

MONSTER_DIR = b"data\\sprite\\\xb8\xf3\xbd\xba\xc5\xcd\\"
NPC_DIR = b"data\\sprite\\npc\\"
JOBNAME_KEY = b"data\\luafiles514\\lua files\\datainfo\\jobname.lub"
NPCIDENTITY_KEY = b"data\\luafiles514\\lua files\\datainfo\\npcidentity.lub"

GATE_RANKS = [
    (10701, "JT_GATE_RANK_E", "gate_rank_e", "Rank E", {
        "shadow": (8, 26, 42),
        "mid1": (22, 138, 220),
        "mid2": (65, 218, 255),
        "bright": (175, 245, 255),
        "core": (242, 255, 255),
    }),
    (10702, "JT_GATE_RANK_D", "gate_rank_d", "Rank D", {
        "shadow": (10, 36, 20),
        "mid1": (20, 155, 75),
        "mid2": (45, 238, 120),
        "bright": (150, 255, 190),
        "core": (235, 255, 245),
    }),
    (10703, "JT_GATE_RANK_C", "gate_rank_c", "Rank C", {
        "shadow": (45, 24, 6),
        "mid1": (215, 110, 15),
        "mid2": (255, 192, 30),
        "bright": (255, 238, 125),
        "core": (255, 252, 235),
    }),
    (10704, "JT_GATE_RANK_B", "gate_rank_b", "Rank B", {
        "shadow": (32, 10, 52),
        "mid1": (135, 35, 215),
        "mid2": (195, 75, 255),
        "bright": (230, 150, 255),
        "core": (252, 240, 255),
    }),
    (10705, "JT_GATE_RANK_A", "gate_rank_a", "Rank A", {
        "shadow": (48, 10, 10),
        "mid1": (218, 30, 20),
        "mid2": (255, 85, 25),
        "bright": (255, 180, 80),
        "core": (255, 245, 230),
    }),
    (10706, "JT_GATE_RANK_S", "gate_rank_s", "Rank S", {
        "shadow": (14, 5, 24),
        "mid1": (115, 18, 215),
        "mid2": (170, 45, 255),
        "bright": (70, 205, 255),  # Contrast Electric Blue / Cyan filaments
        "core": (235, 248, 255),
    }),
]


def load_source_frames() -> list[np.ndarray]:
    """Load the 15 raw RGB flame animation frames."""
    if RAW_GIF.exists():
        im = Image.open(RAW_GIF)
        return [np.array(f.convert("RGB"), dtype=np.float32) for f in ImageSequence.Iterator(im)]

    # Fallback to extracting official from_the_abyss_shadow textures from data.grf
    print("   Extracting fro_shadow frames from data.grf...")
    data_grf = Grf(DATA_GRF)
    frames = []
    try:
        for idx in range(15):
            entry_name = f"data\\texture\\effect\\from_the_abyss\\from_the_abyss_shadow\\fro_shadow_{idx:02d}.bmp".encode("latin-1")
            raw_data = data_grf.read(entry_name)
            img = Image.open(io.BytesIO(raw_data)).convert("RGB")
            frames.append(np.array(img, dtype=np.float32))
    finally:
        data_grf.close()
    return frames


def recolor_frame(rgb_arr: np.ndarray, theme: dict, frame_idx: int = 0) -> Image.Image:
    """Map raw shadow flame intensity into rank-tailored RGBA palette with soft alpha edges."""
    h, w, _ = rgb_arr.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)

    # Use max channel intensity
    val = np.maximum(np.maximum(rgb_arr[:, :, 0], rgb_arr[:, :, 1]), rgb_arr[:, :, 2]) / 255.0

    c_shadow = np.array(theme["shadow"], dtype=np.float32)
    c_mid1 = np.array(theme["mid1"], dtype=np.float32)
    c_mid2 = np.array(theme["mid2"], dtype=np.float32)
    c_bright = np.array(theme["bright"], dtype=np.float32)
    c_core = np.array(theme.get("core", (255, 255, 255)), dtype=np.float32)

    for y in range(h):
        for x in range(w):
            v = val[y, x]
            if v < 0.02:
                continue

            # Smooth anti-aliased alpha boundary
            if v < 0.12:
                t = (v - 0.02) / 0.10
                alpha = int(t * t * (3.0 - 2.0 * t) * 225)
            else:
                alpha = int(min(255, 225 + (v - 0.12) / 0.88 * 30))

            # Multi-stage color ramp
            if v < 0.25:
                # Shadow plume zone
                t = v / 0.25
                rgb = c_shadow * (1.0 - t) + c_mid1 * t
            elif v < 0.60:
                # Vibrant midtone flame zone
                t = (v - 0.25) / 0.35
                rgb = c_mid1 * (1.0 - t) + c_mid2 * t
            elif v < 0.85:
                # Fiery luminous crest
                t = (v - 0.60) / 0.25
                rgb = c_mid2 * (1.0 - t) + c_bright * t
            else:
                # Incandescent singularity core
                t = (v - 0.85) / 0.15
                rgb = c_bright * (1.0 - t) + c_core * t

            out[y, x] = [
                int(np.clip(rgb[0], 0, 255)),
                int(np.clip(rgb[1], 0, 255)),
                int(np.clip(rgb[2], 0, 255)),
                alpha,
            ]

    return Image.fromarray(out, "RGBA")


def build_gate_act(
    num_frames: int = 15,
    w: int = 128,
    h: int = 173,
    target_x: int = 0,
    target_y: int = -70,
    delay: float = 3.5,
) -> bytes:
    """Build a complete, client-compliant 10-action looping ACT archive for RGBA sprites."""
    num_actions = 10
    buf = bytearray()
    buf += b"AC"
    buf += struct.pack("<H", 0x0205)  # ACT version 2.5
    buf += struct.pack("<H", num_actions)
    buf += bytes(10)  # reserved

    for a in range(num_actions):
        buf += struct.pack("<I", num_frames)
        for f in range(num_frames):
            # Bounding box ranges (8 signed ints): min_x, min_y, max_x, max_y
            # Setting min_y=-150 ensures the NPC name label is placed nicely above the flame
            buf += struct.pack("<8i", -w // 2, -150, w // 2, 0, -w // 2, -150, w // 2, 0)
            # Clip count = 1
            buf += struct.pack("<I", 1)
            # Clip parameters: x, y, spr, flg, col, sx, sy, rot, ctype, w, h
            # ctype = 1 specifies RGBA (32-bit) sprite
            buf += struct.pack("<iiiiIffiiii", target_x, target_y, f, 0, 0xFFFFFFFF, 1.0, 1.0, 0, 1, w, h)
            # Sound index (-1 = none)
            buf += struct.pack("<i", -1)
            # Attach point count = 0
            buf += struct.pack("<I", 0)

    # Sound file count = 0
    buf += struct.pack("<I", 0)

    # Action delays (float32 per action)
    for a in range(num_actions):
        buf += struct.pack("<f", float(delay))

    return bytes(buf)


def encode_spr_rgba(frames: list[Image.Image], donor_palette: bytes) -> bytes:
    """Encode RGBA frames into Ragnarok Online SPR v2.1 format."""
    buf = bytearray()
    buf += b"SP"
    buf += struct.pack("<BB", 0x01, 0x02)  # v2.1
    buf += struct.pack("<HH", 0, len(frames))  # 0 indexed, N rgba frames

    for frame in frames:
        # Ragnarok Online client RGBA sprites require bottom-up scanline ordering
        flipped_frame = frame.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        w, h = flipped_frame.size
        buf += struct.pack("<HH", w, h)
        raw_rgba = flipped_frame.tobytes("raw", "RGBA")
        # Convert RGBA to ABGR
        abgr = bytearray(w * h * 4)
        for i in range(0, len(raw_rgba), 4):
            r, g, b, a = raw_rgba[i], raw_rgba[i + 1], raw_rgba[i + 2], raw_rgba[i + 3]
            abgr[i] = a
            abgr[i + 1] = b
            abgr[i + 2] = g
            abgr[i + 3] = r
        buf += abgr

    # Append 1024-byte palette at end of SPR
    if len(donor_palette) == 1024:
        buf += donor_palette
    else:
        pal = bytearray(1024)
        buf += pal

    return bytes(buf)


def patch_jobname_lub(job_entries: list[tuple[int, str]]) -> bytes:
    """Patch jobname.lub to register JobNameTable entries."""
    target_grf = Grf(TARGET_GRF)
    try:
        raw = target_grf.read(JOBNAME_KEY)
    finally:
        target_grf.close()

    p = parse_proto(Reader(raw))

    def encode_abx(op, a, bx):
        return (bx << 14) | (a << 6) | op

    def encode_abc(op, a, b, c):
        return (b << 23) | (c << 14) | (a << 6) | op

    # Check already registered
    existing_ids = {int(c) for c in p["constants"] if isinstance(c, (int, float))}
    entries_to_add = [(jid, name) for jid, name in job_entries if jid not in existing_ids]

    for job_id, sprite_name in entries_to_add:
        idx_id = len(p["constants"])
        p["constants"].append(float(job_id))
        idx_name = len(p["constants"])
        p["constants"].append(sprite_name.encode("latin-1"))

        inst1 = encode_abx(1, 1, idx_id)
        inst2 = encode_abx(1, 2, idx_name)
        inst3 = encode_abc(9, 0, 1, 2)

        p["code"].insert(-2, inst1)
        p["code"].insert(-2, inst2)
        p["code"].insert(-2, inst3)
        if p["lineinfo"]:
            p["lineinfo"].insert(-2, 0)
            p["lineinfo"].insert(-2, 0)
            p["lineinfo"].insert(-2, 0)

    def pack_proto_chunk(proto, is_top=False):
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

    patched = raw[:12] + pack_proto_chunk(p, True)
    _ = parse_proto(Reader(patched))
    return patched


def patch_npcidentity_lub(identity_entries: list[tuple[str, int]]) -> bytes:
    """Patch npcidentity.lub to register jobtbl[JT_NAME] = ID."""
    target_grf = Grf(TARGET_GRF)
    try:
        if NPCIDENTITY_KEY in target_grf.entries:
            raw = target_grf.read(NPCIDENTITY_KEY)
        else:
            data_grf = Grf(DATA_GRF)
            try:
                raw = data_grf.read(NPCIDENTITY_KEY)
            finally:
                data_grf.close()
    finally:
        target_grf.close()

    p = parse_proto(Reader(raw))

    def encode_abx(op, a, bx):
        return (bx << 14) | (a << 6) | op

    def encode_abc(op, a, b, c):
        return (b << 23) | (c << 14) | (a << 6) | op

    existing_names = {c.decode("latin-1") for c in p["constants"] if isinstance(c, bytes)}
    entries_to_add = [(name, jid) for name, jid in identity_entries if name not in existing_names]

    for jt_name, job_id in entries_to_add:
        idx_name = len(p["constants"])
        p["constants"].append(jt_name.encode("latin-1"))
        idx_id = len(p["constants"])
        p["constants"].append(float(job_id))

        inst1 = encode_abx(1, 1, idx_name)
        inst2 = encode_abx(1, 2, idx_id)
        inst3 = encode_abc(9, 0, 1, 2)

        p["code"].insert(-2, inst1)
        p["code"].insert(-2, inst2)
        p["code"].insert(-2, inst3)
        if p["lineinfo"]:
            p["lineinfo"].insert(-2, 0)
            p["lineinfo"].insert(-2, 0)
            p["lineinfo"].insert(-2, 0)

    def pack_proto_chunk(proto, is_top=False):
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

    patched = raw[:12] + pack_proto_chunk(p, True)
    _ = parse_proto(Reader(patched))
    return patched


def main():
    print("=== Building Solo Leveling Abyss Shadow Midnight Gate Sprites (15 Frames) ===")
    UI_SOURCES.mkdir(parents=True, exist_ok=True)

    # 1. Fetch donor palette and load raw 15 flame animation frames
    print("1. Extracting donor palette from data.grf...")
    data_grf = Grf(DATA_GRF)
    try:
        donor_spr = data_grf.read(b"data\\sprite\\npc\\4_energy_blue.spr")
        donor_palette = donor_spr[-1024:]
    finally:
        data_grf.close()

    print("2. Loading 15-frame raw flame animation...")
    raw_frames = load_source_frames()
    num_frames = len(raw_frames)
    h_frame, w_frame, _ = raw_frames[0].shape
    print(f"   Loaded {num_frames} frames ({w_frame}x{h_frame})")

    # Build 15-frame ACT file
    gate_act = build_gate_act(
        num_frames=num_frames,
        w=w_frame,
        h=h_frame,
        target_x=0,
        target_y=-70,
        delay=3.5,
    )
    print(f"   Generated 15-frame ACT ({len(gate_act)} bytes, grounded target_y=-70, delay=3.5)")

    # 3. Generate animations for all 6 Ranks
    gate_assets = {}
    preview_montage_frames = []

    print("3. Rendering flame frames for each rank...")
    for job_id, jt_name, sprite_name, label, theme in GATE_RANKS:
        print(f"   Generating {label} ({sprite_name})...")
        frames = []
        rank_dir = UI_SOURCES / sprite_name
        rank_dir.mkdir(parents=True, exist_ok=True)

        for f_idx, raw_f in enumerate(raw_frames):
            frame_img = recolor_frame(raw_f, theme, f_idx)
            frames.append(frame_img)
            frame_img.save(rank_dir / f"frame_{f_idx:02d}.png")

        # Save animated GIF preview (70ms duration)
        gif_path = rank_dir / f"{sprite_name}_preview.gif"
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=70,
            loop=0,
            disposal=2,
        )

        spr_bytes = encode_spr_rgba(frames, donor_palette)
        (rank_dir / f"{sprite_name}.spr").write_bytes(spr_bytes)
        (rank_dir / f"{sprite_name}.act").write_bytes(gate_act)
        gate_assets[job_id] = (spr_bytes, gate_act)
        print(f"      Saved {sprite_name}.spr ({len(spr_bytes)} bytes) + act ({len(gate_act)} bytes)")

    # 4. Patch jobname.lub and npcidentity.lub
    print("4. Patching jobname.lub and npcidentity.lub with IDs 10701..10706...")
    new_jobs = [(job_id, sprite_name) for job_id, _, sprite_name, _, _ in GATE_RANKS]
    patched_jobname = patch_jobname_lub(new_jobs)
    (UI_SOURCES / "jobname.lub").write_bytes(patched_jobname)

    new_identities = [(jt_name, job_id) for job_id, jt_name, _, _, _ in GATE_RANKS]
    patched_npcidentity = patch_npcidentity_lub(new_identities)
    (UI_SOURCES / "npcidentity.lub").write_bytes(patched_npcidentity)
    print("   Patched jobname.lub and npcidentity.lub successfully!")

    # 5. Package assets into MidnightROClient/midnight.grf
    print("5. Packaging assets into MidnightROClient/midnight.grf...")
    target_grf = Grf(TARGET_GRF)
    all_files = {}
    try:
        for entry in target_grf.entries:
            all_files[entry] = target_grf.read(entry)
    finally:
        target_grf.close()

    # Inject sprites in both NPC and Monster directories
    for job_id, jt_name, sprite_name, _, _ in GATE_RANKS:
        spr_bytes, act_bytes = gate_assets[job_id]
        # NPC directory
        all_files[NPC_DIR + sprite_name.encode("cp949") + b".spr"] = spr_bytes
        all_files[NPC_DIR + sprite_name.encode("cp949") + b".act"] = act_bytes
        # Monster directory
        all_files[MONSTER_DIR + sprite_name.encode("cp949") + b".spr"] = spr_bytes
        all_files[MONSTER_DIR + sprite_name.encode("cp949") + b".act"] = act_bytes

    all_files[JOBNAME_KEY] = patched_jobname
    all_files[NPCIDENTITY_KEY] = patched_npcidentity

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"   Built staged GRF: {staged_grf}")

    try:
        staged_grf.replace(TARGET_GRF)
        print("   Successfully updated Dev client midnight.grf (MidnightROClient/midnight.grf)!")
    except PermissionError:
        print("   WARNING: midnight.grf is locked by a running client process. Staged at midnight.grf.staged")

    print("\n=== All Solo Leveling Abyss Shadow Gate Sprites successfully created & installed! ===")


if __name__ == "__main__":
    main()
