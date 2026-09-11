#!/usr/bin/env python3
"""Inspect Lua 5.1 bytecode prototypes and show referenced globals/constants."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


OPS = [
    "MOVE", "LOADK", "LOADBOOL", "LOADNIL", "GETUPVAL", "GETGLOBAL",
    "GETTABLE", "SETGLOBAL", "SETUPVAL", "SETTABLE", "NEWTABLE", "SELF",
    "ADD", "SUB", "MUL", "DIV", "MOD", "POW", "UNM", "NOT", "LEN",
    "CONCAT", "JMP", "EQ", "LT", "LE", "TEST", "TESTSET", "CALL",
    "TAILCALL", "RETURN", "FORLOOP", "FORPREP", "TFORLOOP", "SETLIST",
    "CLOSE", "CLOSURE", "VARARG",
]
ABX = {"LOADK", "GETGLOBAL", "SETGLOBAL", "CLOSURE"}
ASBX = {"JMP", "FORLOOP", "FORPREP"}


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        if self.take(4) != b"\x1bLua":
            raise ValueError("not a Lua bytecode chunk")
        self.version, self.format, endian = self.u8(), self.u8(), self.u8()
        self.int_size, self.size_t_size = self.u8(), self.u8()
        self.ins_size, self.num_size, self.integral = self.u8(), self.u8(), self.u8()
        if self.version != 0x51 or self.format != 0 or endian != 1:
            raise ValueError("only little-endian standard Lua 5.1 is supported")
        if self.ins_size != 4:
            raise ValueError("unsupported instruction size")

    def take(self, count: int) -> bytes:
        out = self.data[self.pos:self.pos + count]
        if len(out) != count:
            raise ValueError("truncated Lua chunk")
        self.pos += count
        return out

    def u8(self) -> int:
        return self.take(1)[0]

    def uint(self, size: int) -> int:
        return int.from_bytes(self.take(size), "little")

    def integer(self) -> int:
        return self.uint(self.int_size)

    def string(self) -> bytes | None:
        size = self.uint(self.size_t_size)
        if size == 0:
            return None
        raw = self.take(size)
        return raw[:-1]

    def number(self):
        raw = self.take(self.num_size)
        if self.integral:
            return int.from_bytes(raw, "little", signed=True)
        return struct.unpack("<d" if self.num_size == 8 else "<f", raw)[0]


def parse_proto(reader: Reader, inherited_source: bytes | None = None):
    source = reader.string() or inherited_source
    line_start, line_end = reader.integer(), reader.integer()
    proto = {
        "source": source,
        "line_start": line_start,
        "line_end": line_end,
        "nups": reader.u8(),
        "params": reader.u8(),
        "vararg": reader.u8(),
        "stack": reader.u8(),
    }
    code_count = reader.integer()
    proto["code_offset"] = reader.pos
    proto["code"] = [reader.uint(reader.ins_size) for _ in range(code_count)]
    constants = []
    for _ in range(reader.integer()):
        kind = reader.u8()
        if kind == 0:
            value = None
        elif kind == 1:
            value = bool(reader.u8())
        elif kind == 3:
            value = reader.number()
        elif kind == 4:
            value = reader.string()
        else:
            raise ValueError(f"unknown constant type {kind}")
        constants.append(value)
    proto["constants"] = constants
    proto["children"] = [parse_proto(reader, source) for _ in range(reader.integer())]
    proto["lineinfo"] = [reader.integer() for _ in range(reader.integer())]
    proto["locals"] = [
        (reader.string(), reader.integer(), reader.integer())
        for _ in range(reader.integer())
    ]
    proto["upvalues"] = [reader.string() for _ in range(reader.integer())]
    return proto


def text(value) -> str:
    if isinstance(value, bytes):
        return value.decode("latin-1", errors="replace")
    return repr(value)


def instruction(raw: int, constants: list) -> str:
    op = raw & 0x3F
    a = (raw >> 6) & 0xFF
    c = (raw >> 14) & 0x1FF
    b = (raw >> 23) & 0x1FF
    bx = (raw >> 14) & 0x3FFFF
    name = OPS[op] if op < len(OPS) else f"OP_{op}"
    if name in ABX:
        suffix = f" ; {text(constants[bx])}" if name != "CLOSURE" and bx < len(constants) else ""
        return f"{name:<10} A={a} Bx={bx}{suffix}"
    if name in ASBX:
        return f"{name:<10} A={a} sBx={bx - 131071}"
    return f"{name:<10} A={a} B={b} C={c}"


def walk(proto, path="0"):
    yield path, proto
    for index, child in enumerate(proto["children"]):
        yield from walk(child, f"{path}.{index}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("chunk", type=Path)
    ap.add_argument("--contains", default="", help="only prototypes containing this text")
    ap.add_argument("--path", default="", help="only this prototype path (for example 0.10)")
    ap.add_argument("--disassemble", action="store_true")
    args = ap.parse_args()

    reader = Reader(args.chunk.read_bytes())
    root = parse_proto(reader)
    needle = args.contains.lower()
    for path, proto in walk(root):
        if args.path and path != args.path:
            continue
        strings = [text(value) for value in proto["constants"] if isinstance(value, bytes)]
        haystack = "\n".join(strings).lower()
        if needle and needle not in haystack:
            continue
        local_names = [text(name) for name, _start, _end in proto["locals"]]
        print(f"proto={path} lines={proto['line_start']}-{proto['line_end']} "
              f"params={proto['params']} stack={proto['stack']} code={len(proto['code'])}")
        print("locals:", ", ".join(local_names))
        print("strings:", ", ".join(strings))
        if args.disassemble:
            for pc, raw in enumerate(proto["code"]):
                line = proto["lineinfo"][pc] if pc < len(proto["lineinfo"]) else 0
                print(f"  {pc:04d} L{line:<4} {instruction(raw, proto['constants'])}")


if __name__ == "__main__":
    main()
