# MIDNIGHT RO — Client Patch Changelog

บันทึกประวัติการปล่อยแพตช์ฝั่ง Client (`.thor`) สำหรับ MIDNIGHT RO Launcher และตัวเกม

---

## Patch 0131 — 2026-09-26

- **Patch file:** `0131_20260926_ro-style-item-icons-and-collections.thor`
- **Size:** 131,714,560 bytes (125.61 MB)
- **SHA-256:** `C877C6CA8E4888EDBBAE3B9D405D7FF00E48737766262B504E113DF2B8D1D885`
- **Patch type:** Loose-file migration (`use_grf_merging: false`, `-AllowLargeMidnightMigration`)
- **Entries:**
  - `midnight.grf`
- **Details:**
  - **Official RO-Style Graphic Redesign for Items 902269 - 902273:**
    - ปรับปรุงภาพไอคอนในกระเป๋า (Item Icon 24x24 BMP) และภาพรายละเอียดไอเทม (Collection Artwork 75x100 BMP) ใหม่ทั้งหมดให้เป็นลายเส้นและสไตล์ศิลปะทางการของ Ragnarok Online
    - **902269:** `[Hunter C] Kasaka Shadow Fang` — กริชเขี้ยวอสรพิษคาซากะ คมดาบผลึกใสสีฟ้าครามอาบไอพิษสีม่วง ด้ามจับกระดูกงูสีนิล
    - **902270:** `[Hunter B] Obsidian Crown of the Monarch` — มงกุฎจักรพรรดิเงา ผลึกหินออบซิเดียนสีดำขลับ ลวดลายรูนและอัญมณีสีม่วงเข้มเปล่งแสง
    - **902271:** `[Hunter A] Monarch's Shadow Gaze` — แววตาจักรพรรดิเงาสีฟ้าครามสว่างวาบ พร้อมประกายเปลวเพลิงวิญญาณสีม่วงสะบัดพริ้ว
    - **902272:** `[Hunter S] Monarch's Shadow Aura` — ออร่าปีกหมอกเงาแห่งจักรพรรดิสีรัตติกาล สยายพร้อมเปลวเพลิงสีฟ้า-ม่วงอันสง่างาม
    - **902273:** `Newbie Pastel Poring Hat` — แก๊งโพริ่งสีม่วงพาสเทลแสนน่ารัก แก้มอมชมพู สไตล์ภาพวาดเฮดเกียร์โพริ่งของ RO แท้
  - **Graphics Standard Compliance:**
    - Item Icons: 24x24 BMP พร้อมเส้นขอบตัดดำคมชัด (Crisp 1px Contour) บนพื้นหลัง Magenta `(255, 0, 255)` ไม่มีขอบเบลอหรือสีเพี้ยนในเกม
    - Collection Artworks: 75x100 BMP จัดกึ่งกลางบนพื้นหลังสีขาวบริสุทธิ์ `(255, 255, 255)` ตามมาตรฐาน UI Collection ของ RO
- **Verification:**
  - Clothes palette policy: 0 failures, Website palette check 21/21 passed.
  - mkpatch built successfully with verified THOR magic `ASSF (C) 2007 Aeomin DEV`.
  - Uploaded to GitHub Release `patches` successfully; updated `plist.txt` and `patch_status.js` pointing to Index 131.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0130 — 2026-09-26

- **Patch file:** `0130_20260926_newbie-pastel-poring-hat.thor`
- **Size:** 131,745,792 bytes (125.64 MB)
- **SHA-256:** `3279C9996521AE1FCA55D48F5A523922324B12E803EB57D380598D5B97E32DD6`
- **Patch type:** Loose-file migration (`use_grf_merging: false`, `-AllowLargeMidnightMigration`)
- **Entries:**
  - `midnight.grf`
  - `SystemEN\itemInfo_C.lua`
