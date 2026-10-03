#!/usr/bin/env python3
from pathlib import Path

p_utf8 = Path("server/npc/custom/midnight/midnight_gate.utf8.txt")
p_cp = Path("server/npc/custom/midnight/midnight_gate.txt")

lines = p_utf8.read_text(encoding="utf-8").splitlines(keepends=True)

new_block = """\tmes " ";
\tmes "คุณต้องการเข้าสู่ประตูมิติในรูปแบบใด?";
\tnext;
\tswitch (select("1. ลุยเดี่ยว (Solo Instance):2. ทีมปาร์ตี้ (Party Instance):3. เข้าร่วม World Event รวมพลทั้งเซิร์ฟเวอร์:4. ยังไม่พร้อม")) {
\tcase 1: // Solo
\t\t.@has_inst = instance_id(IM_CHAR);
\t\tif (.@has_inst > 0) {
\t\t\tinstance_enter "Midnight Gate";
\t\t\tclose;
\t\t}
\t\t.@inst_id = instance_create("Midnight Gate", IM_CHAR, getcharid(0));
\t\tif (.@inst_id < 0) {
\t\t\tmes "^FF0000ไม่สามารถสร้างเกตเดี่ยวได้ในขณะนี้^000000";
\t\t\tclose;
\t\t}
\t\tinstance_enter "Midnight Gate";
\t\tclose;

\tcase 2: // Party
\t\tif (!getcharid(1)) {
\t\t\tmes "^FF0000คุณยังไม่มีปาร์ตี้!^000000 กรุณาสร้างปาร์ตี้ก่อนเปิดเกตแบบทีม";
\t\t\tclose;
\t\t}
\t\t.@has_inst = instance_id(IM_PARTY);
\t\tif (.@has_inst > 0) {
\t\t\tinstance_enter "Midnight Gate";
\t\t\tclose;
\t\t}
\t\tif (!is_party_leader()) {
\t\t\tmes "^FF0000เฉพาะหัวหน้าปาร์ตี้เท่านั้น^000000 ที่สามารถเปิดเกตของทีมได้";
\t\t\tclose;
\t\t}
\t\t.@inst_id = instance_create("Midnight Gate", IM_PARTY, getcharid(1));
\t\tif (.@inst_id < 0) {
\t\t\tmes "^FF0000ไม่สามารถสร้างเกตของปาร์ตี้ได้ในขณะนี้^000000";
\t\t\tclose;
\t\t}
\t\tpartyannounce getcharid(1), "[Midnight Gate] หัวหน้าปาร์ตี้ได้เปิดประตูมิติแล้ว! กำลังดึงทุกคนเข้าสู่เกต...", bc_blue;
\t\tgetpartymember getcharid(1), 2;
\t\t.@pcount = $@partymembercount;
\t\tcopyarray .@aids[0], $@partymemberaid[0], .@pcount;
\t\tfor (.@i = 0; .@i < .@pcount; .@i++) {
\t\t\tif (isloggedin(.@aids[.@i])) {
\t\t\t\tif (attachrid(.@aids[.@i])) {
\t\t\t\t\tinstance_enter "Midnight Gate";
\t\t\t\t\tdetachrid;
\t\t\t\t}
\t\t\t}
\t\t}
\t\tinstance_enter "Midnight Gate";
\t\tclose;

\tcase 3: // World Event
\t\tbreak;

\tcase 4:
\t\tclose;
\t}
"""

lines[523:529] = [new_block]
full_text = "".join(lines)
p_utf8.write_text(full_text, encoding="utf-8")

crlf_text = full_text.replace("\r\n", "\n").replace("\n", "\r\n")
p_cp.write_bytes(crlf_text.encode("cp874"))
print("Successfully updated midnight_gate.utf8.txt and midnight_gate.txt!")
