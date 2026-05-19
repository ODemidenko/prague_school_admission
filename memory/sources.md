# Source catalogue

Every URL, dataset, or document we touch lands here. Subagents append; main agent reviews.

## Format

For each entry:

```
### <short slug>
- **URL / location:** <url or memory/raw/... path>
- **Tier:** A / B / C  (see CLAUDE.md → Source quality discipline)
- **What it has:** <one line — what data, what years, what granularity>
- **Format:** HTML table / PDF / XLSX / API / CSV
- **Date checked:** YYYY-MM-DD
- **Used by:** WP-XX
- **Notes:** <gotchas, paywalls, language, schema quirks>
```

## Tier A — official statistical sources

### csu-vekove-slozeni-mc-2011-2025
- **URL / location:** `https://csu.gov.cz/docs/107839/afefbae8-c12f-7944-fe52-ce39f88da593/1_PHA_VEK_obyv_mc.xlsx?version=1.5` (direct asset). Landing page: `https://csu.gov.cz/csu/xa/casove-rady-za-mestske-casti-prahy`. Local: `memory/raw/demographics/csu/1_PHA_VEK_obyv_mc.xlsx`.
- **Tier:** A
- **What it has:** "Věkové složení obyvatel v městských částech Prahy v letech 2011-2025". XLSX with one sheet per year (2011..2025), one row per MČ (60 MČ including the 57 districts + 3 Praha-aggregate rows), columns = 5-year age bands × {Celkem, Muži, Ženy}. Bands: 0-4, 5-9, 10-14, 15-19, 20-24, …, 85+. **Single year of age is NOT in this file.**
- **Format:** XLSX (~379 KB).
- **Date checked:** 2026-05-18 — downloaded by main agent (subagent parsed offline).
- **Used by:** WP-01 (primary).
- **Notes:** Schema drift between 2011-2019 and 2020-2025: the early sheets put KOD_SO/KOD_ZUJ in cols 0-3 (KOD_SO first), later sheets put KOD_ZUJ first. First-occurrence-of-band column index is stable at cols 5-8 across all sheets. ČSÚ's KOD_ZUJ for the in-scope MČ: Praha 3=500097, Praha 7=500186, Praha 8=500208, Praha 9=500216, Praha 10=500224, Praha 14=547361. These differ from the IPR/LAU-2 codes (547107, 547141, …) that round 3 used — the aggregated CSV keeps the IPR codes in `mc_code` and stuffs the ČSÚ KOD_ZUJ into `notes` for traceability. **The URL has `version=1.5` — future ČSÚ updates will bump this; re-discover via the landing page rather than hardcoding the asset hash.**

### csu-casova-rada-mc-2004-2025
- **URL / location:** `https://csu.gov.cz/docs/107839/4473deb4-e987-202b-1e15-740fcaccfba3/Casova_rada_MC.xlsx?version=1.9` (direct asset). Landing page: same as above. Local: `memory/raw/demographics/csu/Casova_rada_MC.xlsx`.
- **Tier:** A
- **What it has:** "Souhrnné informace o 57 městských částech 2004-2025" — broad annual summary per MČ. One sheet per year (2004..2025); rows = indicators (population, density, age structure, mean age, live births, deaths, migration, schools by type, healthcare, housing, employment, …), columns = MČ. **Row 23 "Živě narození / Live births" is the birth-cohort primitive** for WP-01. Also has population structure as % in age 0-14 / 15-64 / 65+ (rows 17-19).
- **Format:** XLSX (~1.1 MB).
- **Date checked:** 2026-05-18 — downloaded by main agent.
- **Used by:** WP-01 (births), WP-02 (cross-check of school counts per MČ).
- **Notes:** Last updated 2026-01-09 per the sheet header. The MČ column index for the in-scope districts in 2024 is: Praha 3=4, Praha 7=14, Praha 8=16, Praha 9=20, Praha 10=21, Praha 14=30. Look up by column header text rather than index for robustness — the column order is stable across years but new MČs (rare) could shift it. **Note ČSÚ-domain migration:** `czso.cz` 302-redirects to `csu.gov.cz` as of 2026-05-18; same asset paths under the new host. The `version=1.9` will rotate with each annual republication.

