"""WP-03 (fallback B′) — MŠMT statistical yearbook downloader + parser.

Pulls 20 years × 3 tables × kraj "Hlavní město Praha" from
https://statis.msmt.gov.cz/rocenka/ and writes one long-format CSV.

Run from the repo root:
    uv run --no-project python3 notebooks/wp03_parse/fetch_statis.py

stdlib-only (urllib + html.parser). No third-party deps. Idempotent — the
raw HTML cache and the CSV are overwritten on every run.

Granularity ceiling: kraj. The yearbook does NOT expose per-MČ or
per-school rows for the Praha kraj. This was confirmed before the script
was written; do not try to bend it.
"""

from __future__ import annotations

import csv
import html as html_lib
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "memory" / "raw" / "enrolment" / "statis_msmt"
AGG_DIR = REPO_ROOT / "memory" / "aggregated" / "enrolment"
CSV_OUT = AGG_DIR / "hmp_msmt_yearbook_2005_2025.csv"
README_OUT = AGG_DIR / "_README.md"

ENDPOINT = "https://statis.msmt.gov.cz/rocenka/rocenka.asp"
USER_AGENT = (
    "Mozilla/5.0 (compatible; demography_prague WP-03 research bot; "
    "stdlib urllib)"
)

# rck → school_year. rck '5a' is the 2010/2011 outlier (non-numeric in the
# dropdown). We keep it in the run set; for ordering we assign ord=5.5 → 6
# via a manual map.
RCK_TO_YEAR: dict[str, str] = {
    "1": "2005/2006",
    "2": "2006/2007",
    "3": "2007/2008",
    "4": "2008/2009",
    "5": "2009/2010",
    "5a": "2010/2011",
    "6": "2011/2012",
    "7": "2012/2013",
    "8": "2013/2014",
    "9": "2014/2015",
    "10": "2015/2016",
    "11": "2016/2017",
    "12": "2017/2018",
    "13": "2018/2019",
    "14": "2019/2020",
    "15": "2020/2021",
    "16": "2021/2022",
    "17": "2022/2023",
    "18": "2023/2024",
    "19": "2024/2025",
    "20": "2025/2026",
}

# Ordinal mapping for the CSV. We use the calendar year that the school
# year starts in (2005, 2006, …, 2025) — strictly monotonic, never
# collides with the '5a' rck-id anomaly, and joins naturally against the
# birth-cohort tables in `memory/aggregated/demographics/`.
RCK_TO_ORD: dict[str, int] = {
    rck: int(sy.split("/")[0]) for rck, sy in RCK_TO_YEAR.items()
}

# Three target tables (chapter C — Základní vzdělávání).
TABLES: dict[str, str] = {
    "C1.25.1": "zápis: výsledky",
    "C1.22.1": "1. ročník: nově přijatí podle věku",
    "C1.4.1": "žáci v ročnících",
}

