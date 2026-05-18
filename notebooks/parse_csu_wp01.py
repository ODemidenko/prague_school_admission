"""
WP-01 Round 4 — parse two ČSÚ XLSX files into the project's aggregated CSVs.

Inputs (already on disk, downloaded by the main agent):
  memory/raw/demographics/csu/1_PHA_VEK_obyv_mc.xlsx
  memory/raw/demographics/csu/Casova_rada_MC.xlsx

Outputs:
  memory/aggregated/demographics/children_by_age_mc_year.csv   (APPENDED, not overwritten)
  memory/aggregated/demographics/births_by_mc_year.csv         (NEW)

Run with:  uv run --with openpyxl --no-project python3 notebooks/parse_csu_wp01.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "memory" / "raw" / "demographics" / "csu"
AGG = ROOT / "memory" / "aggregated" / "demographics"

AGE_XLSX = RAW / "1_PHA_VEK_obyv_mc.xlsx"
TS_XLSX = RAW / "Casova_rada_MC.xlsx"

CHILDREN_CSV = AGG / "children_by_age_mc_year.csv"
BIRTHS_CSV = AGG / "births_by_mc_year.csv"

# Targets — order preserved for stable CSV
TARGET_MCS = ["Praha 3", "Praha 7", "Praha 8", "Praha 9", "Praha 10", "Praha 14"]

# Pre-existing IPR mc_code values (LAU-2 family) — keep CSV joinable with IPR rows.
# The ČSÚ XLSX uses KOD_ZUJ (a different codeset). We store the IPR/LAU code in
# the `mc_code` column and stuff the ČSÚ KOD_ZUJ into `notes` for traceability.
IPR_MC_CODE = {
    "Praha 3": "547107",
    "Praha 7": "547141",
    "Praha 8": "547158",
    "Praha 9": "547166",
    "Praha 10": "547174",
    "Praha 14": "547221",
}


CHILDREN_HEADER = [
    "year",
    "reference_date",
    "mc",
    "mc_code",
    "age",
    "age_band_min",
    "age_band_max",
    "count",
    "count_kind",
    "coverage_pct",
    "source_slug",
    "kind",
    "notes",
]

BIRTHS_HEADER = [
    "year",
    "reference_date",
    "mc",
    "mc_code",
    "count",
    "count_kind",
    "source_slug",
    "kind",
    "notes",
]


def parse_age_xlsx() -> list[dict]:
    """Extract 5-year age bands 0-4, 5-9, 10-14, 15-19 per MČ per year.

    The XLSX has one sheet per year (2011..2025). Header layout changes in 2020:
    pre-2020 -> name col = 3, kod_zuj col = 2. From 2020 onward -> name col = 1,
    kod_zuj col = 0. Band columns 5..8 are stable (first occurrence; the same
    band labels repeat at cols 25.. and 45.. for the male/female blocks).
    """
    wb = load_workbook(AGE_XLSX, data_only=True, read_only=True)
    out: list[dict] = []
    for sheet_name in wb.sheetnames:
        year = int(sheet_name)
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True))
        hdr = rows[3]
        if hdr[0] == "KOD_ZUJ":
            kod_col, name_col = 0, 1
        else:
            kod_col, name_col = 2, 3
        # First occurrence of each band (Celkem section)
        band_cols: dict[tuple[int, int], int] = {}
        seen = set()
        for i, v in enumerate(hdr):
            if isinstance(v, str):
                key = v.replace("–", "-")
                if key in {"0-4", "5-9", "10-14", "15-19"} and key not in seen:
                    seen.add(key)
                    lo, hi = (int(x) for x in key.split("-"))
                    band_cols[(lo, hi)] = i
        for r in rows[4:]:
            name = r[name_col]
            if name not in TARGET_MCS:
                continue
            csu_kod = r[kod_col]
            for (lo, hi), col in band_cols.items():
                cnt = r[col]
                if cnt is None:
                    continue
                out.append(
                    {
                        "year": year,
                        "reference_date": f"{year}-12-31",
                        "mc": name,
                        "mc_code": IPR_MC_CODE[name],
                        "age": "",
                        "age_band_min": lo,
                        "age_band_max": hi,
                        "count": int(cnt),
                        "count_kind": "population",
                        "coverage_pct": "",
                        "source_slug": "csu-vekove-slozeni-mc-2011-2025",
                        "kind": "historical",
                        "notes": (
                            f"ČSÚ KOD_ZUJ={csu_kod}; sheet '{sheet_name}'; "
                            f"5-year band (single-year-of-age not available in this dataset); "
                            f"row 'Praha N' / col '{lo}-{hi}'"
                        ),
                    }
                )
    return out


def parse_births_xlsx() -> list[dict]:
    """Extract Živě narození (live births) per MČ per year from Casova_rada_MC."""
    wb = load_workbook(TS_XLSX, data_only=True, read_only=True)
    out: list[dict] = []
    for sheet_name in wb.sheetnames:
        year = int(sheet_name)
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(values_only=True, max_row=35))
        header = rows[2]
        # column index per MČ; some layouts could shift, so look up by name
        mc_cols: dict[str, int] = {}
        for mc in TARGET_MCS:
            try:
                mc_cols[mc] = header.index(mc)
            except ValueError:
                pass
        # find row labelled 'Živě narození'
        kod_row = None
        born_row = None
        for i, r in enumerate(rows):
            lab = r[0]
            if isinstance(lab, str):
                if lab.startswith("Kód ZÚJ"):
                    kod_row = r
                if "Živě narození" in lab:
                    born_row = r
                    break
        if born_row is None:
            continue
        for mc, col in mc_cols.items():
            val = born_row[col]
            if val is None:
                continue
            csu_kod = kod_row[col] if kod_row else ""
            out.append(
                {
                    "year": year,
                    "reference_date": f"{year}-12-31",
                    "mc": mc,
                    "mc_code": IPR_MC_CODE[mc],
                    "count": int(val),
                    "count_kind": "live_births",
                    "source_slug": "csu-casova-rada-mc-2004-2025",
                    "kind": "historical",
                    "notes": (
                        f"ČSÚ KOD_ZUJ={csu_kod}; sheet '{sheet_name}'; "
                        f"row 'Živě narození / Live births'"
                    ),
                }
            )
    return out


def append_children_csv(rows: list[dict]) -> int:
    """Append to the existing children_by_age_mc_year.csv preserving IPR rows."""
    assert CHILDREN_CSV.exists(), "Existing IPR file must be present — refusing to create from scratch"
    # Verify header matches what we expect
    with CHILDREN_CSV.open("r", encoding="utf-8") as f:
        existing_header = next(csv.reader(f))
    assert existing_header == CHILDREN_HEADER, f"Schema drift: {existing_header}"
    with CHILDREN_CSV.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CHILDREN_HEADER)
        for r in rows:
            w.writerow(r)
    return len(rows)


def write_births_csv(rows: list[dict]) -> int:
    with BIRTHS_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BIRTHS_HEADER)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return len(rows)


def main() -> None:
    age_rows = parse_age_xlsx()
    n_age = append_children_csv(age_rows)
    print(f"Appended {n_age} age-band rows to {CHILDREN_CSV}")

    birth_rows = parse_births_xlsx()
    n_births = write_births_csv(birth_rows)
    print(f"Wrote {n_births} birth rows to {BIRTHS_CSV}")


if __name__ == "__main__":
    main()