- **Details:**
  - **Newbie Adventurer Cap Custom Redesign — Pastel Poring Trio (ID: 902273):**
    - ปรับเปลี่ยนดีไซน์หมวกผู้เล่นใหม่จากหมวกแก๊ปเดิมเป็นแก๊งโพริ่งพาสเทล 3 ตัว (ตัวใหญ่ตรงกลาง + เบบี้โพริ่งซ้ายขวา)
    - แอนิเมชันเด้งดึ๋งนุ่มนวลแบบธรรมชาติ (Wave Bouncing) ครบทั้ง 8 ทิศทาง
    - จัดกึ่งกลางพิกัดศีรษะ (Head Anchor Calibration) ครบทั้ง 8 ทิศทาง วางลงพอดีบนกระหม่อมและแนวผม
    - อาร์ตเวิร์ก 3D Realistic สำหรับ Item Icon (24x24) และ Collection Window (75x100) สไตล์ 3D นุ่มนวลพาสเทล
    - ลงทะเบียน View ID `2853` ใน `accessoryid.lub` และ `accname.lub`
    - กำหนดประเภทเป็นหมวกหลัก (`Head_Top`) สเตตัสและคำอธิบายภาษาไทยใน `itemInfo_C.lua`
- **Verification:**
  - Clothes palette policy: 0 failures, Website palette check 21/21 passed.
  - mkpatch built successfully with verified THOR magic `ASSF (C) 2007 Aeomin DEV`.
  - Uploaded to GitHub Release `patches` successfully; updated `plist.txt` and `patch_status.js` pointing to Index 130.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0129 — 2026-09-25

- **Patch file:** `0129_20260925_launcher-config-hotfix.thor`
- **Size:** 695 bytes
- **SHA-256:** `A72183E76914A3BCE5428A1D54A3B604CF26148AB78886E8741FDFDF6317E6B4`
- **Patch type:** Loose-file hotfix (`use_grf_merging: false`)
- **Entries:**
  - `MidnightRO.yml`
- **Details:**
  - แก้ไขคอนฟิก Launcher ให้ผู้เล่นทุกคน โดยตั้งค่า `play.path: MidnightRO-Ragexe.exe` เพื่อป้องกันกรณี `MidnightRO.yml` ค้างอยู่ที่ `MidnightRO-v4.exe` จากช่วงอัปเกรดตัว Launcher ใน Patch 0122
- **Verification:**
  - mkpatch built successfully with verified THOR magic `ASSF (C) 2007 Aeomin DEV`.
  - Staged only 1 file (`MidnightRO.yml`); no Local endpoint, player data, or personal files included.
  - Uploaded to GitHub Release `patches` successfully; updated `plist.txt` and `patch_status.js` pointing to Index 129.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0128 — 2026-09-25

- **Patch file:** `0128_20260925_hunter-costumes-and-midnight-gates.thor`
- **Size:** 131,701,760 bytes (125.6 MB)
- **SHA-256:** `109767C2F10C890B5A05528E64D88BF4F129B351457C98A100AABCE1FEAF6D9B`
- **Patch type:** Loose-file migration (`use_grf_merging: false`, `-AllowLargeMidnightMigration`)
- **Entries:**
  - `midnight.grf`
  - `SystemEN\itemInfo_C.lua`
- **Details:**
  - **Re-sprite Midnight Gate (15 Frames Loop):**
    - อัปเกรด Solo Leveling Abyss Shadow Gate ทั้ง 6 ระดับ (Rank E..S, Job ID 10701..10706) จากแอนิเมชันเดิม 10 เฟรม เป็น 15 เฟรมสมบูรณ์แบบ (`fro_shadow_loop.gif`)
    - สร้างโครงสร้าง ACT 0x0205 แบบ Custom 15 เฟรม โดยเซ็ตตำแหน่ง grounded target_y=-70 และ Frame delay 3.5 (~75ms ต่อเฟรม) ให้จังหวะพวยพุ่งของไอเงาไหลลื่นสมจริง
    - ลงทะเบียนใน `jobname.lub` และ `npcidentity.lub` ครบทั้งโฟลเดอร์ NPC และ Monster
  - **Hunter Rank Costume Set (Solo Leveling Shadow Monarch 4-Piece):**
    - `902269`: `[Hunter C] Kasaka Shadow Fang` (Costume Lower - Dagger in mouth, View 2850)
    - `902270`: `[Hunter B] Obsidian Crown of the Monarch` (Costume Upper - Dark Crown, View 2851)
    - `902271`: `[Hunter A] Monarch's Shadow Gaze` (Costume Middle - Animated Flame Eyes 9-frame RGBA, View 2852)
    - `902272`: `[Hunter S] Monarch's Shadow Aura` (Costume Garment - Animated 360° Surrounding Mist & Soul Fire, HatEffects 217 & 218)
    - รวบรวม HatEffect Wings (214..216) และ Badges (208..213) ลงใน `hateffect_f.lub` และ `hateffectinfo.lub`
    - เพิ่มคำอธิบายภาษาไทยและข้อมูลไอเทมลงใน `SystemEN\itemInfo_C.lua`
