#!/usr/bin/env python3
"""Export the master-tested wing effects as a small, manifest-backed payload.

The candidate contains the changed Lua GRF members and matching loose
itemInfo_C.lua. All aura and footprint references use effects already in the
client GRFs; no custom shadow-rift assets are required. Merge its data members
into each test client's existing midnight.grf; do not replace the whole archive.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from grf import Grf


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MASTER = ROOT / "Client-master-pc"
MEMBERS = (
    b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lua",
    b"data\\luafiles514\\lua files\\hateffectinfo\\hateffect_f.lub",
    b"data\\luafiles514\\lua files\\hateffectinfo\\footprinteffectinfo.lua",
    b"data\\luafiles514\\lua files\\hateffectinfo\\footprinteffectinfo.lub",
    b"SystemEN\\itemInfo_C.lua",
)
LOOSE_ITEMINFO = Path("SystemEN") / "itemInfo_C.lua"


def member_path(name: bytes) -> Path:
    text = name.decode("ascii")
    parts = text.split("\\")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"Unsafe GRF member path: {name!r}")
    return Path(*parts)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "Patch_Test"):
        raise ValueError("Candidate must be created under Patch_Test")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite candidate: {output}")

    loose = (MASTER / LOOSE_ITEMINFO).read_bytes()
    archive = Grf(MASTER / "midnight.grf")
    try:
        payloads = {member: archive.read(member) for member in MEMBERS}
    finally:
        archive.close()
    if payloads[MEMBERS[-1]] != loose:
        raise ValueError("Embedded and loose itemInfo_C.lua differ in the tested master")

    output.mkdir(parents=True)
    try:
        written: dict[Path, bytes] = {}
        for member in MEMBERS[:-1]:
            written[member_path(member)] = payloads[member]
        written[LOOSE_ITEMINFO] = loose
        for relative, data in written.items():
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)

        lines = [
            f"{sha256(data)}  {relative.as_posix()}"
            for relative, data in sorted(written.items(), key=lambda item: item[0].as_posix())
        ]
        (output / "SHA256SUMS.txt").write_text(
            "\n".join(lines) + "\n", encoding="ascii", newline="\n"
        )
        readme = """# Wing color effects candidate: 10 colors

Status: test candidate only; not approved for release.

This candidate contains the Lua tables and matching `SystemEN/itemInfo_C.lua` from PC Client master at export time. All 10 colors use existing aura and footprint effects; the black wing uses its stock black aura and purple Nyar footprint. No custom shadow-rift assets are included. Copy only the paths listed in `SHA256SUMS.txt`.

## Test installation

1. Close the game and Launcher for the target client.
2. Back up the existing `midnight.grf` and `SystemEN/itemInfo_C.lua`.
3. Run `apply_wing_color_effects_candidate.py` to merge only the listed GRF members into the existing `midnight.grf` and replace the loose `SystemEN/itemInfo_C.lua`.
4. Do not replace the entire `midnight.grf` with the PC Client master archive. Do not change `DATA.INI` or the Local endpoint.
5. Restart the client and test all 10 wing colors, including auras, walk effects, and the absence of error dialogs.

Test Client local with Server local first, then Client Linux with Server Linux. Do not release this candidate until both test runs pass and release work is explicitly requested.
"""
        (output / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    except Exception:
        raise

    expected_files = {"README.md", "SHA256SUMS.txt"} | {
        path.as_posix() for path in written
    }
    actual_files = {path.relative_to(output).as_posix() for path in output.rglob("*") if path.is_file()}
    if actual_files != expected_files:
        raise ValueError(f"Unexpected candidate files: {sorted(actual_files ^ expected_files)}")
    for relative, data in written.items():
        if (output / relative).read_bytes() != data:
            raise ValueError(f"Candidate payload mismatch: {relative}")
    print(f"candidate={output}")
    print(f"payload_files={len(written)}")
    print(f"grf_data_members={len(MEMBERS)-1}; loose_itemInfo=1")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
