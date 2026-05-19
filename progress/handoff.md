# Handoff — 2026-05-19 (session 3)

Updated in-session as work progressed. **This supersedes session 2** (whose loose-ends list was already partially stale; session-2 hard-won facts are preserved below in §"Hard-won facts from session 2"). Session 1 facts remain in force (§"Session-1 hard-won facts").

Read this file **first** when picking up the project. Everything else is referenced from here.

## TL;DR

- **WP-01, WP-02, WP-03, WP-04 are done. Only WP-05 (synthesis) remains.**
  - WP-01 (demographics): 6 MČ × age-band × year + birth cohorts 2004–2025.
  - WP-02 (school inventory): 93 ZŠ in `zs_by_mc.csv`, 100 % kapacita populated.
  - **WP-03 (enrolment): done via fallback B′** (MŠMT statistical yearbook at `statis.msmt.gov.cz/rocenka/`). **Granularity ceiling is kraj** (NUTS-3) — Hlavní město Praha is one row per table. Per-school and per-MČ enrolment is structurally unpublished, confirmed across NKOD + StatIS UI + statis.msmt.gov.cz/rocenka/. The output is **1 450 long-format rows** in `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` covering 3 tables (C1.25.1 zápis, C1.22.1 1st-grade-intake×age, C1.4.1 žáci×ročník) × 13–15 school years each.
  - WP-04 (catchment): **1 953 rows** in `memory/aggregated/catchment/streets_to_zs.csv`, all 6 MČs, citywide Vyhláška č. 19/2025 hl. m. Prahy as primary source.
- **WP-05 (synthesis) is fully unblocked.** It now has both an IPR P.3.04 sanity-check anchor AND a Praha-wide MŠMT historical calibration anchor (zápis-from-spádový-obvod ratio over ~15 years).
- **All session-2 "loose ends" resolved.** Of the 6 listed there: 3 were already done at session-2 close (R-06 had been appended; sources.md catchment section was present; no hidden `.claude/` subdir existed) and 3 were knocked out in session 3 (Pyright clean across all 3 parsers; `.gitignore` added; `memory/raw/_scratch/` deleted — its recon findings are absorbed into `progress/WP-03-enrolment.md` + `memory/sources.md` dead-end entries).

## What's on disk

### Aggregated outputs (the actual data)

| File | Rows | What it has |
|---|---|---|
| `memory/aggregated/demographics/children_by_age_mc_year.csv` | 372 | 6 MČ × 5-year age bands × 2011–2025 (ČSÚ) + 6 MČ × MŠ/ZŠ-bands × 2024 (IPR). |
| `memory/aggregated/demographics/births_by_mc_year.csv` | 132 | 6 MČ × **live births** 2004–2025. **Project's primary cohort primitive.** |
| `memory/aggregated/demographics/mc_total_population_ipr_2024_2050.csv` | 66 | 6 MČ × {2023 stav, 2030 × 5 IPR variants, 2050 × 5 variants}. |
| `memory/aggregated/schools/zs_by_mc.csv` | 93 | All ZŠ in MČ 3/7/8/9/10/14: RED-IZO, IZO, address, zřizovatel, type, **kapacita_registered** (100 % populated), snapshot 2025-10-31. |
| `memory/aggregated/catchment/streets_to_zs.csv` | **1 953** | (mc, street, house_number_range, red_izo, zs_name, source_file, effective_date) for the 2026-01-01-effective Vyhláška 19/2025 hl. m. Prahy. |
| `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` | **1 450** | Long-format: (school_year, school_year_ord, table_code, table_topic, indicator, value, source_url, snapshot_fetched_at) for Hlavní město Praha kraj, 3 tables × 13–15 yrs. **NEW from session 3.** |

Each aggregated file has a `_README.md` next to it with schema and coverage. `memory/aggregated/catchment/` also has `_anomalies.md` (1 genuine miss: ZŠ V Olšinách RED-IZO 691019061, plus 5 expected exclusions — hospital schools and logopedická schools). `memory/aggregated/enrolment/_README.md` documents coverage gaps for older school years where the table-code schema differs (HTTP 500 on rck=1..5 for some tables).

### Raw inputs (re-fetchable from R-XX recipes)

