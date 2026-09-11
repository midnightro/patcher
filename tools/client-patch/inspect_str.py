#!/usr/bin/env python3
"""Print the structure of a Ragnarok STR effect for build-time validation."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


KEYFRAME = struct.Struct("<II2f8f8ffIff4fIII")


def inspect(path: Path) -> None:
    payload = path.read_bytes()
    if payload[:4] != b"STRM":
        raise RuntimeError(f"{path}: invalid STR magic")
    version = struct.unpack_from("<I", payload, 4)[0]
    fps, max_key, stored_layer_count = struct.unpack_from("<III", payload, 8)
    if stored_layer_count < 1:
        raise RuntimeError(f"{path}: invalid stored layer count {stored_layer_count}")
    layer_count = stored_layer_count - 1
    offset = 44
    print(
        f"version=0x{version:X} fps={fps} max_key={max_key} "
        f"stored_layers={stored_layer_count} layers={layer_count}"
    )
    for layer_index in range(layer_count):
        texture_count = struct.unpack_from("<I", payload, offset)[0]
        offset += 4
        textures = []
        for _ in range(texture_count):
            raw_name = payload[offset:offset + 128]
            offset += 128
            textures.append(raw_name.split(b"\0", 1)[0].decode("latin-1"))
        key_count = struct.unpack_from("<I", payload, offset)[0]
        offset += 4
        print(f"layer={layer_index} textures={textures!r} keys={key_count}")
        for key_index in range(key_count):
            values = KEYFRAME.unpack_from(payload, offset)
            offset += KEYFRAME.size
            if key_index < 6:
                print(
                    f"  frame={values[0]} type={values[1]} pos={values[2:4]} "
                    f"uv={values[4:12]} xy={values[12:20]} "
                    f"tex={values[20]} anim={values[21:23]} "
                    f"angle={values[23]} color={values[24:28]} "
                    f"blend={values[28:31]}"
                )
    if offset != len(payload):
        raise RuntimeError(f"{path}: parsed {offset} of {len(payload)} bytes")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    inspect(args.path)


if __name__ == "__main__":
    main()
