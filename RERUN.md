# Re-run guide

**Audience:** a Claude Code agent (or human operator) re-running this analysis 6–36 months after the original build, who has only the contents of this repository — no memory of the original conversation.

**Promise of this file:** every section below is a step that was *fruitful* on the original run. Dead-ends, exploratory queries, and "we tried this and it didn't work" entries are deliberately excluded — they live in `memory/sources.md → Dead ends`.

## How to use

1. Read `CLAUDE.md` first — it explains the project's structure and conventions.
2. Pick a mode:
   - **Full refresh** — run every section R-01 … R-NN below, in order. Each section is independent except where `Depends on` says otherwise. Estimated subagent count: one per section.
   - **Partial refresh** — pick a single WP (e.g. only demographics) and run only its sections.
3. Each section follows the same template (see below). After running a section, verify the **Expected output** matches what landed on disk. If the schema has drifted, update the section in place and add a short note in `## Schema drift log` at the bottom of this file.
4. Once all relevant sections are re-run, the analysis in `findings/` can be regenerated.

## Section template

Each `## R-XX <slug>` section contains:

- **WP** — which work package it belongs to.
- **Depends on** — earlier R-XX sections whose outputs feed this one.
- **Source URL** — canonical fetch URL or query.
- **Auth / access** — what permission rule in `.claude/settings.json` covers it.
- **Procedure** — exact steps a subagent should take (parameters, navigation path, parsing notes).
- **Expected output** — file path(s) and schema. If the file already exists, overwrite.
- **Verification** — how to confirm the output is correct (row count expectations, sanity checks).
- **Robustness notes** — what could break (URL rot, schema changes, login walls) and how to recognise it.
- **Last verified** — `YYYY-MM-DD` of the most recent successful run.

## Maintenance contract

Every subagent that completes a fruitful extraction step **must** append a new `## R-XX` section to this file, filled to the template, before reporting back. If a subagent's work was not fruitful (no data produced, source not usable), it must **not** write here — only to `memory/sources.md → Dead ends`.

When a section is re-run successfully against the same source, bump `Last verified`. When a section can no longer succeed at all (source dead), move it to `## Retired sections` at the bottom with the retirement date and reason, and add a replacement section if one exists.

---

## Working sections

### R-01 ipr-prognoza-2024-2050-obyvatelstvo

