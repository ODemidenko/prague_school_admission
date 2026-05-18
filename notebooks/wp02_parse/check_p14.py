import json
from collections import Counter

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']
praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# All entities with B00 obor and castObce in {Hloubětín, Kyje, Hostavice, Černý Most}
zs_p14_cands = []
for r in praha:
    a = r.get('adresa') or {}
    if a.get('castObce') in {'Hloubětín', 'Kyje', 'Hostavice', 'Černý Most'}:
        if any(s.get('druh') == 'B00' for s in r.get('skolyAZarizeni', [])):
            zs_p14_cands.append((a.get('castObce'), a.get('psc'), r.get('uplnyNazev'), r.get('redIzo')))
print(f"Total ZŠ candidates in MČ Praha 14 castObce: {len(zs_p14_cands)}")
for c in zs_p14_cands:
    print(f"  {c}")

# Same for MŠ-only entities (A00 but not B00) to confirm not missing kindergartens that also have a ZŠ
print()
print("=== Sanity: castObce values across whole praha for Hostavice ===")
hosts = [r for r in praha if (r.get('adresa') or {}).get('castObce') == 'Hostavice']
print(f"Total Hostavice entities (any type): {len(hosts)}")
print(Counter((r.get('adresa') or {}).get('psc') for r in hosts))
