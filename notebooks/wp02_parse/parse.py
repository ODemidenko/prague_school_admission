"""
WP-02 ZŠ extraction from MŠMT rejstřík škol JSON-LD.

Snapshot: 2025-10-31. Source: NKOD bulk dump.
Filters: kraj=Hlavní město Praha, druh of obor='B00' (Základní škola), MČ in {P3,P7,P8,P9,P10,P14}.
"""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('/home/oleg/src/demography_prague')
SRC = ROOT / 'memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld'
OUT = ROOT / 'memory/aggregated/schools/zs_by_mc.csv'
SNAPSHOT = '2025-10-31'

# Map (castObce, psc_prefix) -> MČ slug. Built from the obvod 3/7/8/9/10
# distribution; only in-scope MČ are listed. PSČ prefix is the first 3 digits
# of the 5-digit Czech postal code (string compare with the space stripped).
# Where the mapping is unambiguous on castObce alone, psc_prefix is None.
#
# MČ slug = "Praha N" matching the project's six in-scope MČ.

# (castObce, psc) → MČ, with psc as full "NNN NN" string. None means any.
CAST_PSC_TO_MC: dict[tuple[str, str | None], str] = {
    # Praha 3
    ('Žižkov',     '130 00'): 'Praha 3',
    ('Vinohrady',  '130 00'): 'Praha 3',

    # Praha 7  (Troja 171 00 = MČ Praha-Troja, separate small MČ — EXCLUDED).
    ('Holešovice', '170 00'): 'Praha 7',
    ('Bubeneč',    '170 00'): 'Praha 7',

    # Praha 8
    ('Karlín',     '186 00'): 'Praha 8',
    ('Libeň',      '180 00'): 'Praha 8',
    ('Libeň',      '182 00'): 'Praha 8',
    ('Kobylisy',   '182 00'): 'Praha 8',
    ('Bohnice',    '181 00'): 'Praha 8',
    ('Čimice',     '181 00'): 'Praha 8',
    ('Střížkov',   '180 00'): 'Praha 8',
    ('Střížkov',   '182 00'): 'Praha 8',
    ('Troja',      '181 00'): 'Praha 8',
    ('Troja',      '182 00'): 'Praha 8',

    # Praha 9 (MČ proper — Vysočany, Prosek, parts of Libeň/Střížkov/Hloubětín
    # under PSČ 190 00; the 198 00 part of Hloubětín is MČ Praha 14).
    ('Vysočany',   '190 00'): 'Praha 9',
    ('Prosek',     '190 00'): 'Praha 9',
    ('Libeň',      '190 00'): 'Praha 9',
    ('Střížkov',   '190 00'): 'Praha 9',
    ('Hloubětín',  '190 00'): 'Praha 9',
    ('Hrdlořezy',  '190 00'): 'Praha 9',

    # Praha 10
    ('Vršovice',   '100 00'): 'Praha 10',
    ('Vršovice',   '101 00'): 'Praha 10',
    ('Strašnice',  '100 00'): 'Praha 10',
    ('Strašnice',  '108 00'): 'Praha 10',
    ('Vinohrady',  '101 00'): 'Praha 10',
    ('Malešice',   '108 00'): 'Praha 10',
    ('Záběhlice',  '106 00'): 'Praha 10',
    # The Hostivař / Petrovice / Horní Měcholupy / Dolní Měcholupy /
    # Štěrboholy / Dubeč / Kolovraty / Uhříněves cast obce sit in OBVOD
    # Praha 10 but in OTHER MČ (Praha 15 / Praha-Petrovice / Praha-Dubeč /
    # Praha-Kolovraty / Praha-Uhříněves / Praha-Štěrboholy / Praha-Dolní
    # Měcholupy). Not in scope for this project — EXCLUDE.

    # Praha 14 (Hloubětín pod 198 00, Kyje, Hostavice, Černý Most).
    ('Hloubětín',  '198 00'): 'Praha 14',
    ('Kyje',       '198 00'): 'Praha 14',
    ('Hostavice',  '198 00'): 'Praha 14',
    ('Černý Most', '198 00'): 'Praha 14',
}

# Standalone cast obce that are entire MČ and not in scope: skip silently.
# Cast obce that are entire in-scope MČ (no PSČ disambiguation needed) — none,
# because all six MČ have at least one shared cast obce with another MČ.


def classify_type(typ: str | None) -> str:
    """Map typZrizovatele code to coarse type.

    1 = MŠMT (state), 2 = obec/MČ (public/municipal), 3 = kraj, 4 = svazek obcí,
    5 = soukromník (private — s.r.o./o.p.s./association), 6 = registrovaná
    církev (church), 7 = Hl. m. Praha / kraj (regional public).
    """
    return {
        '1': 'state',
        '2': 'state',  # municipal-public
        '3': 'state',
        '4': 'state',
        '5': 'private',
        '6': 'church',
        '7': 'state',  # kraj / Hl. m. Praha
    }.get(typ, 'unknown')


