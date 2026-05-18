# Handoff — 2026-05-18

Written by the outgoing orchestrator at the 50% context threshold. Read this **first** when picking up the project; everything else is referenced from here.

## TL;DR

- WP-01 (demographics) and WP-02 (school inventory) are **done**.
- WP-03 (enrolment), WP-04 (catchment), WP-05 (synthesis) are still **todo**.
- Key architecture: **main agent fetches over the network, subagents parse local files.** Subagents do not inherit project-level WebFetch allowlist — this was the hardest lesson of the original run.
- 5 fruitful recipes (R-01 … R-05) are in `RERUN.md` with verification anchors. Future re-runs use those, not this handoff.

## What's on disk

### Aggregated outputs (the actual data)

| File | Rows | What it has |
|---|---|---|
| `memory/aggregated/demographics/children_by_age_mc_year.csv` | 372 | 6 MČ × **5-year age bands** × 2011–2025 (ČSÚ) + 6 MČ × MŠ-band/ZŠ-band × 2024 (IPR). **Not single-year-of-age** — public ČSÚ only ships bands. |
| `memory/aggregated/demographics/births_by_mc_year.csv` | 132 | 6 MČ × **live births** 2004–2025. **This is the project's primary cohort primitive** — each row is one birth cohort. |
| `memory/aggregated/demographics/mc_total_population_ipr_2024_2050.csv` | 66 | 6 MČ × {2023 stav, 2030 × 5 IPR variants, 2050 × 5 variants}. |
| `memory/aggregated/schools/zs_by_mc.csv` | 93 | All ZŠ in MČ 3/7/8/9/10/14: RED-IZO, IZO, address, zřizovatel, type, **kapacita_registered** (100% populated), snapshot 2025-10-31. |

Each aggregated file has a `_README.md` next to it with the schema and coverage matrix.

### Raw inputs (re-fetchable from R-XX recipes)

- `memory/raw/demographics/ipr/` — two IPR Prognóza 2024–2050 PDFs (~36 MB).
- `memory/raw/demographics/csu/` — two ČSÚ XLSX (~1.5 MB).
- `memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld` — MŠMT bulk registry (30 MB).

## Hard-won facts the next orchestrator must know

1. **Subagent WebFetch is locked even when project `.claude/settings.json` allows it.** The harness ignores project-level allowlists for spawned subagents. Three rounds of WP-01/WP-02 were wasted before pivoting to: orchestrator fetches via WebFetch (or Bash `curl` with `dangerouslyDisableSandbox: true`, which prompts the user once per command), saves to `memory/raw/`, then dispatches a parse-only subagent. **Default to this pattern for WP-03 and WP-04.**

2. **ČSÚ rebranded.** `czso.cz` → `csu.gov.cz`. The old domain 302-redirects but the new domain is canonical. WebFetch follows redirects but reports them.

3. **MŠMT rejstřík has moved.** Old: `rejstriky.msmt.cz/rejskol/` (dead). New UI: `isv.gov.cz/rssz/` (SPA, useless to WebFetch). **Use the NKOD JSON-LD bulk dump instead** (see R-05). NKOD URL: `https://data.gov.cz/dataset?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2F00022985%2F8e4bab9c3d258b0850c9f43080ba78e5`.

4. **Single-year-of-age × MČ is not in public ČSÚ.** ČSÚ ships only 5-year bands publicly. Single-year exists on the IPR `uap.iprpraha.cz/pov` dashboard — blocked from this environment. For the project's actual question (2021/2024 cohort admission chances), single-year-of-age is **not needed**: `births_by_mc_year.csv` keys directly on birth year.

5. **"Praha N" is ambiguous in Czech datasets.** `MČ Praha 9` (the small district, KOD_ZUJ 500208) ≠ `obvod Praha 9` (the larger administrative obvod that also includes parts of P14, P18, P19, P20, P21). ČSÚ usually uses MČ; MŠMT's `cisloObvoduPrahy` field uses obvod and is NOT a valid MČ filter. The WP-02 parser recovered MČ from `(castObce, psc)` via a hand-built lookup — see `notebooks/wp02_parse/parse.py` if extending.

6. **Czech historical names linger.** "ZŠ Praha 9 - Lehovec" is actually in MČ Praha 14. Always cross-check by PSČ + zřizovatel.

7. **5 special-ed ZŠ (`zs_specialni`) are in the data** — flagged in `zs_by_mc.csv` `notes`. They are **not spádové** and should be excluded from the admission-chance computation in WP-05.

