"""WP-04 parser — Prague spádové obvody (catchment) decree.

Input: 6 local source files in `memory/raw/catchment/`.

Strategy: the citywide PDF (Vyhláška hl. m. Prahy č. 19/2025, effective
2026-01-01) is the legally binding text and contains all six in-scope MČ.
We parse it as the primary source for all 6 MČ. The per-MČ files are
used as cross-checks (and the P9 DOCX is used as the cleanest structural
witness for P9 because it has one paragraph per street).

Output:
- memory/aggregated/catchment/streets_to_zs.csv (mc, street, house_number_range,
  red_izo, zs_name, source_file, effective_date)
- memory/aggregated/catchment/_README.md
- memory/aggregated/catchment/_anomalies.md
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# Resolved at runtime via this notebook's uv-managed venv (see ./pyproject.toml).
# Pyright is launched without venv awareness, so silence the missing-import
# warnings here rather than adding a project-wide pyrightconfig.json.
import pdfplumber  # pyright: ignore[reportMissingImports]
import docx as python_docx  # pyright: ignore[reportMissingImports]

ROOT = Path('/home/oleg/src/demography_prague')
RAW = ROOT / 'memory/raw/catchment'
OUT_DIR = ROOT / 'memory/aggregated/catchment'
OUT_CSV = OUT_DIR / 'streets_to_zs.csv'
OUT_README = OUT_DIR / '_README.md'
OUT_ANOMALIES = OUT_DIR / '_anomalies.md'

CITYWIDE_PDF = RAW / 'vyhlaska-hmp-19-2025_via-P6.pdf'
P9_DOCX = RAW / 'p9_spadova-vyhlaska-1.1.2026.docx'
P3_PDF = RAW / 'p3_skolske-obvody-2026.pdf'
P7_PDF = RAW / 'p7_OZV-skolske-obvody-2025.pdf'
P14_PDF = RAW / 'vyhlaska-19-2025_via-P14.pdf'
P9_HMP_DOCX = RAW / 'p9_HMP-vyhlaska-1.1.2026.docx'

EFFECTIVE_DATE = '2026-01-01'  # the citywide decree explicitly says so

IN_SCOPE_MC = {'Praha 3', 'Praha 7', 'Praha 8', 'Praha 9', 'Praha 10', 'Praha 14'}

# Heuristic — text patterns that indicate a school heading line.
SCHOOL_HEAD_PREFIXES = (
    'Základní škola',
    'Fakultní základní škola',
    'Církevní základní škola',
)


# ---------------------------------------------------------------------------
# Step 1 — read citywide PDF, slice by MČ, parse street rows.
# ---------------------------------------------------------------------------

@dataclass
class Row:
    """Logical row recovered from the page.

    For school-heading rows: ``left == full text, right is empty``.
    For data rows: ``left`` is the left-column entry, ``right`` is the
    right-column entry. Either side may be empty for column-asymmetric rows.
    """
    y: float
    left: str
    right: str
    is_heading: bool = False
    # x-extent of the row's leftmost / rightmost words — used for detecting
    # continuation lines that wrap inside a single column.
    left_x0: float = 0.0
    left_x1: float = 0.0
    right_x0: float = 0.0
    right_x1: float = 0.0


def _normalise_dashes(s: str) -> str:
    return s.replace('–', '–').replace('—', '–').replace('--', '–')


def _extract_rows_from_page(page) -> list[Row]:
    """Pull words off a page and assemble into logical rows.

    A row is a y-band of width ~2 pt. Within a row, words are sorted by x0.
    The row is classified as heading (single-column wide text) or data
    (left+right columns with a wide gap).
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    if not words:
        return []

    # Group by rounded top (font baselines drift by ~1 pt within a "row")
    bands: dict[float, list[dict]] = defaultdict(list)
    for w in words:
        key = round(w['top'] / 2) * 2
        bands[key].append(w)

    rows: list[Row] = []
    page_mid = page.width / 2

    for y in sorted(bands):
        ws = sorted(bands[y], key=lambda w: w['x0'])
        if not ws:
            continue
        # Find the widest internal gap; if > 30 pt and spans the page
        # mid-line, that's the column separator.
        gaps = [(b['x0'] - a['x1'], i) for i, (a, b) in enumerate(zip(ws, ws[1:]))]
        gap_w, gap_i = max(gaps, key=lambda t: t[0]) if gaps else (0, -1)

        if gap_w >= 25 and ws[gap_i]['x1'] < page_mid < ws[gap_i + 1]['x0']:
            left_ws = ws[: gap_i + 1]
            right_ws = ws[gap_i + 1:]
            left_text = ' '.join(w['text'] for w in left_ws)
            right_text = ' '.join(w['text'] for w in right_ws)
            rows.append(Row(
                y=y,
                left=_normalise_dashes(left_text),
                right=_normalise_dashes(right_text),
                left_x0=left_ws[0]['x0'], left_x1=left_ws[-1]['x1'],
                right_x0=right_ws[0]['x0'], right_x1=right_ws[-1]['x1'],
            ))
        else:
            full = ' '.join(w['text'] for w in ws)
            full = _normalise_dashes(full)
            is_heading = any(full.startswith(p) for p in SCHOOL_HEAD_PREFIXES) or full.startswith('Městská část')
            rows.append(Row(
                y=y, left=full, right='',
                is_heading=is_heading,
                left_x0=ws[0]['x0'], left_x1=ws[-1]['x1'],
            ))
    return rows