KRAJ_LABEL = "Hlavní město Praha"
KRAJ_CODE = "CZ010"
SLEEP_BETWEEN = 0.5  # seconds between POSTs — be polite.

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def post_yearbook(tab: str, rck: str) -> bytes:
    """POST one (tab, rck) pair to rocenka.asp and return raw bytes.

    Body is form-encoded; response is windows-1250.
    """
    body = urllib.parse.urlencode(
        {"kapit": "C", "tab": tab, "rck": rck}
    ).encode("ascii")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "User-Agent": USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,*/*",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_and_cache(tab: str, rck: str) -> tuple[Path, str] | None:
    """Fetch one page, write UTF-8 transcoded HTML to disk, return (path, text).

    Returns None on hard failure (network error, empty body).
    """
    out_path = RAW_DIR / f"{tab}_rck{rck}.html"
    try:
        raw = post_yearbook(tab, rck)
    except Exception as exc:  # noqa: BLE001 — log and continue
        print(f"  [WARN] fetch failed tab={tab} rck={rck}: {exc}", file=sys.stderr)
        return None
    if len(raw) < 200:
        print(
            f"  [WARN] suspiciously short body tab={tab} rck={rck} "
            f"({len(raw)} bytes)",
            file=sys.stderr,
        )
    try:
        text = raw.decode("windows-1250")
    except UnicodeDecodeError as exc:
        print(f"  [WARN] decode failed tab={tab} rck={rck}: {exc}", file=sys.stderr)
        return None
    out_path.write_text(text, encoding="utf-8")
    return out_path, text


# ---------------------------------------------------------------------------
# HTML → 2D table grid
# ---------------------------------------------------------------------------


@dataclass
class Cell:
    """One logical cell (after rowspan/colspan expansion)."""

    text: str
    css: str = ""  # CSS class — useful to distinguish label vs data vs header
    is_header: bool = False


@dataclass
class GridTable:
    """A rectangular grid with rowspan/colspan expansion done."""

    rows: list[list[Cell | None]] = field(default_factory=list)

    def cell(self, r: int, c: int) -> Cell | None:
        if r < 0 or r >= len(self.rows):
            return None
        row = self.rows[r]
        if c < 0 or c >= len(row):
            return None
        return row[c]


class TableExtractor(HTMLParser):
    """Pull every <table> in the document, expand rowspan/colspan to a grid.

    Designed for the statis.msmt yearbook pages: simple flat tables, no
    nested tables inside the data table we care about. Form-selector tables
    appear before the data table; we capture all and let the caller pick.
    """

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[GridTable] = []
        self._table_stack: list[GridTable] = []
        self._cur_row: list[Cell | None] | None = None
        self._cur_cell_text: list[str] = []
        self._cur_cell_attrs: dict[str, str] | None = None
        self._cur_cell_pending_span: tuple[int, int] = (1, 1)
        self._cur_cell_is_header: bool = False
        self._in_cell: bool = False
        # Track which row-list instances have already had a <tr> open
        # against them (so a sibling <tr> doesn't re-occupy a row that's
        # already populated only by rowspan-continuation cells).
        self._opened_rows: set[int] = set()

    # --- helpers -----------------------------------------------------------

    @staticmethod
    def _attr_int(attrs_dict: dict[str, str], key: str, default: int = 1) -> int:
        try:
            return int(attrs_dict.get(key, default))
        except (ValueError, TypeError):
            return default

    def _place_cell(self, cell: Cell, rowspan: int, colspan: int) -> None:
        """Drop the cell into the current row of the current table, walking
        past columns already filled by earlier rowspans."""
        if not self._table_stack or self._cur_row is None:
            return
        table = self._table_stack[-1]
        # We're inside an open <tr>; its row was already appended to
        # table.rows at start-tag time. Find which index it occupies.
        # (It may not be the last row if a rowspan from a *previous* row
        # pre-filled a future row that an empty <tr></tr> then "claimed".)
        try:
            r_idx = next(
                i for i in range(len(table.rows) - 1, -1, -1)
                if table.rows[i] is self._cur_row
            )
        except StopIteration:
            r_idx = len(table.rows) - 1
        # Find first free column in the current row
        c = 0
        while c < len(self._cur_row) and self._cur_row[c] is not None:
            c += 1
        # Pad current row to width c
        while len(self._cur_row) < c:
            self._cur_row.append(None)
        # Place the cell across colspan columns, marking continuation cells
        for dc in range(colspan):
            while len(self._cur_row) <= c + dc:
                self._cur_row.append(None)
            self._cur_row[c + dc] = cell if dc == 0 else Cell(
                text="", css=cell.css, is_header=cell.is_header
            )
        # For rowspan>1, pre-fill future rows
        if rowspan > 1:
            for dr in range(1, rowspan):
                target_r = r_idx + dr
                while len(table.rows) <= target_r:
                    table.rows.append([])
                target_row = table.rows[target_r]
                # Ensure row is wide enough
                while len(target_row) < c + colspan:
                    target_row.append(None)
                # Mark the spanned cells as continuation (same text, so the
                # row-label survives row-by-row reads)
                for dc in range(colspan):
                    if target_row[c + dc] is None:
                        target_row[c + dc] = Cell(
                            text=cell.text if dc == 0 else "",
                            css=cell.css,
                            is_header=cell.is_header,
                        )

    # --- HTMLParser hooks --------------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        if tag == "table":
            self._table_stack.append(GridTable())
        elif tag == "tr" and self._table_stack:
            table = self._table_stack[-1]
            # Always create a fresh row for each <tr>. Rowspan continuation
            # cells are placed by _place_cell into future row indices,
            # creating "virtual" rows. To distinguish virtual-only rows
            # (which the next real <tr> should absorb) from already-
            # consumed rows, we track whether a row has had a <tr> open
            # against it. The current strategy: at <tr> start, look for
            # the first un-opened row at or beyond len-1 that contains
            # rowspan continuations; if found, attach to it. Otherwise
            # append a new empty row.
            #
            # Crucially this must work for the C1.25.1 layout where the
            # Praha block has CZ010 with rowspan=5 plus a separate "v tom"
            # cell with rowspan=3 — both producing pre-filled future
            # rows that real <tr>s should slot into.
            attached = False
            # Scan from the first un-opened existing row forward (these
            # are the rowspan-pre-filled rows waiting for content).
            for idx in range(len(table.rows)):
                row = table.rows[idx]
                if id(row) in self._opened_rows:
                    continue
                # Attach the <tr> to the first un-opened row that has at
                # least one rowspan-continuation cell.
                if any(c is not None for c in row):
                    self._cur_row = row
                    attached = True
                    break
            if not attached:
                self._cur_row = []
                table.rows.append(self._cur_row)
            self._opened_rows.add(id(self._cur_row))
        elif tag in ("td", "th") and self._cur_row is not None:
            self._in_cell = True
            self._cur_cell_text = []
            self._cur_cell_attrs = attrs_dict
            self._cur_cell_pending_span = (
                self._attr_int(attrs_dict, "rowspan", 1),
                self._attr_int(attrs_dict, "colspan", 1),
            )
            self._cur_cell_is_header = tag == "th"
        elif tag == "br" and self._in_cell:
            self._cur_cell_text.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "table" and self._table_stack:
            self.tables.append(self._table_stack.pop())
        elif tag == "tr":
            self._cur_row = None
        elif tag in ("td", "th") and self._in_cell:
            text = " ".join("".join(self._cur_cell_text).split())
            css = (self._cur_cell_attrs or {}).get("class", "")
            cell = Cell(text=text, css=css, is_header=self._cur_cell_is_header)
            rowspan, colspan = self._cur_cell_pending_span
            self._place_cell(cell, rowspan, colspan)
            self._in_cell = False
            self._cur_cell_text = []
            self._cur_cell_attrs = None

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cur_cell_text.append(data)

    def handle_entityref(self, name: str) -> None:  # &nbsp; etc.
        if self._in_cell:
            self._cur_cell_text.append(html_lib.unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if self._in_cell:
            self._cur_cell_text.append(html_lib.unescape(f"&#{name};"))


# ---------------------------------------------------------------------------
# Extract Praha rows from a parsed grid
# ---------------------------------------------------------------------------


def _find_data_table(tables: list[GridTable]) -> GridTable | None:
    """Pick the table that contains the literal 'Hlavní město Praha'."""
    for t in tables:
        for row in t.rows:
            for cell in row:
                if cell and KRAJ_LABEL in cell.text:
                    return t
    return None


def _collect_header_columns(table: GridTable) -> list[str]:
    """Walk header rows (those with css class containing 'hlav') and build
    one composite label per data column by joining the texts top-to-bottom.

    After rowspan expansion each column index sees one (possibly repeated)
    header text per header row — joining unique non-empty strings yields a
    self-documenting column title like
    "Zapisované děti / celkem" or "Školy".
    """
    header_row_indices: list[int] = []
    for r_idx, row in enumerate(table.rows):
        if not row:
            continue
        # A header row is one where every non-None cell is_header or has
        # css containing 'hlav'. We allow rowspan-continuation cells.
        non_none = [c for c in row if c is not None]
        if not non_none:
            continue
        all_header = all(("hlav" in (c.css or "")) for c in non_none)
        if all_header:
            header_row_indices.append(r_idx)
        else:
            # Stop scanning once we hit the first non-header row.
            if header_row_indices:
                break
    if not header_row_indices:
        return []
    max_width = max(len(table.rows[r]) for r in header_row_indices)
    columns: list[str] = []
    for c in range(max_width):
        seen: list[str] = []
        for r in header_row_indices:
            row = table.rows[r]
            cell = row[c] if c < len(row) else None
            if cell is not None:
                t = cell.text
                if t and (not seen or seen[-1] != t):
                    seen.append(t)
        columns.append(" / ".join(seen))
    return columns


def _is_data_cell(cell: Cell | None) -> bool:
    if cell is None:
        return False
    return "dataC" in (cell.css or "")


def _is_label_cell(cell: Cell | None) -> bool:
    if cell is None:
        return False
    return "levyC" in (cell.css or "")


def extract_praha_rows(html_text: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Parse one yearbook page; return (column_headers, [(row_label, [values])]).

    row_label is the composite of left-side label cells (label hierarchy,
    e.g. "Hlavní město Praha / poprvé u zápisu"). values are the dataC
    strings, in column order.
    """
    parser = TableExtractor()
    parser.feed(html_text)
    table = _find_data_table(parser.tables)
    if table is None:
        return [], []
    columns = _collect_header_columns(table)

    # Find the rowspan group anchored at the Hlavní město Praha label.
    # The Praha label may span multiple sub-rows (Celkem / poprvé / po
    # odkladu / …). Because _place_cell pre-fills rowspan continuations
    # with the source cell's text, the same "Hlavní město Praha" text
    # appears in every row of the group at the same column index. We detect
    # group end by either:
    #   - the kraj label cell at that column no longer reading
    #     "Hlavní město Praha", or
    #   - the NUTS-code cell (CZ010) no longer matching (most robust
    #     signal — code never repeats across kraje).
    praha_start: int | None = None
    praha_label_col: int | None = None
    praha_code_col: int | None = None
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row):
            if cell is not None and KRAJ_LABEL == cell.text.strip():
                praha_start = r_idx
                praha_label_col = c_idx
            if cell is not None and KRAJ_CODE == cell.text.strip():
                if praha_start == r_idx:
                    praha_code_col = c_idx
        if praha_start is not None and praha_label_col is not None:
            break
    if praha_start is None:
        return columns, []

    rows_out: list[tuple[str, list[str]]] = []
    for r_idx in range(praha_start, len(table.rows)):
        row = table.rows[r_idx]
        # End-of-group test: the anchoring kraj cell (label OR code) must
        # still read its Praha value. If neither anchor is preserved at the
        # original column, we've left the Praha rowspan group.
        if r_idx > praha_start:
            label_cell = (
                row[praha_label_col]
                if praha_label_col is not None and praha_label_col < len(row)
                else None
            )
            code_cell = (
                row[praha_code_col]
                if praha_code_col is not None and praha_code_col < len(row)
                else None
            )
            label_ok = label_cell is not None and label_cell.text.strip() == KRAJ_LABEL
            code_ok = code_cell is not None and code_cell.text.strip() == KRAJ_CODE
            if not (label_ok or code_ok):
                break
        # Compose row label: every distinct non-empty levyC text, in order.
        labels: list[str] = []
        for cell in row:
            if cell is None:
                continue
            if _is_label_cell(cell) and cell.text:
                t = cell.text.strip()
                if not labels or labels[-1] != t:
                    labels.append(t)
        # Strip the kraj label itself and the NUTS code if present.
        labels = [l for l in labels if l and l != KRAJ_LABEL and l != KRAJ_CODE]
        # Collect data cells in left-to-right order.
        values = [cell.text for cell in row if cell is not None and _is_data_cell(cell)]
        if not values:
            continue
        # `v tom` is a hierarchical separator (outer rowspan continuation)
        # not a meaningful sub-row name. Collapse a bare ["v tom"] → "(celkem)"
        # so the (celkem) row across all years and tables stays consistent.
        if labels == ["v tom"]:
            labels = []
        row_label = " / ".join(labels) if labels else "(celkem)"
        rows_out.append((row_label, values))
    return columns, rows_out


# ---------------------------------------------------------------------------
# Long-format CSV emission
# ---------------------------------------------------------------------------


@dataclass
class LongRow:
    school_year: str
    school_year_ord: int
    table_code: str
    table_topic: str
    indicator: str
    value: str
    source_url: str
    snapshot_fetched_at: str


def _to_long_rows(
    tab: str,
    topic: str,
    rck: str,
    columns: list[str],
    rows: list[tuple[str, list[str]]],
    snapshot_iso: str,
) -> list[LongRow]:
    """Cartesian (sub-row × column) → one LongRow each."""
    out: list[LongRow] = []
    sy = RCK_TO_YEAR[rck]
    ord_ = RCK_TO_ORD[rck]
    # The first columns of `columns` are the row-label headers (Území,
    # NUTS), which have no matching dataC values. Align by taking the last
    # N columns where N = len(values).
    for row_label, values in rows:
        n = len(values)
        col_names = columns[-n:] if len(columns) >= n else columns[:]
        # Pad if mismatch (shouldn't happen, but be defensive).
        while len(col_names) < n:
            col_names.append(f"col_{len(col_names)+1}")
        for col_name, value in zip(col_names, values):
            indicator = f"{row_label} :: {col_name}".strip()
            out.append(
                LongRow(
                    school_year=sy,
                    school_year_ord=ord_,
                    table_code=tab,
                    table_topic=topic,
                    indicator=indicator,
                    value=value,
                    source_url=(
                        f"{ENDPOINT}?kapit=C&tab={tab}&rck={rck}"
                    ),
                    snapshot_fetched_at=snapshot_iso,
                )
            )
    return out


def write_csv(rows: Iterable[LongRow], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "school_year",
                "school_year_ord",
                "table_code",
                "table_topic",
                "indicator",
                "value",
                "source_url",
                "snapshot_fetched_at",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    r.school_year,
                    r.school_year_ord,
                    r.table_code,
                    r.table_topic,
                    r.indicator,
                    r.value,
                    r.source_url,
                    r.snapshot_fetched_at,
                ]
            )
            n += 1
    return n


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    AGG_DIR.mkdir(parents=True, exist_ok=True)
    snapshot_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    all_rows: list[LongRow] = []
    coverage: dict[tuple[str, str], int] = {}  # (tab, rck) -> n_rows
    failures: list[tuple[str, str, str]] = []  # (tab, rck, reason)

    total = len(TABLES) * len(RCK_TO_YEAR)
    i = 0
    for tab, topic in TABLES.items():
        for rck in RCK_TO_YEAR.keys():
            i += 1
            print(f"[{i:>2}/{total}] tab={tab} rck={rck}  ({RCK_TO_YEAR[rck]})")
            result = fetch_and_cache(tab, rck)
            time.sleep(SLEEP_BETWEEN)
            if result is None:
                failures.append((tab, rck, "fetch failed"))
                coverage[(tab, rck)] = 0
                continue
            _, text = result
            try:
                cols, rows = extract_praha_rows(text)
            except Exception as exc:  # noqa: BLE001 — keep going
                failures.append((tab, rck, f"parse error: {exc}"))
                coverage[(tab, rck)] = 0
                continue
            if not rows:
                failures.append((tab, rck, "no Praha row"))
                coverage[(tab, rck)] = 0
                continue
            long_rows = _to_long_rows(tab, topic, rck, cols, rows, snapshot_iso)
            all_rows.extend(long_rows)
            coverage[(tab, rck)] = len(long_rows)

    n_written = write_csv(all_rows, CSV_OUT)
    print(f"Wrote {n_written} rows → {CSV_OUT.relative_to(REPO_ROOT)}")
    if failures:
        print(f"  {len(failures)} (tab, rck) combos produced no rows:")
        for tab, rck, reason in failures:
            print(f"    - {tab} / rck={rck} / {RCK_TO_YEAR.get(rck, '?')}: {reason}")

    # Write the _README.md sidecar with coverage matrix.
    _write_readme(coverage, failures, snapshot_iso, n_written)
    return 0


def _write_readme(
    coverage: dict[tuple[str, str], int],
    failures: list[tuple[str, str, str]],
    snapshot_iso: str,
    n_rows: int,
) -> None:
    lines: list[str] = []
    lines.append("# memory/aggregated/enrolment/")
    lines.append("")
    lines.append(
        "Kraj-level enrolment indicators for **Hlavní město Praha** (NUTS "
        "CZ010), pulled from MŠMT's Statistická ročenka školství via the "
        "public UI at https://statis.msmt.gov.cz/rocenka/."
    )
    lines.append("")
    lines.append("## Granularity ceiling")
    lines.append("")
    lines.append(
        "**Kraj-level only.** The yearbook does NOT expose per-MČ or "
        "per-school rows for the Praha kraj — confirmed before pulling. "
        "Per-school enrolment data is collected centrally in the matrika "
        "but treated as personal-data-adjacent and is not openly published. "
        "See `progress/WP-03-enrolment.md` for the structural recon."
    )
    lines.append("")
    lines.append("## File")
    lines.append("")
    lines.append(f"- `hmp_msmt_yearbook_2005_2025.csv` — {n_rows} long-format rows.")
    lines.append("")
    lines.append("### Schema")
    lines.append("")
    lines.append("| column | type | meaning |")
    lines.append("|---|---|---|")
    lines.append(
        "| `school_year` | string | Czech school-year notation, e.g. "
        "`2024/2025`. |"
    )
    lines.append(
        "| `school_year_ord` | int | The calendar year the school year "
        "starts in (2005..2025). Monotonic, strictly increasing, joins "
        "naturally against the birth-cohort tables. **Deviates from the "
        "task spec wording (rck-integer 1..20)** because the yearbook "
        "dropdown includes one non-numeric `rck='5a'` (school year "
        "2010/2011) — using the start-year sidesteps the anomaly without "
        "losing any sortability. The original `rck` token is recoverable "
        "from `source_url`. |"
    )
    lines.append(
        "| `table_code` | string | MŠMT table code: `C1.25.1`, `C1.22.1`, "
        "or `C1.4.1`. |"
    )
    lines.append(
        "| `table_topic` | string | Short Czech title (`zápis: výsledky`, "
        "etc.). |"
    )
    lines.append(
        "| `indicator` | string | `<row sub-label> :: <column header>`. "
        "Row sub-labels come from the kraj's rowspan group (e.g. "
        "`(celkem)`, `poprvé u zápisu`, `přicházejí po odkladu`, "
        "`z toho po dodatečném`, `z celku ze spádového obvodu`). Column "
        "headers are stitched from the table's multi-row `<th>` block "
        "(e.g. `Zapisované děti / celkem`). |"
    )
    lines.append("| `value` | string | Raw cell text. May be empty for years that don't carry an indicator. Numeric values are unformatted (no thousands separator). |")
    lines.append("| `source_url` | string | Reconstructable POST URL with query-style preview. |")
    lines.append("| `snapshot_fetched_at` | string | ISO-8601 UTC timestamp of this run. |")
    lines.append("")
    lines.append("## Coverage matrix")
    lines.append("")
    lines.append("Rows extracted per (table × school year):")
    lines.append("")
    lines.append(
        "| school_year | rck | C1.25.1 zápis | C1.22.1 1.roč×věk | "
        "C1.4.1 žáci×ročník |"
    )
    lines.append("|---|---|---|---|---|")
    for rck, sy in RCK_TO_YEAR.items():
        c1251 = coverage.get(("C1.25.1", rck), 0)
        c1221 = coverage.get(("C1.22.1", rck), 0)
        c141 = coverage.get(("C1.4.1", rck), 0)
        lines.append(f"| {sy} | {rck} | {c1251} | {c1221} | {c141} |")
    lines.append("")
    if failures:
        lines.append("## Known gaps")
        lines.append("")
        for tab, rck, reason in failures:
            lines.append(
                f"- `{tab}` rck=`{rck}` ({RCK_TO_YEAR.get(rck, '?')}) — {reason}."
            )
        lines.append("")
    else:
        lines.append("## Known gaps")
        lines.append("")
        lines.append("- None — all (table, year) combos produced rows.")
        lines.append("")
    lines.append("## Verification anchor")
    lines.append("")
    lines.append(
        "Re-runners: after a successful run, the following grep must "
        "return a row. The exact value may shift if MŠMT republishes the "
        "snapshot — bump this anchor if so:"
    )
    lines.append("")
    lines.append("```")
    lines.append(
        "grep -F '2025/2026,20,C1.25.1' hmp_msmt_yearbook_2005_2025.csv "
        "| grep -F 'Zapisované děti / celkem'"
    )
    lines.append("```")
    lines.append("")
    lines.append(
        "Expected: a row for `(celkem) :: Zapisované děti / celkem` with "
        "value `25075` (Hlavní město Praha, school year 2025/2026 — total "
        "zápis attendees)."
    )
    lines.append("")
    lines.append(f"Snapshot fetched at: `{snapshot_iso}`.")
    README_OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