### rejstrik-skol-msmt
- **URL / location:** **Verified working bulk dump (2025-10-31 snapshot):** `https://lkod-ftp.msmt.gov.cz/00022985/e9c07729-877e-4af0-be4a-9d36e45806ae/rssz-cela-cr-2025-10-31.jsonld` (~30 MB JSON-LD). NKOD catalogue entry: `https://data.gov.cz/dataset?iri=https%3A%2F%2Fdata.gov.cz%2Fzdroj%2Fdatov%C3%A9-sady%2F00022985%2F8e4bab9c3d258b0850c9f43080ba78e5`. Local: `memory/raw/schools/rejstrik/rssz-cela-cr-2025-10-31.jsonld`. Web UI (interactive search): `https://isv.gov.cz/rssz/` (replacement for the retired `https://rejstriky.msmt.cz/rejskol/`).
- **Tier:** A — **verified live 2026-05-18 round 4** (parsed; 10 020 entities CZ-wide, 1031 in Hlavní město Praha kraj, 93 in-scope ZŠ extracted).
- **What it has:** Full snapshot of the MŠMT rejstřík škol a školských zařízení (RSSZ). One record per RED-IZO ("school as legal entity"), each with `skolyAZarizeni[]` — the constituent obors (ZŠ `B00`, MŠ `A00`, gymnázium `C00`, ŠJ `L11`, družina `G21`, …). Per obor: IZO, `druh` code, address, `kapacity[]` (legal maximum by měrná jednotka — `01` = žáci for ZŠ), zřizovatel, datum zápisu. Snapshots are quarterly (date appended to filename).
- **Format:** JSON-LD `application/ld+json`, single top-level object with `@context` (URL), `datumVystupu` (snapshot date), `list[]` (the records). Loadable into Python with stdlib `json.load`.
- **Date checked:** 2026-05-18 — bulk dump downloaded by main agent, parsed offline by WP-02 round 4 subagent.
- **Used by:** WP-02 (primary), WP-03 (IZO bridge to enrolment yearbooks).
- **Notes:**
  - Primary key for school-as-legal-entity = `redIzo`; per-obor key = `skolyAZarizeni[*].izo`. `kapacita` is the registered legal maximum, not current enrolment.
  - **`adresa.cisloObvoduPrahy` is the obvod (Praha 1–10), NOT the MČ.** Recovering MČ requires `(adresa.castObce, adresa.psc)` against a manual lookup — see `notebooks/wp02_parse/parse.py → CAST_PSC_TO_MC`. Roughly half the Prague cast obce span multiple MČ.
  - **The old URL `rejstriky.msmt.cz/rejskol/` is retired** (gov.cz consolidation 2024–2025). Its replacement UI is `isv.gov.cz/rssz/` (ISV — Informační systém ve vzdělávání portal). For bulk needs use the NKOD JSON-LD dump rather than scraping the UI — it's denormalised, complete, and quarterly-stable.
  - **Re-discovery for future snapshots:** Visit the NKOD dataset URL above; the JSON-LD distribution link points to the latest `rssz-cela-cr-<YYYY-MM-DD>.jsonld`. The UUID-like asset id may rotate per snapshot — always re-read NKOD rather than hardcoding the asset URL.

### mc-skolstvi-pages
- **URL / location:** `https://www.praha{3,7,8,9,10,14}.cz/` → "Školství" / "Naše školy" sub-page (exact paths to be verified in round 2).
- **Tier:** A (each MČ is the official source for the ZŠ it founded).
- **What it has:** Per-MČ list of the ZŠ the MČ is `zrizovatel` of, with addresses and ředitel contacts. Usually misses private/church ZŠ located in the MČ.
- **Format:** HTML pages, occasional PDFs.
- **Date checked:** 2026-05-18 — listed only, not fetched.
- **Used by:** WP-02 (cross-check), WP-04 (catchment decrees usually linked from here).
- **Notes:** Cross-check vs rejstřík to catch the private/church ZŠ that MČ pages omit.

## Tier A — catchment (spádové obvody) decrees

