#!/usr/bin/env python3
"""Build the server-made clothes-dye palettes: slot 4 and the signature family 12-15.

    py -3 build_clothes_dye_palettes.py --dry-run   # build and audit only
    py -3 build_clothes_dye_palettes.py             # write midnight.grf

Every colour keeps the job's own shading: each dyed index takes its lightness from
the official slot-0 palette, normalised within its 8-entry ramp, and is mapped
through a three-stop ramp (shadow, mid, highlight).  Shadows lean cool and deep,
highlights warm and soft, the way Ragnarok's own palettes are painted.

* Slot 4 recolours exactly the indices Gravity's dyes 1-3 recolour.
* Slots 12-15 paint the areas in ``clothes_palette_roles.json`` (main / accent /
  trim), which come from the approved Midnight design.

The archive must pass ``clothes_palette_policy.audit`` before it is written, and
every member other than the rebuilt palettes must stay byte-identical.  After a
change to slot 15, run ``web/scripts/extract-job-sprites.mjs`` so the website
shows the same design (``make_patch.ps1`` checks that they match).
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clothes_palette_policy as policy  # noqa: E402
from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402

ROLES = Path(__file__).resolve().with_name("clothes_palette_roles.json")

# (hue degrees, saturation, lightness) at shadow / mid / highlight
Stops = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]

CHARCOAL: Stops = ((230, 0.14, 0.08), (222, 0.09, 0.26), (212, 0.07, 0.52))

RED: Stops = ((344, 0.58, 0.14), (356, 0.64, 0.36), (10, 0.56, 0.68))
BLACK: Stops = ((250, 0.18, 0.035), (236, 0.13, 0.11), (222, 0.09, 0.28))
GOLD: Stops = ((24, 0.62, 0.22), (38, 0.70, 0.50), (50, 0.76, 0.82))

# slot 13 "ขาว-เทา-เงิน" (2026-09-22): white-dominant, light grey panels, silver trim
WHITE: Stops = ((222, 0.10, 0.58), (216, 0.07, 0.82), (40, 0.22, 0.97))
LIGHT_GREY: Stops = ((226, 0.08, 0.32), (219, 0.06, 0.56), (212, 0.05, 0.78))
SILVER: Stops = ((222, 0.14, 0.30), (214, 0.10, 0.58), (206, 0.12, 0.88))

# slot 14 "ดำ-เทา-ทอง" (option Y + gold): soft black, dark grey panels, antique gold trim
SOFT_BLACK: Stops = ((248, 0.18, 0.05), (234, 0.13, 0.16), (221, 0.10, 0.36))
DARK_GREY: Stops = ((230, 0.09, 0.13), (221, 0.07, 0.30), (213, 0.05, 0.52))
GOLD_ON_BLACK: Stops = ((30, 0.64, 0.22), (40, 0.76, 0.48), (50, 0.82, 0.78))

# slot 15 "Midnight" (Starlight, softened to option Y + bright gold, 2026-09-22)
MOONLIGHT: Stops = ((242, 0.36, 0.17), (225, 0.34, 0.52), (200, 0.55, 0.90))
MIDNIGHT_BLUE: Stops = ((250, 0.70, 0.10), (234, 0.76, 0.30), (210, 0.78, 0.60))
LUMINOUS_GOLD: Stops = ((24, 0.78, 0.26), (40, 0.90, 0.56), (52, 0.95, 0.84))

SIGNATURE: dict[int, dict[str, Stops]] = {
    12: {"main": RED, "accent": BLACK, "trim": GOLD},  # แดง-ทอง-ดำ
    13: {"main": WHITE, "accent": LIGHT_GREY, "trim": SILVER},  # ขาว-เทา-เงิน
    14: {"main": SOFT_BLACK, "accent": DARK_GREY, "trim": GOLD_ON_BLACK},  # ดำ-เทา-ทอง
    15: {"main": MOONLIGHT, "accent": MIDNIGHT_BLUE, "trim": LUMINOUS_GOLD},  # Midnight
}
SHADE_SLOT = 4
# how much each ramp is stretched to its full shadow..highlight range (rest follows slot-0 lightness)
CONTRAST: dict[int, float] = {SHADE_SLOT: 0.7, 12: 0.7, 13: 0.7, 14: 0.7, 15: 0.75}


def lightness(palette: bytes, index: int) -> float:
    red, green, blue = policy.rgb(palette, index)
    return colorsys.rgb_to_hls(red / 255.0, green / 255.0, blue / 255.0)[1]


def ramp_colour(t: float, stops: Stops) -> bytes:
    """Colour at position t (0 shadow .. 1 highlight), hue taking the short way round."""
    t = min(1.0, max(0.0, t))
    first, second = (stops[0], stops[1]) if t <= 0.5 else (stops[1], stops[2])
    f = t * 2.0 if t <= 0.5 else (t - 0.5) * 2.0
    step = (second[0] - first[0] + 540.0) % 360.0 - 180.0
    hue = ((first[0] + step * f) % 360.0) / 360.0
    saturation = first[1] + (second[1] - first[1]) * f
    light = first[2] + (second[2] - first[2]) * f
    return bytes(round(c * 255) for c in colorsys.hls_to_rgb(hue, light, saturation))


def positions(base: bytes, indices: list[int], contrast: float) -> dict[int, float]:
    """Shade position per index: lightness normalised inside each ramp, kept partly absolute."""
    by_ramp: dict[int, list[int]] = {}
    for index in indices:
        by_ramp.setdefault(index // 8, []).append(index)
    out = {}
    for group in by_ramp.values():
        values = {i: lightness(base, i) for i in group}
        low, high = min(values.values()), max(values.values())
        for i, value in values.items():
            norm = (value - low) / (high - low) if high - low > 0.04 else value
            out[i] = contrast * norm + (1.0 - contrast) * value
    return out


def paint(base: bytes, areas: dict[str, list[int]], scheme: dict[str, Stops], contrast: float) -> bytes:
    out = bytearray(base)
    for role, indices in areas.items():
        for index, t in positions(base, indices, contrast).items():
            out[index * 4 : index * 4 + 3] = ramp_colour(t, scheme[role])
    return bytes(out)


def check_stops() -> None:
    """Every ramp must stay on the short hue arc between its own stops."""
    ramps = [CHARCOAL] + [s for scheme in SIGNATURE.values() for s in scheme.values()]
    for stops in ramps:
        hues = [stop[0] for stop in stops]
        arc = sum(abs((b - a + 540.0) % 360.0 - 180.0) for a, b in zip(hues, hues[1:]))
        for step in range(101):
            colour = ramp_colour(step / 100.0, stops)
            if max(colour) - min(colour) < 16:
                continue  # hue is meaningless on near-greys and near-blacks
            hue = colorsys.rgb_to_hls(*(c / 255.0 for c in colour))[0] * 360.0
            if min(abs((hue - h + 540.0) % 360.0 - 180.0) for h in hues) > arc + 3.0:
                raise RuntimeError(f"ramp {stops} leaves its hue range at {step}%")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", type=Path, help="write to this archive instead of midnight.grf (for review)")
    args = parser.parse_args()
    check_stops()

    roles = json.loads(ROLES.read_text(encoding="utf-8"))["stems"]
    members = policy.read_members(policy.TARGET)
    original = dict(members)
    base_grf = Grf(policy.BASE)
    built = {SHADE_SLOT: 0, **{slot: 0 for slot in SIGNATURE}}
    for stem, slots in sorted(policy.custom_stems(members).items()):
        official = policy.load_official(stem, members, base_grf)
        if official is None:
            continue
        if SHADE_SLOT in slots:
            dye_1_3 = policy.dye_range(
                [official.base] + [base_grf.read(policy.key(stem, s)) for s in (1, 2, 3)]
            )
            name = policy.key(stem, SHADE_SLOT)
            members[name] = paint(official.base, {"all": sorted(dye_1_3)}, {"all": CHARCOAL}, CONTRAST[SHADE_SLOT])
            built[SHADE_SLOT] += 1
        areas = roles.get(policy.stem_label(stem))
        if areas and policy.SIGNATURE_SLOT in slots:
            for slot, scheme in SIGNATURE.items():
                members[policy.key(stem, slot)] = paint(official.base, areas, scheme, CONTRAST[slot])
                built[slot] += 1
    report = policy.audit(members, base_grf)
    base_grf.close()

    missing = sorted(set(roles) - {policy.stem_label(s) for s, sl in policy.custom_stems(members).items() if 15 in sl})
    if missing:
        raise SystemExit(f"role map names stems that have no palette 15: {missing}")
    changed = sum(1 for n in members if members[n] != original[n])
    print("built per slot:", built, f"| {changed} palette(s) differ from the current archive")
    if not report.ok:
        print("\n".join(report.errors))
        raise SystemExit("palette policy failed; nothing written")
    if args.dry_run or not changed:
        return 0

    target = args.out or policy.TARGET
    if target == policy.TARGET:
        backup = policy.TARGET.with_name(f"midnight.grf.bak_before_dye_build_{datetime.now():%Y%m%d_%H%M%S}")
        shutil.copy2(policy.TARGET, backup)
        print(f"backup {backup.name}")
    staged = target.with_suffix(".grf.building")
    build(staged, list(members.items()), verbose=False)
    rebuilt = policy.read_members(staged)
    touched = {n for n in members if members[n] != original[n]}
    if rebuilt != members or not all(policy.split_key(n) for n in touched):
        staged.unlink(missing_ok=True)
        raise SystemExit("rebuilt archive does not match the intended content; nothing written")
    os.replace(staged, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest().upper()
    print(f"wrote {target.name} SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(main())
