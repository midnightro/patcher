#!/usr/bin/env python3
"""Build and install Solo Leveling style Midnight Gate sprites (IDs 25111..25116).

Features:
- Procedurally crafts 10-frame cyclic RGBA animations (155x210) for each rank:
  - 25111: gate_rank_e (Pale Cyan / Ethereal Mist)
  - 25112: gate_rank_d (Emerald Green Magical Abyss)
  - 25113: gate_rank_c (Amber Gold Radiant Vortex)
  - 25114: gate_rank_b (Mystic Amethyst Purple Aura)
  - 25115: gate_rank_a (Crimson Blaze & Sparks)
  - 25116: gate_rank_s (Shadow Monarch Void & Crackling Electric Lightning)
- Employs calibrated 4_energy_blue.act donor action for smooth client looping.
- Patches jobname.lub with IDs 25111..25116.
- Stages and updates MidnightROClient/midnight.grf cleanly.
"""

from __future__ import annotations

import math
import os
import random
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
UI_SOURCES = TOOLS / "ui_sources" / "midnight_gate"

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
        "core_dark": (5, 15, 25),
        "swirl_main": (120, 220, 255),
        "swirl_alt": (55, 150, 220),
        "outer_edge": (170, 240, 255),
        "mist_color": (30, 80, 130),
        "spark_color": (220, 250, 255),
        "lightning": False,
    }),
    (10702, "JT_GATE_RANK_D", "gate_rank_d", "Rank D", {
        "core_dark": (5, 25, 15),
        "swirl_main": (50, 240, 140),
        "swirl_alt": (20, 170, 90),
        "outer_edge": (130, 255, 185),
        "mist_color": (15, 75, 45),
        "spark_color": (200, 255, 220),
        "lightning": False,
    }),
    (10703, "JT_GATE_RANK_C", "gate_rank_c", "Rank C", {
        "core_dark": (25, 15, 5),
        "swirl_main": (255, 195, 45),
        "swirl_alt": (235, 135, 20),
        "outer_edge": (255, 235, 120),
        "mist_color": (80, 50, 15),
        "spark_color": (255, 245, 180),
        "lightning": False,
    }),
    (10704, "JT_GATE_RANK_B", "gate_rank_b", "Rank B", {
        "core_dark": (20, 5, 30),
        "swirl_main": (195, 75, 255),
        "swirl_alt": (135, 35, 215),
        "outer_edge": (225, 140, 255),
        "mist_color": (65, 15, 85),
        "spark_color": (245, 200, 255),
        "lightning": False,
    }),
    (10705, "JT_GATE_RANK_A", "gate_rank_a", "Rank A", {
        "core_dark": (35, 5, 5),
        "swirl_main": (255, 50, 30),
        "swirl_alt": (255, 110, 35),
        "outer_edge": (255, 160, 80),
        "mist_color": (90, 20, 15),
        "spark_color": (255, 220, 160),
        "lightning": False,
    }),
    (10706, "JT_GATE_RANK_S", "gate_rank_s", "Rank S", {
        "core_dark": (0, 0, 0),
        "swirl_main": (175, 40, 255),
        "swirl_alt": (60, 190, 255),
        "outer_edge": (210, 90, 255),
        "mist_color": (25, 5, 40),
        "spark_color": (210, 240, 255),
        "lightning": True,
    }),
]


def fbm_val(x: float, y: float, phase: float) -> float:
    """Harmonic multi-octave periodic noise (seamless over phase in [0, 2*pi])."""
    v1 = math.sin(x + math.sin(phase) * 0.7) * math.cos(y + math.cos(phase) * 0.7)
    v2 = math.sin(2.0 * x - y + phase) * 0.5
    v3 = math.cos(3.0 * y + 2.0 * x - phase) * 0.25
    return (v1 + v2 + v3) / 1.75


