# Demographics — aggregated tables

## TL;DR

After round 4 (2026-05-18) the demographics aggregate is **substantially fuller**: a 2011–2025 ČSÚ time series of children-by-5-year-age-band × MČ × year (360 rows) was appended to `children_by_age_mc_year.csv`, and an annual 2004–2025 birth-cohort series went into the new `births_by_mc_year.csv` (132 rows). The 12 IPR rows from round 3 are preserved unchanged.

**Single-year-of-age is still not present.** The headline ČSÚ file ships in 5-year bands; single-year data only lives on the IPR dashboard `uap.iprpraha.cz/pov`, still blocked at harness level. The age-0–14 question is answered by summing bands `0-4`, `5-9`, `10-14`; the age-15+ portion of the 15–19 band overshoots the 0–18 scope by one year — flag in downstream code, do not pretend the data is finer than it is.

## Files

### `children_by_age_mc_year.csv`

Primary deliverable. **Mixed-source CSV: 12 rows from IPR (2024 walking-distance bands) + 360 rows from ČSÚ (2011–2025 population by 5-year band).** Schema diverges from the dispatch spec — `age` is empty because no source we could reach gives single-year-of-age. Added columns: `age_band_min`, `age_band_max`, `count_kind`, `coverage_pct`, `notes`. **Filter by `source_slug` and `count_kind` before aggregating** — the IPR `walking_distance_to_*` rows and ČSÚ `population` rows are NOT directly comparable.

Columns:

| Column            | Type   | Description |
|---|---|---|
| `year`            | int    | Reference year (only 2024 here). |
| `reference_date`  | date   | "k 1.1.2024" — IPR's stav reference date for school-year-aligned indicators. |
| `mc`              | str    | Normalised MČ label ("Praha 3", …). |
| `mc_code`         | str    | LAU-2 code from the glossary; **not yet re-verified against the source** — values are quoted from `glossary.md` rev 2026-05-18. |
| `age`             | int    | **Empty** for every row — source provides bands, not single year. |
| `age_band_min`    | int    | Lower bound of the age band (inclusive). |
| `age_band_max`    | int    | Upper bound (inclusive). |
| `count`           | int    | The raw number from the IPR table: *children of the band living within walking distance of an MŠ (600m) or ZŠ (800m)*. |
| `count_kind`      | str    | `walking_distance_to_MŠ` or `walking_distance_to_ZŠ` — flags that `count` is a coverage-filtered subset, not the full cohort. |
| `coverage_pct`    | int    | The "% v pásmu dostupnosti" from the same IPR row. **True cohort ≈ count / (coverage_pct / 100).** |
| `source_slug`     | str    | Matches the entry in `memory/sources.md`. |
| `kind`            | str    | `historical` (the 2024 row is "stav", i.e. historical) or `projection`. |
| `notes`           | str    | Source citation (Příloha number, row label). |

Row count: **372** = 12 IPR (round 3) + 360 ČSÚ (round 4: 6 MČ × 4 bands × 15 years). Pre-existing IPR rows are unchanged.

ČSÚ-specific column conventions:
- `mc_code` holds the **IPR/LAU-2 code** (e.g. `547107` for Praha 3), kept stable across both sources so the file remains joinable on `(mc, mc_code)`. The ČSÚ source uses a different code (`KOD_ZUJ`, e.g. `500097` for Praha 3) — that value is captured in `notes` for traceability.
- `count_kind = population` (per the source header "Obyvatelstvo podle pohlaví a věkových skupin … k 31.12.").
- `reference_date = YYYY-12-31` (ČSÚ stock convention).
- `coverage_pct` is empty for ČSÚ rows — these are full population counts, not walking-distance subsets.
- The 15-19 band overshoots the 0–18 scope by one year; we keep it because the source publishes the full band and discarding the single year 19 would still mis-attribute the rest. Consumers should subtract a 1/5 approximation or use only bands 0-4 / 5-9 / 10-14 when answering age-0–14 questions.

### `births_by_mc_year.csv`

Round 4 addition. Annual live births per MČ per year 2004–2025, sourced from the ČSÚ *Časová řada za městské části* file (row "Živě narození / Live births").

Columns: `year, reference_date, mc, mc_code, count, count_kind ("live_births"), source_slug, kind, notes`.

Row count: **132** = 6 MČ × 22 years.

**Why this is the headline cohort primitive.** The project's central question is the chance a child born in 2021 / 2024 gets into a ZŠ. The 2021 birth row × `mc` is the cleanest population denominator for that cohort *as observed at birth* — before migration in/out muddies the picture. The 6–9 years between birth and ZŠ entry can be modelled separately using the age-band time series in `children_by_age_mc_year.csv` (cohort progression / net migration).

### `mc_total_population_ipr_2024_2050.csv`

Sidecar table, NOT in scope of "children by age" but a strong cross-check. Per-MČ total population for 2023 (stav, source: ČSÚ bilance k 31.12.2023) plus 2030 and 2050 across 5 IPR variants (PROG = realistic prognosis; MAX+/MAX/MID/NUL = illustrative projections of building build-out and migration).

