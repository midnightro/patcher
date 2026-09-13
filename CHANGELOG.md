# MIDNIGHT RO — Client Patch Changelog

บันทึกประวัติการปล่อยแพตช์ฝั่ง Client (`.thor`) สำหรับ MIDNIGHT RO Launcher และตัวเกม

---

## แพตช์ 0108 — 2026-09-13

- **ไฟล์แพตช์:** `0108_20260913_clothes-dye-midnight-refined.thor`
- **ขนาด:** 22.19 MB
- **SHA-256:** `113B6511CFF943D57E78BC0752548AA04435E8C1ECD6122E1852D64F9427996B`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `midnight.grf`
- **รายละเอียดการเปลี่ยนแปลง:**
  - ปรับแต่งโทนสีและรายละเอียดชุด Midnight (Palette 15) ครบทุกอาชีพให้สวยงาม สมดุล และเข้าธีม Midnight RO อย่างสมบูรณ์แบบ:
    - **Novice (ช/ญ):** ชุดผ้าด้านใน Deep Midnight Navy, เกราะอก Moonlight Silver, สายสะพาย Midnight Blue, หัวเข็มขัด Luminous Gold
    - **Assassin (ช/ญ):** บอดี้สูท Deep Midnight Navy, ตัดสีทอง Luminous Gold บนเกราะไหล่ คอร์เซ็ตเอว สายรัดอก และปลอกแขน/ขา, ผ้าพันแผล Moonlight Silver, ผ้าคลุมคอ Rich Midnight Blue
    - **Hunter (ช/ญ):** เสื้อและกางเกงรัดรูป Deep Midnight Navy, บูทและผ้าพันคอ Midnight Blue, เกราะอก Moonlight Silver, หัวเข็มขัด Luminous Gold
    - **Blacksmith (ช/ญ):** เสื้อเชิ้ต/ชุดใน Deep Midnight Navy, ผ้ากันเปื้อนช่าง Midnight Blue, หมุดเกราะและหัวเข็มขัด Luminous Gold, ผ้าพันมือ Moonlight Silver
    - **Alchemist (ช):** เสื้อโค้ตนอก Rich Midnight Blue, เสื้อกั๊ก Moonlight Silver, กางเกง Deep Midnight Navy, กระดุม/ขอบทอง Luminous Gold
    - **Swordman (ช/ญ):** เกราะอก/ชายผ้า Moonlight Silver, บูท/สายสะพายอก Midnight Blue, สนับเข่าและหัวเข็มขัด Luminous Gold
    - **Mage (ช/ญ):** ผ้าคลุมไหล่ Moonlight Silver, กระโปรง/ชุดคลุม Rich Midnight Blue, ปลอกแขน ตราสัญลักษณ์อก และสร้อยคอ Luminous Gold
    - **Acolyte (ช/ญ):** ชุดคลุม Moonlight Silver, ผ้าคลุมไหล่ Midnight Blue, กางเขนและเข็มขัดเอว Luminous Gold
    - **Thief (ช/ญ):** แจ็กเก็ต Moonlight Silver, กางเกง/บูท Deep Midnight Blue, ผ้าคาดเอวและสนับเข่า Luminous Gold
    - **Bard (ช และสัตว์ขี่):** ผ้าคลุมยาวด้านหลัง Luminous Gold สีทองสว่าง, กางเกงและบูท Radiant Vibrant Blue สว่างสดใส, เสื้อกั๊ก Rich Midnight Blue, แขนเสื้อ Moonlight Silver, เข็มขัดและคอเสื้อ Luminous Gold
    - **Dancer (ญ, กางเกง และสัตว์ขี่):** ผ้าคลุมเอวโปร่งด้านข้าง Luminous Gold สีทองอร่าม, กำไลต้นแขน/ข้อมือและริบบิ้น Luminous Gold, เกาะอก บิกินี และผ้าคลุมหลัง Rich Midnight Blue
    - **Super Novice (ช/ญ และสัตว์ขี่):** ทูนิก/ชุดนอก Rich Midnight Blue, เกราะอก Moonlight Silver, สายสะพายกากบาท โบว์ และหัวเข็มขัด Luminous Gold, กางเกง/ซับใน Deep Midnight Navy
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 108, `patch_status.js` = 108)

---

