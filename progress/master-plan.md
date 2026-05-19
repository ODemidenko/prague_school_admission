# Master plan

Single source of truth for what the project is doing and where each work package stands. Update after every subagent return.

## Status legend
- `todo` — not started
- `wip` — subagent dispatched or in progress
- `blocked` — needs upstream WP or user input
- `done` — outputs landed in `memory/aggregated/` or `findings/`, summary in WP file

## Work packages

| ID    | Title                | Status | Owner subagent | Last update | Notes |
|-------|----------------------|--------|----------------|-------------|-------|
| WP-01 | Demographics         | done   | (parse pass)   | 2026-05-18  | 372 rows in `children_by_age_mc_year.csv` (5-y bands only, 2011–2025) + 132 rows in `births_by_mc_year.csv` (2004–2025) + 66 cells in `mc_total_population_ipr_2024_2050.csv`. **Single-year-of-age unreachable** (only on blocked IPR dashboard). Recipes R-01–R-04. |
| WP-02 | School inventory     | done   | (parse pass)   | 2026-05-18  | 93 ZŠ in `zs_by_mc.csv`, all 6 MČs, 100% kapacita populated. Recipe R-05. |
| WP-03 | Enrolment series     | done   | (fallback B′)  | 2026-05-19  | **kraj-level only via MŠMT statis; per-MČ structurally unavailable.** 1 450 rows in `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` covering 3 tables (C1.25.1 zápis, C1.22.1 1.roč×věk, C1.4.1 žáci×ročník) × 20 school years 2005/06 → 2025/26 (with HTTP-500 gaps for the older years documented in the README). Recipe R-07. |
| WP-04 | Catchment (spádovky) | done¹  | (parse pass)   | 2026-05-18  | `memory/aggregated/catchment/streets_to_zs.csv` — **1 953 rows**, all 6 MČs covered, citywide Vyhláška č. 19/2025 hl. m. Prahy as primary source. Coverage 100 % for P3/P7/P9/P14; P8 = 78 %, P10 = 93 % (anomalies all justified — see `_anomalies.md`). Recipe R-06 **NOT YET APPENDED** to RERUN.md by the subagent — known loose end. |
| WP-05 | Synthesis            | todo   | —              | —           | For 2021 and 2024 birth cohorts, per-school admission-chance estimate using births × MČ ÷ capacity × MČ. |

## Dispatch order

1. Parallel: WP-01 (demographics) and WP-02 (school inventory).
2. After WP-02 lands a school list per MČ: WP-04 (catchment).
3. After WP-02: WP-03 (enrolment series) — uses the school list as its index.
4. WP-05 last.

## Open questions (resolve before WP-05)

- Is per-school capacity reliably published, or only per-MČ totals?
- Are spádové obvody addresses or street-level zones — what granularity does the user need?
- How far ahead does IPR Praha publish demographic projections? Through 2030?
- Are there private/church ZŠ in the districts of interest that compete for the same children?

¹ **WP-04 done with two open documentation gaps** — see `progress/handoff.md` loose ends.

## Restart marker

Last main-agent context check: **2026-05-18**, after WP-04 parser pass returned and WP-03 structural blocker was identified.
**Handoff rewritten:** `progress/handoff.md` (session-2 version). Next orchestrator should read it first.
