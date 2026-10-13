# PC Login / map-loading images — 2026-10-13

## Scope and result

Owner requested the accepted Mobile Geffen Login and 11 town scenes in PC,
while retaining Ragnarok's native loading bar/percentage. Implementation is
in **Client-master-pc**, tested against **Server local** first as requested.

**OWNER REPORTED — PC MASTER TEST PASS:** owner replied “ทดสอบเองแล้ว ผ่าน”
after master was updated and the native game was opened. Agent independently
captured the Geffen Login/wordmark in the actual native PC window. Login/map
gameplay and loading visuals are owner-reported, not an agent replay. The game
window had closed by the following read-only check. Do not retest this accepted
master merely to collect duplicate evidence.

Client local and Client Linux have only been read to compare existing config;
neither was modified or tested in this task. Their acceptance remains PENDING.
No patch number/THOR/upload/production deployment has been created.

## Source and runtime changes

- Generator: `tools/client-patch/build_pc_login_loading_art.py`.
- Independent PC source snapshots: `ui_sources/pc_login_loading/`, 11 PNGs and
  source SHA-256 manifest adopted from Mobile runtime57d5508. No Mobile writes.
- Baseline RGB JPEG 1024x768 / quality98 / 4:4:4, symmetric 16:9→4:3 crop.
  Logos retained, proportions unchanged, no baked loading caption/bar/%.
- Login Geffen: `data/texture/<Korean UserInterface>/t_login.jpg`.
- Eleven scenes mapped in order to loading00…10.jpg: Prontera, Morocc, Payon,
  Geffen, Alberta, Lutie, Izlude, Aldebaran v2, Comodo, Yuno, Orc Village.
- Same JPEGs in both `data/texture/` and the Korean UserInterface folder for
  existing texture lookup compatibility: 23 image members in midnight.grf.
- Existing clientinfo/sclientinfo `<loading>` listed only loading00.jpg.
  Extended the list to 11 in midnight.grf, Local endpoint GRF and loose master
  data XML. All bytes outside `<loading>` are preserved, including connection,
  encoding declaration, flags, version and admin settings.
- The master Local endpoint matches this PC's network interface; listeners
  6900/6121/5121 were already running. No Server source, config or process changed.

## Audit and rollback

- Existing midnight.grf: 7,367 → 7,389 members (22 new loading paths).
- Existing Local endpoint GRF: same 2 XML members, changed loading list only.
- Every untouched GRF member verified byte-identical after merging; compressed
  original member blocks are retained. Only replacement images/XML are appended.
- DATA.INI, Ragexe, launcher, d3d9.dll and AutoHuntUiPlugin.dll hashes unchanged.
  data.grf/new_ai_final.grf size/mtime unchanged. **2,911 player files** under
  savedata/ScreenShot/Replay/memo/emblem byte-identical after generator apply and
  before launching the game; no claim that normal gameplay never updates saves.
- Backup: `Backups/pc_login_loading/20261013_before_town_art/` contains original
  midnight.grf, Local endpoint archive and two loose XML files. Close game and
  launcher before restoring these exact files. Do not restore over newer work
  without comparing it first. Player directories are outside rollback scope.
- Raw metadata/screenshots/build-report: `.scratch/pc-loading-art-20261013/`.
  Native Login image: `pc-login-initial.png`; original source/pool observation:
  `original-art-layout.json`; `protected-before.json`/`protected-after-apply.json`.
  Private Local XML/endpoint backup and raw evidence must never enter Git/packages.

## Candidate and next steps

Candidate location: `Patch_Test/pc_login_loading_20261013/`. Contains only the
23 JPEG member paths + **Production** clientinfo/sclientinfo (25 files), README
and SHA256SUMS. Production XML outside loading matches both existing Client
local/Linux midnight.grf copies, avoiding unrelated master experiments.

Apply by member merge using `tools/client-patch/apply_pc_login_loading_candidate.py`
with the explicit target directory after the owner schedules that test. Do not
replace a player's entire midnight.grf with the development master and do not
copy the private build staging directory. The helper validates exact allowlist
and SHA-256 before applying, preserves other members, updates the Local image
list in-place without shipping a Local endpoint, and backs up target files.

Candidate is PENDING Client local + Server local, then Client Linux + Server
Linux tests and owner confirmation. New runtime paths remain in dev_hold.txt.
Only a later explicit release request permits remote-number reconciliation and
THOR creation. Images total 7,968,274 unique JPEG bytes / 16,537,391 bytes for
23 lookup members; future numbered patches need size-aware batches under the
existing 8 MiB limit, not a manual full-GRF release. No patch numbers reserved.