def render_gate_frame(frame_idx: int, total_frames: int, theme: dict) -> Image.Image:
    """Render a thrilling, authentic Solo Leveling dimensional dungeon gate frame."""
    w, h = 160, 240
    cx, cy = 80, 114
    rx, ry = 44, 82

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pixels = img.load()

    phase = (frame_idx / float(total_frames)) * 2.0 * math.pi
    sin_p = math.sin(phase)
    cos_p = math.cos(phase)

    core_dark = theme["core_dark"]
    swirl_main = theme["swirl_main"]
    swirl_alt = theme["swirl_alt"]
    outer_edge = theme["outer_edge"]
    mist_color = theme["mist_color"]
    spark_col = theme["spark_color"]

    # Breathing heartbeat of the rift
    pulse = sin_p * 0.04

    for y in range(h):
        dy = (y - cy) / float(ry)
        dy2 = dy * dy
        if dy2 > 2.6:
            continue

        for x in range(w):
            dx = (x - cx) / float(rx)
            dist = math.sqrt(dx * dx + dy2)

            # Ground mist pool on pavement below gate
            if dist > 1.55:
                if 176 <= y <= 226 and abs(x - cx) < 56:
                    gf = (y - 176) / 50.0
                    spread = 18.0 + 28.0 * math.sin(gf * math.pi)
                    dfc = abs(x - cx)
                    if dfc < spread:
                        alpha = int((95.0 + 25.0 * sin_p) * (1.0 - gf) * (1.0 - dfc / spread))
                        if alpha > 5:
                            pixels[x, y] = (mist_color[0], mist_color[1], mist_color[2], min(160, alpha))
                continue

            angle = math.atan2(dy, dx)
            
            # Tear geometry: upright oval tapering into an anchor point at bottom
            tear_taper = (1.0 - 0.18 * dy) if dy > 0 else 1.0
            
            # Rising smoke/flames at the top (dy < -0.5)
            flame_reach = 1.0
            if dy < -0.5:
                f_noise = fbm_val(dx * 4.0, dy * 3.0 - phase, phase)
                flame_lift = max(0.0, -dy - 0.5) * 0.5 * (f_noise + 1.0)
                flame_reach += flame_lift

            boundary_wobble = 1.0 + 0.02 * math.sin(3.0 * angle + phase) + pulse
            eff_dist = dist / (tear_taper * flame_reach * boundary_wobble)

            # Domain warped cosmic vortex (fluid dynamics, NO propeller fan blades!)
            swirl_strength = 2.4 * max(0.0, 1.0 - eff_dist)
            rot_x = dx * math.cos(swirl_strength) - dy * math.sin(swirl_strength)
            rot_y = dx * math.sin(swirl_strength) + dy * math.cos(swirl_strength)

            flow_y = rot_y * 2.4 - dy * 0.7
            flow_x = rot_x * 2.4

            w1_x = fbm_val(flow_x + 1.2, flow_y - 0.5, phase)
            w1_y = fbm_val(flow_x - 0.8, flow_y + 1.1, phase)

            turb = fbm_val(flow_x + 1.8 * w1_x, flow_y + 1.8 * w1_y, phase)
            turb_val = (turb + 1.0) * 0.5  # 0.0 to 1.0

            # 1. Outer Miasma / Billowing Smoke Aura (1.0 < eff_dist <= 1.50)
            if eff_dist > 1.0:
                mist_f = max(0.0, min(1.0, (1.50 - eff_dist) / 0.50))
                up_bias = max(0.0, -dy * 0.5)
                flicker = 0.70 + 0.30 * turb_val
                alpha = int(185.0 * (mist_f ** 1.3) * (0.60 + up_bias) * flicker)
                if alpha > 8:
                    if eff_dist < 1.10:
                        # Dark void shadow silhouette edge
                        b_t = (eff_dist - 1.0) / 0.10
                        r = int(core_dark[0] * (1.0 - b_t) + mist_color[0] * b_t)
                        g = int(core_dark[1] * (1.0 - b_t) + mist_color[1] * b_t)
                        b = int(core_dark[2] * (1.0 - b_t) + mist_color[2] * b_t)
                        pixels[x, y] = (r, g, b, min(245, alpha + 45))
                    else:
                        pixels[x, y] = (mist_color[0], mist_color[1], mist_color[2], min(220, alpha))
                continue

            # 2. INSIDE THE RIFT (eff_dist <= 1.0)
            # Center Singularity (pitch black event horizon)
            core_rad = 0.19 + 0.02 * sin_p
            if eff_dist < core_rad:
                sing_t = eff_dist / core_rad
                r = int(core_dark[0] * sing_t * 0.35)
                g = int(core_dark[1] * sing_t * 0.35)
                b = int(core_dark[2] * sing_t * 0.35)
                pixels[x, y] = (r, g, b, 255)

            # Glowing Event Horizon Corona (0.80 <= eff_dist <= 1.0)
            elif eff_dist > 0.80:
                rim_t = (eff_dist - 0.80) / 0.20
                corona_glow = 0.82 + 0.18 * turb_val + 0.1 * sin_p
                r = min(255, int(outer_edge[0] * corona_glow))
                g = min(255, int(outer_edge[1] * corona_glow))
                b = min(255, int(outer_edge[2] * corona_glow))
                pixels[x, y] = (r, g, b, 255)

            # Turbulent Cosmic Nebula Mantle (core_rad <= eff_dist <= 0.80)
            else:
                mantle_t = (eff_dist - core_rad) / (0.80 - core_rad)
                
                # Dynamic rich fluid color blending
                if mantle_t < 0.45:
                    st = mantle_t / 0.45
                    base_r = int(core_dark[0] * (1.0 - st) + swirl_alt[0] * st)
                    base_g = int(core_dark[1] * (1.0 - st) + swirl_alt[1] * st)
                    base_b = int(core_dark[2] * (1.0 - st) + swirl_alt[2] * st)
                else:
                    st = (mantle_t - 0.45) / 0.55
                    base_r = int(swirl_alt[0] * (1.0 - st) + swirl_main[0] * st)
                    base_g = int(swirl_alt[1] * (1.0 - st) + swirl_main[1] * st)
                    base_b = int(swirl_alt[2] * (1.0 - st) + swirl_main[2] * st)

                # Brilliant plasma flares & filaments
                flare = (turb_val ** 1.6) * (0.35 + 0.65 * mantle_t)
                r = min(255, int(base_r + (outer_edge[0] - base_r) * flare))
                g = min(255, int(base_g + (outer_edge[1] - base_g) * flare))
                b = min(255, int(base_b + (outer_edge[2] - base_b) * flare))
                pixels[x, y] = (r, g, b, 250)

    draw = ImageDraw.Draw(img)

    # 3. Ground Anchor: Dark shadow root spike and soft pavement mist puddle
    draw.ellipse([(cx - 26, 213), (cx + 26, 224)], fill=(mist_color[0], mist_color[1], mist_color[2], int(70 + 20 * sin_p)))
    anchor_poly = [(cx - 7, cy + ry - 8), (cx + 7, cy + ry - 8), (cx, 218)]
    draw.polygon(anchor_poly, fill=(core_dark[0], core_dark[1], core_dark[2], 250))
    draw.line([(cx, cy + ry - 10), (cx, 218)], fill=(outer_edge[0], outer_edge[1], outer_edge[2], 230), width=2)

    # 4. Floating Mana Embers (Rising continuously with vertical convection)
    for i in range(12):
        base_x = cx + rx * (0.95 + 0.22 * math.cos(i * 2.1)) * (1.0 if i % 2 == 0 else -1.0)
        y_cycle = (float(i) / 12.0 + phase / (2.0 * math.pi)) % 1.0
        py = int((cy + ry + 8) - y_cycle * (2.0 * ry + 30))
        px = int(base_x + 5.0 * math.sin(y_cycle * 4.0 * math.pi + i))

        if 2 <= px < w - 2 and 2 <= py < h - 2:
            ember_fade = math.sin(y_cycle * math.pi)
            p_alpha = int(220 * ember_fade)
            if p_alpha > 20:
                c_fill = (spark_col[0], spark_col[1], spark_col[2], p_alpha)
                draw.polygon([(px, py - 2), (px + 2, py), (px, py + 2), (px - 2, py)], fill=c_fill)

    # 5. Rank S: Explosive Jagged Neon Lightning Arcs
    if theme.get("lightning"):
        for l in range(4):
            l_phase = phase * 2.0 + l * 1.57
            l_angle = (l / 4.0) * 2.0 * math.pi + 0.2 * math.sin(l_phase)
            
            sx = cx + rx * 0.85 * math.cos(l_angle)
            sy = cy + ry * 0.85 * math.sin(l_angle)

            reach = 16.0 + 10.0 * math.sin(l_phase + 1.0)
            ex = cx + (rx + reach) * math.cos(l_angle + 0.25 * math.sin(phase + l))
            ey = cy + (ry + reach) * math.sin(l_angle + 0.25 * math.sin(phase + l))

            b1_x = sx * 0.75 + ex * 0.25 + math.sin(phase * 3.0 + l * 2.7) * 6.0
            b1_y = sy * 0.75 + ey * 0.25 + math.cos(phase * 3.0 + l * 2.7) * 6.0
            b2_x = sx * 0.50 + ex * 0.50 - math.cos(phase * 3.0 + l * 1.9) * 7.0
            b2_y = sy * 0.50 + ey * 0.50 + math.sin(phase * 3.0 + l * 1.9) * 7.0
            b3_x = sx * 0.25 + ex * 0.75 + math.sin(phase * 4.0 + l * 3.1) * 5.0
            b3_y = sy * 0.25 + ey * 0.75 - math.cos(phase * 4.0 + l * 3.1) * 5.0

            l_col = (170, 240, 255, 250) if l % 2 == 0 else (245, 130, 255, 250)
            draw.line([(sx, sy), (b1_x, b1_y), (b2_x, b2_y), (b3_x, b3_y), (ex, ey)], fill=l_col, width=2)
            draw.point((int(sx), int(sy)), fill=(255, 255, 255, 255))
            draw.point((int(ex), int(ey)), fill=(255, 255, 255, 255))

    return img