- `memory/raw/demographics/ipr/` — two IPR Prognóza 2024–2050 PDFs (~36 MB).
- `memory/raw/demographics/csu/` — two ČSÚ XLSX (~1.5 MB).
- `memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld` — MŠMT bulk registry (30 MB).
- `memory/raw/catchment/` — **6 files, 1.27 MB total** (session 2 addition):
  - 4 per-MČ excerpts: `p3_skolske-obvody-2026.pdf`, `p7_OZV-skolske-obvody-2025.pdf`, `p9_spadova-vyhlaska-1.1.2026.docx`, `vyhlaska-19-2025_via-P14.pdf`.
  - 1 citywide DOCX for context: `p9_HMP-vyhlaska-1.1.2026.docx`.
  - 1 citywide PDF (**WP-04's primary source**): `vyhlaska-hmp-19-2025_via-P6.pdf` (640 KB). Mirrors of the same Vyhláška č. 19/2025 hl. m. Prahy from praha14.cz, praha6.cz, praha7.cz, praha9.cz, praha3.cz respectively. R-06 recipe owes the next agent.
- `memory/raw/enrolment/statis_msmt/` — **session 3.** 40 cached HTML pages (UTF-8 transcoded from windows-1250), one per (table_code, school_year). Recipe R-07 regenerates these idempotently.

### Source code

- `notebooks/parse_csu_wp01.py` — WP-01 ČSÚ XLSX parser. Pyright-clean as of session 3.
- `notebooks/wp02_parse/parse.py` — WP-02 parser (and `verify.py`).
- `notebooks/wp03_parse/fetch_statis.py` + `pyproject.toml` — **NEW from session 3.** WP-03 fetcher+parser. Stdlib-only (no extra deps). Single sandbox-disabled Bash invocation runs all 60+ POSTs in ~30 s with `time.sleep(0.5)` pacing. Pyright-clean.
- `notebooks/wp04_parse/parse.py` + `pyproject.toml` — WP-04 parser. Reproducibility: `uv run python parse.py` regenerates `streets_to_zs.csv` from `memory/raw/catchment/`. Pyright-clean as of session 3 — a `start_section` refactor was needed to break Pyright's incorrect nonlocal-narrowing on `current`.

## Hard-won facts from **session 3**

1. **The sandbox leaves /dev/null character devices in the project root.** When a sandboxed process attempts to read user dotfiles (`~/.bashrc`, `~/.gitconfig`, `~/.mcp.json`, `~/.idea/`, etc.), the harness creates bind-mount stubs as character devices (major 1 minor 3, owned by `nobody:nogroup`, permissions 666) at those paths in the current working directory. They appear in `git status` as untracked files but cannot be deleted by the project user. **`.gitignore` now silences them.** Future agents: don't be alarmed; never try to `rm` them.

2. **MŠMT yearbook (`statis.msmt.gov.cz/rocenka/`) caps at NUTS-3 (kraj).** Every table whose title says "podle území" reports kraj-level data. Hlavní město Praha is one row. No table at any URL on this host exposes per-MČ, per-obec, or per-school breakdowns. Confirmed against tables C1.1, C1.4.1, C1.22.1, C1.25.1, C1.28.1 in chapter C (Základní vzdělávání). The matrika data exists per-school centrally but is treated as personal-data-adjacent and only published after aggregation to kraj. **Do not re-probe expecting different results.**

3. **Pyright nonlocal-narrowing is unreliable.** `start_section()` in `notebooks/wp04_parse/parse.py` mutated `current` via `nonlocal`; Pyright didn't track the mutation and reported the post-call code as unreachable. Workaround: have such helpers also *return* the new value and assign at the call site (Pyright trusts an explicit assignment over a closure-mediated `nonlocal`).

4. **`statis.msmt.gov.cz` is NOT in `.claude/settings.json`.** Each `Bash(dangerouslyDisableSandbox: true)` call triggers a user prompt. **Bundle multi-step fetches into one Python script + one Bash call** — never loop curls. R-07's recipe enforces this.

## Hard-won facts from **session 2** (in addition to §"Session-1 hard-won facts" below)

1. **MŠMT does NOT publish per-school enrolment as open data.** This is structural, not a fetching failure. Evidence: SPARQL across 100 MŠMT-published NKOD datasets yields the registry, ~80 `číselníky` (lookup tables for the central matrika fields), 2 aggregate datasets, 1 podnět (formal request for ZŠ→SŠ admission data, not yet fulfilled), and nothing per-pupil/per-school. The matrika records exist centrally but are treated as personal-data-adjacent. **Do not re-run the SPARQL search expecting different results.**

2. **`data.msmt.cz` (MŠMT's old LKOD) is decommissioned.** It returns a 258-byte meta-refresh page redirecting to NKOD (`data.gov.cz`) filtered by MŠMT's IČO `00022985`. Stop looking there.

3. **NKOD SPARQL endpoint works from this environment.** `https://data.gov.cz/sparql` accepts standard SPARQL via `curl -G --data-urlencode "query@file.rq" -H 'Accept: application/sparql-results+json'` with `dangerouslyDisableSandbox: true` (data.gov.cz is not in `.claude/settings.json`). The MŠMT publisher IRI for the filter is `https://rpp-opendata.egon.gov.cz/odrpp/zdroj/orgán-veřejné-moci/00022985` — REGEX on `00022985` is sufficient.

4. **`statis.msmt.cz` is a login wall.** Public-facing replacement is **`statis.msmt.gov.cz/rocenka/`** ("Statistiky regionálního školství" — MŠMT's annual yearbook UI). **Not yet probed in this session — interrupted by user before fetch.** This is the single most promising remaining WP-03 lead.

5. **WP-04 source-of-truth was clarified.** The previous handoff said "each MČ publishes its own OZV"; that's wrong. The legal authority is the **citywide** Vyhláška č. 19/2025 hl. m. Prahy (base eff. 2025-04-01, amended 11. 12. 2025 eff. **2026-01-01** — the 2026 amendment is what binds the April 2027 zápis, which is the 2021 birth cohort's entry). Each MČ mirrors its own annex of the streets list, but the binding text is one citywide PDF. Praha 6 (not in our scope) hosts the cleanest mirror of the full citywide PDF; we used that as the primary source. **Reproducibility lesson:** for any future spádový lookup, fetch the citywide vyhláška once rather than 6 MČ mirrors.

6. **Czech `.gov.cz` migration is now universal** (was ~75 % in session 1). Both `msmt.cz` → `msmt.gov.cz` and the previously-noted `czso.cz` → `csu.gov.cz` redirect. `.cz` legacy hostnames mostly still work (302) but the canonical addresses are `.gov.cz`. The project `.claude/settings.json` allowlists the `.cz` versions only; new domains (`msmt.gov.cz`, `statis.msmt.gov.cz`, `sbirkapp.gov.cz`, `praha.eu`, `data.gov.cz`) are reachable only via `dangerouslyDisableSandbox: true` Bash curl, which prompts the user each call. **User's explicit preference (this session): ask each time, don't bulk-update the allowlist.** Honor that.

7. **Vyhláška 19/2025 has special-ed exclusions baked in.** The 5 `zs_specialni` rows in `zs_by_mc.csv` are correctly **NOT** in `streets_to_zs.csv`. Additional ~5 schools are excluded because they're hospital schools (Bulovka, Bohnice, Nemocnice Na Františku) or logopedická schools that admit by diagnosis. **WP-05 should exclude these by joining `streets_to_zs.csv` ⨝ `zs_by_mc.csv` and ignoring `zs_by_mc.csv` rows that don't appear in the catchment table.** Only 1 genuine miss flagged: ZŠ V Olšinách RED-IZO 691019061 (recently opened — not yet in the decree).

## Session-1 hard-won facts (preserved from previous handoff — still in force)

1. **Subagent WebFetch is locked even when project `.claude/settings.json` allows it.** The harness ignores project-level allowlists for spawned subagents. The pattern stays: orchestrator fetches via WebFetch (or Bash `curl` with `dangerouslyDisableSandbox: true`), saves to `memory/raw/`, then dispatches a parse-only subagent.
2. **ČSÚ rebranded.** `czso.cz` → `csu.gov.cz`. (See session-2 fact 6 for the broader pattern.)
3. **MŠMT rejstřík has moved.** Old `rejstriky.msmt.cz/rejskol/` is dead; new UI `isv.gov.cz/rssz/` is a useless SPA. **Use the NKOD JSON-LD bulk dump** (R-05).
4. **Single-year-of-age × MČ is not in public ČSÚ.** ČSÚ ships only 5-year bands publicly. Single-year exists on the `uap.iprpraha.cz/pov` dashboard — blocked from this environment. For the project's actual question (2021/2024 cohort admission chances), single-year-of-age is **not needed**: `births_by_mc_year.csv` keys directly on birth year.
5. **"Praha N" is ambiguous in Czech datasets.** `MČ Praha 9` (KOD_ZUJ 500208) ≠ `obvod Praha 9` (includes parts of P14, P18, P19, P20, P21). ČSÚ uses MČ; MŠMT's `cisloObvoduPrahy` field uses obvod and is NOT a valid MČ filter. The WP-02 parser uses a hand-built `CAST_PSC_TO_MC` lookup.
6. **Czech historical names linger.** "ZŠ Praha 9 - Lehovec" (RED-IZO 600040585) is actually in MČ Praha 14. The WP-04 parser preserved this — joined by RED-IZO, not by name. Verified in `streets_to_zs.csv`.
7. **5 special-ed ZŠ are in `zs_by_mc.csv`** — flagged `zs_specialni` in `notes`. They are NOT spádové and were correctly excluded by the WP-04 parser.

## What WP-05 should look like next session

### WP-05 — synthesis (the actual deliverable)

For each ZŠ:
1. Pull `kapacita_registered` from `zs_by_mc.csv`.
2. Pull the spádová cohort: from `births_by_mc_year.csv` take MČ × (entry_year − 6), then prorate by the school's catchment share within the MČ from `streets_to_zs.csv` (count of streets bound to this RED-IZO ÷ count of streets in this MČ — or, better, weight by population density per street if the IPR ZSJ-level data can be lifted).
3. **Pressure ratio** = expected entrants ÷ annual entry capacity (typically `kapacita_registered / 9`).
4. Output: one row per (ZŠ, entry_year ∈ {2027, 2030}) with `pressure`, `chance_estimate`, uncertainty band.

Deliverables in `findings/`:
- `findings/pressure_per_school.csv`
- `findings/chance_estimate_2021_cohort.md` and `_2024_cohort.md`
- `findings/sanity_checks.md` — comparison vs IPR Příloha P.3.04 (already in `memory/raw/demographics/ipr/`)

**Catchment-share weighting nuance:** simple street-count weighting is wrong (some streets have 1 building, others have 50). The defensible v1 is **uniform weighting** with a documented caveat; v2 would join `streets_to_zs.csv` against IPR's ZSJ population grid. v1 is enough for the first pass.

**WP-03 calibration anchor for WP-05:** the new `hmp_msmt_yearbook_2005_2025.csv` lets you back out a Praha-wide systematic-error multiplier. For each year y, MŠMT reports `zápis_celkem(Praha, y)` and `z_vlastního_spádu(Praha, y)`. Roll up the per-MČ WP-05 prediction to Praha-wide and compare. A persistent gap → fixable bias in the catchment-share assumption.

## How to actually start the next session

1. Read `CLAUDE.md` then this `handoff.md`.
2. Read `RERUN.md` to internalise the recipe template. R-01 through R-07 are all present and last-verified 2026-05-18/19.
3. **Do not re-do WP-01, WP-02, WP-03, or WP-04.** Their outputs are in `memory/aggregated/` and validated.
4. **WP-05 only.** Per the WP-05 section above: produce `findings/pressure_per_school.csv` and the two cohort write-ups, with Praha-wide sanity check against IPR P.3.04 and the MŠMT yearbook anchor.

## Project context invariants (do not re-derive)

- Birth cohorts of interest: **2021** (enters ZŠ in 2027) and **2024** (enters ZŠ in 2030).
- Districts of interest: **MČ Praha 3, 7, 8, 9, 10, 14**.
- Source quality discipline: every number in `findings/` must trace to a Tier-A `sources.md` entry.
- One subagent per task. Orchestrator owns network I/O.
- User preference (set this session): **ask per-domain rather than bulk-updating the WebFetch allowlist.** Honor.