- **Verification:**
  - Clothes palette policy: 0 failures, Website palette check 21/21 passed.
  - mkpatch built successfully with verified THOR magic `ASSF (C) 2007 Aeomin DEV`.
  - Uploaded to GitHub Release `patches` successfully; updated `plist.txt` and `patch_status.js` pointing to Index 128.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0127 — 2026-09-23

- **Patch file:** `0127_20260923_hunter-rank-badges.thor`
- **Size:** 108,444 bytes
- **SHA-256:** `00688BBE51698F574F89B193F0664E738A9B5B3F96D2EBEBBC44C35311D6FA01`
- **Patch type:** Member-level GRF merging (`use_grf_merging: true`, target: `midnight.grf`)
- **Entries:** 22 entries:
  - `data\luafiles514\lua files\hateffectinfo\hateffect_f.lub`
  - `data\luafiles514\lua files\hateffectinfo\hateffect_f.lua`
  - `data\luafiles514\lua files\hateffectinfo\hateffectinfo.lub`
  - `data\luafiles514\lua files\hateffectinfo\hateffectinfo.lua`
  - Textures (6 tiers): `data\texture\effect\midnight_hunter_rank\hunter_rank_{e,d,c,b,a,s}.tga` + fallback paths `data\texture\effect\hunter_rank_{e,d,c,b,a,s}.tga`
  - 3D effects (6 tiers): `data\texture\effect\midnight_hunter_rank\midnight_hunter_rank_{e,d,c,b,a,s}.str`
- **Details:** ระบบเหรียญตราสัญลักษณ์ Hunter Rank (Rank E, D, C, B, A, S) แสดงผลผ่าน Client HatEffect Engine (ID 208–213):
  - ดีไซน์เหรียญตรา Realistic 3D Crest Badge โลหะสีทอง/ทองแดง/ทองคำขาวคมชัด ปราศจากตัวอักษร 2D หยาบ
  - เอฟเฟกต์ STR Static แบบคมชัดคงที่ (กว้าง 24px x สูง 24px) ไม่ลอยขึ้นลง
  - ตำแหน่งจัดวางอยู่ทางขวาของหลอด HP/SP พอดี (`hatEffectPos = -13.0`, `hatEffectPosX = 6.2`) ไม่ทับหลอด HP/SP และไม่บังชื่อกิลด์หรือใต้ชื่อ
  - อัปเดตตาราง HatEffect เป็น Single-Pass Clean Bytecode ไม่ซ้อนทับ ไม่สะดุด
- **Verification:** ตรวจสอบโครงสร้างไฟล์ THOR และ Header `ASSF (C) 2007 Aeomin DEV` ผ่านครบถ้วน 22 ไฟล์; ทดสอบแสดงผลในเครื่องผู้พัฒนาผ่าน `MidnightROClient`; อัปโหลดขึ้น GitHub Release `patches` สำเร็จ พร้อมอัปเดต `plist.txt` และ `patch_status.js` ชี้ไปที่ Index 127
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0126 — 2026-09-23

