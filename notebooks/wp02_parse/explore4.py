import json
from collections import Counter, defaultdict

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']
praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# Only ZŠ druh codes. Let's see which druh maps to ZŠ.
# In MŠMT codes: B00 = základní škola (ZŠ); A00 = MŠ
# Let's print uplnyNazev samples for several druh codes
samples = defaultdict(list)
for r in praha:
    for s in r.get('skolyAZarizeni', []):
        d_code = s.get('druh')
        if len(samples[d_code]) < 3:
            samples[d_code].append((s.get('uplnyNazev'), r.get('uplnyNazev')))

for code in ['B00', 'A00', 'C00', 'G21', 'D00']:
    print(f"\n=== {code} ===")
    for sn, rn in samples[code][:3]:
        print(f"  obor: {sn}")
        print(f"  entity: {rn}")
