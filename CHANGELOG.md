# MIDNIGHT RO — Client Patch Changelog

บันทึกประวัติการปล่อยแพตช์ฝั่ง Client (`.thor`) สำหรับ MIDNIGHT RO Launcher และตัวเกม

---

## Patch 0120 — 2026-09-17

- **Patch file:** `0120_20260917_launcher-bootstrap-config-hotfix.thor`
- **Size:** 693 bytes
- **SHA-256:** `B8630DA1861C0353B3477A4F4D921C57BBBB3B32148828B1A2F12D96368F5DF6`
- **Patch type:** Loose-file hotfix (`use_grf_merging: false`)
- **Entries:** `MidnightRO.yml`
- **Details:** Restores the normal `MidnightRO-Ragexe.exe` launch target after patch 0118’s temporary `MidnightRO-v3.exe` upgrade helper has been removed.
- **Verification:** Client local and Client Linux candidate tests passed. The downloaded public THOR SHA-256 matches the released file; remote `plist.txt` and cache-busted `patch_status.js` both report index 120. The payload is limited to the Production launcher configuration and contains no Local endpoint or player data.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0119 — 2026-09-17

- **Patch file:** `0119_20260917_ip-limit-message.thor`
- **Size:** 168,550 bytes
- **SHA-256:** `C0DF99776A54D9CA14CB727DA4B05E45681B190A41004BD3F4566B053DDF6377`
- **Patch type:** Member-level GRF merging (`use_grf_merging: true`, target: `midnight.grf`)
- **Entries:** `data\msgstringtable.csv`, `data\msgstringtable.txt`
- **Details:** Replaces the obsolete Internet Cafe overflow text with the approved three-line Thai message explaining that the current IP has reached its connection limit.
- **Verification:** User live-test passed with two accounts allowed and a third direct `MidnightRO-Ragexe.exe` connection rejected. The public THOR was downloaded back with matching SHA-256; Launcher applied patches `117 → 119`; both applied GRF member hashes match the tested candidate byte-for-byte. Production `DATA.INI` remained `midnight.grf`, `new_ai_final.grf`, `data.grf`, with no Local endpoint or player data included.
- **Status:** Published to GitHub Release `patches` (`plist.txt` and `patch_status.js` = 119).

---

## Patch 0118 — 2026-09-17

- **Patch file:** `0118_20260917_device-trust-launcher.thor`
- **Size:** 2,046,708 bytes
- **SHA-256:** `65F39EB842657ED3CDE985135312E572E37B43614FDAE283353F94BBE39978B7`
- **Patch type:** Loose-file staged Launcher upgrade (`use_grf_merging: false`)
- **Entries:** `MidnightRO.yml`, `MidnightRO-v3.exe`, `MidnightRO-v3.yml`
- **Details:** Ships the tested Launcher with a compiled two-instance ceiling and Phase 3 opaque installation-presence reporting. A temporary bootstrap starts the staged executable, which promotes itself to `MidnightRO.exe` and restores the normal production configuration.
- **Verification:** Staged executable/config hashes match the user-tested Client Linux candidate. The public THOR was downloaded back with matching SHA-256; Launcher applied the patch, promoted the staged executable/config, retained bookmark 119, and removed staging files on the next normal start. No Local endpoint or player data was included.
- **Status:** Published to GitHub Release `patches`.

---

## แพตช์ 0117 — 2026-09-16

- **ไฟล์แพตช์:** `0117_20260916_gm-sprites-only-2000008-2000009.thor`
- **ขนาด:** 822 bytes
- **SHA-256:** `AF7C7C6FB6E5554124F596183994A74876BA0E3E7E4D0101A08356B890C9BA81`
- **ประเภทแพตช์:** Member-level GRF Merging (`use_grf_merging: true`, target: `midnight.grf`)
- **รายการไฟล์:** `data\clientinfo.xml`, `data\sclientinfo.xml` จำนวน 2 entries
- **รายละเอียด:** ปรับ GM sprite list ให้เหลือเฉพาะ Account ID `2000008` และ `2000009`; Account ID `2000000` และ `2000001` กลับไปแสดงชุดอาชีพ โดยไม่เปลี่ยน Group หรือสิทธิ์ฝั่ง Server
- **ผลตรวจ:** ผู้ใช้ยืนยัน live-test candidate แล้ว; THOR payload ทั้งสองไฟล์มีเฉพาะสอง Account ID ที่กำหนด ใช้ Production endpoint และไม่มี `DATA.INI`, Local endpoint หรือข้อมูลผู้เล่น ดาวน์โหลด THOR, `plist.txt` และ `patch_status.js` กลับจาก GitHub Release แล้วตรวจ SHA-256/เลขแพตช์ตรงกับ local
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0116 — 2026-09-16

