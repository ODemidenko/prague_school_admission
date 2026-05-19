# memory/aggregated/enrolment/

Kraj-level enrolment indicators for **Hlavní město Praha** (NUTS CZ010), pulled from MŠMT's Statistická ročenka školství via the public UI at https://statis.msmt.gov.cz/rocenka/.

## Granularity ceiling

**Kraj-level only.** The yearbook does NOT expose per-MČ or per-school rows for the Praha kraj — confirmed before pulling. Per-school enrolment data is collected centrally in the matrika but treated as personal-data-adjacent and is not openly published. See `progress/WP-03-enrolment.md` for the structural recon.

## File

- `hmp_msmt_yearbook_2005_2025.csv` — 1450 long-format rows.

### Schema

| column | type | meaning |
|---|---|---|
| `school_year` | string | Czech school-year notation, e.g. `2024/2025`. |
| `school_year_ord` | int | The calendar year the school year starts in (2005..2025). Monotonic, strictly increasing, joins naturally against the birth-cohort tables. **Deviates from the task spec wording (rck-integer 1..20)** because the yearbook dropdown includes one non-numeric `rck='5a'` (school year 2010/2011) — using the start-year sidesteps the anomaly without losing any sortability. The original `rck` token is recoverable from `source_url`. |
| `table_code` | string | MŠMT table code: `C1.25.1`, `C1.22.1`, or `C1.4.1`. |
| `table_topic` | string | Short Czech title (`zápis: výsledky`, etc.). |
| `indicator` | string | `<row sub-label> :: <column header>`. Row sub-labels come from the kraj's rowspan group (e.g. `(celkem)`, `poprvé u zápisu`, `přicházejí po odkladu`, `z toho po dodatečném`, `z celku ze spádového obvodu`). Column headers are stitched from the table's multi-row `<th>` block (e.g. `Zapisované děti / celkem`). |
| `value` | string | Raw cell text. May be empty for years that don't carry an indicator. Numeric values are unformatted (no thousands separator). |
| `source_url` | string | Reconstructable POST URL with query-style preview. |
| `snapshot_fetched_at` | string | ISO-8601 UTC timestamp of this run. |

## Coverage matrix

Rows extracted per (table × school year):

| school_year | rck | C1.25.1 zápis | C1.22.1 1.roč×věk | C1.4.1 žáci×ročník |
|---|---|---|---|---|
| 2005/2006 | 1 | 0 | 0 | 15 |
| 2006/2007 | 2 | 0 | 0 | 0 |
| 2007/2008 | 3 | 0 | 0 | 0 |
| 2008/2009 | 4 | 0 | 0 | 0 |
| 2009/2010 | 5 | 0 | 0 | 0 |
| 2010/2011 | 5a | 0 | 0 | 0 |
| 2011/2012 | 6 | 39 | 0 | 0 |
| 2012/2013 | 7 | 39 | 0 | 0 |
| 2013/2014 | 8 | 39 | 0 | 0 |
| 2014/2015 | 9 | 39 | 28 | 32 |
| 2015/2016 | 10 | 39 | 28 | 32 |
| 2016/2017 | 11 | 39 | 28 | 32 |
| 2017/2018 | 12 | 39 | 28 | 32 |
| 2018/2019 | 13 | 39 | 28 | 32 |
| 2019/2020 | 14 | 39 | 28 | 32 |
| 2020/2021 | 15 | 39 | 28 | 32 |
| 2021/2022 | 16 | 65 | 28 | 32 |
| 2022/2023 | 17 | 65 | 28 | 32 |
| 2023/2024 | 18 | 65 | 28 | 32 |
| 2024/2025 | 19 | 65 | 28 | 32 |
| 2025/2026 | 20 | 65 | 28 | 32 |

## Known gaps

- `C1.25.1` rck=`1` (2005/2006) — fetch failed.
- `C1.25.1` rck=`2` (2006/2007) — fetch failed.
- `C1.25.1` rck=`3` (2007/2008) — fetch failed.
- `C1.25.1` rck=`4` (2008/2009) — fetch failed.
- `C1.25.1` rck=`5` (2009/2010) — fetch failed.
- `C1.25.1` rck=`5a` (2010/2011) — fetch failed.
- `C1.22.1` rck=`1` (2005/2006) — fetch failed.
- `C1.22.1` rck=`2` (2006/2007) — fetch failed.
- `C1.22.1` rck=`3` (2007/2008) — fetch failed.
- `C1.22.1` rck=`4` (2008/2009) — fetch failed.
- `C1.22.1` rck=`5` (2009/2010) — fetch failed.
- `C1.22.1` rck=`5a` (2010/2011) — fetch failed.
- `C1.22.1` rck=`6` (2011/2012) — fetch failed.
- `C1.22.1` rck=`7` (2012/2013) — fetch failed.
- `C1.22.1` rck=`8` (2013/2014) — fetch failed.
- `C1.4.1` rck=`2` (2006/2007) — fetch failed.
- `C1.4.1` rck=`3` (2007/2008) — fetch failed.
- `C1.4.1` rck=`4` (2008/2009) — fetch failed.
- `C1.4.1` rck=`5` (2009/2010) — fetch failed.
- `C1.4.1` rck=`5a` (2010/2011) — fetch failed.
- `C1.4.1` rck=`6` (2011/2012) — fetch failed.
- `C1.4.1` rck=`7` (2012/2013) — fetch failed.
- `C1.4.1` rck=`8` (2013/2014) — fetch failed.

## Verification anchor

Re-runners: after a successful run, the following grep must return a row. The exact value may shift if MŠMT republishes the snapshot — bump this anchor if so:

```
grep -F '2025/2026,20,C1.25.1' hmp_msmt_yearbook_2005_2025.csv | grep -F 'Zapisované děti / celkem'
```

Expected: a row for `(celkem) :: Zapisované děti / celkem` with value `25075` (Hlavní město Praha, school year 2025/2026 — total zápis attendees).

Snapshot fetched at: `2026-05-19T12:23:11Z`.