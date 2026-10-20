#!/usr/bin/env python3
"""Apply the ten-color wing test payload by updating only approved files.

The candidate data paths are GRF member payloads. They are merged into the
target's current midnight.grf so unrelated client-specific members survive.
The matching SystemEN/itemInfo_C.lua is installed loose and inside the GRF.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from build_pc_login_loading_art import require_client_closed, stage_archive  # noqa: E402
from grf import Grf  # noqa: E402


DATA_MEMBERS = (
    "data/luafiles514/lua files/hateffectinfo/hateffect_f.lua",
    "data/luafiles514/lua files/hateffectinfo/hateffect_f.lub",
    "data/luafiles514/lua files/hateffectinfo/footprinteffectinfo.lua",
    "data/luafiles514/lua files/hateffectinfo/footprinteffectinfo.lub",
)
LOOSE_ITEMINFO = "SystemEN/itemInfo_C.lua"
EMBEDDED_ITEMINFO = b"SystemEN\\itemInfo_C.lua"
ALLOWED_CLIENTS = {
    Path("D:/MidnightROClient-Local").resolve(),
    Path("D:/MidnightROClient-Linux").resolve(),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_candidate(candidate: Path) -> dict[str, bytes]:
    if not candidate.is_relative_to(ROOT / "Patch_Test"):
        raise ValueError("Candidate must be under workspace Patch_Test")
    manifest: dict[str, str] = {}
    for line in (candidate / "SHA256SUMS.txt").read_text(encoding="ascii").splitlines():
        sha, name = line.split("  ", 1)
        if name in manifest or len(sha) != 64:
            raise ValueError("Invalid or duplicate SHA256SUMS entry")
        manifest[name] = sha.lower()
    expected = set(DATA_MEMBERS) | {LOOSE_ITEMINFO}
    if set(manifest) != expected:
        raise ValueError("Candidate manifest does not match the approved payload paths")
    actual = {
        p.relative_to(candidate).as_posix()
        for p in candidate.rglob("*") if p.is_file()
    }
    if actual != expected | {"README.md", "SHA256SUMS.txt"}:
        raise ValueError("Candidate contains missing or unlisted files")
    payloads = {}
    for name, sha in manifest.items():
        path = candidate.joinpath(*name.split("/"))
        if path.is_symlink() or not path.resolve().is_relative_to(candidate):
            raise ValueError("Candidate path escapes its directory")
        data = path.read_bytes()
        if digest(data) != sha:
            raise ValueError(f"Candidate SHA-256 mismatch: {name}")
        payloads[name] = data
    return payloads


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--client-dir", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve(strict=True)
    client = args.client_dir.resolve(strict=True)
    if client not in ALLOWED_CLIENTS:
        raise ValueError("Target must be D:/MidnightROClient-Local or D:/MidnightROClient-Linux")
    payloads = load_candidate(candidate)
    require_client_closed()

    archive_path = client / "midnight.grf"
    loose_path = client / LOOSE_ITEMINFO
    if not archive_path.is_file() or not loose_path.is_file():
        raise FileNotFoundError("Target must contain midnight.grf and SystemEN/itemInfo_C.lua")
    replacements = {
        name.replace("/", "\\").encode("ascii"): payloads[name]
        for name in DATA_MEMBERS
    }
    replacements[EMBEDDED_ITEMINFO] = payloads[LOOSE_ITEMINFO]
    source_hashes = {
        archive_path: digest(archive_path.read_bytes()),
        loose_path: digest(loose_path.read_bytes()),
    }
    current = Grf(archive_path)
    try:
        matching = [
            member for member, data in replacements.items()
            if member in current.entries and current.read(member) == data
        ]
        if len(matching) == len(replacements):
            raise ValueError("Target already has all candidate members; stop and reconcile")
    finally:
        current.close()

    run_id = uuid.uuid4().hex[:12]
    scratch = ROOT / ".scratch" / "wing_color_effects_20261020" / f"{client.name}-{run_id}"
    backup = ROOT / "Backups" / "wing_color_effects" / f"{client.name}-{run_id}"
    if scratch.exists() or backup.exists():
        raise FileExistsError("Refusing to overwrite prior scratch or backup directory")
    scratch.mkdir(parents=True)
    backup.mkdir(parents=True)
    staged_archive = scratch / "midnight.grf"
    report = stage_archive(archive_path, staged_archive, replacements)
    staged_loose = scratch / "itemInfo_C.lua"
    staged_loose.write_bytes(payloads[LOOSE_ITEMINFO])

    temp_archive = client / "midnight.grf.wing-effects.tmp"
    temp_loose = client / "SystemEN" / "itemInfo_C.lua.wing-effects.tmp"
    if temp_archive.exists() or temp_loose.exists():
        raise FileExistsError("Refusing to overwrite an existing temporary client file")
    shutil.copy2(archive_path, backup / "midnight.grf")
    shutil.copy2(loose_path, backup / "SystemEN_itemInfo_C.lua")
    try:
        require_client_closed()
        if digest(archive_path.read_bytes()) != source_hashes[archive_path] or digest(loose_path.read_bytes()) != source_hashes[loose_path]:
            raise ValueError("Target changed after preflight; stop before apply")
        shutil.copy2(staged_archive, temp_archive)
        if digest(temp_archive.read_bytes()) != digest(staged_archive.read_bytes()):
            raise ValueError("Staged GRF copy verification failed")
        shutil.copy2(staged_loose, temp_loose)
        if digest(temp_loose.read_bytes()) != digest(staged_loose.read_bytes()):
            raise ValueError("Staged itemInfo copy verification failed")
        temp_archive.replace(archive_path)
        temp_loose.replace(loose_path)
        if digest(archive_path.read_bytes()) != digest(staged_archive.read_bytes()):
            raise ValueError("Installed GRF verification failed")
        if digest(loose_path.read_bytes()) != digest(staged_loose.read_bytes()):
            raise ValueError("Installed itemInfo verification failed")
    except Exception:
        if (backup / "midnight.grf").exists():
            shutil.copy2(backup / "midnight.grf", archive_path)
        if (backup / "SystemEN_itemInfo_C.lua").exists():
            shutil.copy2(backup / "SystemEN_itemInfo_C.lua", loose_path)
        for temp in (temp_archive, temp_loose):
            if temp.exists():
                temp.unlink()
        raise

    result = {
        "scope": "Wing effects candidate applied; live test pending",
        "client": client.name,
        "candidate": str(candidate.relative_to(ROOT)),
        "backup": str(backup.relative_to(ROOT)),
        "archive": report,
        "loose_itemInfo_sha256": digest(loose_path.read_bytes()),
        "DATA.INI_changed": False,
        "other_GRF_members_byte_identical": True,
    }
    report_path = scratch / "apply-report.json"
    report_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "applied_to": client.name,
        "updated_GRF_members": len(replacements),
        "unrelated_GRF_members_preserved": True,
        "backup": result["backup"],
        "live_test": "PENDING",
    }))


if __name__ == "__main__":
    main()