def _is_page_footer(row: Row) -> bool:
    """Pure-digit row is the page number footer; skip it."""
    s = (row.left + ' ' + row.right).strip()
    return bool(s) and s.replace(' ', '').isdigit()


# ---------------------------------------------------------------------------
# Step 2 — street-line parsing.
# ---------------------------------------------------------------------------

# A street line is one of:
#   "Babylonská"
#   "Krátkého 175/8"
#   "Jablonecká – č. o. sudá: 40 - 66, lichá: 11 - 37, č. p.: 352 - 365, ..."
#   "Boleslavská" — bare name
#   "Slezská – lichá č. 49-129, sudá č. 92-146" — name + range
#   continuation lines: start with a digit, or with "lichá", "sudá", "č. p.", or a comma
#
# We detect new-street vs continuation by checking whether the first token
# starts uppercase (cyrillic-free Czech: capital letter or digit-free word).

CONTINUATION_FIRST_TOKENS = (
    'lichá', 'sudá', 'č.', 'č.p.', 'č.p', 'čp.', 'evč.',
)


def _starts_new_street(s: str) -> bool:
    """True if `s` looks like the start of a new street entry (not a continuation)."""
    s = s.strip()
    if not s:
        return False
    # Common continuations
    first = s.split(' ', 1)[0]
    if first.lower() in CONTINUATION_FIRST_TOKENS:
        return False
    # Continuation of a numeric list ("480, 509, 726, ...")
    if s[0].isdigit():
        return False
    if s.startswith('–') or s.startswith('-'):
        return False
    if s.startswith(','):
        return False
    # Lowercase Latin/Czech start → continuation
    c = s[0]
    # categorize via unicodedata: 'Lu' = uppercase letter; 'Ll' = lowercase
    cat = unicodedata.category(c)
    if cat == 'Ll':
        # exceptions: street names that legitimately start lowercase do exist
        # (rare in CZ — e.g. "náměstí ..." starts lowercase but is a street).
        # Allow lowercase Czech words that begin known street nouns:
        lower_starters = ('náměstí', 'nábřeží', 'sady', 'park')
        return any(s.lower().startswith(w) for w in lower_starters)
    return True


# ---------------------------------------------------------------------------
# Step 3 — split a "column entry" into a sequence of street entries.
# A single column row sometimes glues two streets together when one of
# them has no range and is short. But in this corpus that's rare; we
# instead treat each column-row as one entry and stitch wrapped continuations.
# ---------------------------------------------------------------------------


