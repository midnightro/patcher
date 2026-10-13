#!/usr/bin/env python3
"""Apply an explicit SHA-verified PC art candidate by merging GRF members.

For an owner-authorized Client local/Linux test only. Preserves that client's
endpoint, DATA.INI, other GRF members and player files. Never publishes a patch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import uuid
from pathlib import Path

from grf import Grf
from build_pc_login_loading_art import (
    ROOT, UI, PLAIN, IMAGE_NAMES, XML_MEMBERS, LOADING, digest,
    replace_loading, require_client_closed, stage_archive,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--client-dir", type=Path, required=True)
    args = parser.parse_args()
    candidate = args.candidate_dir.resolve(strict=True)
    client = args.client_dir.resolve(strict=True)
    if not candidate.is_relative_to(ROOT / "Patch_Test"):
        raise ValueError("Candidate must be within workspace Patch_Test")
    if client not in (Path("D:/MidnightROClient-Local"), Path("D:/MidnightROClient-Linux")):
        raise ValueError("Use the explicitly named Client local or Client Linux")
    require_client_closed()
    expected_names = {prefix + name.encode("ascii") for prefix in (UI, PLAIN) for name in IMAGE_NAMES}
    expected_names.add(UI + b"t_login.jpg")
    expected_names.update(XML_MEMBERS)
    expected_paths = {name.decode("cp949").replace("\\", "/"): name for name in expected_names}
    manifest = {}
    for line in (candidate / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        sha, name = line.split("  ", 1)
        if name in manifest or name not in expected_paths or len(sha) != 64:
            raise ValueError("Unexpected candidate manifest entry")
        manifest[name] = sha
    if set(manifest) != set(expected_paths):
        raise ValueError("Candidate must contain exactly the 25 approved member paths")
    actual = {p.relative_to(candidate).as_posix() for p in candidate.rglob("*") if p.is_file()}
    if actual != set(manifest) | {"README.md", "SHA256SUMS.txt"}:
        raise ValueError("Candidate contains unlisted files")
    payloads = {}
    for name, sha in manifest.items():
        path = candidate.joinpath(*name.split("/"))
        if path.is_symlink() or not path.resolve().is_relative_to(candidate):
            raise ValueError("Candidate path escapes its directory")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != sha:
            raise ValueError("Candidate changed after manifest creation")
        payloads[expected_paths[name]] = data
    run_id = uuid.uuid4().hex[:12]
    staging = ROOT / ".scratch" / "pc-loading-art-20261013" / f"candidate-{run_id}"
    backup = ROOT / "Backups" / "pc_login_loading" / f"{client.name}-{run_id}"
    staging.mkdir(parents=True)
    backup.mkdir(parents=True)
    files = []
    reports = []
    baseline = {}
    for archive_name in ("midnight.grf", "server_Local_endpoint.grf"):
        original = client / archive_name
        if not original.exists():
            if archive_name == "server_Local_endpoint.grf" and client.name.endswith("Linux"):
                continue
            raise ValueError("Required target archive missing")
        current = Grf(original)
        try:
            updates = dict(payloads) if archive_name == "midnight.grf" else {}
            for member in XML_MEMBERS:
                raw = current.read(member)
                if archive_name == "midnight.grf":
                    if LOADING.sub(b"<loading/>", raw) != LOADING.sub(b"<loading/>", payloads[member]):
                        raise ValueError("Target production clientinfo differs outside loading; reconcile first")
                    updates[member] = payloads[member]
                else:
                    # Preserve Local's existing address/admin/version bytes. A
                    # Local endpoint archive is never shipped in the candidate.
                    updates[member] = replace_loading(raw)
        finally:
            current.close()
        staged = staging / archive_name
        reports.append(stage_archive(original, staged, updates))
        baseline[original] = digest(original.read_bytes())
        files.append((original, staged))
    for filename in ("clientinfo.xml", "sclientinfo.xml"):
        original = client / "data" / filename
        if original.exists():
            staged = staging / "loose" / filename
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(replace_loading(original.read_bytes()))
            baseline[original] = digest(original.read_bytes())
            files.append((original, staged))
    require_client_closed()
    for original, staged in files:
        if digest(original.read_bytes()) != baseline[original]:
            raise ValueError("Client changed while staging; stop before apply")
        destination = backup / original.relative_to(client)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)
    for original, staged in files:
        require_client_closed()
        shutil.copy2(staged, original)
        if digest(original.read_bytes()) != digest(staged.read_bytes()):
            raise ValueError("Apply verification failed; backups retained")
    report = {"scope": "Candidate applied only; in-game test pending", "client": client.name,
              "candidate": str(candidate.relative_to(ROOT)), "archives": reports,
              "backup": str(backup.relative_to(ROOT)), "endpoint_and_nonloading_xml_preserved": True}
    (staging / "apply-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"applied_to": client.name, "member_files": len(payloads),
                      "backup": report["backup"], "live_test": "PENDING"}))


if __name__ == "__main__":
    main()
