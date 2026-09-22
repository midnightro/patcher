#!/usr/bin/env python3
"""Make MidnightRO-Ragexe use each job's own body palettes regardless of servicetype.

When ``g_serviceType`` is not Korea (ours is ``thai``, needed for Thai fonts - BUG-064)
the client builds its body-palette name table with 2-1 names for 2-2 and
transcendent jobs (Sage -> 위저드, Bard -> 헌터, Crusader -> 기사, ...), so their dyes
never match the palettes made for them.  The table is built right after

    cmp dword ptr [g_serviceType], 0
    mov eax, [edi+0xfec]
    jne <non-Korean table>          ; 0F 85 rel32

This tool replaces that ``jne`` with NOPs so the Korean (own-name) table is always
used.  It refuses to touch a file whose bytes around the jump do not match, so a
different exe build is never patched blindly.

    py -3 patch_ragexe_own_job_palettes.py IN.exe OUT.exe     # write a patched copy
    py -3 patch_ragexe_own_job_palettes.py --check FILE.exe   # report patched / unpatched
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

# cmp dword [0x16d3b10], 0 ; mov eax, [edi+0xfec] ; jne +0x221
SIGNATURE = bytes.fromhex("833d103b6d0100" "8b87ec0f0000" "0f8521020000")
JNE_OFFSET_IN_SIGNATURE = 13
NOPS = b"\x90" * 6
PATCHED = SIGNATURE[:JNE_OFFSET_IN_SIGNATURE] + NOPS


def locate(data: bytes) -> tuple[int, bool]:
    """Return (offset of the jne, already patched)."""
    unpatched, patched = data.count(SIGNATURE), data.count(PATCHED)
    if unpatched + patched != 1:
        raise SystemExit("palette-table branch not found exactly once; unknown exe build, not patching")
    needle = PATCHED if patched else SIGNATURE
    return data.find(needle) + JNE_OFFSET_IN_SIGNATURE, bool(patched)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, nargs="?")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    data = args.source.read_bytes()
    offset, patched = locate(data)
    print(f"{args.source.name}: branch at file offset {hex(offset)}, {'PATCHED' if patched else 'unpatched'}")
    if args.check:
        return 0
    if args.output is None:
        raise SystemExit("give an output path; the source exe is never modified in place")
    if args.output.exists():
        raise SystemExit(f"{args.output} exists; not overwriting")
    out = bytearray(data)
    out[offset : offset + 6] = NOPS
    args.output.write_bytes(out)
    changed = [i for i in range(len(data)) if data[i] != out[i]]
    print(f"wrote {args.output.name}: {len(changed)} byte(s) changed at {hex(changed[0]) if changed else '-'}")
    print("SHA-256", hashlib.sha256(out).hexdigest().upper())
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    raise SystemExit(main())
