#!/usr/bin/env python3
"""Use existing Shadow item artwork for the Promotion Shadow gacha items.

The target item IDs remain 24012-24017. Only their existing item/collection
bitmap members are replaced in the higher-priority midnight.grf archive.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "patcher" / "tools" / "client-patch"
sys.path.insert(0, str(TOOLS))
from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402


CLIENT = ROOT / "Client"
SOURCE_GRF = CLIENT / "data.grf"
TARGET_GRF = CLIENT / "midnight.grf"
STAGED_GRF = CLIENT / "midnight.grf.staged"
BACKUP_GRF = CLIENT / "midnight.grf.before_shadow_existing_image_20261004"

MAPPING = (
    (24012, "낡은웨폰쉐도우", 24001, "웨폰쉐도우"),
    (24013, "낡은아머쉐도우", 24000, "아머쉐도우"),
    (24014, "낡은슈즈쉐도우", 24003, "슈즈쉐도우"),
    (24015, "낡은쉴드쉐도우", 24002, "쉴드쉐도우"),
    (24016, "낡은이어링쉐도우", 24004, "이어링쉐도우"),
    (24017, "낡은펜던트쉐도우", 24005, "펜던트쉐도우"),
)


def member(kind: str, resource: str) -> bytes:
    return f"data\\texture\\유저인터페이스\\{kind}\\{resource}.bmp".encode("cp949")


def load_existing_art() -> dict[bytes, bytes]:
    source = Grf(str(SOURCE_GRF))
    try:
        artwork = {}
        for target_id, target_resource, source_id, source_resource in MAPPING:
            for kind in ("item", "collection"):
                source_name = member(kind, source_resource)
                if source_name not in source.entries:
                    raise RuntimeError(f"missing existing source member: {source_name!r}")
                artwork[member(kind, target_resource)] = source.read(source_name)
                print(f"source {source_id} -> target {target_id} {kind}")
        return artwork
    finally:
        source.close()


def build_staged() -> None:
    if STAGED_GRF.exists():
        raise FileExistsError(f"remove or inspect existing staged archive first: {STAGED_GRF}")
    artwork = load_existing_art()
    target = Grf(str(TARGET_GRF))
    try:
        files = [(name, target.read(name)) for name in target.entries]
    finally:
        target.close()

    positions = {name: index for index, (name, _) in enumerate(files)}
    for name, payload in artwork.items():
        if name in positions:
            files[positions[name]] = (name, payload)
            action = "replace"
        else:
            positions[name] = len(files)
            files.append((name, payload))
            action = "add"
        print(f"{action} {name!r} ({len(payload)} bytes)")

    build(str(STAGED_GRF), files, verbose=False)
    check = Grf(str(STAGED_GRF))
    try:
        for name, expected in artwork.items():
            if check.read(name) != expected:
                raise RuntimeError(f"staged GRF verification failed: {name!r}")
    finally:
        check.close()
    print(f"verified {len(artwork)} mapped members: {STAGED_GRF}")


def apply_staged() -> None:
    if not STAGED_GRF.exists():
        raise FileNotFoundError(f"staged archive not found: {STAGED_GRF}")
    if not BACKUP_GRF.exists():
        shutil.copy2(TARGET_GRF, BACKUP_GRF)
        print(f"backup -> {BACKUP_GRF}")
    STAGED_GRF.replace(TARGET_GRF)
    print(f"applied -> {TARGET_GRF}")


parser = argparse.ArgumentParser()
parser.add_argument("--apply", action="store_true", help="apply the verified staged GRF")
args = parser.parse_args()
build_staged()
if args.apply:
    apply_staged()
