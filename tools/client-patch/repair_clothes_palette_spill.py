#!/usr/bin/env python3
"""Put server-made clothes palettes (slots 4-15) back inside the official dye range.

Any index a custom palette recolours outside what it is allowed to paint (see
``clothes_palette_policy``: Gravity's dye range, plus the signature allowlist for
slots 12-15) is restored to its slot-0 colour.  Allowed indices are left
byte-for-byte as they are.  Safe to run again: a clean archive is left untouched.

    py -3 repair_clothes_palette_spill.py            # writes midnight.grf
    py -3 repair_clothes_palette_spill.py --dry-run  # report only
    # put the Midnight design (slot 15) back from an older archive first
    py -3 repair_clothes_palette_spill.py --signature-from midnight.grf.bak_before_palette_spill_20260922

Normally not needed: ``build_clothes_dye_palettes.py`` regenerates slots 4 and
12-15 inside the allowed range.  This tool remains for palettes made by hand.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clothes_palette_policy as policy  # noqa: E402
from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--signature-from", type=Path, help="archive to copy slot 15 from before clamping")
    args = parser.parse_args()

    members = policy.read_members(policy.TARGET)
    original = dict(members)
    if args.signature_from:
        source = policy.read_members(args.signature_from)
        for stem, slots in policy.custom_stems(members).items():
            name = policy.key(stem, policy.SIGNATURE_SLOT)
            if policy.SIGNATURE_SLOT in slots and name in source:
                members[name] = source[name]
    base_grf = Grf(policy.BASE)
    repaired: dict[str, list[int]] = {}
    for stem, slots in sorted(policy.custom_stems(members).items()):
        official = policy.load_official(stem, members, base_grf)
        if official is None:
            continue
        for slot in slots:
            name = policy.key(stem, slot)
            members[name] = policy.clamp(members[name], official.base, official.allowed(slot))
            if members[name] != original[name]:
                repaired.setdefault(policy.stem_label(stem), []).append(slot)
    report = policy.audit(members, base_grf)
    base_grf.close()

    for label, slots in repaired.items():
        print(f"repair {label}: slots {sorted(slots)}")
    print(f"{sum(map(len, repaired.values()))} palette(s) in {len(repaired)} stem(s) change")
    if not report.ok:
        print("\n".join(report.errors))
        raise SystemExit("policy still fails after clamping; nothing written")
    if args.dry_run or not repaired:
        return 0

    backup = policy.TARGET.with_name(f"midnight.grf.bak_before_palette_repair_{datetime.now():%Y%m%d_%H%M%S}")
    shutil.copy2(policy.TARGET, backup)
    print(f"backup {backup.name}")

    staged = policy.TARGET.with_suffix(".grf.building")
    build(staged, list(members.items()), verbose=False)
    rebuilt = policy.read_members(staged)
    # only body palettes may differ from the original, and the archive must hold
    # exactly what was intended
    touched = {n for n in members if members[n] != original[n]}
    if set(rebuilt) != set(original) or rebuilt != members or not all(policy.split_key(n) for n in touched):
        staged.unlink(missing_ok=True)
        raise SystemExit("rebuilt archive does not match the intended content; nothing written")
    os.replace(staged, policy.TARGET)
    digest = hashlib.sha256(policy.TARGET.read_bytes()).hexdigest().upper()
    print(f"wrote midnight.grf SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(main())
