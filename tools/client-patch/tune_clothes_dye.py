"""
Update tuned clothes-dye palettes for Blacksmith and Alchemist in midnight.grf.
"""
from pathlib import Path
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
BACKUP_GRF = CLIENT / "midnight.grf.bak_before_bs_alc_tune"
SOURCES_DIR = TOOLS / "ui_sources" / "clothes_dye_tune"

sys.path.insert(0, str(TOOLS))
from grf import Grf
from make_grf import build


def main():
    if not TARGET_GRF.exists():
        print(f"Target GRF {TARGET_GRF} does not exist.")
        return 1

    replacements = {}
    for path in SOURCES_DIR.glob("*.pal"):
        member_name = f"data\\palette\\몸\\{path.name}".encode("cp949")
        replacements[member_name] = path.read_bytes()
        print(f"Loaded replacement: {path.name} ({len(replacements[member_name])} bytes)")

    if not replacements:
        print("No replacement palettes found in", SOURCES_DIR)
        return 1

    if not BACKUP_GRF.exists():
        shutil.copy2(TARGET_GRF, BACKUP_GRF)
        print(f"Created backup at {BACKUP_GRF.name}")
    else:
        print(f"Existing backup retained at {BACKUP_GRF.name}")

    src = Grf(str(TARGET_GRF))
    files = []
    replaced_count = 0
    for name in src.entries:
        if name in replacements:
            files.append((name, replacements[name]))
            replaced_count += 1
            print(f"  Replaced: {repr(name)}")
        else:
            files.append((name, src.read(name)))

    staged_path = CLIENT / "midnight.grf.staged"
    print(f"Building staged GRF with {len(files)} files (replaced {replaced_count})...")
    build(str(staged_path), files, verbose=False)

    src.f.close()

    try:
        staged_path.replace(TARGET_GRF)
        print(f"Successfully updated live {TARGET_GRF.name}!")
        return 0
    except PermissionError:
        print("ERROR: live GRF is locked by running client. Staged file left at", staged_path)
        return 2


if __name__ == "__main__":
    sys.exit(main())
