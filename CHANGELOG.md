# MIDNIGHT RO — Client Patch Changelog

บันทึกประวัติการปล่อยแพตช์ฝั่ง Client (`.thor`) สำหรับ MIDNIGHT RO Launcher และตัวเกม

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