### hmp-vyhlaska-19-2025
- **URL / location:** Local: `memory/raw/catchment/vyhlaska-hmp-19-2025_via-P6.pdf`. Original publication routes: gazette `https://magistrat.praha.eu` (citywide decree); also mirrored on `https://www.praha6.cz/`. Decree title: *Obecně závazná vyhláška hl. m. Prahy č. 19/2025, o školských obvodech základních škol*.
- **Tier:** A (binding legal text; the *only* source-of-truth for spádové obvody in Praha).
- **What it has:** Per-MČ × ZŠ catchment assignment — list of streets (and where partial, house-number ranges) that legally belong to each ZŠ in each MČ. Covers all 22 city districts + 35 small MČs. Original 19/2025 was effective **2025-04-01**; the version on disk was **amended 11. 12. 2025 and is effective 2026-01-01** — this is the version that binds the April 2027 zápis (2021 cohort) and beyond.
- **Format:** PDF, 90 pages, two-column layout per page. Section header is literal `"Městská část Praha N"`. Each school is introduced by a one-line heading starting with `"Základní škola"` or `"Fakultní základní škola"`. Streets follow as two-column lists; some entries carry house-number ranges (`"sudá č. X – Y, lichá č. A – B"`, `"č. p. NNN/M"`, `"(vyjma NNN/M)"`).
- **Date checked:** 2026-05-18 — file already on disk by main agent prior to WP-04 parser dispatch; parsed offline.
- **Used by:** WP-04 (primary).
- **Notes:** PDF column layout merges into linear text under naive extraction — must split by x-coordinate. The parser at `notebooks/wp04_parse/parse.py` uses `pdfplumber.extract_words` with a y-band grouping and an x-gap heuristic (≥25 pt and straddling the page midline = column separator).