## What WP-03 / WP-04 / WP-05 should look like

### WP-03 — Enrolment series

**Goal:** per-school, per-year, enrolled child counts (and ideally per-grade).

**Likely sources:**
- **NKOD / MŠMT open data** — search `data.gov.cz` for "výkonové ukazatele" / "výroční zpráva" / "statistický výkaz S 3-01" (ZŠ statistical return). The annual S 3-01 forms ARE collected centrally and may be on NKOD — main agent should fetch the catalogue first.
- **MŠMT statistical yearbooks** at `data.msmt.cz`.
- **Per-school výroční zprávy** as fallback (variable PDF format — last resort).

**Dispatch shape:** main agent fetches the NKOD catalogue for "výkaz" / "výkonové ukazatele". Identify the latest bulk dump. Curl it. Subagent parses and joins to `zs_by_mc.csv` via IZO (the IZO is the per-obor identifier MŠMT uses in enrolment data, NOT RED-IZO — the WP-02 parser captured both).

### WP-04 — Catchment (spádové obvody)

**Goal:** for each of MČ 3/7/8/9/10/14, the binding decree (`obecně závazná vyhláška`) mapping street addresses to ZŠ.

**Sources:** each MČ publishes its own OZV. Browse MČ websites at `www.praha{3,7,8,9,10,14}.cz`. The decree is usually a PDF attached to the school-information page.

**Dispatch shape:** main agent does six WebFetches (one per MČ "Školství" page) to find each decree's PDF URL. Curl them. Dispatch one parse-only subagent that reads the six PDFs and builds `memory/aggregated/catchment/streets_to_zs.csv` (columns: `mc, street, house_number_range, red_izo`).

**Risk:** PDF formats vary wildly per MČ. Some publish structured tables; some publish prose. May need per-MČ parsing logic. Budget one full subagent per MČ if the unified parser fails.

### WP-05 — Synthesis (the actual deliverable)

For each ZŠ:
1. Pull `kapacita_registered` from `zs_by_mc.csv`.
2. Pull the spádová cohort: from `births_by_mc_year.csv`, take the MČ × (entry_year − 6) cell, then prorate by the school's catchment share within the MČ from WP-04.
3. **Pressure ratio** = expected entrants / annual entry capacity (typically capacity / 9 years).
4. Output: one row per (ZŠ, entry_year ∈ {2027, 2030}) with `pressure`, `chance_estimate`, and the uncertainty band.

Deliverables go in `findings/`:
- `findings/pressure_per_school.csv`
- `findings/chance_estimate_2021_cohort.md` and `_2024_cohort.md` — narrative writeups for each cohort.
- `findings/sanity_checks.md` — comparison vs IPR's published capacity deficit (Příloha P.3.04, captured in R-02 raw PDF).

## Loose ends to clean up

These are not blocking, but the next agent should knock them out early:

1. **Throwaway exploration scripts** — `notebooks/explore4.py`, `notebooks/explore5.py` (and possibly `explore1.py`–`explore3.py`) were the WP-01 parser's scaffolding. They produce Pyright warnings. Delete.
2. **Pyright noise in `notebooks/parse_csu_wp01.py`** — openpyxl `cell.value` has a wide union return type. Add `# type: ignore[arg-type]` on the int conversions, or wrap with `int(str(cell.value))`. Output is correct; only the type-checker is unhappy.
3. **`memory/raw/` deserves an `_index.md`** at its top level pointing to each subfolder's `_origin.md`. Small organisational debt.
4. **`memory/sources.md`** has redundant entries from rounds 1–3 (some "not verified live in this session"). Prune. The verified entries from rounds 4 are the ground truth.

## How to actually start the next session

1. Read `CLAUDE.md` then this `handoff.md`.
2. Read `RERUN.md` to internalise the recipe template.
3. **Do not re-do WP-01 or WP-02.** Their outputs are in `memory/aggregated/` and validated.
4. Dispatch WP-03 first (NKOD enrolment dump). It mirrors WP-02's pattern almost exactly.
5. WP-04 in parallel if you have spare context — it's independent.
6. WP-05 last, when WP-03 + WP-04 outputs are on disk.

## Project context invariants (do not re-derive)

- Birth cohorts of interest: **2021** (enters ZŠ in 2027) and **2024** (enters ZŠ in 2030).
- Districts of interest: **MČ Praha 3, 7, 8, 9, 10, 14**.
- Source quality discipline: every number in `findings/` must trace to a Tier-A `sources.md` entry.
- One subagent per task. Orchestrator owns network I/O.