66 rows = 6 MČ × 11 (year, variant) cells.

## Coverage matrix

ČSÚ 5-year bands (`source_slug=csu-vekove-slozeni-mc-2011-2025`): bands `0-4`, `5-9`, `10-14`, `15-19` populated for every year 2011–2025 × every in-scope MČ (Praha 3, 7, 8, 9, 10, 14). Bands above 19 are in the raw XLSX but excluded from the aggregated CSV (out of project scope).

ČSÚ live births (`source_slug=csu-casova-rada-mc-2004-2025`): every year 2004–2025 × every in-scope MČ. This goes 7 years deeper than the population age series, giving us a clean view of the 2004–2010 birth cohorts that are already in school today.

IPR 2024 stav + projections (`source_slug=ipr-prognoza-2024-2050-vzdelavani`): walking-distance proxy counts for age 3–5 and 6–14, 2024 only. See round-3 R-02 note.

| Year | Band 0–4 | Band 5–9 | Band 10–14 | Band 15–19 | Live births | Single-year 0–18 |
|---|---|---|---|---|---|---|
| 2004–2010 | — | — | — | — | **6 MČ (ČSÚ)** | — |
| 2011–2025 | **6 MČ (ČSÚ)** | **6 MČ (ČSÚ)** | **6 MČ (ČSÚ)** | **6 MČ (ČSÚ)** | **6 MČ (ČSÚ)** | — |
| 2024 (overlay) | — | — | — | — | — | walking-dist proxy for 3–5 and 6–14 (IPR) |
| 2030 (PROG) | — | deficits only* | deficits only* | deficits only* | — | — |
| 2050 (PROG) | — | deficits only* | deficits only* | deficits only* | — | — |

\* The 2030/2050 numbers in the IPR appendix rows are *capacity surplus/deficit* (i.e. cohort minus places), not cohort counts. To recover cohort, you'd need either (a) the per-year per-MČ MŠ/ZŠ capacity from WP-02 + the deficit, or (b) the original cohort series from the dashboard. Neither is in this file.

## Known gaps

- **Single-year-of-age × MČ × year, anywhere.** Round 4's ČSÚ file ships only 5-year bands. The IPR dashboard at `uap.iprpraha.cz/pov` is the canonical source; still blocked. The age-0–4 band cannot be split into "age 0", "age 1" etc. for the 2021/2024 birth-cohort tracking question — use `births_by_mc_year.csv` for the cohort-as-born signal and the 5-year band for the in-school stock.
- **2026+ projections beyond IPR's three reference dates (2024 stav, 2030, 2050).** ČSÚ doesn't publish per-MČ forward projections; the dashboard would, if reachable.
- **The 15–19 band overshoots project scope (0–18) by one year of age.** Document the +1y bias; do not down-weight without source guidance.
- **Praha 9 / obvod Praha 9 disambiguation.** IPR uses "MČ Praha 9" (the self-governing district, BUC rows 19_1…19_5). ČSÚ uses KOD_ZUJ=500216 and the column header "Praha 9" in both XLSXs — same entity. Cross-checked round 4: Praha 9 totals from ČSÚ match the BUC sum from IPR within rounding; the IPR row "MČ Praha 9" is congruent with the ČSÚ "Praha 9" row. Glossary's existing note can be tightened in a follow-up.

## Reference-date convention

- ČSÚ stock tables (`1_PHA_VEK_obyv_mc.xlsx`): "k 31.12." — `reference_date = YYYY-12-31` for all 360 round-4 age-band rows.
- ČSÚ time-series file (`Casova_rada_MC.xlsx`): "Population as at 31 December" / "Live births during the year" — also `YYYY-12-31`.
- IPR education-chapter stav: "k 1.1." for school-year alignment — `reference_date = 2024-01-01` for the 12 round-3 IPR rows.
- IPR population chapter (`mc_total_population_ipr_2024_2050.csv`): "k 31.12." for the 2023 stav row.

So within `children_by_age_mc_year.csv` the ČSÚ rows are end-of-year, the IPR rows are start-of-year. The 1-day calendar gap between e.g. ČSÚ 2023-12-31 and IPR 2024-01-01 is negligible for cohort purposes.

## Source

All numbers traceable to:
- `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_obyvatelstvo.pdf` (Příloha P.2.04, pp. 38–41) — for `mc_total_population_ipr_2024_2050.csv`
- `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_vzdelavani.pdf` (Příloha P.3.02, pp. 59–62, and P.3.04, pp. 63–66) — for the 12 IPR rows in `children_by_age_mc_year.csv`
- `memory/raw/demographics/csu/1_PHA_VEK_obyv_mc.xlsx` (sheets 2011..2025, header row 4, band columns 5–8) — for the 360 ČSÚ age-band rows in `children_by_age_mc_year.csv`
- `memory/raw/demographics/csu/Casova_rada_MC.xlsx` (sheets 2004..2025, row "Živě narození / Live births") — for all 132 rows in `births_by_mc_year.csv`