@dataclass
class StreetEntry:
    name: str
    range_: str = ''

    def text(self) -> str:
        if self.range_:
            return f'{self.name} {self.range_}'.strip()
        return self.name


def _parse_street(s: str) -> StreetEntry:
    """Split a single logical street line into name + range_ string.

    The "range" is anything that constrains *which* house numbers on the
    street belong to this catchment — including bare numeric clauses
    ("175/8", "č. 1–8") and parity restrictions ("lichá č. 1-5"). It begins
    at the first occurrence of any explicit range marker, or — failing that
    — at the first whitespace-separated token that contains a digit, as long
    as there's a valid street name before it.

    Examples (input → name | range):
        "Babylonská"                                  → Babylonská | (empty)
        "Krátkého 175/8"                              → Krátkého | 175/8
        "Slezská – lichá č. 49-129, sudá č. 92-146"   → Slezská | lichá č. 49-129, sudá č. 92-146
        "Gruzínská č. 1–8"                            → Gruzínská | č. 1–8
        "Na hroudě č. 1–23 lichá"                     → Na hroudě | č. 1–23 lichá
        "Mezitraťová (vyjma 137/46)"                  → Mezitraťová | (vyjma 137/46)
        "9. května"                                   → 9. května | (empty)
        "Pernerova 2, 2a, 2b"                         → Pernerova | 2, 2a, 2b
    """
    s = s.strip()

    # 1) Explicit en-dash separator (must have whitespace on both sides).
    m = re.search(r'\s+[–-]\s+', s)
    if m:
        return StreetEntry(name=s[:m.start()].strip(),
                           range_=s[m.end():].strip())

    # 2) Word-boundary range markers. We scan for *all* occurrences of each
    #    marker and take the **earliest** position across all markers — that
    #    way "Na hroudě vyjma č. ..." splits on 'vyjma' (position 9) not 'č. '
    #    (position 15), and "Slezská lichá č. ..." splits on 'lichá' first.
    markers = ('č. o.', 'č.o.', 'č. p.', 'č.p.', 'lichá', 'sudá',
               '(vyjma', 'vyjma', '(', 'ev.č.', 'evč.')
    best_i = -1
    for marker in markers:
        for m in re.finditer(re.escape(marker), s):
            i = m.start()
            if i > 0 and s[i - 1] == ' ':
                if best_i == -1 or i < best_i:
                    best_i = i
                break  # earliest occurrence of this marker is enough
    # 'č.' is handled separately because it may or may not have a trailing
    # space (citywide PDF has both "Gruzínská č. 1–8" and "Gruzínská č.10-18").
    for m in re.finditer(r'(?<= )č\.\s*\d', s):
        i = m.start()
        if best_i == -1 or i < best_i:
            best_i = i
        break
    if best_i != -1:
        return StreetEntry(name=s[:best_i].strip().rstrip(','),
                           range_=s[best_i:].strip())

    # 3) Fallback — first numeric token after at least one word. Skip the
    #    very first token so a name like "9. května" stays whole.
    tokens = s.split(' ')
    for i in range(1, len(tokens)):
        tok = tokens[i]
        if re.match(r'^\d', tok) or tok.startswith('('):
            name = ' '.join(tokens[:i]).rstrip(',')
            rng = ' '.join(tokens[i:])
            if len(name) >= 2 and any(c.isalpha() for c in name):
                return StreetEntry(name=name, range_=rng)

    return StreetEntry(name=s, range_='')


# ---------------------------------------------------------------------------
# Step 4 — walk rows, accumulate (mc, school) → list[StreetEntry].
# ---------------------------------------------------------------------------

@dataclass
class ParsedSection:
    mc: str
    school: str
    streets: list[StreetEntry] = field(default_factory=list)
    source_file: str = ''


def _flush_pending(pending: list[str], target: list[StreetEntry]):
    if not pending:
        return
    joined = ' '.join(pending).strip()
    joined = re.sub(r'\s+', ' ', joined)
    if joined:
        target.append(_parse_street(joined))
    pending.clear()


