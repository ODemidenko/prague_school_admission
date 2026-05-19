# WP-03 — Enrolment series

**Status:** **done via fallback B′** (MŠMT statistical yearbook, kraj-level
only). Per-school and per-MČ data remain structurally unavailable — the
recon documentation below is preserved for forensics.
**Last update:** 2026-05-19.

## Outcome — fallback B′

Pulled 20 school years (2005/2006 → 2025/2026 with one edition gap at
`rck='5a'`/2010/2011) × 3 yearbook tables × kraj **Hlavní město Praha**
(NUTS CZ010) into one long-format CSV at
`memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv`. **1 450
rows** on the 2026-05-19 snapshot. The three tables:

- **C1.25.1** — zápis: výsledky (total zápis attendees, zapsané, odklady,
  spádové-obvod breakdown from 2021/2022). 15 school years available.
- **C1.22.1** — 1. ročník nově přijatí podle věku (intake by age band).
  12 school years available (2014/2015 onward).
- **C1.4.1** — žáci v ročnících (pupils per grade). 13 school years
  available (2005/2006 one-off + 2014/2015 onward).

Source code: `notebooks/wp03_parse/fetch_statis.py` (stdlib-only, ≤300
lines). Re-run recipe: `RERUN.md` § R-07. Source catalogue entry:
`memory/sources.md → msmt-statis-rocenka-hmp` (Tier A).

### Granularity ceiling — the final decision

**Kraj-level only. Per-MČ and per-school enrolment are structurally
unavailable** and we are NOT pursuing them further. Evidence:

1. **NKOD recon (this file, below):** MŠMT publishes the registry,
   ~80 lookup-table číselníky, and 2 aggregate datasets; the matrika
   records are confidential.
2. **`statis.msmt.gov.cz/rocenka/` page-by-page audit:** every published
   table aggregates to NUTS-3 (kraj) or — at finest — `okres` for some
   D-chapter (střední) tables. The Praha kraj never decomposes to MČ
   level in any published yearbook table.
3. **Aggregator cross-check (mapaskol.cz, EDUin) reports kraj/okres
   totals only**, sourced from the same yearbook.

WP-05 will therefore use the kraj-level yearbook series as a **historical
context anchor** rather than a per-school validation. The pressure metric
remains driven by `births_by_mc_year.csv` × catchment share ÷
`kapacita_registered`; this fallback B′ data lets us sanity-check the
*kraj-wide* total against the per-school sum.

---

## Below: original recon (preserved for forensics)

## What the recon established

Per-school × per-year × per-grade pupil counts (the "S 3-01 / M 3 výkaz"
data) are **collected** by MŠMT centrally via the matrika (central pupil
registry) but **not published** at per-school granularity. The open data
publishes the registry structure and aggregates, but not the records.

### Evidence

1. **MŠMT's own LKOD at `data.msmt.cz` is decommissioned** — it
   meta-refreshes to the NKOD national catalogue (`data.gov.cz`), filtered
   by MŠMT's IČO `00022985`. TLS cert is expired, page body is empty.

2. **NKOD has exactly 100 MŠMT-published datasets** (full list cached at
   `memory/raw/_scratch/sparql_all_msmt.json`):
   - **~80 `Číselníky`** (lookup-table code lists for matrika fields —
     `RAFZ`, `RAPD`, `RAUD`, etc.). These define the *codes used in*
     per-pupil records, but the records themselves aren't published.
   - **~20 rejstřík škol** entries (the legal-entity school registry —
     this is what WP-02 used; no enrolment data).
   - **2 aggregate datasets**: "Počet ukrajinských dětí s dočasnou
     ochranou na českých školách" and "Organizace školního roku".
   - **1 podnět (request, NOT yet published)**: "Úspěšnost žáků ZŠ v
     přijímacím řízení na SŠ" — someone formally asked MŠMT to publish
     this; MŠMT has not. Same fence likely blocks per-school enrolment.

3. **MŠMT's "Otevřená data" page on `msmt.gov.cz`** publishes only the
   R13-01 ICT survey (school computer equipment), not the M 3 / S 3-01
   pupil-count výkaz.

### Unverified leads worth one more look (~30 min)

- **`statis.msmt.cz`** — MŠMT Statistical Information System (DSIA). Likely
  has per-school exports but behind a UI; check whether bulk download
  exists.
- **`dsia.msmt.cz/vystupy/region/`** — DSIA's regional output pages.
  Reference materials live here. May host CSV exports.
- **`https://www.czso.cz/csu/czso/skolstvi`** — ČSÚ also publishes school
  statistics. Likely aggregated, but worth checking for per-MČ ZŠ pupil
  counts as a partial substitute.

## Why WP-03 is not strictly blocking for WP-05

WP-05's primary deliverable is:

> pressure_ratio = expected_entrants(MČ, year) / annual_entry_capacity(school)

- `expected_entrants` ← `births_by_mc_year.csv` × catchment share (WP-04)
- `annual_entry_capacity` ← `kapacita_registered` ÷ 9 grades (from WP-02)

**Neither input requires WP-03.** WP-03 would have served as a
historical-pressure validation: comparing current `enrolment / capacity`
against the projected ratio. Without it, the synthesis still ships;
sanity-check is just weaker.

## Fallback options (pick one)

| Option | Effort | Granularity | Useful for sanity check? |
|---|---|---|---|
| **A. Skip WP-03; capacity-only WP-05** | zero | none | partial — IPR Příloha P.3.04 (already on disk) provides MČ-level capacity-deficit numbers to compare against |
| **B. MČ-level aggregate enrolment from ČSÚ / DSIA** | 1 subagent round | per-MČ × per-year | yes — lets us validate the per-MČ scaling |
| **C. Per-school výroční zprávy scrape** | 5–10 subagent rounds (variable PDFs across 93 schools) | per-school × per-year | yes — but expensive |
| **D. `statis.msmt.cz` deep dive** | 1 main-agent recon round | unknown until tried | unknown |

**Recommended:** A or B. C is disproportionate to the value-add for WP-05.
D is cheap enough to attempt before committing to A or B.

## On-disk artefacts

Session-2 recon scratch (NKOD SPARQL queries + the JS-rendered NKOD UI
snapshot) and session-3 StatIS root-page probes were deleted at the end of
session 3 once fallback B′ was committed to RERUN.md as R-07. The findings
they documented are now absorbed into this file and into the dead-end
entries in `memory/sources.md`. If a future re-run needs the raw recon
back, R-07's procedure plus the references in `sources.md` are sufficient
to reproduce it.
