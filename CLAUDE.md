# Prague School Capacity Research

## Project status (2026-05-21)

This project has two directions, run sequentially:

1. **School admission** — original direction. Answered: for the 2021/2024 cohorts, what is the per-school admission pressure across Praha 3/7/8/9/10/14? **Closed and frozen** in `findings/admission_pressure/`.
2. **School quality comparison** — active direction. For a six-school shortlist (Praha 9 + Praha 14, 3 each), produce evidence-anchored quality assessments from public-data sources. Run in two stages:
   - **Stage 1** (faster, the immediate target): strictly standardised outcome comparison — ČŠI inspection reports, CERMAT entrance-exam results, 8-year-gymnázium acceptance flow.
   - **Stage 2** (deferred until Stage 1 lands a result): teacher qualification — aprobovanost, qualification splits between 1./2. stupeň, leadership tenure, teacher turnover.

The reason for two stages is that Stage-1 sources are *outcomes* (standardised, externally produced, comparable) and Stage-2 sources are *inputs* (per-school self-reported, harder to interpret). Doing Stage 1 first delivers the comparable signal fast; Stage 2 then adds context.

Read `findings/school_quality/learning_about_schools_data.md` for the feasibility reasoning that motivated this direction, and `findings/school_quality/scope.md` for the exact deliverable spec. Do not re-open the school-admission direction unless the user asks.

## School admission direction (closed)

Original goal: estimate the chance that a child born in **2021** or **2024** gets into each elementary school in the Prague districts of interest (Praha 3, 7, 8, 9, 10, 14). Decomposed into WP-01..WP-05. Deliverables in `findings/admission_pressure/`. Only retained obligation: the V Olšinách upstream-bug caveat documented in `findings/admission_pressure/README.md` — affects Praha 10 only, out of school-quality-comparison scope.

## School quality comparison direction (active)

For each of the **six target schools** below, compile an evidence-based quality assessment sufficient to answer the user's decision question: *is any non-spádová school in this shortlist materially better than the user's spádovka (Špitálská, Waltariho address), by enough to justify the cost of leaving it?*

The deliverable is one short, evidence-anchored note per school plus a cross-school comparison, all under `findings/school_quality/schools/`. The bracket the analysis aims to resolve is *clearly better / clearly worse / probably indistinguishable* — not a numeric ranking. See `findings/school_quality/scope.md` for the exact field set and stopping criteria.

### Target schools (six)

All six are state ZŠ. Identifiers from `memory/aggregated/schools/zs_by_mc.csv`. **District split is 3 + 3 between Praha 9 and Praha 14.** **`spitalska` is both the user's spádovka (resolved via Waltariho → Špitálská in `memory/aggregated/catchment/streets_to_zs.csv`) and one of the candidates** — it serves as the baseline against which the other five are bracketed.

