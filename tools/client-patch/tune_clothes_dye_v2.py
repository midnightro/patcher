"""
Targeted Surgical Tuner for Midnight RO Outfits (Master Tuned)
Applies refined adjustments onto baseline Palette 15:
- Novice M & F (breastplate Silver, inner shirt Navy, cross-strap Blue, belt buckle Gold)
- Assassin M & F (inner bodysuit/tights Deep Midnight Navy, bandages Silver, buckles Gold)
- Hunter M & F (inner shirt & tights Deep Midnight Navy, scarf/boots Blue, buckles Gold)
- Alchemist M (outer coat Blue, inner tunic Silver, inner pants Navy, boots/collar Gold)
- Swordman M & F (breastplate Silver, boots/sash Blue, armor trim/buckles Gold)
- Mage M & F (mantle Silver, robe Blue, cuffs/chest crest/necklace Gold)
- Acolyte M & F (vestments Silver, stole Blue, cross/belt/wristbands Gold)
- Thief M & F (jacket Silver, pants Blue, knee guards/sash/buckles Gold, inner shirt Navy)
"""
from pathlib import Path
import colorsys
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[2]
CLIENT = ROOT / "MidnightROClient"
TARGET_GRF = CLIENT / "midnight.grf"
DATA_GRF = CLIENT / "data.grf"
SOURCES_DIR = TOOLS / "ui_sources" / "clothes_dye_tune"
SOURCES_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(TOOLS))
from grf import Grf

SIG_STOPS = {
    "silver": [
        (0.00, 222, 0.34, 0.20),
        (0.30, 215, 0.24, 0.42),
        (0.62, 208, 0.13, 0.68),
        (1.00, 202, 0.05, 0.96),
    ],
    "blue": [
        (0.00, 230, 0.62, 0.13),
        (0.32, 224, 0.64, 0.30),
        (0.66, 216, 0.58, 0.48),
        (1.00, 208, 0.42, 0.72),
    ],
    "blue_rich": [
        (0.00, 232, 0.75, 0.14),
        (0.32, 226, 0.78, 0.32),
        (0.66, 220, 0.72, 0.52),
        (1.00, 212, 0.55, 0.78),
    ],
    "blue_vibrant": [
        (0.00, 230, 0.78, 0.18),
        (0.35, 225, 0.82, 0.40),
        (0.70, 218, 0.78, 0.62),
        (1.00, 210, 0.65, 0.85),
    ],
    "gold": [
        (0.00, 32, 0.62, 0.22),
        (0.35, 40, 0.72, 0.42),
        (0.70, 46, 0.76, 0.62),
        (1.00, 50, 0.58, 0.90),
    ],
    "gold_bright": [
        (0.00, 34, 0.70, 0.28),
        (0.35, 42, 0.82, 0.50),
        (0.70, 48, 0.85, 0.70),
        (1.00, 52, 0.70, 0.94),
    ],
    "navy_dark": [
        (0.00, 235, 0.60, 0.08),
        (0.35, 230, 0.55, 0.18),
        (0.70, 225, 0.48, 0.32),
        (1.00, 220, 0.38, 0.52),
    ],
}


def interp_stops(stops, t):
    t = max(0.0, min(1.0, t))
    for i in range(len(stops) - 1):
        p0, h0, s0, l0 = stops[i]
        p1, h1, s1, l1 = stops[i + 1]
        if p0 <= t <= p1:
            span = max(1e-5, p1 - p0)
            f = (t - p0) / span
            h = h0 + f * (h1 - h0)
            s = s0 + f * (s1 - s0)
            l = l0 + f * (l1 - l0)
            r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
            return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
    _, h, s, l = stops[-1]
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return int(round(r * 255)), int(round(g * 255)), int(round(b * 255))


def apply_ramp(palette, ramp_idx, stops):
    start = ramp_idx * 8
    for i in range(8):
        t = 1.0 - (i / 7.0)
        r, g, b = interp_stops(stops, t)
        offset = (start + i) * 4
        palette[offset] = r
        palette[offset + 1] = g
        palette[offset + 2] = b