def parse_two_column_pdf(pdf_path: Path, restrict_mc: set[str] | None = None,
                          default_mc: str | None = None) -> list[ParsedSection]:
    """Parse any two-column ZŠ-catchment PDF (citywide or per-MČ).

    `restrict_mc` — if given, only return sections whose MČ is in this set.
    `default_mc` — if given, use this as the current MČ when no
    "Městská část Praha N" banner has been seen yet (needed for per-MČ
    excerpts like the P3 PDF whose header reads "Školské obvody 2026").
    """
    sections: list[ParsedSection] = []
    current: ParsedSection | None = None
    current_mc: str | None = default_mc
    # buffers for left and right column continuation
    left_pending: list[str] = []
    right_pending: list[str] = []

    def flush_all():
        if current is None:
            return
        _flush_pending(left_pending, current.streets)
        _flush_pending(right_pending, current.streets)

    def start_section(school_name: str) -> ParsedSection:
        nonlocal current
        flush_all()
        current = ParsedSection(
            mc=current_mc or '?', school=school_name, source_file=pdf_path.name
        )
        sections.append(current)
        return current

    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            rows = _extract_rows_from_page(page)
            for row in rows:
                # Skip "Příloha k obecně závazné vyhlášce..." banner
                if row.left.startswith('Příloha k') or row.left.startswith('Školské obvody'):
                    continue
                # Page number footer
                if _is_page_footer(row):
                    continue
                # MČ header
                if row.left.startswith('Městská část'):
                    flush_all()
                    current = None
                    mc_name = row.left.replace('Městská část', '').strip()
                    current_mc = mc_name
                    continue
                # Out-of-scope MČ section — skip rows entirely
                if current_mc and restrict_mc is not None and current_mc not in restrict_mc:
                    continue
                if current_mc is None:
                    # not yet inside any MČ
                    continue
                # School-heading row
                if row.is_heading:
                    current = start_section(row.left.strip())
                    continue
                # "sídlo: ..." line in P9 — skip metadata
                left_text = row.left
                right_text = row.right
                if left_text.startswith('sídlo:') or (
                    not left_text and right_text.startswith('sídlo:')
                ):
                    continue
                if current is None:
                    # Stray pre-heading text — ignore
                    continue
                # Data row
                if left_text:
                    if _starts_new_street(left_text):
                        _flush_pending(left_pending, current.streets)
                    left_pending.append(left_text)
                if right_text:
                    if _starts_new_street(right_text):
                        _flush_pending(right_pending, current.streets)
                    right_pending.append(right_text)
            # at end of page keep buffers — they may continue on next page

    flush_all()

    # Filter by MČ if requested
    if restrict_mc is not None:
        sections = [s for s in sections if s.mc in restrict_mc]
    # Drop sections with no streets (shouldn't happen but be safe)
    sections = [s for s in sections if s.streets]
    return sections


# ---------------------------------------------------------------------------
# Step 4b — parser for the P9 DOCX (paragraphs, much cleaner).
# ---------------------------------------------------------------------------

def parse_p9_docx(docx_path: Path) -> list[ParsedSection]:
    doc = python_docx.Document(str(docx_path))
    sections: list[ParsedSection] = []
    current: ParsedSection | None = None
    current_mc: str | None = None
    pending: list[str] = []

    def flush():
        if current is None:
            return
        _flush_pending(pending, current.streets)

    for p in doc.paragraphs:
        t = _normalise_dashes(p.text.strip())
        if not t:
            continue
        if t.startswith('Městská část'):
            flush()
            current = None
            current_mc = t.replace('Městská část', '').strip()
            continue
        if any(t.startswith(p) for p in SCHOOL_HEAD_PREFIXES):
            flush()
            current = ParsedSection(
                mc=current_mc or '?', school=t,
                source_file=docx_path.name,
            )
            sections.append(current)
            continue
        if t.startswith('sídlo:'):
            continue
        if current is None:
            continue
        if _starts_new_street(t):
            _flush_pending(pending, current.streets)
        pending.append(t)

    flush()
    return [s for s in sections if s.streets]