| Short slug | Full name | MČ | Address | RED-IZO | IZO | Kapacita | Role |
|---|---|---|---|---|---|---|---|
| `novoborska` | Základní škola Novoborská | Praha 9 | Novoborská 371/10, Střížkov | 600040526 | 045245525 | 1150 | candidate |
| `elektra` | Základní škola a Mateřská škola Elektra, p. o. | Praha 9 | Sousedíkova 1044/8, Vysočany | 691017379 | 181142198 | 340 | candidate (qualitative only) |
| `spitalska` | Základní škola Špitálská | Praha 9 | Špitálská 789/4, Vysočany | 600040569 | 045243581 | 720 | **candidate + baseline** (user's spádovka, Waltariho) |
| `venclikova` | ZŠ Bří. Venclíků 1140 (Černý Most) | Praha 14 | Bratří Venclíků 1140/1, Černý Most | 600040496 | 102301841 | 810 | candidate |
| `janouska` | ZŠ Generála Janouška (Dygrýnova) | Praha 14 | Dygrýnova 1006/21, Černý Most | 600040577 | 102761451 | 800 | candidate |
| `chvaleticka` | ZŠ Chvaletická 918 (Lehovec) | Praha 14 | Chvaletická 918/3, Hloubětín | 600040585 | 045244570 | 868 | candidate |

**Elektra is a special case** — opened ~2023, so the standard pipeline will yield mostly empty cells (no full ČŠI cycle, no 5th-grade CERMAT cohort, no gymnázium-flow history, sparse teacher data). For Elektra, fall back to qualitative inputs (founding documents, declared pedagogical model, staff credentials, MČ Praha 9 council resolutions establishing the school). Do not synthesise pseudo-data.

The original primary key (**birth year**) still applies for any cohort framing — e.g. when interpreting gymnázium-flow percentages, a "5th-grade cohort 2030/31" is the 2020 birth cohort.

## Working principles

### 1 — Web research over code
Default to reading official tables and writing down what you found. Use code only when manual aggregation across many tables/years becomes the bottleneck — and then in a `uv`-managed Python project under `notebooks/`.

### 2 — Disk is the memory, conversation is the workspace
Anything that might be needed again — raw files, URLs, partial aggregations, source-quality notes — goes on disk. The main agent's conversation is for orchestration only, not for hoarding facts.

### 3 — Subagents do the heavy work
The main agent orchestrates. Searching, reading PDFs, extracting tables, writing summaries — all done by subagents with narrowly scoped prompts. The main agent reads short summaries, never raw data.

### 4 — Context budget
Main agent has a 1M token window. **When it reaches ~500K (50%), notify the user and recommend a restart**, after writing a handoff into `progress/handoff.md`. Subagents are cheap; the orchestrator is the precious resource.

## Directory layout

```
README.md            ← navigation hub (project root)
CLAUDE.md            ← this file (project constitution)
RERUN.md             ← curated re-run guide; one section per fruitful step
progress/            ← plans & tracking, owned by main agent
  master-plan.md     ← top-level work-package list + status
  WP-XX-<slug>.md    ← one file per work package, updated by its subagent
  handoff.md         ← restart-state snapshot when context nears the limit
memory/
  sources.md         ← full catalogue of data sources, including dead ends
  glossary.md        ← Czech terms, abbreviations, legal concepts
  raw/               ← downloaded PDFs, CSVs, HTML, screenshots — never rewritten
  aggregated/        ← cleaned tables (CSV/parquet), one subfolder per data type
findings/            ← final deliverables: plots, write-ups, the answer
  admission_pressure/← school admission direction outputs (frozen). See README.md inside.
  school_quality/    ← school quality comparison direction outputs.
    learning_about_schools_data.md  ← feasibility note that motivates this direction
    scope.md                        ← exact deliverable spec (Stage 1 + Stage 2)
    schools/<slug>.md               ← one note per target school (filled by WP-10, augmented by WP-11)
notebooks/           ← uv-managed Python, only created when code is needed
pyproject.toml       ← created lazily on first code task
.claude/settings.json← per-project permissions (allowlisted WebFetch domains)
```

**Two separate logs, two separate purposes:**

- `memory/sources.md` is the **exhaustive** log: every source touched, including dead ends with the reason. It serves the original build, audits, and forensic questions.
- `RERUN.md` is the **curated** log: only fruitful steps, written as concrete recipes. It serves future-you (or a fresh agent) refreshing the analysis in 6–36 months without conversation context.

`raw/` is append-only. Anything derived from it goes into `aggregated/` with a note pointing back to its source.

## Work packages

Authoritative status lives in `progress/master-plan.md`. The table below is the structural map.

### School admission direction (closed)

| ID    | Title                  | Status | Output location |
|-------|------------------------|--------|-----------------|
| WP-01 | Demographics           | done   | `memory/aggregated/demographics/` |
| WP-02 | School inventory       | done   | `memory/aggregated/schools/zs_by_mc.csv` |
| WP-03 | Enrolment series       | done (kraj-level, structural ceiling) | `memory/aggregated/enrolment/` |
| WP-04 | Catchment (spádovky)   | done (V Olšinách caveat — see handoff) | `memory/aggregated/catchment/streets_to_zs.csv` |
| WP-05 | Synthesis              | done   | `findings/admission_pressure/` |

### School quality comparison direction (active)

#### Stage 1 — standardised outcomes (the immediate target)

| ID    | Title                                          | Depends on | Goal |
|-------|------------------------------------------------|------------|------|
| WP-06 | Target-school identity verification             | —          | Pin current address, RED-IZO/IZO, ředitel(ka), výroční-zpráva URL pattern, official website per school. One-line freshness gate before any other school-quality work. |
| WP-07 | ČŠI inspection report extraction                | WP-06      | Per school: most recent inspection date, graded dimensions, key findings, red flags. Source: `csicr.cz` Inspekční zprávy. |
| WP-08 | CERMAT results — feasibility + extraction       | WP-06      | First confirm whether CERMAT publishes 5-letá (and 9-letá) jednotné přijímací zkoušky aggregated by school-of-origin in 2026. If yes, extract for the six schools. If no, document the dead end and stop. |
| WP-09 | 8-year-gymnázium acceptance flow                | WP-06      | Per school × year: number of 5th-graders accepted to víceleté gymnázium, divided by 5th-grade cohort size. Source order: výroční zprávy škol → MČ školský odbor reports → MŠMT aggregates. |
| WP-10 | Per-school synthesis + cross-school comparison  | WP-07..09  | One short note per school under `findings/school_quality/schools/<slug>.md`, then a single cross-school comparison in `findings/school_quality/comparison.md`. Bracket: clearly better / clearly worse / probably indistinguishable. |

WP-06 runs first and gates everything else. WP-07, WP-08, WP-09 then run in parallel (each is one focused subagent). WP-10 runs last and is the only WP that the main agent writes itself (the subagents produce the building-block notes; the main agent assembles the comparison so judgement is centralised).

#### Stage 2 — teacher qualification (deferred until Stage 1 lands)

| ID    | Title                                          | Depends on | Goal |
|-------|------------------------------------------------|------------|------|
| WP-11 | Teacher qualification extraction               | WP-06, WP-10 | Per school: aprobovanost % overall; split by 1. stupeň vs 2. stupeň where reported; foreign-language teacher qualifications; ředitel(ka) and zástupce tenure; year-over-year teacher arrivals/departures where reported. Source order: výroční zprávy (primary) → ČŠI reports (cross-check) → MŠMT P 1c-01 aggregates if school-of-origin available. After WP-11 lands, append a new §7 "Teacher qualification (Stage 2)" to each per-school file under `findings/school_quality/schools/`. Do not re-run WP-10 — only augment. |

**Do not start Stage 2 until Stage 1 has delivered the comparison.** Stage 2 is opt-in by the user; the orchestrator should wait for explicit go-ahead before dispatching WP-11.

#### Scope guardrails (both stages)

- Only the six target schools. No cross-Prague benchmarking, no city-wide rankings.
- Only the named source families per stage. Olympiads, Scio/Kalibro, media rankings, and parent forums are explicitly **out of scope** — re-read `learning_about_schools_data.md` if tempted.
- The deliverable answers a binary-ish decision (worth leaving the spádovka or not), not a ranking. Resist the temptation to score schools out of 10.

## Subagent contract

Every dispatch must contain:

- **Goal** — one sentence.
- **Scope** — what's in, what's explicitly out.
- **Inputs** — paths to relevant files in `memory/` and `progress/`.
- **Outputs**
  - Data files saved to `memory/raw/<source-slug>/...` or `memory/aggregated/<topic>/...` with explicit filenames.
  - Updates appended to the relevant `progress/WP-XX-...md` (what was done, what's still missing).
  - Every source touched logged in `memory/sources.md` — fruitful sources in their tier section, unreachable / unusable sources under "Dead ends" with the reason.
  - **For each fruitful step that actually produced data, append a new `## R-XX <slug>` section to `RERUN.md`** following its template. A step is "fruitful" if (a) it wrote to `memory/aggregated/` or `findings/`, (b) the source verified live, and (c) a fresh agent in 6 months could re-run it from the recipe alone. If any of those fail, do **not** add to `RERUN.md` — record the dead end in `sources.md` instead.
- **Report back** — ≤ 200 words. What was found, what's missing, what to try next, and which `R-XX` sections you appended to `RERUN.md`. No raw quotes, no PDF contents.

If a subagent needs to inspect more than ~3 documents, it should spawn its own subagents — context conservation cascades.

## Source quality discipline

Treat sources unequally and tag them in `memory/sources.md`:

- **Tier A** — ČSÚ, MŠMT, IPR Praha, individual MČ official statistical tables, official decrees on spádové obvody, ČŠI inspection reports, CERMAT publications, výroční zprávy on the school's own (.cz) domain.
- **Tier B** — established aggregators (mapaskol.cz, EDUin), news outlets citing Tier A.
- **Tier C** — parent forums, blogs, anecdotes. Use only for sanity checks and qualitative colour.

Every number that ends up in `findings/` must trace back to a Tier A source via `memory/sources.md`. No exceptions.

## Key Czech terms (full glossary in `memory/glossary.md`)

- **MŠ** — mateřská škola (kindergarten, ages ~3–6)
- **ZŠ** — základní škola (elementary, ages 6–15)
- **MČ** — městská část (city district, e.g. Praha 9)
- **spádová oblast / spádovka** — catchment area; a child is legally entitled to enrol in their spádová ZŠ
- **zápis** — enrolment registration, typically held in April
- **kapacita** — registered legal capacity (a ceiling, not actual current enrolment)
- **rejstřík škol** — official school registry maintained by MŠMT
- **aprobovanost** — share of teaching staff who hold the legally required qualification for the subject and stage they teach
- **víceleté gymnázium** — 8-year (also 6-year) gymnázium; selective secondary school children can enter from 5th (or 7th) grade
- **ČŠI** — Česká školní inspekce; the school inspectorate that produces standardised inspection reports
- **CERMAT** — Centrum pro zjišťování výsledků vzdělávání; runs the unified entrance-exam (jednotné přijímací zkoušky)
- **výroční zpráva** — mandatory annual report each ZŠ publishes; contains staffing, results, gymnázium placements

## Constitution clause

This file is the project's constitution. If a section stops being useful, rewrite it — don't fight it. Update the work-package table and the directory layout as the picture clarifies. The only invariants are the three user-set requirements:

1. We can always trace what was tried and what came back.
2. Reusable knowledge lives on disk, not in chat.
3. One task → one subagent. Main agent orchestrates.
