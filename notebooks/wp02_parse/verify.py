"""Cross-check: for each row, the zrizovatel name (where state-municipal) should
mention the same MČ as we assigned. Print any mismatches."""

import csv
from pathlib import Path

ROOT = Path('/home/oleg/src/demography_prague')
CSV = ROOT / 'memory/aggregated/schools/zs_by_mc.csv'

with CSV.open() as f:
    rows = list(csv.DictReader(f))

mismatches = []
for r in rows:
    z = (r.get('zrizovatel') or '').lower()
    if 'městská část' not in z:
        continue  # private/state-kraj/church — no MČ check possible
    mc = r['mc'].replace('Praha ', '')  # "Praha 8" -> "8"
    # Look for an MČ number in zrizovatel
    if f'praha {mc}' not in z:
        # Mismatch
        mismatches.append((r['mc'], r['name'], r['zrizovatel']))

print(f"Mismatches: {len(mismatches)}")
for mc, name, z in mismatches:
    print(f"  assigned {mc!r}, zrizovatel: {z!r} — {name}")
