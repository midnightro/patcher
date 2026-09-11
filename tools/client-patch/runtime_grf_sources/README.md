# Runtime GRF sources

ไฟล์ในโฟลเดอร์นี้เป็น component archive สำหรับสร้าง `Client/midnight.grf`
ด้วย `tools/client-patch/build_midnight_grf.py` ไม่ใช่ไฟล์ที่แจกไว้ในโฟลเดอร์เกม

`build_midnight_core.py` จะสร้างส่วน UI/map เป็น `update.grf` ชั่วคราว แล้ว
`build_midnight_grf.py` รวมส่วนนั้นกับ `item_runtime_assets_1..3.grf` เป็น
GRF 0x200 ตัวเดียวที่ rpatchur สามารถ patch ราย member ได้

ลำดับ source ต้องตรงกับ precedence เดิมใน `DATA.INI`:

1. `midnight_map_fix_v11.grf`
2. `midnight_chat_tabs.grf`
3. `midnight_ro_aura_v7.grf`
4. `midnight_token_item.grf`
5. `vip_premium_cards.grf`
6. `small_runtime_v3.grf`
7. `costume_palette_ui.grf`
8. `lua_compat_ui.grf`
9. `episode5_fixes.grf`

นอกจากนี้ builder จะใส่ `../signboardlist_disabled.lua` เป็น
`data/luafiles514/lua files/signboardlist.lub` ใน `update.grf` เสมอ
เพื่อปิดป้ายและไอคอนประจำพิกัดทุกแผนที่; ไม่กระทบ NPC, waitingroom หรือ
quest marker ที่ server ส่งผ่าน `questinfo`/`showevent`.

เพื่อรองรับ Ragexe ที่ยังโหลด bitmap จากตารางฐานในบาง bootstrap path ตัว builder
จะเพิ่มภาพสี colorkey โปร่งใสแทนเฉพาะกลุ่ม
`data/texture/<Korean UserInterface>/information/*.bmp` ที่ใช้เป็นไอคอนพิกัดคงที่
โดยคงขนาด/format ของภาพต้นฉบับไว้ ไม่แตะภาพ skill/item และไม่ปิดฐานข้อมูล NPC ของ
Navigation.

คำอธิบาย Mammonite ที่ปรับให้ใช้ SP 5 คงที่สร้างจาก
`../patch_mammonite_skill_description.py` และบรรจุทับ
`skillinfoz/skilldescript.lub` ไว้ใน `lua_compat_ui.grf` ก่อนรวมเป็น
ส่วน `update.grf` ชั่วคราวก่อนรวมเป็น `Client/midnight.grf`.

ระบบ Midnight Costume Shop ปัจจุบันใช้ ItemInfo + Item DB แบบ intrinsic และไม่ใช้
`midnight_costume_shop_ui.grf`/Random Option nametable แล้ว ดูขั้นตอนที่
`tools/server/MIDNIGHT_COSTUME_SHOP.md`

`midnight_morocc_ground_v1.grf` เป็น component ของ
`build_clean_minimap_overlay.py` สำหรับ `Client/midnight_map_fix_v11.grf` ไม่ได้
รวมเข้า `update.grf`. Texture ทั้ง 9 ไฟล์ต้องใช้ชื่อ private
`mid_mor_sand*`/`mid_mor_inner*` และใช้คู่กับ `morocc.gnd` ที่ builder patch ให้
อ้างชื่อเหล่านี้เท่านั้น ห้ามเปลี่ยนกลับไป override `moc_*.bmp` เพราะชื่อเดิมเป็น
texture shared ที่แมพ `moc_fild` หลายแมพใช้อยู่ด้วย

เมื่อมีการแก้ component ให้สร้าง component ใหม่ในโฟลเดอร์นี้ แล้วรัน builder กลาง
ก่อนสร้าง Client patch ทุกครั้ง ห้ามรวม `new_ai_final.grf` หรือ `data.grf` เข้ามา
เพราะจะเกินเพดาน 8 MiB ของระบบแพตช์ Launcher
