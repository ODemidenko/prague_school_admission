# Catchment parser anomalies


## Missing state ZŠ (in `zs_by_mc.csv`, no catchment row)
These rejstřík rows are state-founded, non-`zs_specialni` ZŠ that got no catchment row in the decree. Manual classification below: **hospital** = teaches in-patients only (not spádová by design); **logopedická** = speech-therapy school admitted via diagnosis (not spádová); **other** = needs investigation.

- `691019061` Základní škola V Olšinách, Praha 10, příspěvková organizace (MČ Praha 10) — **other — needs investigation (MČ-founded, regular C-class ZŠ, kap 175)**
- `600171442` Základní škola logopedická a Mateřská škola logopedická, Praha 10, Moskevská 29 (MČ Praha 10) — **logopedická — Moskevská 29, founded by Hlavní město Praha**
- `600021246` Základní škola LOPES Čimice, Praha 8, Libčická 399 (MČ Praha 8) — **logopedická — LOPES Čimice, founded by Hlavní město Praha**
- `600021238` Základní škola a Mateřská škola při Nemocnici Na Bulovce (MČ Praha 8) — **hospital — Nemocnice Na Bulovce**
- `610350803` Základní škola a Mateřská škola, Praha 8, Za Invalidovnou 1 (MČ Praha 8) — **hospital — Za Invalidovnou (Nemocnice Na Františku)**
- `600021262` Základní škola při Psychiatrické nemocnici Bohnice, Praha 8, Ústavní 91 (MČ Praha 8) — **hospital — Psychiatrická nemocnice Bohnice**
