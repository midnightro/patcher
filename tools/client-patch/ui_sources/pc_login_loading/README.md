# PC Login and map-loading artwork

Accepted Mobile artwork snapshot: runtime `57d5508`, owner accepted on
2026-10-13; copied only the 11 active PNG scenes and SHA256SUMS.txt. Includes
Aldebaran v2 (Poring + complete Alarm). Rejected Aldebaran v1 is excluded.
Artwork and Midnight RO logos are already baked into PNGs; the PC export adds
no text, progress bar or percentage. Mobile source and documents are not edited.

`build_pc_login_loading_art.py` converts these snapshots to baseline RGB JPEG,
1024x768, quality 98, 4:4:4. It crops 16:9 symmetrically to 4:3 without stretching.
Both legacy texture lookup locations receive identical loading JPEG bytes;
Login uses Geffen as `data/texture/<Korean UserInterface>/t_login.jpg`.
Native Ragexe continues to render the existing loading bar and percentage.

PC artwork source is kept here separately from Mobile. Source SHA-256 is checked
before export. Staging/evidence/backup files must stay outside player packages.
See [PC report](../../docs/PC_LOGIN_LOADING_ART_2026-10-13.md) for master acceptance,
candidate status, hashes, backup, and the next Client local/Linux gates.
