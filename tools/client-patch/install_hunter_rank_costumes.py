#!/usr/bin/env python3
"""Install Solo Leveling Shadow Monarch 4-Piece Hunter Rank Costume Set.

Items:
  902269: [Hunter C] Kasaka Shadow Fang (Costume Lower - Dagger in mouth, View 327)
  902270: [Hunter B] Obsidian Crown of the Monarch (Costume Upper - Dark Crown, View 988)
  902271: [Hunter A] Monarch's Shadow Gaze (Costume Middle - Glowing Eyes, View 1490)
  902272: [Hunter S] 6 Sovereign Shadow Wings (Costume Garment - 8-Direction Robe Wings, View 73)
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]

ITEM_DB_YML = ROOT / "server/db/import/item_db.yml"
ITEMINFO_C = ROOT / "MidnightROClient/SystemEN/itemInfo_C.lua"

KEEPER_UTF8 = ROOT / "server/npc/custom/midnight/midnight_keeper.utf8.txt"
JOURNAL_UTF8 = ROOT / "server/npc/custom/midnight/midnight_journal.utf8.txt"
ANNOUNCE_UTF8 = ROOT / "server/npc/custom/midnight/midnight_announce.utf8.txt"


ITEM_DEFINITIONS_YAML = """
  # ---------------------------------------------------------------------------
  # Midnight RO - Solo Leveling Shadow Monarch Hunter Rank Costumes (Rank C - S)
  # ---------------------------------------------------------------------------
  - Id: 902269
    AegisName: "NFS_Hunter_Dagger_C"
    Name: "[Hunter Rank C] Kasaka Shadow Fang"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Low: true
    View: 327
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902270
    AegisName: "NFS_Hunter_Crown_B"
    Name: "[Hunter Rank B] Obsidian Crown of the Monarch"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Top: true
    View: 988
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902271
    AegisName: "NFS_Hunter_Gaze_A"
    Name: "[Hunter Rank A] Monarch's Shadow Gaze"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Head_Mid: true
    View: 1490
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true

  - Id: 902272
    AegisName: "NFS_Hunter_Wings_S"
    Name: "[Hunter Rank S] 6 Sovereign Shadow Wings"
    Type: "Armor"
    ArmorLevel: 1
    EquipLevelMin: 1
    Locations:
      Costume_Garment: true
    View: 73
    Trade:
      Override: 100
      NoDrop: true
      NoTrade: true
      NoSell: true
      NoCart: true
      NoGuildStorage: true
      NoMail: true
      NoAuction: true
