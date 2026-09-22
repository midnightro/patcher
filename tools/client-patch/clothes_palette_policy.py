#!/usr/bin/env python3
"""Guard rules for clothes-dye body palettes.

Every tool that writes ``data\\palette\\몸\\*.pal`` into ``midnight.grf`` must pass
``audit()`` before replacing the archive.  Run this file directly to check the
current Client master:

    py -3 clothes_palette_policy.py            # exit 1 when any rule fails

Rules
-----
* Slots 0-3 in the game are Gravity's official palettes and come from ``data.grf``.
  ``data.grf`` also carries Gravity's older dyes 4-7 for most jobs; they are not
  offered in game but they document which parts of the outfit Gravity dyes.
* Slots 4-15 are server-made.  They may only recolour the *dye range*: the palette
  indices that any official dye (``data.grf`` slots 1-7) changes relative to slot 0.
  Everything Gravity never dyes (skin, hair, many belts/boots, the reserved magenta
  entries) stays exactly as in slot 0.
* Slot 15 is the server signature ("Midnight") and must visibly differ from slot 0.
  Its design also paints a few parts Gravity never dyes (trim, pauldrons, straps).
  Those indices are listed per stem in ``clothes_palette_signature_allowlist.json``
  and are allowed for slots 12-15, which ``build_clothes_dye_palettes.py`` paints
  from the same role map.
* Every palette is exactly 1,024 bytes.

A stem whose official slots are missing from ``data.grf`` cannot be checked and is
reported as unverified instead of failing.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "MidnightROClient"
TARGET = CLIENT / "midnight.grf"
BASE = CLIENT / "data.grf"

PREFIX = b"data\\palette\\\xb8\xf6\\"  # data\palette\몸\ in CP949
OFFICIAL_SLOTS = (0, 1, 2, 3)  # must exist in data.grf (slot 0 may come from midnight.grf)
OFFICIAL_DYES = tuple(range(1, 8))  # every Gravity dye in data.grf that defines the dye range
CUSTOM_SLOTS = tuple(range(4, 16))
SIGNATURE_SLOT = 15
SIGNATURE_FAMILY = (12, 13, 14, 15)  # slot 15 and the slots derived from it
ALLOWLIST = Path(__file__).resolve().with_name("clothes_palette_signature_allowlist.json")
PALETTE_SIZE = 1024


def key(stem: bytes, slot: int) -> bytes:
    return stem + f"_{slot}.pal".encode("ascii")


def split_key(name: bytes) -> tuple[bytes, int] | None:
    """Return (stem, slot) for a body palette member, else None."""
    if not name.startswith(PREFIX) or not name.endswith(b".pal"):
        return None
    stem, _, slot = name[:-4].rpartition(b"_")
    if not slot.isdigit():
        return None
    return stem, int(slot)


def rgb(palette: bytes, index: int) -> bytes:
    return palette[index * 4 : index * 4 + 3]


def changed(first: bytes, second: bytes) -> set[int]:
    return {i for i in range(256) if rgb(first, i) != rgb(second, i)}


def dye_range(official: list[bytes]) -> frozenset[int]:
    """Indices that any official dye changes relative to slot 0 (``official[0]``)."""
    base, *dyes = official
    mask: set[int] = set()
    for dye in dyes:
        mask |= changed(base, dye)
    mask.discard(0)  # index 0 is the transparent key colour
    return frozenset(mask)


def clamp(palette: bytes, base: bytes, mask: frozenset[int]) -> bytes:
    """Restore every index outside the dye range to its slot-0 colour."""
    out = bytearray(palette)
    for index in range(256):
        if index not in mask:
            out[index * 4 : index * 4 + 3] = rgb(base, index)
    return bytes(out)


def stem_label(stem: bytes) -> str:
    return stem[len(PREFIX) :].decode("cp949", "replace")


def load_allowlist() -> dict[str, frozenset[int]]:
    data = json.loads(ALLOWLIST.read_text(encoding="utf-8"))
    return {stem: frozenset(indices) for stem, indices in data["stems"].items()}


@dataclass
class Official:
    """Slot 0 and the dye range for one job/gender stem."""

    base: bytes
    mask: frozenset[int]
    signature_extra: frozenset[int] = frozenset()

    def allowed(self, slot: int) -> frozenset[int]:
        """Indices ``slot`` may recolour."""
        if slot in SIGNATURE_FAMILY:
            return self.mask | self.signature_extra
        return self.mask


def load_official(stem: bytes, members: dict[bytes, bytes], base_grf) -> Official | None:
    palettes = []
    for slot in OFFICIAL_SLOTS:
        name = key(stem, slot)
        if name in base_grf.entries:
            palettes.append(base_grf.read(name))
        elif slot == 0 and name in members:
            palettes.append(members[name])
        else:
            return None
    for slot in OFFICIAL_DYES[3:]:
        name = key(stem, slot)
        if name in base_grf.entries:
            palettes.append(base_grf.read(name))
    if any(len(p) != PALETTE_SIZE for p in palettes):
        return None
    mask = dye_range(palettes)
    if not mask:
        return None
    extra = load_allowlist().get(stem_label(stem), frozenset())
    return Official(palettes[0], mask, extra - {0})


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)
    checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def custom_stems(members: dict[bytes, bytes]) -> dict[bytes, list[int]]:
    stems: dict[bytes, list[int]] = {}
    for name in members:
        parsed = split_key(name)
        if parsed and parsed[1] in CUSTOM_SLOTS:
            stems.setdefault(parsed[0], []).append(parsed[1])
    return stems


def audit(members: dict[bytes, bytes], base_grf) -> Report:
    report = Report()
    for stem, slots in sorted(custom_stems(members).items()):
        label = stem_label(stem)
        official = load_official(stem, members, base_grf)
        if official is None:
            report.unverified.append(label)
            continue
        for slot in sorted(slots):
            palette = members[key(stem, slot)]
            report.checked += 1
            if len(palette) != PALETTE_SIZE:
                report.errors.append(f"{label} slot {slot}: size {len(palette)} != 1024")
                continue
            spill = sorted(changed(official.base, palette) - official.allowed(slot))
            if spill:
                report.errors.append(
                    f"{label} slot {slot}: recolours {len(spill)} index(es) outside "
                    f"the official dye range {spill[:8]}{'...' if len(spill) > 8 else ''}"
                )
            if slot == SIGNATURE_SLOT and not changed(official.base, palette):
                report.errors.append(f"{label} slot 15: signature palette equals slot 0")
    return report


def read_members(path: Path) -> dict[bytes, bytes]:
    from grf import Grf

    archive = Grf(path)
    try:
        return {name: archive.read(name) for name in archive.entries}
    finally:
        archive.close()


def main(argv: list[str]) -> int:
    from grf import Grf

    target = Path(argv[1]) if len(argv) > 1 else TARGET
    members = read_members(target)
    base_grf = Grf(BASE)
    try:
        report = audit(members, base_grf)
    finally:
        base_grf.close()
    for line in report.errors:
        print("FAIL", line)
    print(
        f"checked {report.checked} custom palettes, {len(report.errors)} failure(s), "
        f"{len(report.unverified)} stem(s) without official slots 0-3 (unverified)"
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    raise SystemExit(main(sys.argv))
