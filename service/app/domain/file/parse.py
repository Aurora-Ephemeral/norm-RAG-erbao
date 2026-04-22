"""
parsing process: 
1. only extract information from ROI, filter out the noise from header footer and margin of each page and catalog
2. classify the extracted information into different types (heading, paragraph, table, list_item)
    2.1 heading recongnized by regex and font-weight 
    2.2 table regonized by pdfplumber find_tables function 
    2.3 list_item regonized by regex
3. extract metadata from the first page. The metadata include: standard_no, issue_date, class_no, title, language

known limitations:
- scanned/image-based PDFs are not supported (no OCR)
- borderless tables are not detected
- headings without bold font will be missed
- language detection is heuristic (DE/EN word frequency), not ML-based
"""

import io
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pdfplumber


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ParsedElement:
    type: str           # "heading" | "paragraph" | "table" | "list_item"
    text: str
    page: int
    level: Optional[int] = None             # heading level 1..3
    rows: Optional[List[List[str]]] = None  # table: all rows including header
    footnotes: Optional[List[str]] = None   # table: footnote texts


@dataclass
class ParseResult:
    elements: List[ParsedElement] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Height in PDF points to strip from top/bottom of every page (≈21mm at 72dpi)
_BAND_PTS = 60
# Width in PDF points to strip from left/right of every page (≈14mm at 72dpi)
_MARGIN_PTS = 40


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r'^(\d+(?:\.\d+)*)\s+[A-Z]')
_BOLD_RE = re.compile(r'bold', re.IGNORECASE)
_TABLE_TITLE_RE = re.compile(r'^(Table\s+\d+[^\n]*)', re.IGNORECASE)
_CONTINUED_RE = re.compile(r'\(continued\)', re.IGNORECASE)
_FOOTNOTE_RE = re.compile(r'^[a-z]\)\s+\S')
_DOT_LEADER_RE = re.compile(r'\.{3,}\s*\d+\s*$')
_STANDARD_NO_RE = re.compile(r'\b(TL|VW|PV|TK)\s+\d[\w\-]*')
_ISSUE_DATE_RE = re.compile(r'Issue\s+(\d{4}-\d{2})')
_CLASS_NO_RE = re.compile(r'Class\.\s*No\.:\s*(\d+)')


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

_DE_WORDS = [' und ', ' der ', ' die ', ' das ', ' ist ', ' von ', ' für ', ' mit ', ' ein ']
_EN_WORDS = [' the ', ' and ', ' of ', ' is ', ' for ', ' are ', ' with ', ' this ', ' that ']


def _detect_language(text: str) -> str:
    sample = text[:3000].lower()
    de_score = sum(sample.count(w) for w in _DE_WORDS)
    en_score = sum(sample.count(w) for w in _EN_WORDS)
    return 'de' if de_score > en_score else 'en'


# ---------------------------------------------------------------------------
# TOC detection
# ---------------------------------------------------------------------------

_TOC_SECTION_HEADERS = {'contents', 'table of contents', 'inhaltsverzeichnis'}


def _is_toc_line(line: str) -> bool:
    stripped = line.strip()
    if stripped.lower() in _TOC_SECTION_HEADERS:
        return True
    return bool(_DOT_LEADER_RE.search(stripped))


def _is_toc_table(rows: List[List[str]]) -> bool:
    """Single-column 'tables' are TOC dot-leader misdetections — real tables always have ≥2 columns."""
    if not rows:
        return True
    max_cols = max(len([c for c in row if c and c.strip()]) for row in rows)
    return max_cols <= 1


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def _extract_metadata(all_text: str, first_lines: List[str]) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    header_block = ' '.join(first_lines[:40])

    std = _STANDARD_NO_RE.search(header_block)
    if std:
        meta['standard_no'] = std.group().strip()

    date = _ISSUE_DATE_RE.search(header_block)
    if date:
        meta['issue_date'] = date.group(1)

    cls = _CLASS_NO_RE.search(header_block)
    if cls:
        meta['class_no'] = cls.group(1)

    _noise = re.compile(r'^(Page\s+\d+|TL\s+\d|VW\s+\d|Issue\s+\d|Class\.|Descriptors?:|QUELLE)', re.IGNORECASE)
    for line in first_lines:
        line = line.strip()
        if len(line) > 15 and not _noise.match(line) and not re.fullmatch(r'[\d\s\.\-]+', line):
            meta['document_title'] = line
            break

    meta['language'] = _detect_language(all_text)
    return meta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _heading_level(numbered: str) -> int:
    return min(numbered.count('.') + 1, 3)


