#!/usr/bin/env python3
"""Add the durable VIP Premium timer icon to the compact core component."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from grf import Grf  # noqa: E402
from make_grf import build  # noqa: E402

TARGET = TOOLS / "runtime_grf_sources" / "lua_compat_ui.grf"
LUAC = ROOT / "tools" / "lua51" / "luac.exe"
STATE_INFO = b"data\\luafiles514\\lua files\\stateicon\\stateiconinfo.lub"
STATE_IMG = b"data\\luafiles514\\lua files\\stateicon\\stateiconimginfo.lub"
ICON = b"data\\texture\\effect\\vip_premium.tga"
ICON_SOURCE = TOOLS / "ui_sources" / "vip_premium_status_icon_v6.png"
VIP_EFST = 1511  # EFST_C_BUFF_3; reserved here as a client-only VIP timer.


def lua_string(payload: bytes) -> str:
    return "".join(f"\\{value:03d}" for value in payload)


def thai_lua_string(text: str) -> str:
    """Return an ASCII-only Lua literal with this client's CP874 text."""
    return lua_string(text.encode("cp874", errors="strict"))


def compile_wrapper(stock: bytes, source: str, label: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="vip_premium_icon_") as temp:
        src = Path(temp) / f"{label}.lua"
        out = Path(temp) / f"{label}.lub"
        src.write_text(source.replace("{STOCK}", lua_string(stock)), encoding="ascii")
        result = subprocess.run([str(LUAC), "-s", "-o", str(out), str(src)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"cannot compile {label}: {result.stdout}{result.stderr}")
        return out.read_bytes()


def make_icon() -> bytes:
    if not ICON_SOURCE.is_file():
        raise FileNotFoundError(f"missing VIP status icon source: {ICON_SOURCE}")

    # This source is authored and approved at the client's native size. Do not
    # resize or repaint it here: doing so reintroduces blur around the VIP text.
    with Image.open(ICON_SOURCE) as source:
        if source.size != (32, 32):
            raise RuntimeError(f"VIP status icon must be 32x32, got {source.size}")
        image = source.convert("RGBA")
    alpha_min, alpha_max = image.getchannel("A").getextrema()
    if alpha_min == alpha_max == 255:
        raise RuntimeError("VIP status icon source has no translucent pixels")

    with tempfile.NamedTemporaryFile(suffix=".tga", delete=False) as temp:
        path = Path(temp.name)
    try:
        image.save(path, format="TGA")
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def main() -> None:
    current = Grf(TARGET)
    try:
        assets = {member: current.read(member) for member in current.entries}
    finally:
        current.close()
    if STATE_INFO not in assets or STATE_IMG not in assets:
        raise RuntimeError("VIP status dependencies are missing from lua_compat_ui.grf")

    # The component is its own reproducible input after the first run. Avoid
    # wrapping the already wrapped LUBs again when a release build is repeated.
    card_stack = "เวลาใช้งานสะสมจากบัตร VIP Premium".encode("cp874")
    box_stack = "เวลาใช้งานสะสมจากกล่อง VIP Premium".encode("cp874")
    card_position = assets[STATE_INFO].find(card_stack)
    box_position = assets[STATE_INFO].find(box_stack)
    # The compiled wrapper stores its own strings before the embedded stock
    # bytecode. This also distinguishes the current card wrapper from the old
    # box wrapper, whose embedded stock still contains the original card text.
    expected_icon = make_icon()
    wrapper_installed = (card_position >= 0
            and (box_position < 0 or card_position < box_position)
            and b"vip_premium.tga" in assets[STATE_IMG]
            and ICON in assets)
    if wrapper_installed and assets[ICON] == expected_icon:
        print("VIP Premium status icon is already installed")
        print(f"sha256={hashlib.sha256(TARGET.read_bytes()).hexdigest().upper()}")
        return

    title = thai_lua_string("VIP Premium")
    active = thai_lua_string("สถานะ VIP Premium กำลังทำงาน")
    stack = thai_lua_string("เวลาใช้งานสะสมจากบัตร VIP Premium")
    if not wrapper_installed:
        assets[STATE_INFO] = compile_wrapper(assets[STATE_INFO], f'''local stock = assert(loadstring("{{STOCK}}", "@StateIconInfo.stock"))
stock()
StateIconList[1511] = {{ haveTimeLimit = 1, posTimeLimitStr = 2, descript = {{
    {{ "{title}", COLOR_TITLE_BUFF }}, {{ "%s", COLOR_TIME }},
    {{ "{active}" }}, {{ "{stack}" }}
}} }}
''', "stateiconinfo")
        assets[STATE_IMG] = compile_wrapper(assets[STATE_IMG], '''local stock = assert(loadstring("{STOCK}", "@StateIconImgInfo.stock"))
stock()
StateIconImgList[2][1511] = "vip_premium.tga"
''', "stateiconimginfo")
    assets[ICON] = expected_icon

    temporary = TARGET.with_suffix(".grf.building")
    try:
        build(temporary, list(assets.items()), verbose=False)
        check = Grf(temporary)
        try:
            for member, expected in assets.items():
                if check.read(member) != expected:
                    raise RuntimeError(f"GRF round-trip mismatch: {member!r}")
        finally:
            check.close()
        temporary.replace(TARGET)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"members={len(assets)} icon_sha256={hashlib.sha256(assets[ICON]).hexdigest().upper()}")
    print(f"sha256={hashlib.sha256(TARGET.read_bytes()).hexdigest().upper()}")


if __name__ == "__main__":
    main()