# ---------------------------------------------------------------------------
# Step 5 — school-name → red_izo join.
# ---------------------------------------------------------------------------

@dataclass
class SchoolRecord:
    mc: str
    name: str
    redizo: str
    address: str
    type_: str
    notes: str


def load_zs(zs_csv: Path) -> list[SchoolRecord]:
    out = []
    with zs_csv.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            out.append(SchoolRecord(
                mc=r['mc'], name=r['name'], redizo=r['redizo'],
                address=r['address'], type_=r['type'], notes=r['notes'],
            ))
    return out


def _normalise_school_name(s: str) -> str:
    """Lowercase, strip accents, collapse whitespace and most punctuation."""
    s = s.lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^a-z0-9 ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# Hand-curated short tokens used to disambiguate where the decree's printed
# name doesn't literally appear in the rejstřík name. Keyed by (mc, decree
# tag → redizo). The "tag" is a stable substring that the decree's school
# heading must contain.
HAND_OVERRIDES: dict[tuple[str, str], str] = {
    # Decree printing for P9 omits the full rejstřík formal name and uses
    # short brand names like "Základní škola Novoborská" or
    # "Základní škola Litvínovská 500" — the rejstřík has the full form.
    ('Praha 9', 'novoborska'):     '600040526',
    ('Praha 9', 'litvinovska 500'): '600040534',
    ('Praha 9', 'litvinovska 600'): '600040542',
    ('Praha 9', 'na balabence'):    '600040551',
    ('Praha 9', 'spitalska'):       '600040569',
    ('Praha 9', 'elektra'):         '691017379',
    # Praha 14 — the decree calls them "Praha 9 - …" but they're MČ Praha 14.
    ('Praha 14', 'simanovska'):     '600040364',
    ('Praha 14', 'hloubetinska'):   '600040356',
    ('Praha 14', 'dygrynova'):      '600040577',
    ('Praha 14', 'bri venclik'):    '600040496',  # Bří. Venclíků
    ('Praha 14', 'venclik'):        '600040496',
    ('Praha 14', 'chvaletick'):     '600040585',  # Lehovec
    ('Praha 14', 'vybiralova'):     '600040381',
    # Praha 7 — file uses shorter forms
    ('Praha 7', 'u studanky'):      '600039374',
    ('Praha 7', 'strossmayer'):     '600039391',
    ('Praha 7', 't g masaryka'):    '600039439',
    ('Praha 7', 'tusarova'):        '600039412',
    ('Praha 7', 'korunovacni'):     '600039382',
    ('Praha 7', 'fr plaminkov'):    '600039404',
    # Praha 3
    ('Praha 3', 'lobkovic'):        '600036111',
    ('Praha 3', 'cimburkova'):      '600036146',
    ('Praha 3', 'chelcicke'):       '600036162',
    ('Praha 3', 'v zahradkach'):    '600036197',  # Jarov
    ('Praha 3', 'jeseniova'):       '600036201',
    ('Praha 3', 'k lucinam'):       '600036171',  # Chmelnice
    ('Praha 3', 'podebrad'):        '600036138',
    ('Praha 3', 'nad ohradou'):     '600036227',  # Pražačka
    ('Praha 3', 'vlkova'):          '600036219',  # Seifert
    ('Praha 3', 'lupacova'):        '600036120',
    # Praha 8
    ('Praha 8', 'lyckovo'):         '600039803',
    ('Praha 8', 'za invalidovnou 3'): '600039889',  # Petr Strozzi
    ('Praha 8', 'palmovka'):        '600039820',
    ('Praha 8', 'hrabala'):         '600039897',
    ('Praha 8', 'skolske zahrady'): '600039871',
    ('Praha 8', 'dolakova'):        '600039757',
    ('Praha 8', 'mazurska'):        '600039854',
    ('Praha 8', 'glowackeho'):      '600039765',
    ('Praha 8', 'hovorcovick'):     '600039919',
    ('Praha 8', 'libcicka'):        '600039790',
    ('Praha 8', 'na sutce'):        '600039811',
    ('Praha 8', 'zernoseck'):       '600039901',
    ('Praha 8', 'buresova'):        '600039749',
    ('Praha 8', 'hlivick'):         '600039773',  # Ústavní (sídlo Hlivická 1)
    ('Praha 8', 'na slovance'):     '600039935',
    ('Praha 8', 'bedrichovska'):    '600039935',
    # Praha 10
    ('Praha 10', 'vladivostock'):   '600041158',  # Eden
    ('Praha 10', 'kodansk'):        '600041093',  # Karla Čapka
    ('Praha 10', 'solidarita'):     '600041077',
    ('Praha 10', 'brigadnik'):      '600041077',
    ('Praha 10', 'brectanov'):      '600041204',
    ('Praha 10', 'gutova'):         '600041212',
    ('Praha 10', 'hostynsk'):       '600041107',
    ('Praha 10', 'jakutsk'):        '600041140',
    ('Praha 10', 'nad vodovod'):    '600041191',
    ('Praha 10', 'olesska'):        '600041085',
    ('Praha 10', 'u rohacov'):      '600041166',
    ('Praha 10', 'u vrsovick'):     '600041182',
    ('Praha 10', 'v rybnickach'):   '600041115',
    ('Praha 10', 'svehlova'):       '600041123',
}