## แพตช์ 0107 — 2026-09-13

- **ไฟล์แพตช์:** `0107_20260913_midnight-monsters-suite.thor`
- **ขนาด:** 22.24 MB
- **SHA-256:** `0F838B9319C5DB5CED9B82553DA80BFCFF57BA5ABDFE52364638BA09103594F8`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `midnight.grf`
  - `System\monster_size_effect_new.lub`
  - `SystemEN\monster_size_effect_new.lub`
- **รายละเอียดการเปลี่ยนแปลง:**
  - เพิ่ม Custom Sprite, Action, Palette Recolor และ Thematic Visual Effect สำหรับมอนสเตอร์กลางคืนครบชุด (IDs 25000–25006):
    - **ID 25000 (Midnight Poring):** สไปรต์ Poring สีม่วงคอสมิก + สัญลักษณ์พระจันทร์เสี้ยวสีทองบนหน้าผาก (`EF_MOONSTAR`, `EF_GLOW1`)
    - **ID 25001 (Midnight Familiar):** ปีกและลำตัวสีน้ำเงินอมม่วงมิดไนท์ + ตาสีทับทิม (`EF_TORCH_PURPLE`)
    - **ID 25002 (Midnight Skeleton):** โครงกระดูกสีเงินแสงจันทร์ + เกราะน้ำเงินเข้มมิดไนท์ (`EF_BLUELIGHTBODY`)
    - **ID 25003 (Midnight Zombie):** ชุดสีม่วงสนธยา + ผิวสีเถ้าผีดิบ (`EF_POISONSMOKE`)
    - **ID 25004 (Midnight Shadow Willow):** ลำต้นสีออบซิเดียน + ผลึกใบไม้แซฟไฟร์ (`EF_GLOW2`)
    - **ID 25005 (Midnight Demon):** ปรับโฉมจาก Mini Demon ลำตัวม่วงมิดไนท์ + กรงเล็บ/ตาสีทอง + เคียวทมิฬ (`EF_TORCH_PURPLE`)
    - **ID 25006 (Midnight Hyegun):** ชุดเจียงซือสีกรมท่าเข้ม + ยันต์หน้าผากสีทองลงอักขระสีแดงเข้ม (`EF_GHOST`, `EF_SOULLIGHT`)
  - อัปเดต `data\luafiles514\lua files\datainfo\jobname.lub` เชื่อมโยง ID 25000–25006 เข้ากับ Sprite ตระกูล midnight
  - ปรับปรุง `System\monster_size_effect_new.lub` ให้เอฟเฟกต์เข้าธีมรัตติกาล สวยงามและสบายตา
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 107, `patch_status.js` = 107)

---

## แพตช์ 0106 — 2026-09-13

- **ไฟล์แพตช์:** `0106_20260913_event-moon-items.thor`
- **ขนาด:** 21.99 MB
- **SHA-256:** `EE1D615C0121075836BFD10D3B1A6DF607CE06ACB099A1441C6CD3BFF9F8E659`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `midnight.grf`
  - `SystemEN\itemInfo_C.lua`
- **รายละเอียดการเปลี่ยนแปลง:**
  - เพิ่ม visual assets ครบชุดสำหรับไอเทมกิจกรรมเซิร์ฟเวอร์ Midnight RO ได้แก่:
    - **ID 902247 (Moon Fragment):** ไอคอนช่องเก็บของ 24×24, ภาพ Collection View 75×100 บนพื้นหลังสีขาวบริสุทธิ์ (`RGB 255, 255, 255`), สไปรต์ตกพื้น (`.spr`, `.act`) ไร้ขอบสีชมพู (De-fringed)
    - **ID 902248 (Moonlit Dust):** ไอคอนช่องเก็บของ 24×24, ภาพ Collection View 75×100 บนพื้นหลังสีขาวบริสุทธิ์ (`RGB 255, 255, 255`), สไปรต์ตกพื้น (`.spr`, `.act`)
  - เพิ่มคำอธิบายภาษาไทยและข้อมูลคุณสมบัติใน `SystemEN\itemInfo_C.lua` ด้วย Encoding CP874
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 106, `patch_status.js` = 106)

---

## แพตช์ 0105 — 2026-09-12