def format_address(addr: dict) -> str:
    """Czech address: 'Ulice cisloDomovni/cisloOrientacni, castObce, PSC obec'."""
    ulice = addr.get('ulice') or ''
    cd = addr.get('cisloDomovni')
    co = addr.get('cisloOrientacni')
    cislo = ''
    if cd and co:
        cislo = f'{cd}/{co}'
    elif cd:
        cislo = f'{cd}'
    castobce = addr.get('castObce') or ''
    psc = addr.get('psc') or ''
    obec = addr.get('obec') or ''
    head = f'{ulice} {cislo}'.strip()
    return f'{head}, {castobce}, {psc} {obec}'.strip()


def main():
    d = json.loads(SRC.read_text())
    recs = d['list']
    praha = [r for r in recs if r.get('kraj') == 'Hlavní město Praha']

    in_scope_mc = {'Praha 3', 'Praha 7', 'Praha 8', 'Praha 9', 'Praha 10', 'Praha 14'}

    # rows keyed by redIzo so combined ZŠ+MŠ entities collapse to one row
    rows: dict[str, dict] = {}
    rejected_ambiguous = []

    for r in praha:
        addr = r.get('adresa') or {}
        key = (addr.get('castObce'), addr.get('psc'))
        mc = CAST_PSC_TO_MC.get(key)
        if not mc or mc not in in_scope_mc:
            continue
        # find ZŠ obory (B00) within this entity
        zs_obors = [s for s in r.get('skolyAZarizeni', []) if s.get('druh') == 'B00']
        if not zs_obors:
            continue

        # IZO and kapacita aggregation
        izos = []
        kapacita_total = 0
        kapacita_any = False
        obor_nazvy = []
        for s in zs_obors:
            izos.append(s.get('izo'))
            obor_nazvy.append(s.get('uplnyNazev') or '')
            for k in s.get('kapacity', []):
                if k.get('mernaJednotka') == '01' and k.get('nejvyssiPovolenyPocet') is not None:
                    kapacita_total += int(k['nejvyssiPovolenyPocet'])
                    kapacita_any = True

        # If multiple zrizovatele, take the first names.
        zriz = r.get('zrizovatele') or []
        zriz_str = '; '.join(z.get('nazevOsoby') or '' for z in zriz) if zriz else ''

        # Detect zákl. škola speciální among obory
        notes_bits = []
        is_special = False
        for s in zs_obors:
            for o in s.get('obory', []):
                kod = o.get('kod') or ''
                if kod.startswith('79-01-B'):
                    is_special = True
        if is_special:
            notes_bits.append('zs_specialni')
        if len(zs_obors) > 1:
            notes_bits.append(f'multi_izo({len(zs_obors)})')

        redizo = r.get('redIzo')
        row = {
            'mc': mc,
            'name': r.get('uplnyNazev'),
            'redizo': redizo,
            'izo_zs': ';'.join(izos),
            'address': format_address(addr),
            'zrizovatel': zriz_str,
            'type': classify_type(r.get('typZrizovatele')),
            'kapacita_registered': kapacita_total if kapacita_any else '',
            'snapshot_date': SNAPSHOT,
            'source_url': 'https://lkod-ftp.msmt.gov.cz/00022985/e9c07729-877e-4af0-be4a-9d36e45806ae/rssz-cela-cr-2025-10-31.jsonld',
            'notes': ';'.join(notes_bits),
        }
        rows[redizo] = row

    # Write CSV
    header = ['mc', 'name', 'redizo', 'izo_zs', 'address', 'zrizovatel',
              'type', 'kapacita_registered', 'snapshot_date', 'source_url', 'notes']
    sorted_rows = sorted(rows.values(), key=lambda r: (r['mc'], r['name']))
    with OUT.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for row in sorted_rows:
            w.writerow(row)

    # Summary
    by_mc = Counter(r['mc'] for r in sorted_rows)
    print(f'Total rows: {len(sorted_rows)}')
    print('By MČ:')
    for mc in sorted(by_mc):
        print(f'  {mc}: {by_mc[mc]}')

    # Field population stats
    n = len(sorted_rows)
    if n:
        for col in header:
            filled = sum(1 for r in sorted_rows if r.get(col) not in (None, ''))
            print(f'  {col}: {filled}/{n} ({100*filled//n}%)')

    # Print weird cases
    print('\nMulti-IZO entities:')
    for r in sorted_rows:
        if 'multi_izo' in r['notes']:
            print(f"  {r['mc']}: {r['name']} (RED-IZO {r['redizo']}, IZOs {r['izo_zs']})")
    print('\nSpecial-ed only entities (zs_specialni note):')
    for r in sorted_rows:
        if 'zs_specialni' in r['notes']:
            print(f"  {r['mc']}: {r['name']} kap={r['kapacita_registered']}")
    print('\nMissing kapacita:')
    for r in sorted_rows:
        if r['kapacita_registered'] == '':
            print(f"  {r['mc']}: {r['name']}")


if __name__ == '__main__':
    main()
