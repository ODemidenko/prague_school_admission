import json
from collections import Counter

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']

praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# Look for things in Praha 9 obvod with various castObce/obec values
p9 = [r for r in praha if r.get('adresa', {}).get('cisloObvoduPrahy') == 'Praha 9']
print(f"Praha 9 obvod: {len(p9)}")

# obec values
obecs = Counter(r.get('adresa', {}).get('obec') for r in p9)
print("obec in Praha 9 obvod:")
for k, v in obecs.items():
    print(f"  {k}: {v}")

# castObce values
casts = Counter(r.get('adresa', {}).get('castObce') for r in p9)
print("castObce in Praha 9 obvod:")
for k, v in sorted(casts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# uzemiDleORP values for all Praha entities
print("\nuzemiDleORP in all Praha:")
orps = Counter(r.get('adresa', {}).get('uzemiDleORP') for r in praha)
for k, v in sorted(orps.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# okres
print("\nokres in all Praha:")
okrs = Counter(r.get('adresa', {}).get('okres') for r in praha)
for k, v in sorted(okrs.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

# Look at obec values across all praha
print("\nobec in all Praha:")
obecs_all = Counter(r.get('adresa', {}).get('obec') for r in praha)
for k, v in sorted(obecs_all.items(), key=lambda x: -x[1])[:20]:
    print(f"  {k}: {v}")
