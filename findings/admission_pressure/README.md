# School admission direction — deliverables (frozen)

These outputs answer the original project question: **for the 2021 and 2024 birth cohorts, what is the per-school admission pressure across the six Prague districts (P3, P7, P8, P9, P10, P14)?**

This direction is closed. The project has moved on to the **school quality comparison** direction — detailed quality analysis on a six-school shortlist (see `../school_quality/scope.md`).

## Files

| File | What it is |
|---|---|
| `chance_estimate_2021_cohort.md` | Narrative + per-MČ tables for the 2021 birth cohort (entering ZŠ in 2027). |
| `chance_estimate_2024_cohort.md` | Same, for the 2024 birth cohort (entering ZŠ in 2030). |
| `pressure_per_school.csv` | 114 rows = 57 schools × 2 cohorts. Nominal + corrected pressure with one-at-a-time ±10 % sensitivity. |
| `external_flow_history.csv` | Five-year average zápis-to-spádový-obvod ratio (0.5777) used as the external-flow correction. |
| `sanity_checks.md` | Cross-checks against IPR P.3.04 and MŠMT historical yearbook anchors. |

## Known caveat — upstream join bug

These files were generated against the **WP-04 catchment CSV before the V Olšinách join fix** (documented in `progress/handoff.md` session-3 closeout). The bug is in Prague 10, not in the Phase-2 target districts (Praha 9 and Praha 14), so it does not affect any Phase-2 decisions — but if any of these tables is ever re-read for a P10 question, re-run `notebooks/wp05_synthesis/synthesize.py` against the corrected upstream CSV first.

## Provenance

All numbers trace to Tier A sources via `memory/sources.md`. Generation script: `notebooks/wp05_synthesis/synthesize.py` (stdlib only). Modelling decisions and parameter choices: `progress/handoff.md` § "WP-05 modeling decisions signed off by the user".