- **WP:** WP-01 (Demographics).
- **Depends on:** none.
- **Source URL:** `https://iprpraha.cz/assets/files/files/c2a6a24d6250739cf644c646eed3b77a.pdf` (asset URL on IPR's static host; surfaced from the listing page `https://iprpraha.cz/vybavenost`).
- **Auth / access:** Covered by `WebFetch(domain:iprpraha.cz)` in `.claude/settings.json`. No login. **Caveat for re-runs:** WebFetch returns "binary content" rather than text for any PDF >~1 MB — you must download with `curl -sL -o <path> <url>` first, then parse with `uv run --with pypdf --no-project python3 …`. Sandbox-writable scratch dir is `$TMPDIR` (not `/tmp`).
- **Procedure:**
  1. `curl -sL -o memory/raw/demographics/ipr/ipr_prognoza_2024-2050_uvod_a_obyvatelstvo.pdf https://iprpraha.cz/assets/files/files/c2a6a24d6250739cf644c646eed3b77a.pdf`
  2. Parse with pypdf: pages **38, 39, 40, 41** hold Příloha P.2.04 — the per-MČ × variant population matrix. Each row begins with the literal string `MČ Praha N ` followed by 11 integers (Czech-style thousands separator = space). The column order is fixed: `2023_stav, 2030_PROG, 2030_MAX+, 2030_MAX, 2030_MID, 2030_NUL, 2050_PROG, 2050_MAX+, 2050_MAX, 2050_MID, 2050_NUL`.
  3. Filter to the six in-scope rows (`MČ Praha 3 / 7 / 8 / 9 / 10 / 14`) and 11 columns → 66 cells.
  4. Write to `memory/aggregated/demographics/mc_total_population_ipr_2024_2050.csv` with columns `mc, mc_code, year, variant, population, source_slug, notes`.
- **Expected output:**
  - `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_uvod_a_obyvatelstvo.pdf` (~10.4 MB).
  - `memory/aggregated/demographics/mc_total_population_ipr_2024_2050.csv` (66 rows, 6 MČ × 11 cells).
- **Verification:**
  - Row count = 66 (`wc -l` ≥ 67 including header).
  - For Praha 3, 2023 stav = `80761` and 2050 PROG = `100147`.
  - The sum of BUC rows (e.g. `03_1` + `03_2` on p. 38) must equal the `MČ Praha 3` row total — sanity check against `80 761` and `100 147`.
- **Robustness notes:**
  - This is a one-shot 2024–2050 study (IPR publishes a fresh edition every 2–3 years). A 2025 or 2026 update will have a different asset hash. **Re-discover by re-fetching `https://iprpraha.cz/vybavenost` and parsing the "Prognóza obyvatel a veřejné vybavenosti" PDF list.**
  - The column order in Příloha P.2.04 has been stable since the 2022 edition; if the 2025 edition changes it, re-read the header row on page 38.
  - The MČ-row label is exactly `MČ Praha 3 ` (with trailing space) — robust to different MČ codings.
- **Last verified:** 2026-05-18.

### R-02 ipr-prognoza-2024-2050-vzdelavani

- **WP:** WP-01 (Demographics) primary; WP-02 (planned schools, Příloha P.3.05) and WP-05 (capacity-deficit headline) as bonus.
- **Depends on:** none.
- **Source URL:** `https://iprpraha.cz/assets/files/files/48480fbb0bfe91c363bdbfca1d658a6d.pdf` (asset URL on IPR; surfaced from `https://iprpraha.cz/vybavenost`).
- **Auth / access:** Same as R-01 — `WebFetch(domain:iprpraha.cz)` works; PDF too big for direct text extraction so use `curl` then pypdf.
- **Procedure:**
  1. `curl -sL -o memory/raw/demographics/ipr/ipr_prognoza_2024-2050_vzdelavani.pdf https://iprpraha.cz/assets/files/files/48480fbb0bfe91c363bdbfca1d658a6d.pdf`
  2. With pypdf:
     - **MŠ table (age 3–5)** — Příloha P.3.02 on pages **59, 60, 61, 62**. Rows starting with `MČ Praha N ` give: `<#MŠ_zřizovaných_MČ> <count_in_walking_distance> (<pct>%) <deficit_2024_stav> <deficit_2030_PROG> <2030_MAX+> <MAX> <MID> <NUL> <2050_PROG> <2050_MAX+> <MAX> <MID> <NUL>`.
     - **ZŠ table (age 6–14)** — Příloha P.3.04 on pages **63, 64, 65, 66**. Same row shape with walking-distance radius 800 m.
  3. Capture `count_in_walking_distance` + `pct` for the 2024 stav cell — these are the only cohort-related numbers in the table; everything else is capacity deficit (cohort − places). True cohort ≈ count / (pct/100).
  4. Write per-MČ rows for the 6 in-scope districts to `memory/aggregated/demographics/children_by_age_mc_year.csv`. Schema: `year, reference_date, mc, mc_code, age (empty), age_band_min, age_band_max, count, count_kind ("walking_distance_to_MŠ"|"walking_distance_to_ZŠ"), coverage_pct, source_slug, kind, notes`.
- **Expected output:**
  - `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_vzdelavani.pdf` (~25.9 MB).
  - `memory/aggregated/demographics/children_by_age_mc_year.csv` (12 rows: 6 MČ × 2 bands × 1 reference year 2024).
  - `memory/aggregated/demographics/_README.md` documenting the schema deviation (no single-year `age` column populated).
- **Verification:**
  - Row count = 12.
  - For Praha 3, MŠ band: count=1879, coverage=94. For Praha 3, ZŠ band: count=4778, coverage=96.
  - Sanity: `count / (coverage/100)` for Praha 3 ZŠ ≈ 4977; divided by MČ Praha 3 total (80761) ≈ 6.2% — plausible age-6–14 population share.
- **Robustness notes:**
  - The "count in walking distance" columns are NOT raw cohort counts. If a re-run agent reports the count as cohort, they are wrong — the coverage-pct correction is required.
  - Page numbers may shift across editions. The Příloha label (P.3.02 for MŠ, P.3.04 for ZŠ) is stable; if pypdf-by-page fails, search every page for the literal `Příloha P.3.02` / `Příloha P.3.04` heading.
  - The IPR dashboard at `uap.iprpraha.cz/pov` ↗ (referenced on p. 46) is the canonical source of single-year-of-age × MČ × year data, but was not reachable in the original run. If the harness can reach that host in a future run, prefer it over this PDF; this section becomes superseded.
- **Last verified:** 2026-05-18.

### R-03 csu-vekove-slozeni-mc-2011-2025

- **WP:** WP-01 (Demographics).
- **Depends on:** none.
- **Source URL:** Asset (as of 2026-05-18): `https://csu.gov.cz/docs/107839/afefbae8-c12f-7944-fe52-ce39f88da593/1_PHA_VEK_obyv_mc.xlsx?version=1.5`. Landing page (re-discovery start): `https://csu.gov.cz/csu/xa/casove-rady-za-mestske-casti-prahy`. Title to search for on the landing page: **"Věkové složení obyvatel v městských částech Prahy v letech 2011-2025"**.
- **Auth / access:** Main-agent `WebFetch(domain:csu.gov.cz)` works without prompt and was used to download. The sandboxed Bash for the subagent does NOT have `csu.gov.cz` in its network allowlist — if the subagent needs to re-fetch, it must do so with `Bash(dangerouslyDisableSandbox: true)` using `curl -fsSL -o <path> <url>`. **Domain note: ČSÚ rebranded from `czso.cz` to `csu.gov.cz` (302 redirect still works as of 2026-05-18); when the old domain disappears, only `csu.gov.cz` will resolve.**
- **Procedure:**
  1. Main agent: `WebFetch` the asset URL above (or re-discover from the landing page if `version` has bumped). Write to `memory/raw/demographics/csu/1_PHA_VEK_obyv_mc.xlsx`.
  2. Subagent: `uv run --with openpyxl --no-project python3 notebooks/parse_csu_wp01.py` — script already on disk; logic summarised below in case it needs to be re-derived.
     - Open workbook with `openpyxl, data_only=True, read_only=True`. Sheets named `'2011'..'2025'`.
     - Header row 4 (0-indexed 3) contains column names. Layout switches at sheet 2020: pre-2020 → name col = 3, KOD_ZUJ col = 2; from 2020 → name col = 1, KOD_ZUJ col = 0.
     - Take FIRST occurrence of band labels `'0-4'`, `'5-9'`, `'10-14'`, `'15-19'` (they recur in the Muži/Ženy blocks at cols 25.. and 45..). On every sheet they sit at cols 5,6,7,8.
     - Filter rows where name column ∈ {Praha 3, 7, 8, 9, 10, 14}.
     - Map MČ → IPR LAU-2 code (Praha 3=547107, 7=547141, 8=547158, 9=547166, 10=547174, 14=547221) for the CSV's `mc_code` column. Capture ČSÚ KOD_ZUJ in `notes`.
  3. **APPEND** to `memory/aggregated/demographics/children_by_age_mc_year.csv` — round-3 IPR rows must be preserved.
- **Expected output:**
  - `memory/raw/demographics/csu/1_PHA_VEK_obyv_mc.xlsx` (~379 KB, 15 sheets).
  - `+360` rows in `memory/aggregated/demographics/children_by_age_mc_year.csv` (6 MČ × 4 bands × 15 years). Total file row count after = 1 header + 12 IPR + 360 ČSÚ = 373 lines.
- **Verification:**
  - Total file row count = 373 lines (`wc -l`). Filtered by `source_slug=csu-vekove-slozeni-mc-2011-2025` = 360 rows.
  - **Praha 3, band 5-9, year 2020 = 3453.**
  - **Praha 8, band 0-4, year 2015 = 5611.**
  - **Praha 9, band 10-14, year 2024 = 3481.**
  - Praha 3 totals across the 4 in-scope bands for year 2024 = 4134+3817+3409+3962 = 15 322; divided by MČ Praha 3 total population 82 149 ≈ 18.7 % — plausible age-0–19 share for an urban MČ.
- **Robustness notes:**
  - **Asset hash + `version=1.5` will rotate** with every ČSÚ republication (annual). Always re-discover from the landing page; do not hardcode.
  - **`czso.cz` → `csu.gov.cz` migration** is the most fragile load-bearing assumption. If the asset 404s, try the old `czso.cz` host; if both fail, search for the file title on the new portal's search.
  - **Header schema can shift** when ČSÚ adds new bands (e.g. 90+, 95+) or splits 85+. The script keys on band label text and takes first occurrence — robust to suffix changes but assumes labels stay in the "0-4" / "5-9" form (em-dash variant `0–4` is also handled).
  - **The XLSX has 5-year bands only.** If a re-runner reports single-year-of-age from this file, they are wrong. Single-year data needs the IPR `uap.iprpraha.cz/pov` dashboard (still blocked) or the ČSÚ VDB DEM01 table (still blocked).
  - In-scope MČ list is hardcoded in the script. To re-extend to other MČs, edit `TARGET_MCS` and the `IPR_MC_CODE` map.
- **Last verified:** 2026-05-18.

### R-04 csu-casova-rada-mc-2004-2025

- **WP:** WP-01 (Demographics) — produces the `births_by_mc_year.csv` companion file.
- **Depends on:** none.
- **Source URL:** Asset (as of 2026-05-18): `https://csu.gov.cz/docs/107839/4473deb4-e987-202b-1e15-740fcaccfba3/Casova_rada_MC.xlsx?version=1.9`. Landing page: same as R-03. Title to search for: **"Souhrnné informace o 57 městských částech 2004-2025"**.
- **Auth / access:** Same as R-03 — main-agent WebFetch on `csu.gov.cz` works; subagent re-fetch needs `Bash(dangerouslyDisableSandbox: true)`.
- **Procedure:**
  1. Main agent: download to `memory/raw/demographics/csu/Casova_rada_MC.xlsx`.
  2. Subagent: same `notebooks/parse_csu_wp01.py`, `parse_births_xlsx` function.
     - Sheets `'2004'..'2025'`.
     - Header row 3 (idx 2) lists MČ names; look up the in-scope six by name (Praha 3, 7, 8, 9, 10, 14) — column indices in the 2024 sheet are (4, 14, 16, 20, 21, 30) but **always look them up** because new MČ rows could shift them.
     - Row 4 (idx 4) has label "Kód ZÚJ" — captures ČSÚ KOD_ZUJ codes per column.
     - Scan column A for the row whose label starts with `"Živě narození"` — typically row 24 (idx 23). Read counts at the MČ columns.
  3. **WRITE** (do NOT append — this is a new file) `memory/aggregated/demographics/births_by_mc_year.csv` with columns: `year, reference_date, mc, mc_code, count, count_kind, source_slug, kind, notes`. `count_kind = 'live_births'`, `reference_date = YYYY-12-31`.
- **Expected output:**
  - `memory/raw/demographics/csu/Casova_rada_MC.xlsx` (~1.1 MB, 22 sheets).
  - `memory/aggregated/demographics/births_by_mc_year.csv` (133 lines = 1 header + 132 data rows = 6 MČ × 22 years).
- **Verification:**
  - Row count = 132 (`wc -l` ≥ 133 including header).
  - **Praha 3, year 2021, live_births = 951.**
  - **Praha 10, year 2024, live_births = 1050.**
  - **Praha 14, year 2014, live_births = 531.**
  - Sanity: 2021 Praha 3 births ≈ 951; population age-0-4 in band as of 2021-12-31 = 3968 (R-03 anchor: divide by 5 ≈ 794 per age — same order of magnitude with the expected dampening from infant mortality + net migration).
- **Robustness notes:**
  - Row order inside the workbook is **not** guaranteed across editions. Look up "Živě narození" by label, not by index. The label string is the language-bilingual `"Živě narození\nLive births"` in the cell — `'Živě narození' in label` is the robust test.
  - The columns are MČ names — look up by exact string "Praha 3", "Praha 7", etc.
  - The XLSX has MANY indicators beyond births (population dynamics, schools by type, healthcare facilities, employment). If WP-02 / WP-03 ever needs a fallback school-counts cross-check, this same file has rows around idx 40-50.
  - Same `version=1.9` rotation caveat as R-03.
  - `count_kind = 'live_births'` is distinct from the `'population'` and `'walking_distance_to_*'` values in `children_by_age_mc_year.csv` — downstream code should filter by `count_kind` before summing.
- **Last verified:** 2026-05-18.

### R-05 msmt-rejstrik-skol-jsonld

- **WP:** WP-02 (School inventory).
- **Depends on:** none.
- **Source URL:**
  - **NKOD catalogue entry** (re-discovery point): `https://data.gov.cz/dataset?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2F00022985%2F8e4bab9c3d258b0850c9f43080ba78e5` ("Rejstřík škol a školských zařízení pro rok 2025 - celá ČR", publisher IČO 00022985 = MŠMT).
  - **Asset (snapshot 2025-10-31):** `https://lkod-ftp.msmt.gov.cz/00022985/e9c07729-877e-4af0-be4a-9d36e45806ae/rssz-cela-cr-2025-10-31.jsonld` (~30 MB). The UUID-like component (`e9c07729-…`) and the date suffix both rotate at every quarterly snapshot — DO NOT hardcode for a fresh run; re-read the NKOD page.
- **Auth / access:** Main-agent WebFetch on `data.gov.cz` and `lkod-ftp.msmt.gov.cz` works; subagent re-fetch needs `Bash(dangerouslyDisableSandbox: true)` (the sandbox network allowlist does not include either host). The interactive UI replacement at `https://isv.gov.cz/rssz/` is not needed if the JSON-LD dump is available — and is harder to use.
- **Discovery path** (for the first re-runner who only has this section):
  1. Open NKOD: `https://data.gov.cz/datové-sady` (or English: `/datasets`).
  2. Filter by publisher = "Ministerstvo školství, mládeže a tělovýchovy" (IČO 00022985). The dataset is titled `Rejstřík škol a školských zařízení pro rok <YYYY> - celá ČR` (new edition per calendar year).
  3. On the dataset detail page, find the most recent JSON-LD distribution. Its access URL is the asset to download. There are also CSV and XML variants — JSON-LD is the most stable to parse with Python stdlib.
  4. Note `datumVystupu` inside the file (the snapshot date) — this is the truth, the filename can lie.
- **Procedure:**
  1. Main agent:
     ```bash
     curl -fsSL -o memory/raw/schools/rejstrik/rssz-cela-cr-<YYYY-MM-DD>.jsonld <asset-url>
     ```
     (sandbox-disabled). File is ~30 MB.
  2. Subagent: run `notebooks/wp02_parse/parse.py`. It does:
     - `json.load` the whole file (fits in memory).
     - Filter `list[]` to records with `kraj == 'Hlavní město Praha'`.
     - For each, look at `skolyAZarizeni[]`; keep only the obors with `druh == 'B00'` (Základní škola — covers both regular obor `79-01-C/01` and special-ed obor `79-01-B/01`).
     - **MČ assignment:** look up `(adresa.castObce, adresa.psc)` against the hardcoded `CAST_PSC_TO_MC` table at the top of the script. Roughly half the Prague cast obce span multiple MČ; PSČ disambiguates them. `adresa.cisloObvoduPrahy` is the administrative obvod (Praha 1–10) and is **insufficient** as an MČ key — e.g. obvod Praha 9 contains MČ Praha 9 proper plus MČ Praha 14 (Hloubětín 198 00, Kyje, Černý Most, Hostavice), MČ Čakovice, MČ Vinoř, MČ Horní Počernice, and ~7 more.
     - For each surviving entity, aggregate kapacita = `sum(kapacity[mernaJednotka='01'].nejvyssiPovolenyPocet)` across the B00 obors.
     - Classify `type` from `typZrizovatele`: 1/2/3/4/7 → `state`; 5 → `private`; 6 → `church`.
  3. Write CSV to `memory/aggregated/schools/zs_by_mc.csv` with header `mc,name,redizo,izo_zs,address,zrizovatel,type,kapacita_registered,snapshot_date,source_url,notes`. One row per RED-IZO.
- **Expected output:**
  - `memory/raw/schools/rejstrik/rssz-cela-cr-<YYYY-MM-DD>.jsonld` (~30 MB).
  - `memory/aggregated/schools/zs_by_mc.csv` (~94 rows on the 2025-10-31 snapshot — exactly 93). Per-MČ row counts on the 2025-10-31 snapshot:
    | MČ | Rows |
    |---|---|
    | Praha 3  | 15 |
    | Praha 7  | 10 |
    | Praha 8  | 26 |
    | Praha 9  | 10 |
    | Praha 10 | 23 |
    | Praha 14 |  9 |
- **Verification:**
  - Row count = 93 (`wc -l` ≥ 94 including header) on 2025-10-31 snapshot. ±5 is reasonable for adjacent snapshots.
  - All `kapacita_registered` populated (no empty strings).
  - Three concrete anchors (verify by `grep` on `zs_by_mc.csv`):
    - `600041212` → "Základní škola, Praha 10, Gutova 1987/39", MČ Praha 10, kapacita 720.
    - `600040585` → "Základní škola, Praha 9 - Lehovec, Chvaletická 918", MČ Praha 14, kapacita 868. (Note: legal name says "Praha 9", MČ is Praha 14 — verified via zrizovatel = MČ Praha 14.)
    - `600039382` → "Základní škola Praha 7, Korunovační 8", MČ Praha 7, kapacita 560.
  - **MČ-mismatch sanity** (built into `notebooks/wp02_parse/verify.py`): for every row where `zrizovatel` contains "městská část", the MČ number in `zrizovatel` must match the `mc` column. Expected mismatch count = 0.
- **Robustness notes:**
  - **Snapshots are quarterly.** The NKOD page lists every snapshot — the filename suffix encodes the date. Always pick the latest.
  - **The URL has a UUID-like asset id + date suffix that both rotate.** Re-fetch the NKOD catalogue page first, parse out the current JSON-LD distribution URL, then download.
  - **JSON-LD `@context` can change between snapshots.** If a field name shifts (e.g. `castObce` → `nazevCastiObce`), re-inspect a single record before re-running the filter. The 2025-10-31 schema is documented inline in `notebooks/wp02_parse/parse.py`.
  - **The MČ lookup table `CAST_PSC_TO_MC` is hardcoded** for the six in-scope MČ + their PSČ partitions, derived from manual inspection of obvod-3/7/8/9/10 ZŠ-bearing entities in this snapshot. If MŠMT changes the `castObce` strings or the PSČ partition of an MČ changes (rare), some schools will silently drop out of the result. Re-validate via the MČ-mismatch sanity check — a zero is required.
  - **Old URL `rejstriky.msmt.cz/rejskol/` is retired** (gov.cz consolidation). UI replacement is `isv.gov.cz/rssz/`. Use the NKOD bulk dump rather than scraping either UI.
  - **Excluded by design** (in scope: only MČ 3/7/8/9/10/14): all schools in adjacent MČs that share an obvod, including MČ Praha-Troja (Trojská 110), MČ Praha 15 (Hostivař/Petrovice/Horní Měcholupy), MČ Praha-Čakovice, MČ Horní Počernice, MČ Letňany, MČ Kbely, MČ Vinoř, etc. If a future round needs them, add their `(castObce, psc)` entries to `CAST_PSC_TO_MC`.
- **Last verified:** 2026-05-18.

### R-06 hmp-vyhlaska-19-2025-spadove-obvody

- **WP:** WP-04 (Catchment).
- **Depends on:** R-05 (`memory/aggregated/schools/zs_by_mc.csv` — RED-IZO join target).
- **Source URL:**
  - **Citywide (primary):** *Obecně závazná vyhláška hl. m. Prahy č. 19/2025, o školských obvodech základních škol*, amended by usnesení ZHMP 11. 12. 2025, effective **2026-01-01**. The PDF on disk was downloaded as `vyhlaska-hmp-19-2025_via-P6.pdf` — MČ Praha 6's mirror of the citywide decree. Re-discovery: original publication on the city's úřední deska (`https://magistrat.praha.eu` → Předpisy → OZV → 19/2025); MČ-6 mirror at `https://www.praha6.cz/` under Školství / Spádové obvody. The two are textually identical.
  - **Per-MČ excerpts (cross-checks only):** each in-scope MČ publishes its own excerpt on its website. The set already on disk:
    - P3: `https://www.praha3.cz/skolstvi` → `p3_skolske-obvody-2026.pdf` (Rada MČ P3 usnesení 855/2025-10-08).
    - P7: `https://www.praha7.cz/skolstvi` → `p7_OZV-skolske-obvody-2025.pdf` (2025-04-01 base; P7 content matches 2026 amendment).
    - P9 (cleanest format, **used as primary for P9**): `https://praha9.cz/skolstvi` → `p9_spadova-vyhlaska-1.1.2026.docx`.
    - P9 citywide DOCX: `p9_HMP-vyhlaska-1.1.2026.docx` (held as DOCX-form cross-check; not parsed by default).
    - P14: `https://www.praha14.cz/skolstvi` → `vyhlaska-19-2025_via-P14.pdf`.
    - P8 and P10: no per-MČ excerpt downloaded — citywide is canonical.
- **Auth / access:** All six files are local on disk under `memory/raw/catchment/`. No network access needed at re-run time. For a fresh download of an updated decree, main-agent WebFetch works on `praha3.cz`, `praha7.cz`, `praha9.cz`, `praha14.cz` (subagent re-fetch needs `Bash(dangerouslyDisableSandbox: true)` because the sandbox network allowlist excludes most MČ hosts). The citywide source — `magistrat.praha.eu` or `praha.eu` — is **not** in the sandbox allowlist; if the citywide must be refetched, do it via `curl -fsSL` with sandbox disabled.
- **Procedure:**
  1. **No fetch needed for the existing snapshot** — the six files are checked in under `memory/raw/catchment/`. For a fresh 2027+ amendment: fetch the citywide PDF and the per-MČ excerpts to the same paths.
  2. Subagent runs `notebooks/wp04_parse/parse.py`:
     ```
     cd notebooks/wp04_parse
     uv run python parse.py
     ```
     The script depends on `pdfplumber` and `python-docx` (declared in `pyproject.toml`); uv resolves them on first run. It performs:
     - Two-column PDF parse via `pdfplumber.extract_words`, y-banded into rows, x-gap heuristic for column split (gap ≥ 25 pt that straddles page midline ⇒ column separator).
     - Heading detection by literal prefix (`"Základní škola"`, `"Fakultní základní škola"`, `"Církevní základní škola"`, `"Městská část"`).
     - Wrapped-line stitching: a row whose first character is lowercase or digit (excluding known new-street starters like `náměstí`, `nábřeží`, `sady`, `park`) is appended to the previous street's text in the same column.
     - DOCX parse (P9 streets-only excerpt only): paragraph-by-paragraph.
     - School-name → RED-IZO join via the hand-curated `HAND_OVERRIDES` table — keyed on `(mc, short_address_tag)` such as `('Praha 9', 'litvinovska 500')`. The decree prints short brand names; the rejstřík uses long legal names. Don't try fuzzy matching on the long names alone — the address tag is the stable bridge.
  3. The deliverable CSV is written to `memory/aggregated/catchment/streets_to_zs.csv`. Schema: `mc, street, house_number_range, red_izo, zs_name, source_file, effective_date`. UTF-8, no BOM, LF newlines. `effective_date` is hardcoded to `2026-01-01` (citywide decree's stated účinnost).
  4. Sidecar files at the same path: `_README.md` (schema + coverage matrix + invariant-check results) and `_anomalies.md` (unmatched school headings, missing state ZŠ with manual classification, format ambiguities).
- **Expected output:**
  - `memory/aggregated/catchment/streets_to_zs.csv` — **1 953 rows** on the 2026-01-01 snapshot. Per-MČ row counts:
    | MČ | Rows |
    |---|---|
    | Praha 3  | 235 |
    | Praha 7  | 131 |
    | Praha 8  | 527 |
    | Praha 9  | 263 |
    | Praha 10 | 521 |
    | Praha 14 | 276 |
  - `memory/aggregated/catchment/_README.md`, `_anomalies.md` — companion docs.
- **Verification:**
  - Total row count = 1953 (`wc -l` ≥ 1954 including header). ±50 is reasonable for adjacent amendments.
  - **Three concrete anchors** (verify by `grep` on `streets_to_zs.csv`):
    - `grep "^Praha 14,Chvaletická" streets_to_zs.csv` → has `red_izo=600040585` (Lehovec — name says "Praha 9" but MČ is Praha 14).
    - `grep "^Praha 3,Vinohradská" streets_to_zs.csv` → returns ≥ 3 rows (Vinohradská is split across 3 P3 ZŠ by house-number ranges).
    - `grep "^Praha 10,Vinohradská" streets_to_zs.csv` → returns ≥ 1 row (Vinohradská also spans P10).
  - **Coverage invariant:** 57 / 62 state non-`zs_specialni` ZŠ from `zs_by_mc.csv` appear at least once in the catchment CSV. The 5 missing are 3 hospital schools (Bulovka, Bohnice, Nemocnice Na Františku/Za Invalidovnou 1), 2 logopedická (LOPES Čimice, Moskevská 29) — none are spádové by design. One non-classified miss: RED-IZO `691019061` (ZŠ V Olšinách, P10) — possibly a new school post-decree; flagged in `_anomalies.md`.
  - **Lehovec invariant:** `awk -F, '$4=="600040585" {print $1}' streets_to_zs.csv | sort -u` returns exactly `Praha 14`.
  - **Red-izo validity invariant:** every distinct `red_izo` in the CSV exists in `zs_by_mc.csv`.
- **Robustness notes:**
  - **Decree amendments rotate filenames.** The 19/2025 base was 2025-04-01; the 2026-01-01 amendment uses the same decree number. A future amendment may rename the file to a new decree number (e.g. `7/2027`). Re-fetch from `magistrat.praha.eu` and check the `§ … nabývá účinnosti dnem …` line on page 1 of the PDF to confirm the effective date.
  - **PDF column-flow is brittle.** The parser depends on a clean two-column layout. If a future amendment switches to single-column or table layout, the column-gap heuristic in `_extract_rows_from_page` must be revised. The DOCX P9 excerpt is the most stable format; if any MČ publishes DOCX versions, prefer them.
  - **School-name → RED-IZO join is hand-curated.** New ZŠ entering the decree require adding an entry to `HAND_OVERRIDES`. The pattern is `(mc, normalised-address-tag) → redizo`. Normalise via the script's `_normalise_school_name` (lowercase + strip accents + alphanumerics only).
  - **Per-MČ excerpts may lag the citywide.** P7 and P14 files on disk pre-date the 2026 amendment; they were verified by content-diff to match the citywide for those MČ in this snapshot. Re-run agents must re-verify on any new amendment cycle.
  - **The P3 PDF has no `"Městská část Praha 3"` banner** — its header reads `"Školské obvody 2026 - MČ Praha 3"`. The parser handles this by accepting a `default_mc=` argument when calling `parse_two_column_pdf` on a per-MČ excerpt.
  - **House-number ranges are kept as the raw decree string.** No range-expansion is done — too brittle (lichá/sudá parity, comma-separated lists, `(vyjma …)`-exclusion clauses, č. p. vs. č. o. distinction). Downstream code that needs to test "does house X fall in this catchment?" must parse the string itself; the project does not currently require this.
- **Last verified:** 2026-05-18.

### R-07 msmt-statis-rocenka-hmp-2005-2025

- **WP:** WP-03 (Enrolment series) — fallback B′ after the open-data dead end (per-school data structurally unavailable; see `progress/WP-03-enrolment.md` and the Tier-A `msmt-statis-rocenka-hmp` entry in `memory/sources.md`).
- **Depends on:** none.
- **Source URL:** UI root `https://statis.msmt.gov.cz/rocenka/`. Form endpoint: `POST https://statis.msmt.gov.cz/rocenka/rocenka.asp` with form-encoded body `kapit=C&tab=<TABLE>&rck=<N>`. `N` maps to school years via the dropdown: `1`→2005/2006, …, `5`→2009/2010, **`5a`→2010/2011**, `6`→2011/2012, …, `20`→2025/2026 (21 values total). Response is HTML in **windows-1250**.
- **Auth / access:** **Host `statis.msmt.gov.cz` is NOT in `.claude/settings.json` allowlist.** All POSTs must run with `Bash(dangerouslyDisableSandbox: true)` — the user will be prompted once per Bash call. The script `notebooks/wp03_parse/fetch_statis.py` bundles all 63 fetches into a single Bash invocation, so only one prompt is required for the whole refresh. No HTTP auth; no Cookie required; a polite `User-Agent` header is set in the script. Polite pacing: `time.sleep(0.5)` between requests (≈ 30 s total).
- **Procedure:**
  1. From repo root: `python3 notebooks/wp03_parse/fetch_statis.py` (run under `Bash(dangerouslyDisableSandbox: true)`). The script is stdlib-only — no `uv` env needed; just CPython 3.11+ on PATH.
  2. The script does, for each (tab ∈ {C1.25.1, C1.22.1, C1.4.1}, rck ∈ 21 values):
     - POSTs the form-encoded body, decodes `windows-1250`, caches the transcoded UTF-8 HTML at `memory/raw/enrolment/statis_msmt/<tab>_rck<N>.html`.
     - Parses the page with a stdlib `html.parser.HTMLParser` that expands rowspan/colspan into a 2-D grid. Finds the data `<table>` (the one containing the literal `Hlavní město Praha`), extracts the kraj's rowspan group, and emits one row per (sub-label × column-header) pair.
     - Column headers are stitched from the table's multi-row `<th>` block — captured from the HTML, not hardcoded. Sub-labels come from the left-side `<td class='levyC'>` cells inside Praha's rowspan group (e.g. `(celkem)`, `v tom / poprvé u zápisu`, `v tom / přicházejí po odkladu`, `v tom / z toho po dodatečném`, `z celku ze spádového obvodu`).
     - The Praha-group end is detected by checking the NUTS-code anchor `CZ010` — stops as soon as the rowspan-continuation no longer carries `CZ010` at its original column index. This sidesteps drift across yearbook editions (kraj-name changes like "Střední Čechy" → "Středočeský kraj" cannot leak).
  3. Writes the long-format CSV at `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` with columns `school_year, school_year_ord, table_code, table_topic, indicator, value, source_url, snapshot_fetched_at`. **`school_year_ord` deviates from the spec wording (rck integer 1..20):** the dropdown's `rck='5a'` (2010/2011) is non-numeric, so the ordinal column carries the school-year **start year** (2005..2025) instead — strictly monotonic, joins naturally against `births_by_mc_year.csv` and the `children_by_age_mc_year.csv` tables in `memory/aggregated/demographics/`.
  4. Sidecar README: `memory/aggregated/enrolment/_README.md` — schema, full coverage matrix, list of known gaps (the (tab, rck) combos that returned HTTP 500), and the verification anchor.
- **Expected output:**
  - `memory/raw/enrolment/statis_msmt/*.html` — 40 files (~6.1 MB total). The 23 missing combos (HTTP 500 on the older years) are documented in the sidecar README and do NOT write a file.
  - `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` — **1 450 long-format rows** on the 2026-05-19 snapshot.
  - `memory/aggregated/enrolment/_README.md` — schema + coverage matrix + verification anchor.
- **Verification:**
  - Total row count = 1450 (`wc -l ≥ 1451` including header) on the 2026-05-19 snapshot. ±50 is reasonable for adjacent yearbook editions.
  - **Verification anchor:** `grep -F "2025/2026,2025,C1.25.1" memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv | grep "(celkem) :: Zapisované děti / celkem"` → expected value `25075` (Hlavní město Praha, school year 2025/2026, total registered zápis attendees).
  - **Coverage matrix** (table × year availability — see `_README.md` for full):
    - C1.25.1 (zápis výsledky): 2011/2012 → 2025/2026 (15 years × 39 or 65 indicators).
    - C1.22.1 (1. ročník × věk): 2014/2015 → 2025/2026 (12 years × 28 indicators).
    - C1.4.1 (žáci v ročnících): 2005/2006 + 2014/2015 → 2025/2026 (13 years × 15 to 32 indicators).
  - **Schema-drift indicator counts:** C1.25.1 stepped from 39 → 65 indicators in 2021/2022 (MŠMT added the spádový-obvod breakdown). C1.4.1 stepped from 15 → 32 indicators in 2014/2015 (added speciální-třídy sub-row). These are documented in the `value` strings — column headers self-document.
- **Robustness notes:**
  - **`windows-1250` decode is mandatory.** The server emits a `Content-Type: text/html; charset=Windows-1250` header but most parsers default to UTF-8 and silently mangle the diacritics. The script forces `bytes.decode('windows-1250')` before parsing.
  - **The rowspan-group end-test uses the NUTS-code anchor (CZ010).** Earlier-yearbook drafts used kraj-name regex (`other_kraj_re`), but that leaked rows when MŠMT introduced NUTS-2 aggregations (`Střední Čechy`, `Střední Morava`, `Moravskoslezsko`) that don't match the kraj-name pattern. The NUTS-code anchor is yearbook-edition-stable — every kraj's code is unique and persistent.
  - **HTML has stray `<tr></tr>` pairs** between header and data rows. The parser handles these by allowing fresh `<tr>` tags to attach to un-opened rowspan-pre-filled grid rows — see `TableExtractor._opened_rows` logic.
  - **Granularity ceiling = kraj.** This is structural, not a parser limitation. The yearbook publishes by NUTS-3 region only; per-MČ and per-school enrolment is not surfaced. **Do NOT try to bend the script to extract finer rows — they aren't in the HTML.** See `progress/WP-03-enrolment.md` for the recon receipt.
  - **HTTP 500s for the older years are expected** — the table codes C1.22.1 and C1.4.1 didn't exist in MŠMT's 2005-2013 yearbooks; the schema was renumbered around 2013/2014. The script logs each failure and continues; the sidecar README documents the gap.
  - **`uv` is not needed.** stdlib-only (urllib + html.parser). The accompanying `pyproject.toml` declares no dependencies — exists only to mark the directory as a project for tool consistency with WP-02 / WP-04.
- **Last verified:** 2026-05-19.

---

## Retired sections

_(none yet)_

## Schema drift log

_(empty — record here any in-place edits made because a source's schema changed between runs)_
