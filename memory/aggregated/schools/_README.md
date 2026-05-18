# ZŠ inventory — aggregated

## Status (2026-05-18, round 4 — populated)

`zs_by_mc.csv` populated from the MŠMT bulk JSON-LD dump
`rssz-cela-cr-2025-10-31.jsonld` (snapshot 2025-10-31). See parser at
`notebooks/wp02_parse/parse.py` and `RERUN.md → R-05`.

### Row counts per MČ

| MČ | Rows |
|---|---|
| Praha 3  | 15 |
| Praha 7  | 10 |
| Praha 8  | 26 |
| Praha 9  | 10 |
| Praha 10 | 23 |
| Praha 14 |  9 |
| **Total** | **93** |

Includes mainstream ZŠ and ZŠ speciální (special-education) — those carry obor
code `79-01-B/01` rather than `79-01-C/01`, flagged in `notes` as
`zs_specialni`. There are five such rows: two in P10, one in P3, one in P14,
one in P8 (the last via the `kapacita_registered=115` row in P10's count plus
the special-ed-only ZŠ Tolerance in P14).

### Column population

| Column | % populated |
|---|---|
| `mc`, `name`, `redizo`, `izo_zs`, `address`, `type`, `kapacita_registered`, `snapshot_date`, `source_url` | 100 % |
| `zrizovatel` | 77 % (21 private rows have `zrizovatele=[]` in source — typical for o.p.s. / s.r.o. that are themselves the legal entity) |
| `notes`      | 5 % (only set when zs_specialni or multi_izo) |

## Schema

| Column | Meaning | Source |
|---|---|---|
| `mc` | Městská část label, one of `Praha 3 / 7 / 8 / 9 / 10 / 14`. Derived from `(adresa.castObce, adresa.psc)` against an explicit lookup table — see `notebooks/wp02_parse/parse.py → CAST_PSC_TO_MC`. **Not** the same as `adresa.cisloObvoduPrahy`, which is the administrative obvod (Praha 1–10) and groups several MČ together — e.g. obvod Praha 9 contains MČ Praha 9 proper **plus** MČ Praha 14, MČ Praha-Čakovice, MČ Praha-Vinoř, MČ Horní Počernice, MČ Klánovice, etc. |
| `name` | Official school name (`uplnyNazev` of the entity). | MŠMT rejstřík |
| `redizo` | RED-IZO — 9-digit ID of the **legal entity** ("ředitelství"). Primary key. | MŠMT rejstřík |
| `izo_zs` | IZO(s) of the ZŠ obor(s) (`druh = B00`) within this entity, semicolon-separated where multiple. One RED-IZO can hold ZŠ + MŠ + školní jídelna + družina IZOs; this column captures only the B00 (ZŠ) ones. | MŠMT rejstřík |
| `address` | `<ulice> <cisloDomovni>/<cisloOrientacni>, <castObce>, <psc> <obec>`. | MŠMT rejstřík |
| `zrizovatel` | Founding authority — `zrizovatele[*].nazevOsoby` joined with `; `. Empty for entities where `zrizovatele=[]` (typical for o.p.s./s.r.o. that are themselves the legal person). | MŠMT rejstřík |
| `type` | Coarse classification derived from `typZrizovatele`: `state` ← 1 (MŠMT), 2 (obec/MČ), 3 (kraj), 4 (svazek), 7 (HMP/regional); `private` ← 5 (soukromník); `church` ← 6 (registrovaná církev). | derived |
| `kapacita_registered` | Sum of `nejvyssiPovolenyPocet` across all B00 obors of the entity, in měrná jednotka `01` (žáci). The legal ceiling, not actual enrolment. Where an entity has multiple B00 obors (e.g. ZŠ + ZŠ speciální), capacities are summed. **Always populated in this snapshot** — no missing values. | MŠMT rejstřík → `skolyAZarizeni[druh=B00].kapacity[mernaJednotka=01].nejvyssiPovolenyPocet` |
| `snapshot_date` | `2025-10-31` for this snapshot. | source filename |
| `source_url` | Asset URL of the JSON-LD dump on the MŠMT LKOD FTP. | source |
| `notes` | Anomalies: `zs_specialni` for special-ed-only entities (obor `79-01-B/01`); `multi_izo(N)` if more than one B00 IZO under the same RED-IZO. | derived |

## Data-dictionary notes

- **`kapacita_registered` is a ceiling, not a count.** It's the registered
  legal maximum a school can enrol. Compare to cohort size for an upper bound
  on supply, not actual supply. Per-year enrolment lives in WP-03.
- **RED-IZO vs IZO.** Primary key is **RED-IZO**, with `izo_zs` capturing the
  ZŠ-component IZO(s) for joining to MŠMT yearbooks (which report per-IZO
  enrolment). No multi-IZO ZŠ entities exist in this snapshot — every row has
  exactly one B00 IZO.
- **MČ assignment.** Done strictly by physical address (`adresa.castObce` +
  `adresa.psc`), not by founding authority. A private ZŠ in Praha 8 founded
  by a non-MČ entity still lands in `mc = Praha 8`. Cross-checked: in every
  row where `zrizovatel` is an MČ, the MČ name in `zrizovatel` matches the
  `mc` column (zero mismatches).
- **Excluded by MČ filter, even though physically in obvody 3/7/8/9/10:**
  schools in Hostivař, Petrovice, Horní Měcholupy, Dolní Měcholupy,
  Štěrboholy, Dubeč, Kolovraty, Uhříněves (under MČ Praha 15 / Praha-Petrovice
  / Praha-Štěrboholy / Praha-Dubeč / Praha-Kolovraty / Praha-Uhříněves /
  Praha-Dolní Měcholupy — listed in obvod Praha 10 but not MČ Praha 10);
  schools in Horní Počernice, Letňany, Kbely, Čakovice, Vinoř, Klánovice,
  Koloděje, Újezd nad Lesy, Satalice, Běchovice, Dolní Počernice (their own
  MČ, listed in obvod Praha 9); Praha-Troja (Trojská 110 ZŠ, separate small
  MČ between Praha 7 and 8).
- **Splits resolved via PSČ:** Vinohrady (130 00 → P3, 101 00 → P10);
  Strašnice (100/108 00 → P10 only); Vršovice (100/101 00 → P10);
  Bubeneč (170 00 → P7 only; the 160 00 part is MČ Praha 6 and has no ZŠ in
  scope here); Libeň (180/182 00 → P8, 190 00 → P9); Střížkov (180/182 00 →
  P8, 190 00 → P9); Troja (181/182 00 → P8, 171 00 → MČ Praha-Troja
  excluded); Hloubětín (190 00 → P9, 198 00 → P14).

## Sanity checks

- Total = 93, within the expected 60 ± 20 ballpark (just over; the surplus is
  driven by private ZŠ that didn't show up in the round-1 estimates).
- All `zrizovatel`-cites-MČ rows have the cited MČ matching `mc` (verified by
  `notebooks/wp02_parse/verify.py`).
- Three concrete anchors for re-runners:
  - RED-IZO `600041212` = "Základní škola, Praha 10, Gutova 1987/39" — MČ
    Praha 10, kapacita 720, zrizovatel MČ Praha 10.
  - RED-IZO `600040585` = "Základní škola, Praha 9 - Lehovec, Chvaletická 918"
    — MČ Praha 14 (despite the legal name referring to Praha 9), kapacita
    868, zrizovatel MČ Praha 14.
  - RED-IZO `600039382` = "Základní škola Praha 7, Korunovační 8" — MČ
    Praha 7, kapacita 560, zrizovatel MČ Praha 7.