- **Patch file:** `0126_20260923_skill-balance-round1.thor`
- **Size:** 269,873 bytes
- **SHA-256:** `36CEC3D41A4C59D92E49A895FC22030F85B794216EB6C3EBEA5734E18CF11142`
- **Patch type:** Member-level GRF merging (`use_grf_merging: true`, target: `midnight.grf`)
- **Entries:** `data\luafiles514\lua files\skillinfoz\skilldescript.lub`, `data\luafiles514\lua files\skillinfoz\skillinfolist.lub`
- **Details:** Skill tooltips for skill balance round 1 so the client matches the server: Class 1 changes following Rune Classic (Sword/2H Mastery, Magnum Break 30 s, Demon Bane, Holy Light 250%, Enlarge Weight Limit ASPD, Cart Revolution 250%, Double Attack, Soul Strike/Fire Wall 50 SP, Double Strafe 15 SP, Steal 50 SP), Class 2 buffs (Holy Cross, Shield Boomerang, Raid, Musical Strike, Throw Arrow, Acid Terror, Demonstration, Autospell), and a red "not available" line on Arrow Crafting and the two wedding HP/SP skills. Several pre-renewal tooltips that still showed Renewal numbers were corrected. `skillinfolist.lub` SP amounts updated for Soul Strike, Fire Wall, Double Strafe, Steal and Autospell.
- **Verification:** Both members are plain Lua in CP874/CRLF, compile under Lua 5.1 and pass a strict table-shape check; the THOR header and file table were parsed and both payloads match the verified files byte for byte. Downloaded back from the release: SHA-256, size and header match; remote `plist.txt` and `patch_status.js` end at 126. Server side (server commit `3994a0bae`) deployed to production by the owner before release.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0125 — 2026-09-22

- **Patch file:** `0125_20260922_clothes-dye-2-2-palettes.thor`
- **Size:** 31.71 MB
- **SHA-256:** `3A0A861047C1674C9BF79F4750C174FD45561BAF45B19B97C33E3F328421DB1E`
- **Patch type:** Loose-file migration (`use_grf_merging: false`, `-AllowLargeMidnightMigration`)
- **Entries:** `MidnightRO-Ragexe.exe`, `midnight.grf`
- **Details:**
  - **สีชุดใหม่ใน `midnight.grf`** (SHA-256 `E981D84E7EE189A256E914EA39F21461E7AE3CB3051B436261611A8CD22DFE35`):
    - สี 4 เทาถ่าน (แทนฟ้าน้ำแข็ง) ย้อมเฉพาะส่วนที่สีทางการ 1-3 ย้อม
    - สี 12 แดง-ทอง-ดำ ไม่มีจุดสีรุ้งแทรกแล้ว
    - สี 13 ขาว-เทา-เงิน
    - สี 14 ดำ-เทา-ทอง
    - สี 15 Midnight โทน Starlight แบบนุ่มกับขอบทองสว่าง
    - ทุกพาเลตผ่าน `tools/client-patch/clothes_palette_policy.py` และสี 15 ตรงกับภาพบนเว็บ
  - **`MidnightRO-Ragexe.exe` แก้ BUG-100** (SHA-256 `5F1B3672213485769FAA9A61BFBFE7F4A12D78CC6D366C84F88A91E3EE1C6B0A`):
    - แทน `jne` ที่ file offset `0x9f1172` ด้วย NOP 6 byte (`tools/client-patch/patch_ragexe_own_job_palettes.py`)
    - อาชีพ 2-2 และอาชีพเกิดใหม่ใช้พาเลตของอาชีพตัวเอง แทนพาเลตของอาชีพ 2-1 ที่ใช้มาตลอดเพราะ `servicetype=thai`
    - exe ต้นฉบับ SHA-256 ขึ้นต้น `898997E5F3F6A836`
  - **ผลที่ผู้เล่นจะเห็น:** อาชีพ 2-2 (Crusader, Monk, Sage, Rogue, Alchemist, Bard, Dancer) เห็นสีชุดเปลี่ยนทุกสี รวมสีทางการ 1-3 เพราะได้พาเลตของอาชีพตัวเองเป็นครั้งแรก
- **Verification:**
  - ก่อนสร้างแพตช์: palette policy 0 failures, website palette check 21/21
  - ดาวน์โหลด THOR กลับจาก GitHub ได้ SHA-256 ตรงและมี header `ASSF (C) 2007 Aeomin DEV`
  - remote `plist.txt` และ `patch_status.js` = 125
  - ในเกมก่อนปล่อย: Bard และ Sage สี 12/15 ตรงกับภาพตัวอย่าง
- **Status:** Published to GitHub Release `patches`. ชื่อสีใหม่ในร้านย้อม (server `cloth_dyer`) ต้อง reload NPC แยกต่างหาก.

