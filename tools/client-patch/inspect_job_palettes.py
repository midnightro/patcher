import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

tools = Path(__file__).resolve().parent
sys.path.insert(0, str(tools))
from grf import Grf

g_mid = Grf("e:/.midnight-ro/MidnightROClient/midnight.grf")
g_data = Grf("e:/.midnight-ro/MidnightROClient/data.grf")

jobs = [
    ("Novice", "초보자"),
    ("Assassin", "어세신"),
    ("Hunter", "헌터"),
    ("Alchemist", "연금술사"),
    ("Swordman", "검사"),
    ("Mage", "마법사"),
    ("Acolyte", "성직자"),
    ("Thief", "도둑"),
]

for name_en, name_kr in jobs:
    print(f"\n=== {name_en} ({name_kr}) ===")
    for s in ["남", "여"]:
        van_fn = f"data\\palette\\몸\\{name_kr}_{s}_0.pal".encode("cp949")
        mid_fn = f"data\\palette\\몸\\{name_kr}_{s}_15.pal".encode("cp949")
        
        has_van = van_fn in g_data.entries or van_fn in g_mid.entries
        has_mid = mid_fn in g_mid.entries
        print(f"  {s}: van={has_van}, mid_15={has_mid}")

g_mid.f.close()
g_data.f.close()
