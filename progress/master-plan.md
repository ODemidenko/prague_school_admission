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
| WP-03 | Enrolment series     | wip    | (recon)        | 2026-05-18  | Per-school per-year enrolled counts. **Pattern: main agent fetches MŠMT statistical yearbooks → subagent parses**. `data.gov.cz` is NOT in the WebFetch allowlist; using `data.msmt.cz` LKOD (MŠMT's own catalogue, which feeds NKOD) as the primary entry point. |
| WP-04 | Catchment (spádovky) | wip    | (recon)        | 2026-05-18  | Per-MČ decree (OZV) mapping addresses → ZŠ. Each MČ publishes its own; main agent must fetch each. Variable formats — likely PDF. Six MČ "Školství" pages allowlisted. |
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

## Restart marker

Last main-agent context check: 2026-05-18, after WP-01 + WP-02 parse passes returned.
**Handoff written:** `progress/handoff.md`. Next orchestrator should read it first.
