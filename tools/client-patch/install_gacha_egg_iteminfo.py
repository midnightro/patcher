#!/usr/bin/env python3
"""Install all Midnight Gacha Egg tooltips in the Client master ItemInfo table."""

from __future__ import annotations

import re
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[3]
TARGET = WORKSPACE / "MidnightROClient" / "SystemEN" / "itemInfo_C.lua"

ITEMS = (
    (902250, "Costume 1 Gacha Egg", "mid_gacha1_egg", "Costume 1", "6.90%"),
    (902251, "Costume 2 Gacha Egg", "mid_gacha2_egg", "Costume 2", "7.20%"),
    (902252, "Shadow Gacha Egg", "mid_shadow_egg", "Promotion Shadow", "6.00%"),
)


def entry(item_id: int, name: str, resource: str, machine: str, rate: str) -> bytes:
    text = f'''\t[{item_id}] = {{
\t\tunidentifiedDisplayName = "{name}",
\t\tunidentifiedResourceName = "{resource}",
\t\tunidentifiedDescriptionName = {{ "An egg containing one {machine} Gacha draw." }},
\t\tidentifiedDisplayName = "{name}",
\t\tidentifiedResourceName = "{resource}",
\t\tidentifiedDescriptionName = {{
\t\t\t"^FFD700{name}^000000\\n" ..
\t\t\t"^111111Open to make one draw from the {machine} Gacha NPC reward table.^000000\\n" ..
\t\t\t"^00AAFFUses the same {machine} pity counter and grants one Gacha Fragment.^000000\\n" ..
\t\t\t"^00AAFFFeatured reward rate: {rate}; guaranteed featured reward on the 20th draw.^000000\\n" ..
\t\t\t"^B7DFE5====================^000000\\n" ..
\t\t\t"^111111The egg is not consumed if inventory weight or slots are insufficient.^000000\\n" ..
\t\t\t"^B7DFE5====================^000000\\n" ..
\t\t\t"^111111Type: Consumable Box | Weight: 0.1^000000"
\t\t}},
\t\tslotCount = 0,
\t\tClassNum = 0,
\t\tcostume = false
\t}},
'''
    return text.encode("cp874", errors="strict")


def main() -> None:
    data = TARGET.read_bytes()
    data.decode("cp874", errors="strict")
    newline = b"\r\n" if b"\r\n" in data else b"\n"
    marker = b"tbl_custom = {" + newline
    if data.count(marker) != 1:
        raise RuntimeError(f"could not locate custom ItemInfo table in {TARGET}")

    top_level = re.compile(rb"(?m)^\t\[(\d+)\]\s*=\s*\{")
    for item_id, *_ in ITEMS:
        matches = list(top_level.finditer(data))
        index = next((i for i, match in enumerate(matches) if int(match.group(1)) == item_id), None)
        if index is not None:
            start = matches[index].start()
            end = matches[index + 1].start() if index + 1 < len(matches) else data.find(newline + b"}" + newline, matches[index].end())
            if end < 0:
                raise RuntimeError(f"truncated ItemInfo entry {item_id}")
            data = data[:start] + data[end:]

    entries = b"".join(entry(*item).replace(b"\n", newline) for item in ITEMS)
    data = data.replace(marker, marker + entries, 1)
    data.decode("cp874", errors="strict")
    TARGET.write_bytes(data)
    print("installed ItemInfo entries: " + ", ".join(str(item[0]) for item in ITEMS))


if __name__ == "__main__":
    main()
