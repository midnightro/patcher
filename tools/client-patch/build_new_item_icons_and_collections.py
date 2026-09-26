"""
Midnight RO - Update RO-Style Item Icons & Collection Artworks
Target Items:
  902269: [Hunter C] Kasaka Shadow Fang
  902270: [Hunter B] Obsidian Crown of the Monarch
  902271: [Hunter A] Monarch's Shadow Gaze
  902272: [Hunter S] Monarch's Shadow Aura
  902273: Newbie Pastel Poring Hat
"""

import io
import os
import shutil
from collections import deque
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# Import GRF library from client-patch
import sys
CLIENT_PATCH_DIR = Path(__file__).resolve().parent
sys.path.append(str(CLIENT_PATCH_DIR))
from grf import Grf

WORKSPACE_ROOT = CLIENT_PATCH_DIR.parents[2]
MIDNIGHT_GRF_PATH = WORKSPACE_ROOT / "MidnightROClient" / "midnight.grf"
SOLO_SOURCES = CLIENT_PATCH_DIR / "ui_sources" / "solo_leveling_hunter_set"
NEWBIE_SOURCES = CLIENT_PATCH_DIR / "ui_sources" / "newbie_adventurer_cap"

BRAIN_DIR = Path(r"C:\Users\Burin\.gemini\antigravity-ide\brain\3f9dbc23-1886-47d1-b501-2fafea5766ce")

ITEMS_CONFIG = {
    902269: {
        "resname": "kasaka_shadow_fang",
        "name": "[Hunter C] Kasaka Shadow Fang",
        "source_art": BRAIN_DIR / "kasaka_fang_ro_1790435749440.jpg",
        "dest_dir": SOLO_SOURCES,
        "max_icon_box": (22, 22),
    },
    902270: {
        "resname": "obsidian_monarch_crown",
        "name": "[Hunter B] Obsidian Crown of the Monarch",
        "source_art": BRAIN_DIR / "obsidian_crown_ro_1790435766091.jpg",
        "dest_dir": SOLO_SOURCES,
        "max_icon_box": (22, 20),
    },
    902271: {
        "resname": "monarch_shadow_gaze",
        "name": "[Hunter A] Monarch's Shadow Gaze",
        "source_art": BRAIN_DIR / "shadow_gaze_ro_1790435848405.jpg",
        "dest_dir": SOLO_SOURCES,
        "max_icon_box": (22, 16),
    },
    902272: {
        "resname": "monarch_shadow_aura",
        "name": "[Hunter S] Monarch's Shadow Aura",
        "source_art": BRAIN_DIR / "shadow_aura_ro_1790435865711.jpg",
        "dest_dir": SOLO_SOURCES,
        "max_icon_box": (22, 22),
    },
    902273: {
        "resname": "pastel_poring_trio",
        "name": "Newbie Pastel Poring Hat",
        "source_art": BRAIN_DIR / "pastel_poring_ro_1790435886033.jpg",
        "dest_dir": NEWBIE_SOURCES,
        "max_icon_box": (22, 19),
    },
}


def isolate_foreground(img: Image.Image) -> Image.Image:
    """Isolate solid foreground from white background using border flood-fill."""
    arr = np.array(img.convert("RGB"), dtype=np.int32)
    h, w, _ = arr.shape
    is_bg = (
        (arr[:, :, 0] > 238)
        & (arr[:, :, 1] > 238)
        & (arr[:, :, 2] > 238)
        & (np.max(np.abs(arr[:, :, :3] - arr[:, :, 0:1]), axis=2) < 20)
    )

    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    for x in range(w):
        if is_bg[0, x]:
            q.append((0, x))
            visited[0, x] = True
        if is_bg[h - 1, x]:
            q.append((h - 1, x))
            visited[h - 1, x] = True
    for y in range(h):
        if is_bg[y, 0]:
            q.append((y, 0))
            visited[y, 0] = True
        if is_bg[y, w - 1]:
            q.append((y, w - 1))
            visited[y, w - 1] = True

    while q:
        cy, cx = q.popleft()
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if is_bg[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    alpha = np.where(visited, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, "RGBA")


def make_ro_collection(rgba_img: Image.Image, target_size=(75, 100), max_box=(71, 94)) -> Image.Image:
    """Generate 75x100 Collection image with pure white background (255, 255, 255)."""
    bbox = rgba_img.getbbox()
    cropped = rgba_img.crop(bbox)
    w, h = cropped.size
    ratio = min(max_box[0] / w, max_box[1] / h)
    new_w = max(1, int(w * ratio))
    new_h = max(1, int(h * ratio))

    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    resized = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=140, threshold=3))

    canvas = Image.new("RGB", target_size, (255, 255, 255))
    paste_x = (target_size[0] - new_w) // 2
    paste_y = (target_size[1] - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y), resized)
    return canvas