"""


def update_server_item_db() -> None:
    print(f"Updating server item_db: {ITEM_DB_YML}")
    content = ITEM_DB_YML.read_text(encoding="utf-8")
    
    # Check if already present
    if "NFS_Hunter_Dagger_C" in content:
        pattern = r"(?ms)  # -+\s+# Midnight RO - Solo Leveling Shadow Monarch Hunter Rank Costumes.*?NoAuction: true\n"
        content = re.sub(pattern, ITEM_DEFINITIONS_YAML.strip() + "\n", content)
    else:
        content = content.rstrip() + "\n" + ITEM_DEFINITIONS_YAML

    ITEM_DB_YML.write_text(content, encoding="utf-8")
    print("  Server item_db updated successfully.")


def update_client_iteminfo_c() -> None:
    print(f"Updating client itemInfo_C.lua: {ITEMINFO_C}")
    raw = ITEMINFO_C.read_bytes()
    text = raw.decode("cp874", errors="ignore")

    lua_block = '''
-- Solo Leveling Shadow Monarch Hunter Rank Costumes
local function makeHunterCostume(baseId, displayName, descLines)
	local base = tbl[baseId] or (tbl_custom and tbl_custom[baseId])
	local item = {}
	if base then
		for k, v in pairs(base) do
			item[k] = v
		end
	end
	item.unidentifiedDisplayName = displayName
	item.identifiedDisplayName = displayName
	item.unidentifiedDescriptionName = descLines
	item.identifiedDescriptionName = descLines
	item.slotCount = 0
	item.costume = true
	return item
end

tbl_custom[902269] = makeHunterCostume(19584, "[Hunter C] Kasaka Shadow Fang", {
	"^FF9900[Hunter C] Kasaka Shadow Fang^000000\\n" ..
	"^111111กริชเขี้ยวพิษคาซากะสีดำขลับ คมดาบอาบไอพิษสีฟ้าคราม^000000\\n" ..
	"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank C^000000\\n" ..
	"^B7DFE5====================^000000\\n" ..
	"^111111ประเภท : Costume^000000\\n" ..
	"^111111ตำแหน่ง : ส่วนล่าง (Lower)^000000\\n" ..
	"^111111น้ำหนัก : 0^000000\\n" ..
	"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
	"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
})

tbl_custom[902270] = makeHunterCostume(19751, "[Hunter B] Obsidian Crown of the Monarch", {
	"^FF9900[Hunter B] Obsidian Crown of the Monarch^000000\\n" ..
	"^111111มงกุฎผลึกหินสีดำออบซิเดียน สลักอักขระรูนโบราณเรืองแสงสีม่วง-คราม^000000\\n" ..
	"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank B^000000\\n" ..
	"^B7DFE5====================^000000\\n" ..
	"^111111ประเภท : Costume^000000\\n" ..
	"^111111ตำแหน่ง : ส่วนบน (Upper)^000000\\n" ..
	"^111111น้ำหนัก : 0^000000\\n" ..
	"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
	"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
})

tbl_custom[902271] = makeHunterCostume(31375, "[Hunter A] Monarch\'s Shadow Gaze", {
	"^FF9900[Hunter A] Monarch\'s Shadow Gaze^000000\\n" ..
	"^111111ดวงตาเปลวไฟสีฟ้าครามสว่างวาบ พร้อมไอวิญญาณสีฟ้าลอยพริ้วจากหางตา^000000\\n" ..
	"^111111รางวัลเกียรติยศสำหรับ Hunter ผู้ผ่านการประเมิน Rank A^000000\\n" ..
	"^B7DFE5====================^000000\\n" ..
	"^111111ประเภท : Costume^000000\\n" ..
	"^111111ตำแหน่ง : ส่วนกลาง (Middle)^000000\\n" ..
	"^111111น้ำหนัก : 0^000000\\n" ..
	"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
	"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
})

tbl_custom[902272] = makeHunterCostume(480056, "[Hunter S] 6 Sovereign Shadow Wings", {
	"^FF9900[Hunter S] 6 Sovereign Shadow Wings^000000\\n" ..
	"^111111ปีกวิญญาณเงาแห่งจักรพรรดิ 6 ปีก ขอบเปลวไฟสีฟ้าคราม 8 ทิศทางพริ้วไหว^000000\\n" ..
	"^111111รางวัลเกียรติยศสูงสุดสำหรับ Hunter ผู้ผ่านการประเมิน Rank S^000000\\n" ..
	"^B7DFE5====================^000000\\n" ..
	"^111111ประเภท : Costume^000000\\n" ..
	"^111111ตำแหน่ง : มัฟหลัง (Garment)^000000\\n" ..
	"^111111น้ำหนัก : 0^000000\\n" ..
	"^111111เลเวลที่ต้องการ : 1^000000\\n" ..
	"^111111อาชีพที่ใช้ได้ : ทุกอาชีพ^000000"
})
'''

    marker = "-- Solo Leveling Shadow Monarch Hunter Rank Costumes"
    if marker in text:
        idx = text.find(marker)
        end_idx = text.find("tbl_custom[902272]", idx)
        if end_idx != -1:
            closing = text.find("})", end_idx)
            if closing != -1:
                text = text[:idx] + text[closing+2:]

    insert_point = text.find("-- Table for Official Overrides")
    if insert_point != -1:
        text = text[:insert_point] + lua_block.strip() + "\n\n" + text[insert_point:]
    else:
        text = text + "\n\n" + lua_block.strip() + "\n"

    encoded = text.encode("cp874", errors="replace")
    ITEMINFO_C.write_bytes(encoded)
    print("  Client itemInfo_C.lua updated successfully (CP874).")


def transcode_npc_files() -> None:
    print("Transcoding NPC files to CP874 + CRLF...")
    for base in ["midnight_keeper", "midnight_journal", "midnight_announce"]:
        utf8_path = ROOT / f"server/npc/custom/midnight/{base}.utf8.txt"
        txt_path = ROOT / f"server/npc/custom/midnight/{base}.txt"
        if utf8_path.is_file():
            content = utf8_path.read_text(encoding="utf-8")
            content = content.replace("\r\n", "\n").replace("\n", "\r\n")
            txt_path.write_bytes(content.encode("cp874", errors="replace"))
            print(f"  Synchronized {txt_path.name}")


def main() -> None:
    update_server_item_db()
    update_client_iteminfo_c()
    transcode_npc_files()
    print("\nAll Solo Leveling Hunter Costumes installed successfully!")


if __name__ == "__main__":
    main()