def _chars_to_lines(chars: List[dict]) -> List[dict]:
    """Group pdfplumber chars into lines with bold metadata."""
    if not chars:
        return []

    lines_map: Dict[int, List[dict]] = {}
    for char in chars:
        # find onw line character by top coordinate 2: tolerance
        key = round(char['top'] / 2) * 2
        lines_map.setdefault(key, []).append(char)

    result = []
    for key in sorted(lines_map):
        line_chars = sorted(lines_map[key], key=lambda c: c['x0'])
        text = ''.join(c['text'] for c in line_chars).strip()
        if not text:
            continue
        is_bold = any(_BOLD_RE.search(c.get('fontname', '') or '') for c in line_chars)
        result.append({'text': text, 'is_bold': is_bold})

    return result


def _in_bbox(obj: dict, bbox: Tuple[float, float, float, float]) -> bool:
    return bbox[0] <= obj.get('x0', 0) <= bbox[2] and bbox[1] <= obj.get('top', 0) <= bbox[3]


def _make_content_filter(page_height: float, page_width: float, table_bboxes: List[Tuple]):
    """Returns a filter keeping only objects inside the content area and outside tables."""
    def _filter(obj: dict) -> bool:
        top = obj.get('top', 0)
        x0 = obj.get('x0', 0)
        if top < _BAND_PTS or top > page_height - _BAND_PTS:
            return False
        if x0 < _MARGIN_PTS or x0 > page_width - _MARGIN_PTS:
            return False
        return not any(_in_bbox(obj, b) for b in table_bboxes)
    return _filter


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def parse_pdf(pdf_bytes: bytes) -> ParseResult:
    result = ParseResult()

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        if not pdf.pages:
            return result

        # Metadata uses full first-page text (header band contains standard_no, issue_date etc.)
        first_text = pdf.pages[0].extract_text() or ''
        first_lines = [ln for ln in first_text.splitlines() if ln.strip()]
        sample_text = '\n'.join(
            (pdf.pages[i].extract_text() or '') for i in range(min(3, len(pdf.pages)))
        )
        result.metadata = _extract_metadata(sample_text, first_lines)

        accumulated: Optional[Tuple[str, List[List[str]], List[str], int]] = None  # title, rows, footnotes, start_page
        pending_table_title: Optional[str] = None

        def _flush_table() -> None:
            nonlocal accumulated
            if accumulated:
                t, rows, fns, start_page = accumulated
                result.elements.append(ParsedElement(
                    type='table', text=t, page=start_page, rows=rows, footnotes=fns
                ))
                accumulated = None

        for page_num, page in enumerate(pdf.pages, start=1):
            # Exclude TOC misdetections before using table bboxes
            found_tables = [t for t in page.find_tables() if not _is_toc_table(t.extract())]
            table_bboxes = [t.bbox for t in found_tables]
            table_data_list = [t.extract() for t in found_tables]

            # Extract lines with font metadata from content area (no header/footer, no tables)
            filtered_page = page.filter(_make_content_filter(page.height, page.width, table_bboxes))
            content_lines = _chars_to_lines(filtered_page.chars)

            for line_info in content_lines:
                stripped = line_info['text']

                if _is_toc_line(stripped):
                    continue

                tm = _TABLE_TITLE_RE.match(stripped)
                if tm:
                    pending_table_title = tm.group(1)
                    continue

                hm = _HEADING_RE.match(stripped)
                if hm and line_info['is_bold']:
                    result.elements.append(ParsedElement(
                        type='heading', text=stripped, page=page_num,
                        level=_heading_level(hm.group(1))
                    ))
                    continue

                if re.match(r'^[–\-•]\s+\S', stripped):
                    result.elements.append(ParsedElement(
                        type='list_item', text=stripped.lstrip('–-• '), page=page_num
                    ))
                    continue

                if len(stripped) > 30:
                    result.elements.append(ParsedElement(
                        type='paragraph', text=stripped, page=page_num
                    ))

            for table_data in table_data_list:
                if not table_data:
                    continue

                main_rows: List[List[str]] = []
                footnotes: List[str] = []

                for row in table_data:
                    cells = [c.strip() if c else '' for c in row]
                    non_empty = [c for c in cells if c]
                    if len(non_empty) == 1 and _FOOTNOTE_RE.match(non_empty[0]):
                        footnotes.append(non_empty[0])
                    else:
                        main_rows.append(cells)

                title = pending_table_title or ''
                if _CONTINUED_RE.search(title) and accumulated:
                    _, acc_rows, acc_fns, __ = accumulated
                    acc_rows.extend(main_rows[1:] if len(main_rows) > 1 else main_rows)
                    acc_fns.extend(footnotes)
                else:
                    _flush_table()
                    accumulated = (title, main_rows, footnotes, page_num)

                pending_table_title = None

        _flush_table()

    return result
