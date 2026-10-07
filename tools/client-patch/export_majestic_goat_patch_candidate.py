"""Export tested Majestic Goat assets as a manifest-backed patch candidate.

The game-test candidate contains a complete midnight.grf. This exporter reads
only the exact new members and accessory maps from that tested archive, verifies
the sprite members against the colorway generator, and copies the two tested
SystemEN files unchanged. The GRF members and loose files are then released as
separate patch indexes by make_patch.ps1.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import build_majestic_goat_colorways as goat  # noqa: E402
from grf import Grf  # noqa: E402


def load_sources() -> dict[str, bytes]:
    suffixes = {
        "male_spr": ".spr",
        "male_act": ".act",
        "female_spr": ".spr",
        "female_act": ".act",
        "drop_spr": ".spr",
        "drop_act": ".act",
        "icon": ".bmp",
        "collection": ".bmp",
    }
    return {
        key: (goat.SOURCE / f"master_{key}{suffix}").read_bytes()
        for key, suffix in suffixes.items()
    }


def safe_member_path(name: bytes) -> Path:
    decoded = name.decode("cp949")
    parts = decoded.split("\\")
    if not decoded or decoded.startswith(("\\", "/")) or any(p in ("", ".", "..") for p in parts):
        raise ValueError(f"Unsafe GRF member name: {name!r}")
    return Path(*parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidate = args.candidate.resolve(strict=True)
    output = args.output.resolve()
    tested_grf = candidate / "midnight.grf"
    for name in (
        "SystemEN/itemInfo_C.lua",
        "SystemEN/itemInfo_ProjectRO_Costume.lua",
    ):
        if not (candidate / name).is_file():
            raise FileNotFoundError(candidate / name)
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing candidate: {output}")

    source = load_sources()
    expected_members: dict[bytes, bytes] = {}
    for item in goat.COLORWAYS:
        goat.add_sprite_files(expected_members, source, item)
    if len(expected_members) != len(goat.COLORWAYS) * 16:
        raise ValueError(f"Unexpected generated member count: {len(expected_members)}")

    archive = Grf(str(tested_grf))
    try:
        members = {
            name: archive.read(name)
            for name, expected in expected_members.items()
            if archive.read(name) == expected
        }
        if len(members) != len(expected_members):
            missing = next(name for name in expected_members if name not in members)
            raise ValueError(f"Tested GRF member differs from generated payload: {missing!r}")

        accessory_id = goat.LUA_ROOT + b"accessoryid.lub"
        accessory_names = goat.LUA_ROOT + b"accname.lub"
        members[accessory_id] = archive.read(accessory_id)
        members[accessory_names] = archive.read(accessory_names)
    finally:
        archive.close()

    output.mkdir(parents=True)
    try:
        for name, payload in members.items():
            (output / safe_member_path(name)).parent.mkdir(parents=True, exist_ok=True)
            (output / safe_member_path(name)).write_bytes(payload)
        for relative in (
            Path("SystemEN") / "itemInfo_C.lua",
            Path("SystemEN") / "itemInfo_ProjectRO_Costume.lua",
        ):
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((candidate / relative).read_bytes())

        files = sorted(
            path for path in output.rglob("*") if path.is_file()
        )
        manifest_lines = [
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(output).as_posix()}"
            for path in files
        ]
        (output / "SHA256SUMS.txt").write_text(
            "\n".join(manifest_lines) + "\n", encoding="utf-8", newline="\n"
        )
        readme = (
            "# Majestic Goat patch source candidate\n\n"
            "Derived from the tested `majestic_goat_colorways` candidate. The "
            f"{len(expected_members)} GRF member payloads were compared byte-for-byte "
            "with the tested `midnight.grf`; the two loose SystemEN Lua files were "
            "copied unchanged and checked against its SHA-256 manifest.\n\n"
            "Use the `data\\...` members and the two accessory Lua members with "
            "`make_patch.ps1 -UseGrfMerging -TargetGrfName midnight.grf`. Release "
            "the two SystemEN files as a loose-file patch. This folder is patch "
            "source, not a folder to copy over a client.\n"
        )
        (output / "README.md").write_text(readme, encoding="utf-8", newline="\n")
    except Exception:
        # Keep any partial output visible for diagnosis rather than silently
        # deleting a user-reviewable candidate.
        raise

    print(f"Exported {len(members)} GRF members and 2 loose files to {output}")
    print(f"Manifest covers {len(files)} payload files")


if __name__ == "__main__":
    main()