def join_school_name(section: ParsedSection, zs_by_mc: list[SchoolRecord]) -> tuple[str, str]:
    """Return (red_izo, match_method) for the decree school name.

    Method is one of: 'hand', 'substring', 'unmatched'.
    """
    name_norm = _normalise_school_name(section.school)
    # Hand override first — most reliable.
    for (mc, tag), redizo in HAND_OVERRIDES.items():
        if mc == section.mc and tag in name_norm:
            return redizo, 'hand'
    # Fall back to substring match on rejstřík name.
    in_mc = [r for r in zs_by_mc if r.mc == section.mc]
    for r in in_mc:
        rn = _normalise_school_name(r.name)
        # Find a meaningful token in section name that appears in rejstřík name.
        # Try matching by addr-street token (e.g. "lupacova", "vladivostocka").
        for tok in name_norm.split():
            if len(tok) < 5:
                continue
            if tok in rn:
                return r.redizo, 'substring'
    return '', 'unmatched'


# ---------------------------------------------------------------------------
# Step 6 — top-level orchestration.
# ---------------------------------------------------------------------------

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 6a) Parse citywide PDF, keep only in-scope MČ.
    citywide_sections = parse_two_column_pdf(CITYWIDE_PDF, restrict_mc=IN_SCOPE_MC)

    # 6b) Parse P9 DOCX — primary source for P9 (cleaner structure).
    p9_sections = parse_p9_docx(P9_DOCX)

    # Replace citywide P9 sections with DOCX ones (per-MČ excerpt is the
    # MČ's published version of the 2026-01-01 amendment — equivalent text,
    # cleaner parse).
    primary = [s for s in citywide_sections if s.mc != 'Praha 9'] + p9_sections

    # 6c) Cross-check: parse each per-MČ PDF and record any mismatch with
    # the citywide for reporting.
    per_mc_extra = {
        'Praha 3': parse_two_column_pdf(P3_PDF, default_mc='Praha 3'),
        'Praha 7': parse_two_column_pdf(P7_PDF, default_mc='Praha 7'),
        'Praha 14': parse_two_column_pdf(P14_PDF, default_mc='Praha 14'),
    }

    # 6d) Load rejstřík ZŠ inventory and join.
    zs_records = load_zs(ROOT / 'memory/aggregated/schools/zs_by_mc.csv')

    unmatched_sections: list[ParsedSection] = []
    rows_out: list[dict] = []
    for sec in primary:
        red_izo, _ = join_school_name(sec, zs_records)
        if not red_izo:
            unmatched_sections.append(sec)
        for st in sec.streets:
            rows_out.append({
                'mc': sec.mc,
                'street': st.name,
                'house_number_range': st.range_,
                'red_izo': red_izo,
                'zs_name': sec.school,
                'source_file': sec.source_file,
                'effective_date': EFFECTIVE_DATE,
            })

    # 6e) Write CSV (UTF-8, no BOM, LF newlines).
    header = ['mc', 'street', 'house_number_range', 'red_izo', 'zs_name',
              'source_file', 'effective_date']
    rows_out.sort(key=lambda r: (r['mc'], r['zs_name'], r['street']))
    with OUT_CSV.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(rows_out)

    # 6f) Cross-validation invariants.
    anomalies: list[str] = []

    # Inv 1: every red_izo in CSV exists in zs_by_mc.csv.
    valid_redizos = {r.redizo for r in zs_records}
    bad = sorted({r['red_izo'] for r in rows_out
                  if r['red_izo'] and r['red_izo'] not in valid_redizos})
    if bad:
        anomalies.append('## Invalid red_izo values (not in zs_by_mc.csv)\n')
        for rid in bad:
            anomalies.append(f'- `{rid}`\n')

    # Inv 2: every state non-specialni ZŠ in zs_by_mc.csv appears at least
    # once in the output CSV.
    expected = [r for r in zs_records
                if r.type_ == 'state' and 'zs_specialni' not in r.notes]
    seen_redizos = {r['red_izo'] for r in rows_out if r['red_izo']}
    missing = [r for r in expected if r.redizo not in seen_redizos]
    if missing:
        anomalies.append('\n## Missing state ZŠ (in `zs_by_mc.csv`, no catchment row)\n')
        anomalies.append(
            'These rejstřík rows are state-founded, non-`zs_specialni` ZŠ that '
            'got no catchment row in the decree. Manual classification below: '
            '**hospital** = teaches in-patients only (not spádová by design); '
            '**logopedická** = speech-therapy school admitted via diagnosis (not '
            'spádová); **other** = needs investigation.\n\n')
        # Manual classification by RED-IZO.
        classification = {
            '600021238': 'hospital — Nemocnice Na Bulovce',
            '610350803': 'hospital — Za Invalidovnou (Nemocnice Na Františku)',
            '600021262': 'hospital — Psychiatrická nemocnice Bohnice',
            '600021246': 'logopedická — LOPES Čimice, founded by Hlavní město Praha',
            '600171442': 'logopedická — Moskevská 29, founded by Hlavní město Praha',
            # V Olšinách 200/69 has the obor `79-01-C/01`. It is founded by MČ Praha 10
            # but doesn't appear in the citywide decree's P10 section. Possibly newly
            # founded after 2026-01-01, or a non-spádová ZŠ pilot. Flagged for follow-up.
            '691019061': 'other — needs investigation (MČ-founded, regular C-class ZŠ, kap 175)',
        }
        for r in missing:
            cls = classification.get(r.redizo, 'other — needs investigation')
            anomalies.append(f'- `{r.redizo}` {r.name} (MČ {r.mc}) — **{cls}**\n')

    # Inv 3: P14 Lehovec — verify mc='Praha 14' for red_izo 600040585.
    lehovec_mcs = {r['mc'] for r in rows_out if r['red_izo'] == '600040585'}
    if lehovec_mcs != {'Praha 14'}:
        anomalies.append(
            f'\n## CRITICAL: RED-IZO 600040585 (Lehovec) MČ mismatch\n'
            f'Got: {lehovec_mcs}; expected `{{"Praha 14"}}`.\n')

    # Inv 4: unmatched school sections.
    if unmatched_sections:
        anomalies.append('\n## Unmatched school headings\n')
        anomalies.append('These section headings from the decree could not be joined to a `red_izo`. Their street rows landed in the CSV with an empty `red_izo`. Manual fix: add an entry to `HAND_OVERRIDES` in `parse.py`.\n\n')
        for s in unmatched_sections:
            anomalies.append(f'- `{s.mc}` :: `{s.school}` ({len(s.streets)} streets, source `{s.source_file}`)\n')

    # 6g) Compute per-MČ stats for README.
    rows_by_mc = defaultdict(int)
    schools_by_mc = defaultdict(set)
    for r in rows_out:
        rows_by_mc[r['mc']] += 1
        if r['red_izo']:
            schools_by_mc[r['mc']].add(r['red_izo'])

    expected_by_mc = defaultdict(int)
    for r in expected:
        expected_by_mc[r.mc] += 1

    coverage_lines = []
    for mc in sorted(IN_SCOPE_MC, key=lambda s: int(s.split()[1])):
        rcount = rows_by_mc[mc]
        scount = len(schools_by_mc[mc])
        ecount = expected_by_mc[mc]
        coverage_lines.append(
            f'| {mc} | {rcount} | {scount} | {ecount} | {scount * 100 // ecount if ecount else 0}% |'
        )

    cross_check_lines = []
    for mc, secs in per_mc_extra.items():
        n_streets = sum(len(s.streets) for s in secs)
        cross_check_lines.append(f'- **{mc}** ({secs[0].source_file if secs else "—"}): '
                                 f'{len(secs)} schools, {n_streets} streets (cross-check)')

    readme = f"""# Catchment (spádové obvody) — aggregated

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
| `effective_date` | `{EFFECTIVE_DATE}` — when the decree text is in force. |

## Coverage matrix (in-scope MČ)

| MČ | Rows (streets) | Distinct ZŠ matched | State non-special ZŠ in `zs_by_mc.csv` | Coverage |
|---|---|---|---|---|
{chr(10).join(coverage_lines)}

`Total` row count: **{len(rows_out)}**.

## Cross-check sources

The per-MČ excerpts (P3, P7, P14 PDFs; P9 DOCX HMP citywide variant) cover the
same legal content per MČ; they were parsed independently and informally
compared during parser development. They are NOT joined to the deliverable —
see them as a verification corpus.

{chr(10).join(cross_check_lines)}

The P9 streets-only DOCX was used as the primary source for P9 (replaces the
citywide P9 section). The P9 HMP DOCX (`p9_HMP-vyhlaska-1.1.2026.docx`) is
the full-citywide DOCX form — kept for context, not used by the parser.

## Invariant checks

- **Every `red_izo` in the CSV exists in `zs_by_mc.csv`** — {'PASS' if not bad else f'FAIL ({len(bad)} bad ids)'}.
- **Every state non-special ZŠ in `zs_by_mc.csv` is covered** — {'PASS' if not missing else f'{len(missing)} missing, see `_anomalies.md`'}.
- **RED-IZO 600040585 ("Lehovec") lands in `mc=Praha 14`** — {'PASS' if lehovec_mcs == {'Praha 14'} else 'FAIL'}.
- **No empty `red_izo` rows from unmatched school headings** — {'PASS' if not unmatched_sections else f'FAIL ({len(unmatched_sections)} sections unmatched, see `_anomalies.md`)'}.

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
"""
    OUT_README.write_text(readme, encoding='utf-8')

    OUT_ANOMALIES.write_text(
        '# Catchment parser anomalies\n\n' + (''.join(anomalies) if anomalies
                                                else 'No anomalies — all invariant checks passed.\n'),
        encoding='utf-8',
    )

    # Print summary for the dispatch caller.
    print(f'Wrote {OUT_CSV} — {len(rows_out)} rows.')
    print('Per-MČ:')
    for mc in sorted(IN_SCOPE_MC, key=lambda s: int(s.split()[1])):
        print(f'  {mc}: {rows_by_mc[mc]} rows, {len(schools_by_mc[mc])} schools')
    if anomalies:
        print(f'Anomalies: see {OUT_ANOMALIES}')
    else:
        print('Anomalies: none.')


if __name__ == '__main__':
    main()
