#!/usr/bin/env python3
"""Export accepted town art for PC Ragexe and optionally apply to PC master.

Changes only background JPEG members and <loading> image lists. The native
Ragnarok loading bar/percentage, executable, DATA.INI and player data are outside
this builder's write scope. No patch number, candidate or release is created.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

from PIL import Image
from grf import Grf

ROOT = Path(__file__).resolve().parents[3]
PC_MASTER = ROOT / "Client-master-pc"
SOURCES = Path(__file__).resolve().parent / "ui_sources" / "pc_login_loading"
UI = b"data\\texture\\\xc0\xaf\xc0\xfa\xc0\xce\xc5\xcd\xc6\xe4\xc0\xcc\xbd\xba\\"
PLAIN = b"data\\texture\\"
XML_MEMBERS = (b"data\\clientinfo.xml", b"data\\sclientinfo.xml")
SCENES = (
    "prontera.png", "morocc.png", "payon.png", "geffen.png", "alberta.png",
    "lutie.png", "izlude.png", "aldebaran-v2.png", "comodo.png", "yuno.png",
    "orc_village.png",
)
IMAGE_NAMES = tuple(f"loading{i:02d}.jpg" for i in range(len(SCENES)))
LOADING = re.compile(br"<loading\b[^>]*>.*?</loading>", re.I | re.S)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_loading(raw: bytes) -> bytes:
    # XML declarations may specify EUC-KR. Keep every original byte outside the
    # ASCII loading section, including connection, admin and encoding settings.
    matches = list(LOADING.finditer(raw))
    if len(matches) != 1:
        raise ValueError("Expected exactly one existing <loading> section")
    newline = b"\r\n" if b"\r\n" in raw else b"\n"
    replacement = b"<loading>" + newline + newline.join(
        b"            <image>" + name.encode("ascii") + b"</image>"
        for name in IMAGE_NAMES
    ) + newline + b"        </loading>"
    changed = LOADING.sub(lambda _: replacement, raw, count=1)
    if LOADING.sub(b"<loading/>", raw) != LOADING.sub(b"<loading/>", changed):
        raise ValueError("Content outside loading list changed")
    # Latin-1 maps bytes without changing them; only validate XML structure and
    # ASCII image names here. Do not reinterpret or reserialize server text.
    tree = ET.fromstring(changed.decode("latin1"))
    if [node.text for node in tree.findall(".//loading/image")] != list(IMAGE_NAMES):
        raise ValueError("Exported loading list does not contain all 11 scenes")
    return changed


def export_images(source: Path, output: Path) -> tuple[dict[bytes, bytes], list[dict]]:
    expected = {}
    for line in (source / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        sha, name = line.split("  ", 1)
        expected[name] = sha
    if set(expected) != set(SCENES):
        raise ValueError("Source manifest must contain exactly the 11 accepted scenes")
    members: dict[bytes, bytes] = {}
    records = []
    for filename, image_name in zip(SCENES, IMAGE_NAMES):
        data = (source / filename).read_bytes()
        if digest(data) != expected[filename]:
            raise ValueError(f"Source SHA-256 mismatch: {filename}")
        with Image.open(io.BytesIO(data)) as original:
            image = original.convert("RGB")
            # Existing PC Login canvas is 4:3. Crop symmetrically rather than
            # squeezing the 16:9 artwork; logos are already baked into sources.
            width = min(image.width, round(image.height * 4 / 3))
            height = min(image.height, round(image.width * 3 / 4))
            left, top = (image.width - width) // 2, (image.height - height) // 2
            crop = (left, top, left + width, top + height)
            image = image.crop(crop).resize((1024, 768), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=98, subsampling=0,
                       progressive=False, optimize=False)
            encoded = buffer.getvalue()
            for prefix in (UI, PLAIN):
                members[prefix + image_name.encode("ascii")] = encoded
            if filename == "geffen.png":
                members[UI + b"t_login.jpg"] = encoded
            records.append({"source": filename, "source_sha256": digest(data),
                            "source_size": list(original.size), "crop": list(crop),
                            "pc_image": image_name, "pc_size": [1024, 768],
                            "jpeg_bytes": len(encoded), "jpeg_sha256": digest(encoded)})
    for name, payload in members.items():
        path = output.joinpath(*name.decode("cp949").split("\\"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return members, records


def stage_archive(original: Path, staged: Path, replacements: dict[bytes, bytes]) -> dict:
    """Preserve original compressed member bytes; append only replacement data."""
    archive = Grf(original)
    try:
        if archive.version != 0x200:
            raise ValueError("Only the existing 0x200 custom archives may be changed")
        entries = {name: dict(value) for name, value in archive.entries.items()}
        table_start = 46 + archive.table_offset
        archive.f.seek(table_start)
        compressed_size, table_size = struct.unpack("<II", archive.f.read(8))
        original_table = zlib.decompress(archive.f.read(compressed_size))
        if len(original_table) != table_size:
            raise ValueError("Original GRF table size mismatch")
        cursor = 0
        while cursor < len(original_table):
            end = original_table.index(b"\0", cursor)
            name = original_table[cursor:end]
            aligned = struct.unpack_from("<I", original_table, end + 5)[0]
            entries[name]["aligned"] = aligned
            cursor = end + 1 + 17
        with original.open("rb") as old, staged.open("xb") as new:
            remaining = table_start
            while remaining:
                chunk = old.read(min(1024 * 1024, remaining))
                if not chunk:
                    raise ValueError("Unexpected end of archive")
                new.write(chunk)
                remaining -= len(chunk)
            for name, payload in replacements.items():
                compressed = zlib.compress(payload, 9)
                offset = new.tell() - 46
                new.write(compressed)
                entries[name] = {"csize": len(compressed), "rsize": len(payload),
                                 "aligned": len(compressed), "flags": 1, "offset": offset}
            table_offset = new.tell() - 46
            table = bytearray()
            for name, value in entries.items():
                table.extend(name + b"\0")
                table.extend(struct.pack("<IIIBI", value["csize"], value["aligned"],
                                         value["rsize"], value["flags"], value["offset"]))
            compressed_table = zlib.compress(table, 9)
            new.write(struct.pack("<II", len(compressed_table), len(table)))
            new.write(compressed_table)
            new.seek(30)
            new.write(struct.pack("<III", table_offset, archive.seed,
                                  len(entries) + archive.seed + 7))
        check = Grf(staged)
        try:
            if set(check.entries) != set(archive.entries) | set(replacements):
                raise ValueError("GRF member inventory mismatch")
            for name in check.entries:
                expected = replacements[name] if name in replacements else archive.read(name)
                if check.read(name) != expected:
                    raise ValueError(f"GRF member round-trip mismatch: {name!r}")
        finally:
            check.close()
        return {"archive": original.name, "original_sha256": digest(original.read_bytes()),
                "staged_sha256": digest(staged.read_bytes()), "members_before": len(archive.entries),
                "members_after": len(entries), "replaced_or_added": len(replacements),
                "all_other_members_byte_identical": True}
    finally:
        archive.close()


def require_client_closed() -> None:
    for process in ("MidnightRO-Ragexe.exe", "MidnightRO.exe"):
        result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {process}", "/FO", "CSV", "/NH"],
                                capture_output=True, check=True, timeout=15)
        for row in csv.reader(result.stdout.decode("utf-8", errors="replace").splitlines()):
            if row and row[0].casefold() == process.casefold():
                raise ValueError(f"Close {process} before modifying PC master")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=SOURCES)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--apply-master", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output.exists():
        raise ValueError("Use a new output directory; prior build evidence is preserved")
    if not output.is_relative_to(ROOT / ".scratch"):
        raise ValueError("Build staging must be below workspace .scratch, not a player package")
    if args.apply_master:
        require_client_closed()
        if not args.backup_dir:
            raise ValueError("--apply-master requires an explicit new --backup-dir")
        backup = args.backup_dir.resolve()
        if not backup.is_relative_to(ROOT / "Backups") or backup.exists():
            raise ValueError("Backup must be a new directory below workspace Backups")
    output.mkdir(parents=True)
    images, records = export_images(args.source_dir, output / "image_members")
    archives = []
    staged_files: list[tuple[Path, Path]] = []
    for archive_name in ("midnight.grf", "server_Local_endpoint.grf"):
        original = PC_MASTER / archive_name
        archive = Grf(original)
        try:
            xml = {name: replace_loading(archive.read(name)) for name in XML_MEMBERS}
        finally:
            archive.close()
        replacements = dict(images) if archive_name == "midnight.grf" else {}
        replacements.update(xml)
        staged = output / archive_name
        archives.append(stage_archive(original, staged, replacements))
        staged_files.append((original, staged))
    for filename in ("clientinfo.xml", "sclientinfo.xml"):
        original = PC_MASTER / "data" / filename
        staged = output / "local_loose" / filename
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(replace_loading(original.read_bytes()))
        staged_files.append((original, staged))
    report = {"scope": "PC master backgrounds and loading image lists only; not a patch/release/live-test pass",
              "source_scene_count": len(SCENES), "runtime_image_members": len(images),
              "login_scene": "geffen.png", "loading_bar": "Existing native Ragexe; no art/text overlay generated",
              "scenes": records, "archives": archives, "master_applied": False}
    if args.apply_master:
        require_client_closed()
        backup.mkdir(parents=True)
        # Back up all files before replacing any; current endpoints/player state
        # stay local and never become generator source or downloadable output.
        for original, staged in staged_files:
            saved = backup / original.relative_to(PC_MASTER)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(original, saved)
            if original.name.endswith(".grf"):
                expected = next(r["original_sha256"] for r in archives if r["archive"] == original.name)
                if digest(original.read_bytes()) != expected:
                    raise ValueError("PC master archive changed while staging; stop before apply")
        for original, staged in staged_files:
            require_client_closed()
            shutil.copy2(staged, original)
            if digest(staged.read_bytes()) != digest(original.read_bytes()):
                raise ValueError("Applied file verification failed; original backups retained")
        report["master_applied"] = True
        report["backup_dir"] = str(backup.relative_to(ROOT))
    (output / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"scene_count": len(SCENES), "image_members": len(images),
                      "master_applied": report["master_applied"],
                      "all_other_grf_members_preserved": all(r["all_other_members_byte_identical"] for r in archives)}))


if __name__ == "__main__":
    main()
