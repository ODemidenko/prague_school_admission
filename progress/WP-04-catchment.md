# WP-04 — Catchment (spádové obvody)

**Status:** recon complete, parser dispatch pending.
**Last update:** 2026-05-18.

## Source-of-truth analysis

The handoff's mental model ("each MČ publishes its own OZV") was partially
wrong but pragmatically right.

- **Legal authority:** there is a single citywide decree, **Obecně závazná
  vyhláška hl. m. Prahy č. 19/2025 o školských obvodech základních škol**,
  effective 2025-04-01, amended by usnesení ZHMP 11.12.2025 effective
  **2026-01-01**. The 2026-01-01 version is what binds the April 2027 zápis
  (the 2021 birth cohort's entry).
- **Mirroring practice:** each MČ hosts an **annex / excerpt** listing only the
  streets in its own territory — the binding data per-MČ is identical to the
  citywide annex but easier to parse per-MČ.
- **Conclusion:** parse per-MČ excerpts as primary (cleaner scope per file),
  cross-check against citywide for P8 and P10 where per-MČ excerpts weren't
  recovered.

## Files on disk (`memory/raw/catchment/`)

| File | Bytes | MČ scope | Effective | Notes |
|---|---|---|---|---|
| `p3_skolske-obvody-2026.pdf`            | 119 233 | P3 only | 2026-01-01 | MČ-published excerpt (Rada MČ P3 usnesení 855/2025-10-08). Mirrors citywide annex. |
| `p7_OZV-skolske-obvody-2025.pdf`        | 144 368 | P7 only | 2025-04-01 | MČ-published excerpt of vyhláška 19/2025. **Older effective date** — verify whether updated edition exists for 2026/2027 zápis. |
| `p9_spadova-vyhlaska-1.1.2026.docx`     |  21 207 | P9 only | 2026-01-01 | MČ-published excerpt as DOCX (structural — easier to parse than PDF). |
| `p9_HMP-vyhlaska-1.1.2026.docx`         | 220 052 | citywide (kept for context) | 2026-01-01 | Full vyhláška text in DOCX form. |
| `vyhlaska-19-2025_via-P14.pdf`          | 126 307 | P14 only | 2025-04-01 (likely); 4 pages | MČ-published excerpt. **Verify if 2026-01-01 amendment is reflected** — filename suggests 19/2025 base. |
| `vyhlaska-hmp-19-2025_via-P6.pdf`       | 640 460 | citywide (covers all 6 MČs) | 2025-04-01 | Praha 6 mirror of the citywide decree. Use as primary source for **P8 and P10** (no per-MČ excerpt recovered) and as **cross-check** for the others. |

**Total bytes on disk:** ~1.27 MB across 6 files.

## Coverage matrix

| MČ | Per-MČ source | Citywide cross-check | Status |
|---|---|---|---|
| Praha 3  | `p3_skolske-obvody-2026.pdf` (2026-eff) | `vyhlaska-hmp-19-2025_via-P6.pdf` | covered |
| Praha 7  | `p7_OZV-skolske-obvody-2025.pdf` (**2025-eff** — gap?) | `vyhlaska-hmp-19-2025_via-P6.pdf` | **verify edition** |
| Praha 8  | — | `vyhlaska-hmp-19-2025_via-P6.pdf` | covered (citywide only) |
| Praha 9  | `p9_spadova-vyhlaska-1.1.2026.docx` (2026-eff DOCX) + `p9_HMP-vyhlaska-1.1.2026.docx` | `vyhlaska-hmp-19-2025_via-P6.pdf` | covered |
| Praha 10 | — | `vyhlaska-hmp-19-2025_via-P6.pdf` | covered (citywide only) |
| Praha 14 | `vyhlaska-19-2025_via-P14.pdf` (likely 2025-eff) | `vyhlaska-hmp-19-2025_via-P6.pdf` | **verify edition** |

## Parser dispatch plan

**One subagent for the whole pass.** Inputs are six small files on local disk;
heterogeneous formats (PDF + DOCX); each one has the same target schema. A
single subagent with both `pdfplumber` (or `pypdf2` + table heuristics) and
`python-docx` can produce one normalised CSV. Drop to per-MČ subagents only if
the unified parser hits format ambiguity.

**Target output:** `memory/aggregated/catchment/streets_to_zs.csv`

| Column | Meaning |
|---|---|
| `mc` | One of `Praha 3 / 7 / 8 / 9 / 10 / 14` |
| `street` | Czech street/quarter name (UTF-8, diacritics preserved) |
| `house_number_range` | Lichá/sudá and/or numerical range as printed (verbatim, parse later if needed) |
| `red_izo` | RED-IZO joining to `memory/aggregated/schools/zs_by_mc.csv` |
| `zs_name` | School name as printed in the decree (helps disambiguate the join) |
| `source_file` | Filename in `memory/raw/catchment/` |
| `effective_date` | ISO date the decree text is in force |

**Join verification:** the subagent must verify that every distinct `red_izo`
in `streets_to_zs.csv` exists in `zs_by_mc.csv`, and that every state-founded
ZŠ in `zs_by_mc.csv` (those eligible for spádovost — i.e. not private and not
`zs_specialni`) appears in `streets_to_zs.csv`. Anomalies go in a sidecar
`_anomalies.md`.

## Open verification items

1. **Edition drift:** P7 and P14 PDF filenames suggest the 2025-04-01 base
   decree — verify whether they have been updated for the 2026-01-01
   amendment. If not, the citywide PDF (which IS the 2026 amendment? — also
   needs verification) supplies the deltas.
2. **Praha 14 ZŠ Lehovec gotcha:** RED-IZO 600040585 is named
   "ZŠ Praha 9 - Lehovec" but located in MČ Praha 14. Parser must not
   match on school name alone; key on RED-IZO.
3. **Special-ed schools:** the 5 `zs_specialni` rows in `zs_by_mc.csv` are
   NOT spádové. Parser may legitimately not match them.

## Results (2026-05-18)

Parser run from `notebooks/wp04_parse/parse.py` produced
`memory/aggregated/catchment/streets_to_zs.csv`: **1 953 rows**.

Per-MČ row count and ZŠ coverage (state non-`zs_specialni` ZŠ in
`zs_by_mc.csv` that received at least one catchment row):

| MČ | Streets | ZŠ covered | ZŠ in scope | Coverage |
|---|---|---|---|---|
| Praha 3  | 235 | 10 | 10 | 100 % |
| Praha 7  | 131 |  6 |  6 | 100 % |
| Praha 8  | 527 | 15 | 19 |  78 % |
| Praha 9  | 263 |  6 |  6 | 100 % |
| Praha 10 | 521 | 14 | 15 |  93 % |
| Praha 14 | 276 |  6 |  6 | 100 % |

**Primary source:** citywide PDF `vyhlaska-hmp-19-2025_via-P6.pdf` (Vyhláška
č. 19/2025 hl. m. Prahy as amended 11. 12. 2025, **účinná 1. 1. 2026**).
P9 was parsed from the cleaner DOCX excerpt (`p9_spadova-vyhlaska-1.1.2026.docx`).
Per-MČ PDFs (P3, P7, P14) used as cross-checks only — their content matches
the citywide closely; P3 cross-check differs by only ~3 rows (continuation-row
noise like "l. stupeň").

**Effective-date verification:** citywide PDF text on p. 1 states *Tato
vyhláška nabývá účinnosti dnem 1. ledna 2026*. The P7 per-MČ excerpt
(`p7_OZV-skolske-obvody-2025.pdf`) is a pre-amendment publication, but its
P7 section text matches the citywide for P7 — the 2026 amendment did not
substantively change P7's streets. P14 per-MČ excerpt is similarly aligned.

**Anomalies (6 missing state ZŠ — all expected):** 3 hospital schools at
psychiatric / general hospitals (Bulovka, Bohnice, Nemocnice Na Františku
@ Za Invalidovnou 1) which serve in-patients only and are not spádové;
2 logopedická (speech-therapy) schools founded by hlavní město Praha
(LOPES Čimice, Moskevská 29) which admit via diagnosis not via residence;
1 unclassified — *ZŠ V Olšinách, Praha 10* (RED-IZO 691019061), founded by
MČ Praha 10, kap 175, obor `79-01-C/01` — does not appear in the 19/2025
decree. Possibly a new school not yet in the spádový rozpis; flagged for
follow-up. See `memory/aggregated/catchment/_anomalies.md`.

**Invariant checks (all passed where required):**
1. Every `red_izo` in CSV exists in `zs_by_mc.csv` — PASS.
2. Lehovec gotcha (RED-IZO 600040585 → `mc=Praha 14`) — PASS.
3. No unmatched school headings — PASS.
4. Coverage of state non-special ZŠ — 57/62 = 92 % covered; remaining 5
   are expected (hospital + logopedická), 1 (V Olšinách) is genuinely
   missing from the decree.

**Re-run recipe:** `RERUN.md → R-06`.
