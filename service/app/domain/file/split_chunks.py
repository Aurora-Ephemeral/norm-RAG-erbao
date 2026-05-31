from app.domain.file.parse import ParseResult
from dataclasses import dataclass, field
from typing import List, Optional
import re

# Constants TODO: move to enviroment varialbles later
CHUNK_SIZE = 512


@dataclass
class Chunk:
    text: str
    page: int
    chunk_type: str # "text" | "table"
    token_count: int
    section_path: List[str] = field(default_factory=list)
    referenced_standards: List[str] = field(default_factory=list)
    rows: Optional[List[List[str]]] = None
    footnotes: Optional[List[str]] = None


_STANDARD_NO_RE = re.compile(r'\b(?:TL|VW|PV|TK)\s+\d[\w\-]*')

def _extract_standards(text:str) -> List[str]:
    seen: set = set()
    result: List[str] = []
    for m in _STANDARD_NO_RE.finditer(text):
        val = re.sub(r'\s+', '', m.group())
        if val not in seen:
            seen.add(val)
            result.append(val)
    return result

def _calculate_text_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def _table_2_buffer(rows: List[List[str]]) -> List[str]:
    lines: List[str] = []
    for row in rows:
        lines.append(' | '.join(cell for cell in row))
    return lines

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def split_chunks(parsed_result: ParseResult) -> List[Chunk]:
    result: List[Chunk] = []
    buffer_text: List[str] = []
    buffer_page:int = 1
    buffer_type: str = ''
    buffer_table_title: str = ''
    buffer_table_footer: List[str] = []
    buffer_table_rows: List[List[str]] = []
    section_path: List[str] = []

    def _flush_table():
        if not buffer_text:
            return
        table_header: str = buffer_text[0]
        header_row: List[str] = buffer_table_rows[0] if buffer_table_rows else []
        curr_buffer: List[str] = []
        curr_rows: List[List[str]] = [header_row]
        for i, line in enumerate(buffer_text[1:], start=1):
            curr_buffer.append(line)
            curr_rows.append(buffer_table_rows[i] if i < len(buffer_table_rows) else [])
            if _calculate_text_tokens('\n'.join(curr_buffer)) > CHUNK_SIZE:
                curr_chunk_text = buffer_table_title + '\n' \
                    + table_header + '\n' \
                    + '\n'.join(curr_buffer) + '\n' \
                    + '\n'.join(buffer_table_footer)
                result.append(Chunk(
                    text=curr_chunk_text,
                    page=buffer_page,
                    chunk_type='table',
                    token_count=_calculate_text_tokens(curr_chunk_text),
                    section_path=section_path.copy(),
                    referenced_standards=_extract_standards(curr_chunk_text),
                    rows=curr_rows.copy(),
                    footnotes=buffer_table_footer,
                ))
                curr_buffer = []
                curr_rows = [header_row]
        if curr_buffer:
            body = buffer_table_title + '\n' + '\n'.join(curr_buffer)
            curr_chunk_text = body + ('\n' + '\n'.join(buffer_table_footer) if buffer_table_footer else '')
            result.append(Chunk(
                text=curr_chunk_text,
                page=buffer_page,
                chunk_type='table',
                token_count=_calculate_text_tokens(curr_chunk_text),
                section_path=section_path.copy(),
                referenced_standards=_extract_standards(curr_chunk_text),
                rows=curr_rows.copy(),
                footnotes=buffer_table_footer,
            ))

    def _flush_text():
        if not buffer_text:
            return
        text = '\n'.join(buffer_text)
        result.append(Chunk(
            text=text,
            page=buffer_page,
            chunk_type='text',
            token_count=_calculate_text_tokens(text),
            section_path=section_path.copy(),
            referenced_standards=_extract_standards(text),
        ))

    def _flush():
        nonlocal buffer_text
        if buffer_type == 'text':
            _flush_text()
            buffer_text = []
        elif buffer_type == 'table':
            _flush_table()
            buffer_text = []

    if parsed_result is None:
        return result
    for element in parsed_result.elements:
        ele_type = element.type
        if ele_type in ('paragraph', 'list_item'):
            if not buffer_text:
                buffer_page = element.page
                buffer_type = 'text'
            buffer_text.append(element.text)
            if _calculate_text_tokens(''.join(buffer_text)) > CHUNK_SIZE:
                _flush()
        elif ele_type == 'table':
            _flush()
            rows = element.rows or []
            footnotes = element.footnotes or []
            buffer_type = 'table'
            buffer_text = _table_2_buffer(rows)
            buffer_table_title = element.text or ''
            buffer_table_footer = footnotes
            buffer_table_rows = rows

        elif ele_type == 'heading':
            _flush()
            level = element.level or 1
            section_path = section_path[:level - 1]
            section_path.append(element.text)
            buffer_page = element.page
    _flush()

    return result