- **ไฟล์แพตช์:** `0105_20260912_clothes-dye-16-colors.thor`
- **ขนาด:** 21.96 MB
- **SHA-256:** `C602D2467853080F4A301F67743922A16962E602A723E36BFF4A15D120C119F0`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`, whole-file replace of `midnight.grf`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `midnight.grf` (25.87 MB → 26.20 MB)
- **รายละเอียดการเปลี่ยนแปลง:**
  - ขยายจำนวนสีชุด (clothes dye) จาก 8 สี (index 0-7) เป็น 16 สี (index 0-15) ครบทั้ง 46 อาชีพ/เพศ (สอง class รวมทั้งอาชีพขี่พาหนะ)
  - ตัดสีดำเดิมของ Gravity ที่ index 4 ทิ้งทั้งหมด เพราะจมเป็นเงาทึบไม่เห็นลายและทาสีทับส่วนที่ไม่ใช่ผ้า (เกราะ กางเกง ตัวพาหนะ) ที่ไม่มีสีย้อมอื่นแตะเลย สีเดิม index 5-7 เลื่อนลงมาแทนที่เป็น 4-6
  - index 7-14 เป็นสีใหม่ทั้งหมด สร้างด้วยการถ่วงน้ำหนักตามช่วงเนื้อสีที่สีย้อมทางการ 0-3 เคยขยับจริง ไม่ย้อมทับส่วนที่ไม่เคยเปลี่ยนสี เช่น หนัง รองเท้า
  - index 15 คือ "Midnight" สีประจำเซิร์ฟ ขาว-น้ำเงิน-ทอง แยกบทบาทตามพื้นที่ที่แถบสีนั้นกินบนตัวละครจริง (แถบใหญ่สุด=ขาวเงิน รองลงมา=น้ำเงิน แถบขอบเล็ก=ทอง)
  - เครื่องมือสร้างพาเลตทั้งหมดเก็บไว้ที่ `server/tools/palette-gen/` พร้อม README สำหรับสร้างอาชีพเพิ่มในอนาคต
  - ปรับ NPC ร้านย้อมสีชุด (`npc/custom/etc/cloth_dyer.txt`) ให้เสนอครบ 16 สีแทนที่จะจำกัดไว้แค่ 7 (แพตช์ฝั่ง server แยกต่างหาก ไม่อยู่ใน `.thor` นี้)
  - แพตช์นี้ชิปทั้งไฟล์ `midnight.grf` แทนการ merge เฉพาะ member เพราะชื่อไฟล์ palette ภายในเป็นภาษาเกาหลี (สืบมาจากชื่อสไปรท์ต้นฉบับ) ซึ่ง THOR เก็บ path เป็น windows-1252 เข้ารหัสภาษาเกาหลีไม่ได้
- **ผลกระทบกับผู้เล่น:** ตัวละครที่ตั้งค่าสีชุดเป็น index 4-7 อยู่ก่อนแพตช์นี้จะเห็นสีเปลี่ยนทันทีหลังแพตช์ เพราะ index เดิมชี้ไปที่ไฟล์ใหม่ ไม่ใช่บั๊ก
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 105, `patch_status.js` = 105)

---

## แพตช์ 0102 — 2026-09-11

- **ไฟล์แพตช์:** `0102_20260911_autohunt-tactical-ground-reticle.thor`
- **ขนาด:** 0.07 MB (71.68 KB)
- **SHA-256:** `C374B8B3859615B1A45E724659845A22DC4A53F7DF91B44897490009A8784B2D`
- **ประเภทแพตช์:** Member-level GRF Merging (`use_grf_merging: true`, target: `midnight.grf`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `data\texture\effect\midnight_auto_hunt\midnight_auto_hunt.tga`
  - `data\texture\effect\midnight_auto_hunt\midnight_auto_hunt.str`
  - `data\luafiles514\lua files\hateffectinfo\hateffect_f.lub`
  - `data\luafiles514\lua files\hateffectinfo\hateffect_f.lua`
- **รายละเอียดการเปลี่ยนแปลง:**
  - เปลี่ยนแปลงการแสดงผลภาพของสถานะ Auto Hunt (บอทค้นหาและล่ามอนสเตอร์อัตโนมัติ) จากป้ายลอยหัวเดิม เป็น **วงเรดาร์ยุทธวิธีใต้ฝ่าเท้า (Option 8: Hunter Tactical Ground Reticle)**
  - **โทนสี Theme 1 (Midnight Violet & Cyber Cyan):** เส้นนอกและตัวอักษรทิศ N / E / S / W สีม่วงนีออนมิดไนท์ พร้อม Bloom เรืองแสง, วงในและกากบาทสีฟ้าไซเบอร์ประกายขาว
  - **การปรับแต่งขนาด:** ปรับรัศมีวงกว้าง 106 px / สูง 53 px พอดีกับขอบด้านในของวงแหวนสีเหลืองใต้ฝ่าเท้า
  - **แอนิเมชันแสง (Slow Breathing Pulse):** จังหวะแสงวูบวาบหายใจช้าๆ นุ่มนวล 6.0 วินาทีต่อรอบ แนบสนิทกับระนาบพื้นผิว ไม่เกะกะสายตา
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 102, `patch_status.js` = 102)

---

## แพตช์ 0101 — 2026-09-11

- **ไฟล์แพตช์:** `0101_20260911_pecopeco-hairband-info.thor`
- **ขนาด:** 2.29 MB
- **SHA-256:** `80473C5A251FA0FD70B974F0E33B4816EFF38F08F3AEB1903FC6574553F1D8EE`
- **ประเภทแพตช์:** Loose-file (`use_grf_merging: false`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `SystemEN\LuaFiles514\itemInfo.lua`
- **รายละเอียดการเปลี่ยนแปลง:**
  - อัปเดตคำอธิบายภาษาไทยและข้อมูลคุณสมบัติของไอเทม **Pecopeco Hairband (ID: 5286)** ให้ตรงกับสเตตัสฝั่ง Server:
    - ปรับพลังป้องกัน (Defense): 6
    - ปรับเลเวลที่ต้องการ (Equip Level): 1
    - ปรับเพิ่ม ASPD: +5% (Delay หลังการโจมตีลดลง 5%)
    - ปรับลดระยะเวลาร่ายเวทมนตร์: -5%
    - เพิ่มโบนัสสถานะ VIP: All Stats +1 เมื่อมีสถานะ VIP ทำงาน
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 101, `patch_status.js` = 101)

---

## แพตช์ 0100 — 2026-09-11

- **ไฟล์แพตช์:** `0100_20260911_gm03-white-suit-gold-name.thor`
- **ขนาด:** 3.73 KB
- **SHA-256:** `8D160FA1AFBB459718D00B2CE3555A1B83EEC2B6E5DAE45F93633339C29DF5CB`
- **ประเภทแพตช์:** Loose-file (`use_grf_merging: false`)
- **รายการไฟล์ที่รวมในแพตช์:**
  - `data\clientinfo.xml`
  - `data\sclientinfo.xml`
- **รายละเอียดการเปลี่ยนแปลง:**
  - อัปเดต clientinfo สำหรับการแสดงผลรูปลักษณ์ชุดขาวและชื่อสีทองของ GM
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 100)

---

## แพตช์ 0099 — 2026-09-10

- **ไฟล์แพตช์:** `0099_20260910_vip-status-icon-and-gold-priority.thor`
- **ขนาด:** 11.45 KB
- **SHA-256:** `29EB26A666A59E8704285D96525E731F2A7E4BF3729938B401D3960A81282BBE`
- **ประเภทแพตช์:** Loose-file / Asset update
- **รายการไฟล์ที่รวมในแพตช์:**
  - `data\texture\유저อินเตอร์เฟซ\basic_interface\vip_premium.tga`
  - `System\stateiconimginfo.lub`
- **รายละเอียดการเปลี่ยนแปลง:**
  - อัปเดตไอคอนบัฟ VIP Premium สไตล์น้ำเงินอมม่วง (32×32) ขอบขาวทอง ปีกทอง
  - ยกระดับ EFST 1511 ขึ้น Priority 0 (`StateIconImgList[0]` - PRIORITY_GOLD) นำหน้าบัฟอาหารและสกิล
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches` (`plist.txt` = 99)

---

> หมายเหตุ: ประวัติแพตช์ลำดับ 0001 ถึง 0098 สามารถตรวจสอบได้จากรายการไฟล์ย้อนหลังใน `tools/patcher/patch_defs/` และประวัติ commit ของ repository นี้
