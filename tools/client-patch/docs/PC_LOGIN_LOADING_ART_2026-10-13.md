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

Owner subsequently authorized applying the candidate to both Client local and
Client Linux. Both were updated by member merge and the installed bytes audited
on 2026-10-13. Owner then replied **“โอเคผ่านทั้ง 2 ตรวจเลขแพตซ์แล้วรันเลขแพทต่อได้เลย”**:
both Client local + Server local and Client Linux + Server Linux are now
**OWNER REPORTED PASS**, and numbered publication is explicitly authorized.
These are owner live-tests, not inferred from installation or file checks.
Numbered release **0157–0159 is published and Launcher-verified** on both test
clients. Final publication evidence is recorded below.

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

Tested candidate location: `Patch_Test/pc_login_loading_20261013/`. Contains only the
23 JPEG member paths + **Production** clientinfo/sclientinfo (25 files), README
and SHA256SUMS. Production XML outside loading matches both existing Client
local/Linux midnight.grf copies, avoiding unrelated master experiments.

Apply by member merge using `tools/client-patch/apply_pc_login_loading_candidate.py`
with the explicit target directory after the owner schedules that test. Both
targets have now been applied as recorded below; do not reapply before testing.
Do not replace a player's entire midnight.grf with the development master or
copy the private build staging directory. The helper validates exact allowlist
and SHA-256 before applying, preserves other members, updates the Local image
list in-place without shipping a Local endpoint, and backs up target files.

Candidate passed Client local + Server local, then Client Linux + Server Linux
according to the owner's explicit confirmation. Only this approved artwork/XML
scope is removed from dev_hold.txt in the same commit as its numbered release.
Images total 7,968,274 unique JPEG bytes / 16,537,391 bytes for 23 lookup members.
Release uses three batches, each below 8 MiB, merging into the existing GRF.

## Test-client installation — 2026-10-13

An initial apply attempt stopped before making changes because a native PC game
process was open. Owner then confirmed game/launcher were closed. A fresh
protected-file baseline was recorded, followed by Local apply, then Linux apply.

| Target | Installed member hashes | Protected files unchanged | Player files included | Owner live-test |
|---|---|---|---|---|
| `D:/MidnightROClient-Local` | 25/25 match candidate | 2,945 | 2,905 | OWNER REPORTED PASS — Server local |
| `D:/MidnightROClient-Linux` | 25/25 match candidate | 49 | 9 | OWNER REPORTED PASS — Server Linux |

- Each midnight.grf has 7,389 members, up from 7,367. Every unrelated member was
  verified byte-identical; each client's original non-artwork content is retained.
- Local's existing private endpoint GRF and loose clientinfo/sclientinfo received
  only the 11-image loading list. All XML bytes outside loading, including the
  existing endpoint settings, match the fresh baseline on both targets.
- DATA.INI/native EXE/DLL and player-file hashes are unchanged immediately after
  installation, before owner gameplay. Base data.grf/new_ai_final.grf size/mtime
  are unchanged. No loose image overrides were found in either client.
- Linux remains Production-configured with no private Local endpoint GRF. No
  Local DATA.INI or private endpoint was copied to Linux or into the candidate.
- Installed archive SHA-256 and backup hashes match the apply reports. Backups:
  `Backups/pc_login_loading/MidnightROClient-Local-e46fb8e4e0dc/` and
  `Backups/pc_login_loading/MidnightROClient-Linux-f28c706b9092/`.
- Evidence under `.scratch/pc-loading-art-20261013/`:
  `test-clients-before.json`, `test-clients-preflight.json`,
  `test-clients-after-audit.json`, `candidate-e46fb8e4e0dc/apply-report.json` and
  `candidate-f28c706b9092/apply-report.json`. Raw/private evidence is outside Git.

Installed midnight.grf SHA-256 before the subsequent Launcher update:

- Local: `467bd84f3a0266f06ee55773a8b27f065f68b4523e49fd4c0c1f1d9f004326d8`.
- Linux: `2bc06d04e2a25db0b7326d824528dd1b9a392ffc9f66a997a1de5b319e196ce2`.

Owner completed these tests and confirmed both passed: Geffen Login/wordmark,
loading scene changes, native Ragnarok bar/percentage, map entry and walking.
The owner's subsequent instruction explicitly authorized numbered publication.

## Publication and Launcher verification — 2026-10-13

Before publication, `git pull --ff-only` fetched a separately published 0156
checkpoint but could not fast-forward past the local artwork commits. A normal
merge retained both histories. Public plist/status/Release assets agreed on 156;
local definitions agreed, all 35 cached THOR SHA-256 digests matched public
assets, and the missing cached 0156 was downloaded. Metadata differed only by
line endings and was reconciled to the exact public bytes. One legacy private
endpoint reference was removed from released_state.json; no master snapshot
was taken and GRF CRC entries follow the existing member-merge state policy.

| Patch | Contents | THOR bytes | Payload members |
|---|---|---|---|
| 0157 | Plain texture loading00–10 | 7,952,387 | 11 |
| 0158 | Korean UserInterface loading00–10 | 7,952,432 | 11 |
| 0159 | Geffen Login + Production XML loading pool | 600,762 | 3 |

- Each part was built with make_patch.ps1 `-CandidateDir`, an explicit subset,
  `-UseGrfMerging -TargetGrfName midnight.grf -NoUpload`. The built THOR header,
  target, exact cp949 member names and decompressed payload SHA-256 were audited
  before publication. Together, the parts contain exactly the 25 accepted runtime
  members, with one standard THOR integrity record per part; no removal entries.
- Actual published plist/status/assets were rechecked before each next index.
  THOR upload used no clobber; only mutable status/list assets were replaced,
  in THOR → status → plist order. Each public THOR/status/list was downloaded
  back and verified byte-for-byte; no old patch was changed.
- Native Launcher in Local, then Linux, displayed successful installation of
  four patches (the previously published 0156 plus 0157–0159). Both real
  MidnightRO.dat bookmarks advanced **155 → 159**, and the UI displayed 159/159.
  Neither bookmark was set manually. The agent closed each Launcher normally
  after the check, without logging into or replaying the owner's game tests.
- All 25 installed art/XML payloads match the accepted candidate. Both published
  0156 skill members match that public artifact. **7,362 unrelated GRF members**
  remain byte-identical per target; native EXE/DLL, DATA.INI, player files and base
  archives are unchanged. Local and Production endpoints remain as before.
- Source/member/THOR hashes and install evidence summary are tracked in
  `PC_LOGIN_LOADING_RELEASE_0157_0159.json`; source PNGs and generator are retained
  at checkpoint 12691c9. JPEG export used Pillow 12.2.0. No Mobile writes or
  Server deployment were part of this release.
- Raw evidence under `.scratch/pc-loading-art-20261013/release/`: preflight and
  audit-0157/0158/0159 JSON, downloaded public snapshots, launcher-after-audit.json,
  launcher-local-initial.png and launcher-linux-complete.png. Private/raw evidence
  is not committed or included in player packages.
- Public distribution: `https://github.com/midnightro/patcher/releases/tag/patches`.
  Current public list/status end at 159. Source, tooling and released-member
  provenance remain. Cleanup of only `Patch_Test/pc_login_loading_20261013/`
  was attempted after all release checks passed, with exact resolved-path and
  reparse-point guards. Automatic approval review rejected execution with
  "blocked by policy" and no further stated reason. No cleanup command executed:
  the candidate remains, and other jobs/player data were untouched. This is an
  outstanding housekeeping action, not an unverified patch publication.
