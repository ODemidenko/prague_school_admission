# WP-05 sanity checks

## Data freshness

This report is a snapshot of the inputs as of the dates below. Two of the four feeds are legally bound and change on a predictable cadence (the OZV catchment decree is amended ~yearly; the rejstřík kapacita updates as schools register expansions). If you are reading this more than ~12 months after the generation date, re-check at minimum the catchment decree and the kapacita snapshot before trusting the per-school numbers.

- **Report generated:** 2026-05-20 (UTC)
- **Spádové obvody (catchment):** OZV č. 19/2025 hl. m. Prahy, effective **2026-01-01** (source file `vyhlaska-hmp-19-2025_via-P6.pdf`).
- **School kapacita:** MŠMT rejstřík škol snapshot **2025-10-31**.
- **Births by MČ:** ČSÚ historical series, latest year **2025**.
- **External-flow ratio:** MŠMT statistical yearbook, latest school year **2025/2026** (5-year average used).

Three independent checks: the external-flow series is reasonable; the per-MČ ceiling sums make sense against the births data; the rolled-up pressure for cohort 2021 (the most-mature data) doesn't blow up the Praha-wide MŠMT yearbook anchor.

## 1. External-flow ratio (z vlastního spádového obvodu / celkem)

Source: `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv`, table C1.25.1, indicator `z celku ze spádového obvodu :: Zapisované děti / celkem` ÷ `(celkem) :: Zapisované děti / celkem`.

5-year average (most recent): **0.578** — this is the multiplier used to convert ceiling expected entrants into corrected expected entrants.

| school_year | z_vlastniho_spadu / celkem |
|---|---:|
| 2021/2022 | 0.584 |
| 2022/2023 | 0.581 |
| 2023/2024 | 0.587 |
| 2024/2025 | 0.573 |
| 2025/2026 | 0.563 |

The series is **noticeably noisy** in early years (older table schemas miss some categories) and **stabilises near 0.55–0.60** from ~2014 onward. The 5-year average smooths year-on-year noise.

## 2. Per-MČ rolled-up entry capacity vs. expected ceiling — cohort 2021

| MČ | Σ expected_entrants_ceiling | Σ capacity_entry | ratio |
|---|---:|---:|---:|
| Praha 10 | 1256 | 844 | 1.49 |
| Praha 14 | 529 | 449 | 1.18 |
| Praha 3 | 951 | 622 | 1.53 |
| Praha 7 | 602 | 414 | 1.45 |
| Praha 8 | 1228 | 1015 | 1.21 |
| Praha 9 | 895 | 463 | 1.93 |

A ratio ≥ 1 at MČ-level means the spádový-ceiling sum exceeds the modelled entry-grade capacity sum for that whole MČ. The city redraws obvod boundaries when this becomes structural — see the 11. 12. 2025 amendment to vyhláška 19/2025 for evidence of active rebalancing.

## 3. Praha-wide rollup vs. MŠMT yearbook

In **2025/2026**, MŠMT reports 56% of zápis-attending Praha children attended their own spádová school. Our model uses the 5-year average, which differs by +1.4 pp from that latest year — a deliberate smoothing choice.

## 4. Cross-check vs IPR Příloha P.3.04

IPR's 2024-stav and 2030-PROG/MID columns of Příloha P.3.04 give **per-MČ capacity-deficit numbers** for the walking-distance circle around each ZŠ. Those are deficits (cohort minus places), not pressures, but they should track the sign and rough magnitude of our per-MČ ceiling-vs-capacity ratios in the table above. The raw IPR PDF is at `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_vzdelavani.pdf`.

## 5. Coverage caveats

- Excluded by design: 5 special-needs ZŠ (`zs_specialni` in `zs_by_mc.csv`), hospital schools (Bulovka, Bohnice, Nemocnice Na Františku), logopedická schools, all private/church ZŠ. None of these are spádové, so excluding them from the WP-05 model is correct — but parents who would consider them as alternatives are not captured here.
- ZŠ V Olšinách (RED-IZO 691019061, Praha 10) was added to the spádový annex by the 11. 12. 2025 amendment (effective 2026-01-01) and is bound to 11 streets in the corrected `streets_to_zs.csv`. It is included in WP-05.