- **ไฟล์แพตช์:** `0116_20260916_admin99-gm-sprites.thor`
- **ขนาด:** 830 bytes
- **SHA-256:** `3DF298C89BBA14E8A87303D324DBA516C46E2CCE47BB96095A80029D36AA2774`
- **ประเภทแพตช์:** Member-level GRF Merging (`use_grf_merging: true`, target: `midnight.grf`)
- **รายการไฟล์:** `data\clientinfo.xml`, `data\sclientinfo.xml` จำนวน 2 entries
- **รายละเอียด:** กำหนด Account ID `2000000`, `2000001` และ `2000009` เป็น GM sprite เพื่อให้บัญชี Admin Group 99 ที่ยืนยันในงานนี้แสดงชุด GM ทั้ง Client local และ Client Linux
- **ผลตรวจ:** THOR และ payload ผ่าน audit; endpoint เป็น Production และไม่มี `DATA.INI`, `server_Local_endpoint.grf` หรือข้อมูลผู้เล่นในแพตช์ ดาวน์โหลด THOR, `plist.txt` และ `patch_status.js` กลับจาก GitHub Release แล้วตรวจ SHA-256/เลขแพตช์ตรงกับ local
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0115 — 2026-09-16

- **ไฟล์แพตช์:** `0115_20260916_costume-2-gacha-moon-size-fix.thor`
- **ขนาด:** 23,281,754 bytes (22.20 MB)
- **SHA-256:** `83D7632C5E39484F30DCD18C794C468B4B9B4D0AD650E685A6178403F08005C1`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`)
- **รายการไฟล์:** `midnight.grf` จำนวน 1 entry
- **รายละเอียด:** ปรับภาพ Costume 2 Gacha Egg ให้มีขนาดและทรงกะทัดรัดเท่ากับ Costume 1 และ Shadow Gacha Egg พร้อมเพิ่มพระจันทร์เสี้ยวเป็นองค์ประกอบกลาง และอัปเดต BMP inventory/collection กับ SPR ภายใน GRF
- **ผลตรวจ:** THOR header และ checksum ผ่าน; ดาวน์โหลด THOR, `plist.txt` และ `patch_status.js` กลับจาก GitHub Release แล้ว SHA-256 ตรงกับ local ทุกไฟล์
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0114 — 2026-09-16

- **ไฟล์แพตช์:** `0114_20260916_gacha-eggs.thor`
- **ขนาด:** 23,282,523 bytes (22.20 MB)
- **SHA-256:** `1A28D2E7017C221BD63B07CAC1A9ECD779C8603A6DFF4A290F04C2D0ECB755D5`
- **ประเภทแพตช์:** Loose-file migration (`use_grf_merging: false`)
- **รายการไฟล์:** `SystemEN\itemInfo_C.lua`, `midnight.grf` จำนวน 2 entries
- **รายละเอียด:** เพิ่ม tooltip และรูปไอเท็มของ Costume 1, Costume 2 และ Shadow Gacha Egg (`902250`–`902252`) โดย `midnight.grf` มี BMP inventory/collection และ SPR/ACT ครบทั้งสาม resource. ใช้ full custom GRF เพราะ member path ภายในเป็นภาษาเกาหลีซึ่ง THOR ไม่รองรับการเข้ารหัส path แบบ member-level.
- **ผลตรวจ:** THOR header, patch definition และ checksum ผ่าน; ไม่มี `DATA.INI`, `server_Local_endpoint.grf` หรือข้อมูลผู้เล่นในแพตช์. ดาวน์โหลด THOR, `plist.txt` และ `patch_status.js` กลับจาก GitHub Release แล้ว SHA-256 ตรงกับ local; remote metadata และบรรทัดท้าย plist ชี้เลข 114/ชื่อไฟล์เดียวกัน. ตรวจเว็บไซต์สาธารณะ `https://midnight-ro.divlab.co` ตอบ HTTP 200.
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0113 — 2026-09-15

