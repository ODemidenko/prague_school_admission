import json
from collections import Counter

d = json.load(open('/home/oleg/src/demography_prague/memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'))
recs = d['list']

praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

# Need to find the kodRUIAN mapping. kodRUIAN is the RUIAN code for the cast obce.
# Each RUIAN castObce code maps to one MČ.
# Let's see kodRUIAN values
print("kodRUIAN by castObce (sample):")
seen = {}
for r in praha:
    a = r.get('adresa', {})
    cob = a.get('castObce')
    kod = a.get('kodRUIAN')
    if cob and kod and cob not in seen:
        seen[cob] = kod
for cob, kod in sorted(seen.items()):
    print(f"  {cob}: {kod}")

# The MČ for each cast obce is fixed. Let's look at the obvody combinations to confirm
print("\n(castObce, cisloObvoduPrahy) combinations:")
combos = Counter()
for r in praha:
    a = r.get('adresa', {})
    combos[(a.get('castObce'), a.get('cisloObvoduPrahy'))] += 1
for k, v in sorted(combos.items()):
    print(f"  {k}: {v}")