### p9-spadova-vyhlaska-docx
- **URL / location:** Local: `memory/raw/catchment/p9_spadova-vyhlaska-1.1.2026.docx`. Likely published from `https://praha9.cz/` "Školství" area.
- **Tier:** A (MČ Praha 9's published excerpt of the citywide decree).
- **What it has:** P9-only section of the 2026-01-01 spádové obvody — one Word paragraph per street, structurally cleaner than the citywide PDF for P9.
- **Format:** DOCX, 308 paragraphs (~263 streets across 6 P9 ZŠ).
- **Date checked:** 2026-05-18 — already on disk; parsed offline.
- **Used by:** WP-04 (primary for P9; replaces citywide P9 section).
- **Notes:** Each ZŠ is introduced by a paragraph that starts with `Základní škola …` followed by `sídlo: <address>`. Streets follow as bare paragraphs. House-number ranges sometimes wrap across paragraphs; the parser stitches continuations whose first character is lowercase / digit.

### p9-hmp-vyhlaska-docx
- **URL / location:** Local: `memory/raw/catchment/p9_HMP-vyhlaska-1.1.2026.docx`.
- **Tier:** A (MČ Praha 9's mirror of the full citywide decree, in DOCX form).
- **What it has:** Citywide 19/2025 amended text as DOCX. Kept as a cross-check for the citywide PDF.
- **Format:** DOCX, 220 KB.
- **Date checked:** 2026-05-18 — already on disk; not used by the parser (citywide PDF is canonical), retained for cross-validation in future re-runs.
- **Used by:** WP-04 (cross-check, not run).

### p3-skolske-obvody-pdf
- **URL / location:** Local: `memory/raw/catchment/p3_skolske-obvody-2026.pdf`. Likely published from `https://www.praha3.cz/` (usnesení Rady MČ P3 855/2025-10-08).
- **Tier:** A (P3 MČ's published excerpt of the 2026-01-01 amendment).
- **What it has:** P3-only catchment lists, 3 pages, 10 schools, ~232 streets.
- **Format:** PDF (two-column). File header reads `"Školské obvody 2026 - MČ Praha 3"` — no `"Městská část Praha 3"` banner, so the parser passes `default_mc='Praha 3'`.
- **Date checked:** 2026-05-18 — on disk; parsed as cross-check only.
- **Used by:** WP-04 (cross-check).

### p7-ozv-skolske-obvody-pdf
- **URL / location:** Local: `memory/raw/catchment/p7_OZV-skolske-obvody-2025.pdf`.
- **Tier:** A (MČ Praha 7's excerpt of vyhláška 19/2025).
- **What it has:** P7-only catchment lists, 2 pages, 6 schools, 131 streets. **Filename suggests 2025-04-01 base** — pre-amendment edition; but its P7 content matches the 2026-01-01 citywide for P7. The 2026 amendment did not substantively change P7.
- **Format:** PDF (two-column).
- **Date checked:** 2026-05-18 — on disk; parsed as cross-check.
- **Used by:** WP-04 (cross-check).
- **Notes:** For a future re-run that needs to detect edition drift, the parser should diff the P7 cross-check against the citywide P7 section.

### p14-vyhlaska-19-2025
- **URL / location:** Local: `memory/raw/catchment/vyhlaska-19-2025_via-P14.pdf`. Likely from `https://www.praha14.cz/`.
- **Tier:** A.
- **What it has:** P14 section of vyhláška 19/2025, 4 pages, 6 ZŠ, 276 streets.
- **Format:** PDF (two-column). Has the `"Příloha k …"` and `"Městská část Praha 14"` banners.
- **Date checked:** 2026-05-18 — on disk; parsed as cross-check.
- **Used by:** WP-04 (cross-check).
- **Notes:** The P14 ZŠ have legal names starting `"Základní škola, Praha 9 - …"` — they're MČ Praha 14 schools despite the historic "Praha 9" naming. RED-IZO is the only safe join key; the parser's `HAND_OVERRIDES` table maps each P14 school's address tag to its RED-IZO.

## Tier A — enrolment (MŠMT statistical yearbook)

### msmt-statis-rocenka-hmp
- **URL / location:** UI root: `https://statis.msmt.gov.cz/rocenka/`. Form endpoint: `POST https://statis.msmt.gov.cz/rocenka/rocenka.asp` with body `kapit=C&tab=<TABLE>&rck=<N>` (windows-1250 response). Local: `memory/raw/enrolment/statis_msmt/<TAB>_rck<N>.html` (40 files, ~6.1 MB) + aggregated CSV at `memory/aggregated/enrolment/hmp_msmt_yearbook_2005_2025.csv` (1 450 rows). Cross-reference: **R-07 in `RERUN.md`** documents the full recipe.
- **Tier:** A — **MŠMT's official statistical yearbook**, "Statistická ročenka školství — výkonové ukazatele" (the public face of the M 3 / S 3-01 výkaz aggregated to NUTS-3 regions).
- **What it has:** Kraj-level enrolment indicators for the **Hlavní město Praha** kraj (NUTS CZ010), across **20 school years (2005/2006 → 2025/2026)** with one yearbook-edition gap for `rck='5a'` (2010/2011). Three tables pulled in this round:
  - **C1.25.1** "Zahájení povinné školní docházky — školy, zapisované děti podle výsledku zápisu, z toho dívky — podle organizace vyučování, území" — the **zápis (enrolment registration) outcome**: total zapisované děti, zapsané na dané škole, převedené na jinou školu, s žádostí o odklad, etc. Available 2011/2012 → 2025/2026. The 2021/2022 edition added the `z celku ze spádového obvodu` sub-row, which jumped the indicator count from 39 to 65.
  - **C1.22.1** "Nově přijatí do 1. ročníků, z toho dívky — podle věku" — **1st-grade intake by age (5letí, 6letí, 7letí, 8letí, …)**, the cohort-bridging table. Available 2014/2015 → 2025/2026.
  - **C1.4.1** "Žáci v ročnících" — **pupils per grade** (1. ročník through 9. ročník, plus age breakdowns). Available 2005/2006 (one-off) + 2014/2015 → 2025/2026.
- **Format:** Server-rendered HTML tables (windows-1250); two-row `<th>` block with rowspan/colspan for column headers; left-side `<td class='levyC'>` cells with rowspan groups for the kraj's sub-rows; right-side `<td class='dataC'>` cells for values.
- **Date checked:** **2026-05-19** — full 20-year pull completed; CSV anchor verified (Praha 2025/2026 zápis total = 25 075).
- **Used by:** WP-03 (primary — fallback B′ after the open-data dead end).
- **Notes:**
  - **Granularity ceiling = kraj.** The yearbook does NOT publish per-MČ or per-school rows for the Praha kraj. Per-school enrolment is held in MŠMT's central matrika but treated as personal-data-adjacent — see `progress/WP-03-enrolment.md` for the structural recon (NKOD + DSIA confirmed the open-data fence is structural).
  - **Older yearbooks return HTTP 500.** Pre-2011 yearbooks don't carry C1.25.1; pre-2014 don't carry C1.22.1 and don't carry most of C1.4.1. The script logs each (tab, rck) failure and continues; the sidecar README enumerates the 23 known gaps.
  - **`rck='5a'` is a non-numeric ordinal** (the school year 2010/2011 was a one-off transitional edition). The CSV's `school_year_ord` uses the calendar start-year (2005..2025) to keep ordering numeric while preserving the anomaly's traceability via `source_url`.
  - **Host is not in `.claude/settings.json` allowlist.** Every refresh must run under `Bash(dangerouslyDisableSandbox: true)`; the script bundles all 63 POSTs into one Bash call so the user is prompted only once.
  - **The yearbook UI publishes ZIP exports** of full chapters (`https://statis.msmt.gov.cz/rocenka/2025/kapitola_a.zip`, etc.) — kept in mind as a future shortcut if a refresh needs ALL of chapter C at once rather than three named tables.

## Tier B — aggregators & quality journalism

### mapaskol-cz
- **URL / location:** https://www.mapaskol.cz/ (candidate — not verified live).
- **Tier:** B
- **What it has:** Aggregator of CZ schools with map UI and per-school summary pages.
- **Format:** HTML.
- **Date checked:** 2026-05-18 — listed only.
- **Used by:** WP-02 (sanity-check pass on rejstřík output).
- **Notes:** Especially useful for catching private ZŠ that MČ "Naše školy" pages omit.

### ipr-praha-landing
- **URL / location:** https://iprpraha.cz/ (entry point); productive deep paths confirmed in round 3: `/vybavenost`, `/bydleni`, `/obyvatelstvo`, `/struktura`, `/stranka/4318`. Asset path: `https://iprpraha.cz/assets/files/files/<hash>.pdf`.
- **Tier:** A
- **What it has:** Entry point + asset host for IPR demographic publications. **Verified live 2026-05-18 (round 3).**
- **Format:** HTML index + PDF asset URLs.
- **Date checked:** 2026-05-18.
- **Used by:** WP-01.
- **Notes:** Only the bare `iprpraha.cz` host is reachable; every other IPR-family host (`www.iprpraha.cz`, `uap.iprpraha.cz`, `opendata.iprpraha.cz`, `app.iprpraha.cz`, `geoportalpraha.cz`) returns harness-level permission denied. The `/vybavenost` page is the productive jump-off — it lists every chapter of the *Prognóza obyvatel a veřejné vybavenosti 2024–2050* with direct `assets/files/files/<hash>.pdf` links.

### ipr-prognoza-2024-2050-obyvatelstvo
- **URL / location:** https://iprpraha.cz/assets/files/files/c2a6a24d6250739cf644c646eed3b77a.pdf (PDF, 10.4 MB, 46 pages). Local: `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_uvod_a_obyvatelstvo.pdf`.
- **Tier:** A
- **What it has:** Chapter 2 ("Úvod a obyvatelstvo") of IPR's 2024–2050 demographic projection. Methodology (fertility 1.31→1.51, mortality from PřF UK, migration from territorial-capacity model). Příloha P.2.04 (pp. 38–41): per-MČ total population, 2023 stav + 2030 + 2050 across PROG / MAX+ / MAX / MID / NUL variants. **No single-year-of-age tables in the PDF** — those live on the dashboard at `uap.iprpraha.cz/pov` (unreachable).
- **Format:** PDF.
- **Date checked:** 2026-05-18 — downloaded and parsed.
- **Used by:** WP-01.
- **Notes:** Cite as `Brabec, T., Dvořáková, N., Havlová, Z. (2025). Prognóza obyvatel a veřejné vybavenosti v Praze 2024–2050. 2/ Úvod a obyvatelstvo. Praha: IPR Praha.` Source data input is ČSÚ bilance obyvatel k 31.12.2023 — the "stav 2023" column is ČSÚ-derived. Aggregator BUC ("bilanční územní celek") is finer than MČ — every MČ has 1–10 BUCs; MČ totals are sums of constituent BUC rows.

### ipr-prognoza-2024-2050-vzdelavani
- **URL / location:** https://iprpraha.cz/assets/files/files/48480fbb0bfe91c363bdbfca1d658a6d.pdf (PDF, 25.9 MB, 71 pages). Local: `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_vzdelavani.pdf`.
- **Tier:** A
- **What it has:** Chapter 3 ("Školství") of the same study. Příloha P.3.02 (pp. 59–62): per-MČ MŠ-capacity deficit, with "count of age-3–5 children in walking distance of MŠ (600m)" + coverage %, plus deficit projections 2024/2030/2050 across 5 variants. Příloha P.3.04 (pp. 63–66): same shape for ZŠ (age 6–14, 800m). Příloha P.3.05 (pp. 68–69): registry of planned new MŠ/ZŠ projects per MČ — directly useful for WP-02. Block on p. 67: správní obvod-level SŠ table (age 15–18).
- **Format:** PDF.
- **Date checked:** 2026-05-18 — downloaded and parsed.
- **Used by:** WP-01 (primary, this round), WP-02 (planned-schools registry), WP-05 (capacity-deficit headline).
- **Notes:** The "count in walking distance" number is **smaller than the true cohort** by (1 − coverage_pct/100). True cohort = count / coverage_pct × 100. Verify against MČ total population (e.g. Praha 3: 1879 / 0.94 ≈ 2000 children age 3–5 ÷ 80761 total ≈ 2.5 % — plausible for an age-3–5 share). The deficit columns are **not cohort counts**; they're cohort minus available MŠ/ZŠ places. Don't mistake them for cohort projections.

### ipr-prognoza-2024-2050-klicova-zjisteni
- **URL / location:** https://iprpraha.cz/assets/files/files/42d197f039977ec0d1a67165b69f8121.pdf (3.3 MB, 20 pages). Local: `memory/raw/demographics/ipr/ipr_prognoza_2024-2050_klicova_zjisteni.pdf`.
- **Tier:** A
- **What it has:** "Klíčová zjištění" — summary of all 10 chapters with one infographic page per topic. Repeats the headline numbers from the underlying volumes; useful for sanity-checking but no original tables.
- **Format:** PDF.
- **Date checked:** 2026-05-18 — downloaded.
- **Used by:** WP-01 narrative.

### ipr-populacni-vyvoj-2022
- **URL / location:** https://iprpraha.cz/assets/files/files/13aaaf25fa5138605af833330489fdac.pdf (2.7 MB, 28 pages). Local: `memory/raw/demographics/ipr/ipr_populacni_vyvoj_socialni_struktura_2022.pdf`.
- **Tier:** A
- **What it has:** Brabec (2022) — Prague population in European-cities context. **No per-MČ tables** — entirely Prague-aggregate. Kept as cross-reference for the city-level trends narrative.
- **Format:** PDF.
- **Date checked:** 2026-05-18 — downloaded and inspected; not useful for WP-01's per-MČ goal.
- **Used by:** WP-01 background context only.

### csu-vdb
- **URL / location:** https://vdb.czso.cz/vdbvo2/ (likely now also on `csu.gov.cz` under the post-migration scheme) — *still not reached directly*
- **Tier:** A
- **What it has:** ČSÚ Veřejná databáze. Tables in the DEM family (DEM01 *Obyvatelstvo podle pohlaví a věku* etc.) provide population by single year of age × MČ × year for Praha. CSV/XLSX export per table.
- **Format:** HTML UI + CSV/XLSX export.
- **Date checked:** 2026-05-18 — **harness permission denied** before any HTTP request. **Partially superseded by `csu-vekove-slozeni-mc-2011-2025` for the band-level need**, but VDB remains the canonical single-year-of-age source if reachable.
- **Used by:** WP-01.
- **Notes:** Round 3 must verify table IDs and the MČ coding (LAU-2 / `KOD_OBEC`). MČ cut needs explicit configuration.

### csu-demograficka-rocenka-praha
- **URL / location:** https://www.czso.cz/csu/czso/demograficka-rocenka-hl-m-prahy-<year> — *candidate, not reachable in this session*
- **Tier:** A
- **What it has:** Annual "Demografická ročenka hl. m. Prahy". Each edition ships a city-wide PDF plus per-MČ XLSX/CSV with single-year-of-age population, births, migration. Series back to at least 2014.
- **Format:** HTML index → XLSX/CSV files.
- **Date checked:** 2026-05-18 — **harness permission denied**.
- **Used by:** WP-01.
- **Notes:** Probably the single most useful source for the historical half of WP-01.

### opendata-praha
- **URL / location:** https://opendata.praha.eu/ — *candidate, not reachable in this session*
- **Tier:** A
- **What it has:** Prague Open Data portal. Republishes ČSÚ MČ-level demographic slices in CSV with consistent MČ identifiers.
- **Format:** CSV/JSON via CKAN API.
- **Date checked:** 2026-05-18 — **harness permission denied**.
- **Used by:** WP-01.

### geoportal-praha
- **URL / location:** https://www.geoportalpraha.cz/ — *candidate, not reachable in this session*
- **Tier:** A
- **What it has:** Geospatial demographic layers (population by MČ, by ZSJ) maintained by IPR.
- **Format:** Map UI + WFS / CSV.
- **Date checked:** 2026-05-18 — **harness permission denied**.
- **Used by:** WP-01 (cross-check), WP-04 (geometry).

## Tier C — qualitative / sanity-check sources

_(empty)_

## Dead ends

_Sources we checked and decided not to use, with the reason. Saves re-checking._

- **None permanently dead.** Seven candidate hosts (czso.cz, vdb.czso.cz, www.iprpraha.cz, uap.iprpraha.cz, opendata.praha.eu, geoportalpraha.cz, plus WebSearch) were blocked by the harness allowlist in round 2 on 2026-05-18. These are **temporarily unreachable**, not dead. Round 3 must widen the sandbox before retrying.
- **WP-01 round 3 (2026-05-18) — same hosts still blocked.** Even after the dispatch stated allowlists were widened (and project `.claude/settings.json` indeed lists `www.czso.cz`, `czso.cz`, `vdb.czso.cz`, `opendata.praha.eu`, `data.praha.eu`, `opendata.iprpraha.cz`), every WebFetch to those hosts is still rejected with "Permission to use WebFetch has been denied" — and raw `curl` to the same hosts returns HTTP 000 (the sandbox network allowlist is `pypi.org` + `files.pythonhosted.org` only). WebSearch also rejected. **Conclusion: the harness's effective allowlist is narrower than `.claude/settings.json` and excludes every Czech statistical host.** Only `iprpraha.cz` (bare host) works. To unblock, a future round needs either (a) the user runs claude-code with the sandbox disabled (`--dangerously-skip-permissions` or equivalent), (b) the user manually drops ČSÚ files into `memory/raw/demographics/csu/`, or (c) MCP-level fetch tooling not subject to this allowlist.
- **WP-02 round 3 (2026-05-18) — still blocked at the subagent level.** Project-level `.claude/settings.json` was updated to allowlist `isv.gov.cz`, `*.msmt.cz`, the six `praha{3,7,8,9,10,14}.cz` hosts, and `mapaskol.cz` (verified — 28 allow entries present). Despite this, every `WebFetch` and `WebSearch` call from this subagent was rejected with "Permission to use … has been denied" (harness denial, not a network error). `Bash dangerouslyDisableSandbox: true` was also denied. Likely cause: a user-global `~/.claude/settings.json` deny rule, a `settings.local.json`, or a session-level `--allowedTools` overlay that excludes web tools for subagents and overrides the project allows. The `isv.gov.cz/rssz` host is still the correct target; **the blocker is permission scope, not the source**. See `progress/WP-02-schools.md → Round 3 results` for the unblock options.