def main():
    backup_grf = CLIENT / "midnight.grf.bak_before_bs_alc_tune"
    g_base = Grf(str(backup_grf if backup_grf.exists() else TARGET_GRF))

    def get_pal15(stem):
        mid_entry = f"data\\palette\\몸\\{stem}_15.pal".encode("cp949")
        return bytearray(g_base.read(mid_entry))

    results = {}

    # 1. Novice Male:
    pal = get_pal15("초보자_남")
    apply_ramp(pal, 2, SIG_STOPS["blue"])       # loincloth cross-strap -> Midnight Blue
    apply_ramp(pal, 3, SIG_STOPS["silver"])     # breastplate -> Moonlight Silver
    apply_ramp(pal, 5, SIG_STOPS["navy_dark"])  # inner shirt -> Deep Midnight Navy
    apply_ramp(pal, 7, SIG_STOPS["silver"])     # upper breastplate highlight -> Moonlight Silver
    # set buckle (index 79) to gold
    r, g, b = interp_stops(SIG_STOPS["gold"], 0.8)
    pal[79*4] = r; pal[79*4+1] = g; pal[79*4+2] = b
    results["초보자_남_15.pal"] = bytes(pal)

    # Novice Female:
    pal = get_pal15("초보자_여")
    apply_ramp(pal, 3, SIG_STOPS["silver"])     # breastplate -> Moonlight Silver
    apply_ramp(pal, 5, SIG_STOPS["navy_dark"])  # inner shirt -> Deep Midnight Navy
    apply_ramp(pal, 7, SIG_STOPS["silver"])     # upper breastplate highlight -> Moonlight Silver
    # set buckle to gold
    r, g, b = interp_stops(SIG_STOPS["gold"], 0.8)
    pal[79*4] = r; pal[79*4+1] = g; pal[79*4+2] = b
    results["초보자_여_15.pal"] = bytes(pal)

    # 2. Assassin Male:
    pal = get_pal15("어세신_남")
    apply_ramp(pal, 1, SIG_STOPS["gold_bright"]) # shoulder pauldron & forearm/knee straps -> Luminous Gold!
    apply_ramp(pal, 2, SIG_STOPS["blue_rich"])   # cowl scarf -> Rich Midnight Blue
    apply_ramp(pal, 3, SIG_STOPS["gold_bright"]) # shoulder spaulders -> Luminous Gold!
    apply_ramp(pal, 5, SIG_STOPS["gold_bright"]) # elbow trim -> Luminous Gold!
    apply_ramp(pal, 7, SIG_STOPS["silver"])      # chest harness & bandages -> Moonlight Silver
    apply_ramp(pal, 8, SIG_STOPS["navy_dark"])   # thigh & panels -> Deep Midnight Navy
    apply_ramp(pal, 9, SIG_STOPS["gold_bright"]) # belt buckle -> Luminous Gold!
    apply_ramp(pal, 11, SIG_STOPS["navy_dark"])  # inner bodysuit -> Deep Midnight Navy
    results["어세신_남_15.pal"] = bytes(pal)

    # Assassin Female:
    pal = get_pal15("어세신_여")
    apply_ramp(pal, 1, SIG_STOPS["gold_bright"]) # waist corset & knee/boot guards -> Luminous Gold!
    apply_ramp(pal, 2, SIG_STOPS["blue_rich"])   # collar cowl & neck choker -> Rich Midnight Blue
    apply_ramp(pal, 3, SIG_STOPS["silver"])      # hip sash & side wraps -> Moonlight Silver
    apply_ramp(pal, 5, SIG_STOPS["gold_bright"]) # armlet bangles -> Luminous Gold!
    apply_ramp(pal, 7, SIG_STOPS["gold_bright"]) # cowl rim & shoe caps -> Luminous Gold!
    apply_ramp(pal, 8, SIG_STOPS["navy_dark"])   # shoulder/back coat -> Deep Midnight Navy
    apply_ramp(pal, 10, SIG_STOPS["gold_bright"])# ankle trim & ribbons -> Luminous Gold!
    apply_ramp(pal, 11, SIG_STOPS["navy_dark"])  # inner bodysuit & stockings -> Deep Midnight Navy
    results["어세신_여_15.pal"] = bytes(pal)

    # 3. Hunter Male:
    pal = get_pal15("헌터_남")
    apply_ramp(pal, 1, SIG_STOPS["blue"])       # scarf & boots -> Deep Midnight Blue
    apply_ramp(pal, 2, SIG_STOPS["navy_dark"])  # inner shirt & tights -> Deep Midnight Navy
    apply_ramp(pal, 7, SIG_STOPS["silver"])     # shoulders & vest -> Moonlight Silver
    apply_ramp(pal, 8, SIG_STOPS["gold"])       # buckles & trim -> Luminous Gold
    results["헌터_남_15.pal"] = bytes(pal)

    # Hunter Female:
    pal = get_pal15("헌터_여")
    apply_ramp(pal, 1, SIG_STOPS["blue"])       # boots -> Deep Midnight Blue
    apply_ramp(pal, 2, SIG_STOPS["navy_dark"])  # inner sleeves & tights -> Deep Midnight Navy
    apply_ramp(pal, 6, SIG_STOPS["gold"])       # waist belt & buckles -> Luminous Gold
    results["헌터_여_15.pal"] = bytes(pal)

    # 4. Alchemist Male:
    pal = get_pal15("연금술사_남")
    apply_ramp(pal, 1, SIG_STOPS["blue"])       # outer coat -> Deep Midnight Blue
    apply_ramp(pal, 2, SIG_STOPS["blue"])       # coat lining -> Deep Midnight Blue
    apply_ramp(pal, 5, SIG_STOPS["navy_dark"])  # inner pants -> Deep Midnight Navy
    apply_ramp(pal, 6, SIG_STOPS["gold"])       # collar buttons -> Luminous Gold
    apply_ramp(pal, 8, SIG_STOPS["silver"])     # inner tunic -> Moonlight Silver
    apply_ramp(pal, 9, SIG_STOPS["gold"])       # boots & trim -> Luminous Gold
    results["연금술사_남_15.pal"] = bytes(pal)

    # 5. Swordman Male:
    pal = get_pal15("검사_남")
    apply_ramp(pal, 6, SIG_STOPS["blue"])       # boots & straps -> Deep Midnight Blue
    apply_ramp(pal, 8, SIG_STOPS["gold"])       # waist buckle -> Luminous Gold
    apply_ramp(pal, 9, SIG_STOPS["silver"])     # chest plate -> Moonlight Silver
    apply_ramp(pal, 10, SIG_STOPS["gold"])      # knee guards & rivets -> Luminous Gold
    results["검사_남_15.pal"] = bytes(pal)

    # Swordman Female:
    pal = get_pal15("검사_여")
    apply_ramp(pal, 6, SIG_STOPS["blue"])       # diagonal chest sash -> Deep Midnight Blue
    apply_ramp(pal, 9, SIG_STOPS["gold"])       # spaulder trim & waist band -> Luminous Gold
    apply_ramp(pal, 10, SIG_STOPS["gold"])      # boot buckles & trim -> Luminous Gold
    results["검사_여_15.pal"] = bytes(pal)

    # 6. Mage Male:
    pal = get_pal15("마법사_남")
    apply_ramp(pal, 7, SIG_STOPS["gold"])       # cuffs & collar -> Luminous Gold
    apply_ramp(pal, 10, SIG_STOPS["gold"])      # chest emblem & mantle hem -> Luminous Gold
    results["마법사_남_15.pal"] = bytes(pal)

    # Mage Female:
    pal = get_pal15("마법사_여")
    apply_ramp(pal, 7, SIG_STOPS["gold"])       # armlet & gold accents -> Luminous Gold
    apply_ramp(pal, 9, SIG_STOPS["gold"])       # waist jewelry -> Luminous Gold
    apply_ramp(pal, 10, SIG_STOPS["gold"])      # necklace jewel -> Luminous Gold
    results["마법사_여_15.pal"] = bytes(pal)

    # 7. Acolyte Male:
    pal = get_pal15("성직자_남")
    apply_ramp(pal, 5, SIG_STOPS["gold"])       # belt buckle -> Luminous Gold
    apply_ramp(pal, 6, SIG_STOPS["blue"])       # upper cowl -> Deep Midnight Blue
    apply_ramp(pal, 7, SIG_STOPS["gold"])       # liturgical cross -> Luminous Gold
    results["성직자_남_15.pal"] = bytes(pal)

    # Acolyte Female:
    pal = get_pal15("성직자_여")
    apply_ramp(pal, 3, SIG_STOPS["gold"])       # waist belt -> Luminous Gold
    results["성직자_여_15.pal"] = bytes(pal)

    # 8. Thief Male:
    pal = get_pal15("도둑_남")
    apply_ramp(pal, 3, SIG_STOPS["navy_dark"])  # inner shirt -> Deep Midnight Navy
    apply_ramp(pal, 5, SIG_STOPS["gold"])       # belt buckle & studs -> Luminous Gold
    apply_ramp(pal, 6, SIG_STOPS["gold"])       # knee guard borders -> Luminous Gold
    apply_ramp(pal, 7, SIG_STOPS["gold"])       # knee guards (circles) -> Luminous Gold
    results["도둑_남_15.pal"] = bytes(pal)

    # Thief Female:
    pal = get_pal15("도둑_여")
    apply_ramp(pal, 6, SIG_STOPS["gold"])       # red waist sash & ribbons (indices 48-55) -> Luminous Gold
    results["도둑_여_15.pal"] = bytes(pal)

    # 9. Bard Male & Mount:
    pal = get_pal15("바드_남")
    apply_ramp(pal, 1, SIG_STOPS["silver"])       # sleeves & thigh flaps -> Moonlight Silver
    apply_ramp(pal, 2, SIG_STOPS["gold_bright"])  # belt buckle & central zipper -> Luminous Gold
    apply_ramp(pal, 3, SIG_STOPS["blue_rich"])    # shoulder vest / wings -> Rich Midnight Blue
    apply_ramp(pal, 5, SIG_STOPS["blue_vibrant"]) # trousers -> Radiant Vibrant Blue (bright & non-dark)
    apply_ramp(pal, 6, SIG_STOPS["blue_rich"])    # boots -> Rich Midnight Blue
    apply_ramp(pal, 7, SIG_STOPS["gold_bright"])  # grand long cape tails -> Luminous Gold!
    apply_ramp(pal, 8, SIG_STOPS["gold_bright"])  # collar rim & shoulder embroidery -> Luminous Gold!
    apply_ramp(pal, 9, SIG_STOPS["gold_bright"])  # boot soles / trims -> Luminous Gold!
    results["바드_남_15.pal"] = bytes(pal)

    pal_mount = get_pal15("타조바드_남")
    apply_ramp(pal_mount, 1, SIG_STOPS["silver"])
    apply_ramp(pal_mount, 2, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 3, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 5, SIG_STOPS["blue_vibrant"])
    apply_ramp(pal_mount, 6, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 7, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 8, SIG_STOPS["gold_bright"])
    results["타조바드_남_15.pal"] = bytes(pal_mount)

    # 10. Dancer Female, Pants & Mount:
    pal = get_pal15("무희_여")
    apply_ramp(pal, 1, SIG_STOPS["blue_rich"])    # halterneck top / bra & thong -> Rich Midnight Blue
    apply_ramp(pal, 2, SIG_STOPS["gold_bright"])  # flank sheer skirt drapes -> Luminous Gold!
    apply_ramp(pal, 3, SIG_STOPS["gold_bright"])  # hip ornaments & buckle -> Luminous Gold!
    apply_ramp(pal, 4, SIG_STOPS["gold_bright"])  # anklets & heel jewelry -> Luminous Gold!
    apply_ramp(pal, 5, SIG_STOPS["gold_bright"])  # upper arm bangles & wrist ribbons -> Luminous Gold!
    apply_ramp(pal, 7, SIG_STOPS["gold_bright"])  # hair accessories -> Luminous Gold!
    apply_ramp(pal, 8, SIG_STOPS["gold_bright"])  # gladiator sandals -> Luminous Gold!
    apply_ramp(pal, 9, SIG_STOPS["blue_rich"])    # long back drape -> Rich Midnight Blue
    results["무희_여_15.pal"] = bytes(pal)

    pal_pants = get_pal15("무희바지_여")
    apply_ramp(pal_pants, 1, SIG_STOPS["blue_rich"])
    apply_ramp(pal_pants, 2, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 3, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 4, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 5, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 7, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 8, SIG_STOPS["gold_bright"])
    apply_ramp(pal_pants, 9, SIG_STOPS["blue_rich"])
    apply_ramp(pal_pants, 10, SIG_STOPS["blue_vibrant"]) # pants -> Radiant Vibrant Blue
    results["무희바지_여_15.pal"] = bytes(pal_pants)

    pal_mount = get_pal15("타조무희_여")
    apply_ramp(pal_mount, 1, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 2, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 3, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 4, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 5, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 7, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 8, SIG_STOPS["gold_bright"])
    apply_ramp(pal_mount, 9, SIG_STOPS["blue_rich"])
    results["타조무희_여_15.pal"] = bytes(pal_mount)

    # 11. Super Novice Male & Mount:
    pal = get_pal15("슈퍼노비스_남")
    apply_ramp(pal, 1, SIG_STOPS["silver"])     # collar & sleeve trim -> Moonlight Silver
    apply_ramp(pal, 2, SIG_STOPS["gold"])       # small accents -> Luminous Gold
    apply_ramp(pal, 3, SIG_STOPS["navy_dark"])  # trousers -> Deep Midnight Navy
    apply_ramp(pal, 5, SIG_STOPS["gold"])       # chest cross strap -> Luminous Gold
    apply_ramp(pal, 7, SIG_STOPS["silver"])     # breastplate -> Moonlight Silver
    apply_ramp(pal, 8, SIG_STOPS["gold"])       # waist buckle -> Luminous Gold
    apply_ramp(pal, 10, SIG_STOPS["gold"])      # knee guards -> Luminous Gold
    apply_ramp(pal, 11, SIG_STOPS["blue_rich"]) # main tunic & apron -> Rich Midnight Blue
    results["슈퍼노비스_남_15.pal"] = bytes(pal)

    pal_mount = get_pal15("슈퍼노비스포링_남")
    apply_ramp(pal_mount, 1, SIG_STOPS["silver"])
    apply_ramp(pal_mount, 2, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 3, SIG_STOPS["navy_dark"])
    apply_ramp(pal_mount, 5, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 7, SIG_STOPS["silver"])
    apply_ramp(pal_mount, 8, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 10, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 11, SIG_STOPS["blue_rich"])
    results["슈퍼노비스포링_남_15.pal"] = bytes(pal_mount)

    # 12. Super Novice Female & Mount:
    pal = get_pal15("슈퍼노비스_여")
    apply_ramp(pal, 1, SIG_STOPS["silver"])     # neckline collar -> Moonlight Silver
    apply_ramp(pal, 3, SIG_STOPS["gold"])       # trim -> Luminous Gold
    apply_ramp(pal, 4, SIG_STOPS["navy_dark"])  # inner shorts / leggings -> Deep Midnight Navy
    apply_ramp(pal, 5, SIG_STOPS["blue_rich"])  # outer vest & straps -> Rich Midnight Blue
    apply_ramp(pal, 7, SIG_STOPS["blue_rich"])  # suspenders / drapes -> Rich Midnight Blue
    apply_ramp(pal, 8, SIG_STOPS["gold"])       # waist buckle -> Luminous Gold
    apply_ramp(pal, 9, SIG_STOPS["gold"])       # wrist accents -> Luminous Gold
    apply_ramp(pal, 11, SIG_STOPS["blue_rich"]) # main dress & outer skirt -> Rich Midnight Blue
    apply_ramp(pal, 12, SIG_STOPS["gold"])      # chest studs & bow -> Luminous Gold
    results["슈퍼노비스_여_15.pal"] = bytes(pal)

    pal_mount = get_pal15("슈퍼노비스포링_여")
    apply_ramp(pal_mount, 1, SIG_STOPS["silver"])
    apply_ramp(pal_mount, 3, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 4, SIG_STOPS["navy_dark"])
    apply_ramp(pal_mount, 5, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 7, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 8, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 9, SIG_STOPS["gold"])
    apply_ramp(pal_mount, 11, SIG_STOPS["blue_rich"])
    apply_ramp(pal_mount, 12, SIG_STOPS["gold"])
    results["슈퍼노비스포링_여_15.pal"] = bytes(pal_mount)

    g_base.f.close()

    for fname, data in results.items():
        out_path = SOURCES_DIR / fname
        out_path.write_bytes(data)
        print(f"Generated master tuned {fname}")

    return results


if __name__ == "__main__":
    main()