- **ไฟล์แพตช์:** `0113_20260915_midnight-aura-hateffect-fix.thor`
- **ขนาด:** 2,777 bytes
- **SHA-256:** `730D16503C4276A0BB17AC170A2A9AC679DFE5C9733A5AEC70774D8893D8AF31`
- **ประเภทแพตช์:** Member-level GRF Merging (`use_grf_merging: true`, target: `midnight.grf`)
- **รายการไฟล์:** `data\luafiles514\lua files\hateffectinfo\hateffect_f.lub` จำนวน 1 entry
- **รายละเอียด:** รวม HatEffect ของ Auto Hunt ID 1 กับ Costume Midnight RO Aura ID 289 ไว้ใน wrapper เดียว แก้ Aura ของไอเทม 35022 ที่หายหลังแพตช์ 0102 โดยคง tactical ground reticle ของ Auto Hunt ไว้
- **ผลตรวจ:** ผู้ใช้ยืนยัน live-test candidate ว่า Aura และ Auto Hunt แสดงถูกต้อง; THOR header/target/entry/payload/CRC32 ผ่าน, payload ตรงกับไฟล์ที่ทดสอบทุก byte และไม่มี Local endpoint หรือข้อมูลผู้เล่น; ดาวน์โหลด THOR, `patch_status.js` และ `plist.txt` กลับจาก GitHub แล้ว SHA-256 ตรง local โดย remote metadata ชี้เลข 113 และชื่อไฟล์เดียวกัน
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0110 — 2026-09-14

- **ไฟล์แพตช์:** `0110_20260914_coin-bundle-10.thor`
- **ขนาด:** 5,450 bytes
- **SHA-256:** `9A662AB9ADEBB8D4F7AF01A52AF8072E30BB14FDA1770DA43540FBC5795CF72F`
- **ประเภทแพตช์:** Loose file (`use_grf_merging: false`)
- **รายการไฟล์:** `SystemEN\itemInfo_C.lua` จำนวน 1 entry
- **รายละเอียด:** แก้คำอธิบาย Gold Coin (`671`) ให้ระบุว่ากดใช้ครั้งละ 10 Coin เพื่อรับ 10 Point, ต้องมีอย่างน้อย 10 Coin และซื้อกลับจาก Cash Shop ในราคา 10 Point ต่อ 10 Coin
- **ผลตรวจ:** ผู้ใช้ยืนยัน live-test tooltip และระบบแลก/ซื้อใน Client master; THOR header/definition ผ่าน, ไม่พบ Local endpoint หรือข้อมูลผู้เล่น, ดาวน์โหลด THOR กลับจาก GitHub แล้วขนาดและ SHA-256 ตรงกับ Release asset digest; remote asset `plist.txt` และ `patch_status.js` มี digest ตรงกับไฟล์ local และชี้เลข 110
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

---

## แพตช์ 0109 — 2026-09-13

- **ไฟล์แพตช์:** `0109_20260913_costume-tooltip-cleanup.thor`
- **ขนาด:** 2,392,112 bytes (2.28 MB)
- **SHA-256:** `4FBBEFAC455A566356D216751FD56BE577EC0F7BA0BABFF7630AE639D54B93D3`
- **ประเภทแพตช์:** Loose file (`use_grf_merging: false`)
- **รายการไฟล์:** `SystemEN\LuaFiles514\itemInfo.lua` จำนวน 1 entry
- **รายละเอียด:** ลบข้อความแลก Costume Enchant Stone Box ของ Designer/Disigner Heidam ที่เลิกใช้งานออกจาก tooltip Costume ทุกชิ้นที่มีข้อความดังกล่าว โดยไม่เปลี่ยนข้อมูลไอเทมส่วนอื่น
- **ผลตรวจ:** ผู้ใช้ยืนยัน live-test จาก Client master ว่าข้อความหายและ Costume/Shadow สวมได้ตามนโยบายใหม่; THOR header และ definition ผ่าน, ไม่มี `server_Local_endpoint.grf`; ดาวน์โหลด THOR กลับจาก GitHub ได้ 2,392,112 bytes และ SHA-256 ตรง Release digest; remote `plist.txt` กับ `patch_status.js` ตรงกันที่ 109
- **สถานะ:** ปล่อยแล้วบน GitHub Release `patches`

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
