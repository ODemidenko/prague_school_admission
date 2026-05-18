import json
from collections import Counter

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']

praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']
print(f"Praha entities: {len(praha)}")

obvody = Counter(r.get('adresa', {}).get('cisloObvoduPrahy') for r in praha)
print("cisloObvoduPrahy distribution:")
for k, v in sorted(obvody.items(), key=lambda x: (x[0] or '')):
    print(f"  {k}: {v}")

all_druhy = Counter()
for r in praha:
    for s in r.get('skolyAZarizeni', []):
        all_druhy[s.get('druh')] += 1
print("\nAll druh codes for Praha:")
for k, v in sorted(all_druhy.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