def make_ro_item_icon(rgba_img: Image.Image, target_size=(24, 24), max_box=(22, 22)) -> Image.Image:
    """
    Generate 24x24 Inventory Item icon with:
      - Crisp 1px dark perimeter contour
      - High contrast and saturation for small-scale readability
      - Pure magenta (255, 0, 255) transparent background
    """
    bbox = rgba_img.getbbox()
    cropped = rgba_img.crop(bbox)
    w, h = cropped.size
    ratio = min(max_box[0] / w, max_box[1] / h)
    new_w = max(1, int(w * ratio))
    new_h = max(1, int(h * ratio))

    resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
    enh_c = ImageEnhance.Color(resized).enhance(1.35)
    enh_s = ImageEnhance.Sharpness(enh_c).enhance(1.6)

    arr = np.array(enh_s)
    solid_mask = arr[:, :, 3] >= 100

    # 1px dilation for crisp contour
    outline_mask = np.zeros_like(solid_mask)
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dy == 0 and dx == 0:
                continue
            shifted = np.roll(np.roll(solid_mask, dy, axis=0), dx, axis=1)
            if dy > 0:
                shifted[:dy, :] = False
            elif dy < 0:
                shifted[dy:, :] = False
            if dx > 0:
                shifted[:, :dx] = False
            elif dx < 0:
                shifted[:, dx:] = False
            outline_mask |= shifted

    outline_only = outline_mask & (~solid_mask)

    canvas = np.full((24, 24, 3), [255, 0, 255], dtype=np.uint8)
    px = (24 - new_w) // 2
    py = (24 - new_h) // 2

    for y in range(new_h):
        for x in range(new_w):
            if (py + y) >= 24 or (px + x) >= 24:
                continue
            if outline_only[y, x]:
                canvas[py + y, px + x] = [18, 16, 24]
            elif solid_mask[y, x]:
                canvas[py + y, px + x] = arr[y, x, :3]

    return Image.fromarray(canvas, "RGB")


def main():
    print("=" * 70)
    print("Midnight RO - Generating RO-Style Item & Collection Assets (902269 - 902273)")
    print("=" * 70)

    grf_files_to_update: dict[bytes, bytes] = {}

    for item_id, cfg in ITEMS_CONFIG.items():
        resname = cfg["resname"]
        name = cfg["name"]
        source_art = cfg["source_art"]
        dest_dir = cfg["dest_dir"]
        dest_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nProcessing Item ID {item_id}: {name} ({resname})...")
        if not source_art.exists():
            raise FileNotFoundError(f"Source art not found: {source_art}")

        # Copy raw source art to repository ui_sources
        raw_repo_dest = dest_dir / f"{resname}_raw_art.jpg"
        shutil.copy2(source_art, raw_repo_dest)

        img = Image.open(source_art)
        rgba = isolate_foreground(img)

        # Generate Collection (75x100)
        col_img = make_ro_collection(rgba)
        col_bmp_path = dest_dir / f"{resname}_collection_75x100.bmp"
        col_png_path = dest_dir / f"{resname}_collection_75x100.png"
        col_img.save(col_bmp_path, format="BMP")
        col_img.save(col_png_path, format="PNG")

        # Generate Icon (24x24)
        icon_img = make_ro_item_icon(rgba, max_box=cfg["max_icon_box"])
        icon_bmp_path = dest_dir / f"{resname}_icon_24.bmp"
        icon_png_path = dest_dir / f"{resname}_icon_24.png"
        icon_img.save(icon_bmp_path, format="BMP")
        icon_img.save(icon_png_path, format="PNG")

        print(f"  Saved collection: {col_bmp_path.name}")
        print(f"  Saved icon:       {icon_bmp_path.name}")

        col_bytes = col_bmp_path.read_bytes()
        icon_bytes = icon_bmp_path.read_bytes()

        # Korean paths for GRF (CP949)
        # item: data\texture\유저인터페이스\item\<resname>.bmp
        # collection: data\texture\유저인터페이스\collection\<resname>.bmp
        item_grf_path = f"data\\texture\\유저인터페이스\\item\\{resname}.bmp".encode("cp949")
        col_grf_path = f"data\\texture\\유저인터페이스\\collection\\{resname}.bmp".encode("cp949")
        grf_files_to_update[item_grf_path] = icon_bytes
        grf_files_to_update[col_grf_path] = col_bytes

        # Underscore alias for poring trio
        if item_id == 902273:
            item_grf_path_u = f"data\\texture\\유저인터페이스\\item\\_{resname}.bmp".encode("cp949")
            col_grf_path_u = f"data\\texture\\유저인터페이스\\collection\\_{resname}.bmp".encode("cp949")
            grf_files_to_update[item_grf_path_u] = icon_bytes
            grf_files_to_update[col_grf_path_u] = col_bytes

    from make_grf import build as build_grf

    print("\nReading current entries from midnight.grf...")
    mgrf = Grf(str(MIDNIGHT_GRF_PATH))
    entries_dict: dict[bytes, bytes] = {}
    for name in mgrf.entries:
        entries_dict[name] = mgrf.read(name)
    mgrf.close()

    print(f"  Existing files in GRF: {len(entries_dict)}")
    for name, data in grf_files_to_update.items():
        entries_dict[name] = data
    print(f"  Total files after updating: {len(entries_dict)}")

    staged_path = MIDNIGHT_GRF_PATH.parent / (MIDNIGHT_GRF_PATH.name + ".staged")
    file_list = list(entries_dict.items())
    print(f"  Building {staged_path.name}...")
    build_grf(str(staged_path), file_list, verbose=False)

    staged_path.replace(MIDNIGHT_GRF_PATH)
    print(f"Successfully applied {MIDNIGHT_GRF_PATH.name} ({MIDNIGHT_GRF_PATH.stat().st_size} bytes)!")

    # Verify updated entries
    print("\nVerifying entries in midnight.grf:")
    verify_grf = Grf(str(MIDNIGHT_GRF_PATH))
    for entry_path in grf_files_to_update:
        if entry_path in verify_grf.entries:
            data = verify_grf.read(entry_path)
            res_name = entry_path.split(b"\\")[-1].decode("ascii", errors="replace")
            sub_folder = entry_path.split(b"\\")[-2].decode("ascii", errors="replace")
            print(f"  [OK] {sub_folder}\\{res_name} (size: {len(data)} bytes)")
        else:
            print(f"  [FAIL] Missing: {entry_path.decode('ascii', errors='replace')}")

    print("\nALL ITEMS (902269 - 902273) SUCCESSFULLY UPDATED WITH RO-STYLE GRAPHICS!")


if __name__ == "__main__":
    main()