---

## Patch 0124 — 2026-09-22

- **Patch file:** `0124_20260922_solo-leveling-gates.thor`
- **Size:** 26.35 MB
- **SHA-256:** `A8EEA6609689CC8233750ED65BD7C948B7F6B08C48954DE60A0B6A2FFAF4D28A`
- **Patch type:** Loose-file migration (`use_grf_merging: false`)
- **Entries:** `midnight.grf`
- **Details:**
  - ลบ Sprite ที่เคยไปทับของทางการออกจาก `midnight.grf` ทั้ง 14 ไฟล์ (`4_energy_*`, `4_m_death`) เพื่อดึงภาพ Vanilla RO ดั้งเดิมจาก `data.grf` กลับมาสมบูรณ์
  - เพิ่ม Custom Sprite เฉพาะของ Solo Leveling Gate ครบ 6 ระดับ (`gate_rank_e` ถึง `gate_rank_s`, Job IDs 10701..10706) ในแนวตั้งตรง พร้อม Fluid dynamics animation
  - เชื่อมโยง Job ID และ Display Name ใน `jobname.lub` และ `npcidentity.lub`
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0122 — 2026-09-20

- **Patch file:** `0122_20260920_launcher-repair-cleanup.thor`
- **Size:** 2,051,143 bytes
- **SHA-256:** `C923FD262BB7FEA4FA6B4B258E12BAFFA76EF747BA464BE61CD4E020BD1F6A7A`
- **Patch type:** Loose-file staged Launcher upgrade (`use_grf_merging: false`)
- **Entries:** `MidnightRO.yml`, `MidnightRO-v4.exe`, `MidnightRO-v4.yml`
- **Details:** Upgrades the Launcher so Update/Repair removes empty retired `launcher_ui_v2`/`launcher_ui_v3` directories and obsolete v2/v3/v4 staging files without deleting non-empty directories, links, or player data.
- **Verification:** Launcher unit tests passed 16/16. The final executable SHA-256 `4960B6A8B7D7AFBA9F83240D6F4CDEFAC62867D2874046086CA447D138939E42` passed Client local + Server local and Client Linux + Server Linux tests. THOR integrity/file-table audit found only the three declared payload entries; no `DATA.INI`, Local endpoint, or player data. The public THOR downloaded back at the same size and SHA-256, remote `plist.txt`/`patch_status.js` report 122, and the production Launcher advanced bookmark 121→122, promoted v4 to `MidnightRO.exe`, restored the normal Production config, and removed all staging/UI artifacts on the next start.
- **Status:** Published to GitHub Release `patches`.

---

## Patch 0121 — 2026-09-18

- **Patch file:** `0121_20260918_morocc-guild-stone-test.thor`
- **Size:** 82,700 bytes
- **SHA-256:** `5965FE1D4660253B5875F7B8DA9C33D83D9206F8DFF59AB61A091CCC886F0B6D`
- **Patch type:** Member-level GRF merging (`use_grf_merging: true`, target: `midnight.grf`)
- **Entries:** `data\luafiles514\lua files\datainfo\jobname.lub`
- **Details:** Maps only private test mob ID `22562` to the stock `Empelium90_0.gr2` model, allowing the ordinary attackable Morocc damage target to look like a guild stone without changing real Emperium ID `1288` or WoE rules.
- **Verification:** The same candidate byte passed Client master + Server local, Client local + Server local, and Client Linux + Server Linux live tests, including attack with and without a guild. Production Server runs commit `e1a1d67f0061b2bbc17f61a6844d061bf004cd98` with all four services healthy and no `No castle set at map morocc` error. THOR header/file table passed audit and contains one GRF member only; no `DATA.INI`, Local endpoint, or player data. The public THOR downloaded back at the same size and SHA-256, remote `plist.txt`/`patch_status.js` report `121`, and the actual Launcher advanced `MidnightRO.dat` from `120` to `121`; the merged member SHA-256 is `FE6705937A6F90066BC686CD74DFFE6A8255D54835B6038DF3F12EFA56BA25F2`, matching the tested candidate.
- **Status:** Published to GitHub Release `patches`.

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
