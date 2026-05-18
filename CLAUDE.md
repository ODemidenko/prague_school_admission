# Prague School Capacity Research

## Goal

Estimate the chance that a child born in **2021** or **2024** gets into each elementary school in the Prague districts of interest: **Prague 3, 7, 8, 9, 10, 14**.

Building blocks:

1. **Cohort dynamics.** Number of children of each age, for whole Prague and per district, year by year — historical and projected.
2. **School capacity dynamics.** Places available per age per year — ideally per school, otherwise per district.
3. **Pressure metric.** Cohort size ÷ available places, sliced by district and cohort year.

The natural primary key of this project is **birth year**, not "age in year X". The 2021 cohort enters ZŠ in 2027; the 2024 cohort in 2030. Today's enrolment is only useful as a baseline for projecting forward.

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
notebooks/           ← uv-managed Python, only created when code is needed
pyproject.toml       ← created lazily on first code task
.claude/settings.json← per-project permissions (allowlisted WebFetch domains)
```

**Two separate logs, two separate purposes:**

- `memory/sources.md` is the **exhaustive** log: every source touched, including dead ends with the reason. It serves the original build, audits, and forensic questions.
- `RERUN.md` is the **curated** log: only fruitful steps, written as concrete recipes. It serves future-you (or a fresh agent) refreshing the analysis in 6–36 months without conversation context.

`raw/` is append-only. Anything derived from it goes into `aggregated/` with a note pointing back to its source.

## Work packages

The initial decomposition. Update `progress/master-plan.md` as the picture clarifies — do not treat this list as frozen.

| ID    | Title                  | Depends on | Notes                                                                                                            |
|-------|------------------------|------------|------------------------------------------------------------------------------------------------------------------|
| WP-01 | Demographics           | —          | Children counts by age × district × year. ČSÚ historical + IPR Praha projection.                                 |
| WP-02 | School inventory       | —          | List of ZŠ (and MŠ) per district, registered capacity, address, type. MŠMT rejstřík škol + MČ pages.            |
| WP-03 | Enrolment series       | WP-02      | Actual enrolled children per school per year. Výroční zprávy, MŠMT yearbooks. Likely sparse — note gaps.        |
| WP-04 | Catchment (spádovky)   | WP-02      | Spádové obvody per MČ. These are legal bindings: a child has a right to a place in their spádová ZŠ.            |
| WP-05 | Synthesis              | 01–04      | Pressure metric per school × admission-chance estimate for 2021/2024 cohorts. Lives under `findings/`.          |

Run WP-01 and WP-02 in parallel first. WP-04 can start as soon as WP-02 has a school list per MČ.

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

- **Tier A** — ČSÚ, MŠMT, IPR Praha, individual MČ official statistical tables, official decrees on spádové obvody.
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

## Constitution clause

This file is the project's constitution. If a section stops being useful, rewrite it — don't fight it. Update the work-package table and the directory layout as the picture clarifies. The only invariants are the three user-set requirements:

1. We can always trace what was tried and what came back.
2. Reusable knowledge lives on disk, not in chat.
3. One task → one subagent. Main agent orchestrates.