def encode_spr_rgba(frames: list[Image.Image], donor_palette: bytes) -> bytes:
    """Encode RGBA frames into Ragnarok Online SPR v2.1 format."""
    buf = bytearray()
    buf += b"SP"
    buf += struct.pack("<BB", 0x01, 0x02)  # v2.1
    buf += struct.pack("<HH", 0, len(frames))  # 0 indexed, N rgba frames

    for frame in frames:
        # Ragnarok Online client RGBA sprites require bottom-up scanline ordering
        flipped_frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
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
        # Generate dummy 1024-byte palette
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

    for job_id, sprite_name in job_entries:
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

    for jt_name, job_id in identity_entries:
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


def scale_act_bytes(donor_act: bytes, scale_factor: float = 1.0, target_y: int = -96, target_x: int = 0, delay: float = 8.0) -> bytes:
    """Scale all clips in an ACT 0x0205 archive, position base on ground, and set animation delay."""
    act = bytearray(donor_act)
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
                x, y, spr, flg, col, sx, sy, rot, ctype, w, h = struct.unpack_from('<iiiiIffiiii', act, pos)
                new_x = target_x
                new_y = target_y
                new_sx = sx * scale_factor
                new_sy = sy * scale_factor
                new_w = int(160 * scale_factor)
                new_h = int(240 * scale_factor)
                struct.pack_into('<iiiiIffiiii', act, pos, new_x, new_y, spr, flg, col, new_sx, new_sy, rot, ctype, new_w, new_h)
                pos += 44
            pos += 4
            att = struct.unpack_from('<I', act, pos)[0]
            pos += 4 + att * 8

    # Set action delay at the end of ACT
    # Delay unit in RO client is 25ms per unit.
    # delay = 8.0 -> 200ms per frame -> 10 frames = 2.0s per complete cycle (slow, majestic, natural)
    delay_pos = len(act) - action_count * 4
    for a in range(action_count):
        struct.pack_into('<f', act, delay_pos + a * 4, float(delay))

    return bytes(act)


