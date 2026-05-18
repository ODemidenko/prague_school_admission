# memory/raw/demographics/ — origin log

Created in WP-01 round 2 (2026-05-18); first downloads landed in round 3 (2026-05-18, same dispatch day).

Subfolder convention:
- `csu/` — files from ČSÚ (csu.gov.cz; legacy czso.cz). **Populated in round 4 (2026-05-18).**
- `ipr/` — files from IPR Praha. Populated in round 3.
- `opendata-praha/` — files from opendata.praha.eu and geoportalpraha.cz. Still empty.

## Files

### ipr/

| Filename | Source URL | Fetched | Pages | Note |
|---|---|---|---|---|
| `ipr_prognoza_2024-2050_klicova_zjisteni.pdf` | https://iprpraha.cz/assets/files/files/42d197f039977ec0d1a67165b69f8121.pdf | 2026-05-18 | 20 | Key findings summary, all 10 chapters. 3.3 MB. |
| `ipr_prognoza_2024-2050_uvod_a_obyvatelstvo.pdf` | https://iprpraha.cz/assets/files/files/c2a6a24d6250739cf644c646eed3b77a.pdf | 2026-05-18 | 46 | Population chapter — methodology, fertility/mortality assumptions, MČ totals 2023/2030/2050 (Příloha P.2.04 on pp. 38–41). 10.4 MB. |
| `ipr_prognoza_2024-2050_vzdelavani.pdf` | https://iprpraha.cz/assets/files/files/48480fbb0bfe91c363bdbfca1d658a6d.pdf | 2026-05-18 | 71 | Education chapter — MŠ (age 3–5) capacity-deficit table on pp. 59–62 (Příloha P.3.02), ZŠ (age 6–14) on pp. 63–66 (Příloha P.3.04), SŠ (age 15–18) on p. 67. Both tables include "count of children in walking distance" + coverage %. 25.9 MB. |
| `ipr_populacni_vyvoj_socialni_struktura_2022.pdf` | https://iprpraha.cz/assets/files/files/13aaaf25fa5138605af833330489fdac.pdf | 2026-05-18 | 28 | 2022 study by Brabec on Prague in European context. **No per-MČ tables.** Kept for cross-reference. 2.7 MB. |

All four PDFs are first editions / current versions as of the iprpraha.cz landing page on 2026-05-18.

### csu/

Populated in round 4 (2026-05-18). ČSÚ rebranded its primary domain from `czso.cz` to `csu.gov.cz` (the old domain still 302-redirects). The main agent fetched both files directly via WebFetch on `csu.gov.cz`; subagent parsing was offline.

| Filename | Source URL | Fetched | Sheets | Note |
|---|---|---|---|---|
| `1_PHA_VEK_obyv_mc.xlsx` | https://csu.gov.cz/docs/107839/afefbae8-c12f-7944-fe52-ce39f88da593/1_PHA_VEK_obyv_mc.xlsx?version=1.5 | 2026-05-18 | 15 (2011..2025) | "Věkové složení obyvatel v městských částech Prahy v letech 2011-2025". One sheet per year. Per MČ × **5-year age bands** (0–4, 5–9, …, 85+) split into Celkem / Muži / Ženy blocks. ~379 KB. Single-year-of-age is **not** present in this file. |
| `Casova_rada_MC.xlsx` | https://csu.gov.cz/docs/107839/4473deb4-e987-202b-1e15-740fcaccfba3/Casova_rada_MC.xlsx?version=1.9 | 2026-05-18 | 22 (2004..2025) | "Souhrnné informace o 57 městských částech 2004-2025". One sheet per year, rows = indicators, columns = MČ. Includes Živě narození (live births, row 23) — the birth cohort primitive. ~1.1 MB. |

### opendata-praha/

Empty. `opendata.praha.eu`, `data.praha.eu`, `geoportalpraha.cz`, `uap.iprpraha.cz`, `opendata.iprpraha.cz`, `app.iprpraha.cz` all return harness-level permission denied for WebFetch and time out for raw curl.

## Reachability map for round 3 (2026-05-18)

| Host | WebFetch | curl direct | Notes |
|---|---|---|---|
| iprpraha.cz | OK | — | Only host that consistently works. Assets at `/assets/files/files/<hash>.pdf` are downloadable. |
| www.iprpraha.cz | denied | times out | — |
| uap.iprpraha.cz | denied | times out | Holds the interactive dashboards `uap.iprpraha.cz/pov` where single-year-of-age × MČ data lives. Unreachable. |
| opendata.iprpraha.cz | denied | — | — |
| www.czso.cz, czso.cz, vdb.czso.cz | denied | times out | Project settings.json lists these as allowed, harness denies anyway. |
| opendata.praha.eu, data.praha.eu | denied | times out | — |
| geoportalpraha.cz | denied | — | — |
| www.praha9.cz | denied | — | MČ self-government pages also blocked. |
| WebSearch | denied | n/a | The tool returns permission denied for every query. |
