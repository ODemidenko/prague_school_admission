# Catchment (spádové obvody) — aggregated

## Status

`streets_to_zs.csv` populated 2026-05-18 from the six raw decree files in
`memory/raw/catchment/`. Parser at `notebooks/wp04_parse/parse.py`. See
`RERUN.md → R-06`.

## Primary source

**Citywide:** *Obecně závazná vyhláška hl. m. Prahy č. 19/2025, o školských
obvodech základních škol*, schválena 11. 12. 2025, **účinná od 1. 1. 2026**.
The text was read from the P6-mirrored copy `vyhlaska-hmp-19-2025_via-P6.pdf`
(citywide, all 22+ MČ). Praha 9 section was read from the DOCX excerpt
`p9_spadova-vyhlaska-1.1.2026.docx` instead — DOCX paragraphs map 1:1 to
streets, eliminating PDF column-flow ambiguity; manual diff against the
citywide P9 section showed equivalent content.

## Schema

| Column | Meaning |
|---|---|
| `mc` | Městská část label, one of `Praha 3 / 7 / 8 / 9 / 10 / 14`. From the "Městská část Praha N" section header in the decree. |
| `street` | Czech street/náměstí/nábřeží name with full diacritics. Verbatim from the decree (UTF-8, no BOM). |
| `house_number_range` | Verbatim house-number specification — empty if the decree assigns the entire street; otherwise the printed clause (e.g. "sudá č. 2-30, lichá č. 1-29", "č. p. 175/8", "(vyjma 137/46)"). **Not parsed into individual numbers** — too brittle and not needed downstream. |
| `red_izo` | RED-IZO of the assigned ZŠ, joining to `memory/aggregated/schools/zs_by_mc.csv`. Empty if the decree's printed school name could not be matched (see `_anomalies.md`). |
| `zs_name` | School name **as printed in the decree** — useful for disambiguation against the rejstřík form (which is often longer and includes the legal address). |
| `source_file` | Filename in `memory/raw/catchment/`. |
| `effective_date` | `2026-01-01` — when the decree text is in force. |

## Coverage matrix (in-scope MČ)

| MČ | Rows (streets) | Distinct ZŠ matched | State non-special ZŠ in `zs_by_mc.csv` | Coverage |
|---|---|---|---|---|
| Praha 3 | 235 | 10 | 10 | 100% |
| Praha 7 | 131 | 6 | 6 | 100% |
| Praha 8 | 527 | 15 | 19 | 78% |
| Praha 9 | 263 | 6 | 6 | 100% |
| Praha 10 | 521 | 14 | 15 | 93% |
| Praha 14 | 276 | 6 | 6 | 100% |

`Total` row count: **1953**.

## Cross-check sources

The per-MČ excerpts (P3, P7, P14 PDFs; P9 DOCX HMP citywide variant) cover the
same legal content per MČ; they were parsed independently and informally
compared during parser development. They are NOT joined to the deliverable —
see them as a verification corpus.

- **Praha 3** (p3_skolske-obvody-2026.pdf): 10 schools, 232 streets (cross-check)
- **Praha 7** (p7_OZV-skolske-obvody-2025.pdf): 6 schools, 131 streets (cross-check)
- **Praha 14** (vyhlaska-19-2025_via-P14.pdf): 6 schools, 276 streets (cross-check)

The P9 streets-only DOCX was used as the primary source for P9 (replaces the
citywide P9 section). The P9 HMP DOCX (`p9_HMP-vyhlaska-1.1.2026.docx`) is
the full-citywide DOCX form — kept for context, not used by the parser.

## Invariant checks

- **Every `red_izo` in the CSV exists in `zs_by_mc.csv`** — PASS.
- **Every state non-special ZŠ in `zs_by_mc.csv` is covered** — 6 missing, see `_anomalies.md`.
- **RED-IZO 600040585 ("Lehovec") lands in `mc=Praha 14`** — PASS.
- **No empty `red_izo` rows from unmatched school headings** — PASS.

## Reproduce

```
cd notebooks/wp04_parse
uv run python parse.py
```

Dependencies (declared in `pyproject.toml`): `pdfplumber`, `python-docx`.
`uv` resolves and installs them into a project venv on first run. **No
network access to the underlying source needed** — all six raw files are
already on disk under `memory/raw/catchment/`. (uv itself needs network to
fetch wheels on first run.)

## Known limitations

- `house_number_range` is left as the raw decree string. Some entries glue
  two ranges into one cell when the decree's PDF wraps a long enumeration
  across multiple lines and the parser couldn't unambiguously split (rare —
  visible in `_anomalies.md` when a street name looks weird).
- The parser keys the school name → `red_izo` join on a hand-curated
  `HAND_OVERRIDES` table (substring tags such as "novoborska", "lupacova").
  The decree prints short brand names ("ZŠ Litvínovská 500") while the
  rejstřík uses longer formal names. If a new ZŠ appears in a future
  amendment, add its tag to the table.
- The two per-MČ PDFs for P7 and P14 are dated 2025-04-01 (the original
  19/2025 decree); their content matches the 2026-01-01 amendment for the
  P7/P14 streets in this snapshot — but a future re-run must re-verify.
