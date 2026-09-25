import re

with open(r'MidnightROClient/SystemEN/itemInfo_C.lua', 'rb') as f:
    text = f.read().decode('cp874', errors='ignore')

print("--- Searching itemInfo_C.lua ---")
for line in text.splitlines():
    if any(k in line for k in ['Rank', 'rank', 'Badge', 'badge', 'Kasaka', 'Monarch', 'Hunter']):
        if 'DisplayName' in line or 'tbl_custom' in line:
            print(line)

print("\n--- Searching server/db/import/item_db.yml ---")
with open(r'server/db/import/item_db.yml', 'rb') as f:
    item_db_text = f.read().decode('utf-8', errors='ignore')

for line in item_db_text.splitlines():
    if any(k in line for k in ['Rank', 'rank', 'Badge', 'badge', 'Kasaka', 'Monarch', 'Hunter', '9022']):
        print(line)
