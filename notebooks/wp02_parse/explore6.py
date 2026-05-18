import json
from collections import Counter, defaultdict

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']
praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# Sample of typZrizovatele=7 entities to identify what that means
print("=== typZrizovatele=7 samples (ZŠ-bearing) ===")
n = 0
for r in praha:
    if r.get('typZrizovatele') == '7' and any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
        print(f"  entity: {r['uplnyNazev']}")
        print(f"    zrizovatele: {[(z.get('nazevOsoby'), z.get('pravniForma')) for z in r.get('zrizovatele', [])]}")
        n += 1
        if n >= 6: break

print("\n=== typZrizovatele=1 samples ===")
n = 0
for r in praha:
    if r.get('typZrizovatele') == '1' and any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
        print(f"  entity: {r['uplnyNazev']}")
        print(f"    zrizovatele: {[(z.get('nazevOsoby'), z.get('pravniForma')) for z in r.get('zrizovatele', [])]}")
        n += 1
        if n >= 6: break

print("\n=== typZrizovatele=5 samples ===")
n = 0
for r in praha:
    if r.get('typZrizovatele') == '5' and any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
        print(f"  entity: {r['uplnyNazev']}")
        print(f"    zrizovatele: {[(z.get('nazevOsoby'), z.get('pravniForma')) for z in r.get('zrizovatele', [])]}")
        n += 1
        if n >= 6: break

print("\n=== typZrizovatele=2 samples ===")
n = 0
for r in praha:
    if r.get('typZrizovatele') == '2' and any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
        print(f"  entity: {r['uplnyNazev']}")
        print(f"    zrizovatele: {[(z.get('nazevOsoby'), z.get('pravniForma')) for z in r.get('zrizovatele', [])]}")
        n += 1
        if n >= 6: break