def main():
    print("=== Building Solo Leveling Midnight Gate Sprites Suite (1.0x Native Grounded Scale) ===")
    UI_SOURCES.mkdir(parents=True, exist_ok=True)

    # 1. Fetch donor action and palette
    print("1. Extracting donor action (4_energy_blue.act) from data.grf...")
    data_grf = Grf(DATA_GRF)
    try:
        donor_act = data_grf.read(b"data\\sprite\\npc\\4_energy_blue.act")
        donor_spr = data_grf.read(b"data\\sprite\\npc\\4_energy_blue.spr")
        donor_palette = donor_spr[-1024:]
    finally:
        data_grf.close()

    scaled_gate_act = scale_act_bytes(donor_act, 1.0, target_y=-96, target_x=0, delay=8.0)
    print(f"   Scaled ACT (1.0x, delay=8.0): {len(scaled_gate_act)} bytes, Donor Palette: {len(donor_palette)} bytes")

    # 2. Generate 10-frame animations for all 6 Ranks
    gate_assets = {}
    total_frames = 10
    print("2. Rendering procedural gate frames for each rank...")
    for job_id, jt_name, sprite_name, label, theme in GATE_RANKS:
        print(f"   Generating {label} ({sprite_name})...")
        frames = []
        rank_dir = UI_SOURCES / sprite_name
        rank_dir.mkdir(parents=True, exist_ok=True)

        for f in range(total_frames):
            frame_img = render_gate_frame(f, total_frames, theme)
            frames.append(frame_img)
            frame_img.save(rank_dir / f"frame_{f:02d}.png")

        # Save animated APNG preview (200ms per frame)
        frames[0].save(
            rank_dir / "preview.png",
            save_all=True,
            append_images=frames[1:],
            duration=200,
            loop=0,
        )

        spr_bytes = encode_spr_rgba(frames, donor_palette)
        (rank_dir / f"{sprite_name}.spr").write_bytes(spr_bytes)
        (rank_dir / f"{sprite_name}.act").write_bytes(scaled_gate_act)
        gate_assets[job_id] = (spr_bytes, scaled_gate_act)
        print(f"      Saved {sprite_name}.spr ({len(spr_bytes)} bytes) + act ({len(scaled_gate_act)} bytes)")

    # 3. Patch jobname.lub and npcidentity.lub
    print("3. Patching jobname.lub and npcidentity.lub with IDs 10701..10706...")
    new_jobs = [(job_id, sprite_name) for job_id, _, sprite_name, _, _ in GATE_RANKS]
    patched_jobname = patch_jobname_lub(new_jobs)
    (UI_SOURCES / "jobname.lub").write_bytes(patched_jobname)

    new_identities = [(jt_name, job_id) for job_id, jt_name, _, _, _ in GATE_RANKS]
    patched_npcidentity = patch_npcidentity_lub(new_identities)
    (UI_SOURCES / "npcidentity.lub").write_bytes(patched_npcidentity)
    print("   Patched jobname.lub and npcidentity.lub successfully!")

    # 4. Update MidnightROClient/midnight.grf
    print("4. Packaging assets into MidnightROClient/midnight.grf...")
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

    # Purge any previous overrides of official NPC sprites to restore vanilla graphics from data.grf
    official_to_purge = [
        NPC_DIR + b"4_energy_blue.spr", NPC_DIR + b"4_energy_blue.act",
        NPC_DIR + b"4_energy_white.spr", NPC_DIR + b"4_energy_white.act",
        NPC_DIR + b"4_energy_yellow.spr", NPC_DIR + b"4_energy_yellow.act",
        NPC_DIR + b"4_energy_black.spr", NPC_DIR + b"4_energy_black.act",
        NPC_DIR + b"4_energy_red.spr", NPC_DIR + b"4_energy_red.act",
        NPC_DIR + b"4_m_death.spr", NPC_DIR + b"4_m_death.act",
        NPC_DIR + b"4_energy.spr", NPC_DIR + b"4_energy.act",
    ]
    for key in official_to_purge:
        if key in all_files:
            del all_files[key]
            print(f"   Purged override {key.decode('latin-1', errors='ignore')} -> Restored to vanilla data.grf")

    all_files[JOBNAME_KEY] = patched_jobname
    all_files[NPCIDENTITY_KEY] = patched_npcidentity

    staged_grf = CLIENT / "midnight.grf.staged"
    build(staged_grf, list(all_files.items()), verbose=False)
    print(f"   Built staged GRF: {staged_grf}")

    try:
        staged_grf.replace(TARGET_GRF)
        print("   Successfully updated Dev client midnight.grf (MidnightROClient/midnight.grf)!")
    except PermissionError:
        print("   WARNING: midnight.grf is locked. Staged at midnight.grf.staged")

    print("\n=== All Solo Leveling Gate Sprites successfully created & installed in Dev Client! ===")


if __name__ == "__main__":
    main()
