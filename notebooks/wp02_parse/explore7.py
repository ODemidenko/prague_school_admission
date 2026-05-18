import json
from collections import Counter, defaultdict

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']
praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# For ZŠ-bearing entities in obvody 3,7,8,9,10 list castObce + PSČ
in_obvody = {'Praha 3', 'Praha 7', 'Praha 8', 'Praha 9', 'Praha 10'}
zs = [r for r in praha if any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', []))
      and r.get('adresa', {}).get('cisloObvoduPrahy') in in_obvody]
print(f"ZŠ-bearing entities in obvody 3/7/8/9/10: {len(zs)}")

# distribution by (obvod, castObce)
combos = Counter()
for r in zs:
    a = r['adresa']
    combos[(a.get('cisloObvoduPrahy'), a.get('castObce'), a.get('psc'))] += 1
print("\n(obvod, castObce, psc) -> count:")
for k, v in sorted(combos.items()):
    print(f"  {k}: {v}")
