import json
from collections import Counter, defaultdict

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']
praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# Show some entities that have a ZŠ obor — look at typZrizovatele variety and zrizovatele structure
zs_entities = []
for r in praha:
    if any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
        zs_entities.append(r)
print(f"Praha entities with at least one ZŠ obor: {len(zs_entities)}")

typ_z = Counter(r.get('typZrizovatele') for r in zs_entities)
print(f"typZrizovatele on those: {typ_z}")

# Look at kapacita inside ZŠ obor
print("\n--- sample ZŠ obors with kapacity ---")
for r in zs_entities[:3]:
    print(f"\n{r['uplnyNazev']} | redIzo={r['redIzo']} | typZrizovatele={r['typZrizovatele']}")
    print(f"  zrizovatele: {[(z.get('nazevOsoby'), z.get('pravniForma'), z.get('ico')) for z in r.get('zrizovatele', [])]}")
    for s in r['skolyAZarizeni']:
        if s.get('druh') == 'B00':
            print(f"  ZŠ izo={s['izo']} kapacity={s.get('kapacity')}")
            print(f"  obory: {s.get('obory')}")

# typZrizovatele code list — what values exist all over praha
print("\ntypZrizovatele distribution:")
print(Counter(r.get('typZrizovatele') for r in praha))

# kapacity mernaJednotka codes for B00
mj = Counter()
for r in zs_entities:
    for s in r['skolyAZarizeni']:
        if s.get('druh') == 'B00':
            for k in s.get('kapacity', []):
                mj[k.get('mernaJednotka')] += 1
print(f"\nB00 mernaJednotka codes: {mj}")
