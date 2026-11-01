"""Ограниченный Markdown → HTML для обзорного сайта (stdlib)."""
from __future__ import annotations

import html
import re


LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD_RE = re.compile(r'\*\*(.+?)\*\*')
CODE_RE = re.compile(r'`([^`]+)`')
ITALIC_RE = re.compile(r'(?<!\*)\*([^*]+)\*(?!\*)')


def rewrite_md_href(href: str) -> str:
    if href.startswith(('http://', 'https://', 'mailto:', '#')):
        return href
    if href.endswith('.md'):
        return href[:-3] + '.html'
    if '/index.md#' in href:
        return href.replace('.md#', '.html#')
    return href


def inline(text: str) -> str:
    parts: list[str] = []
    pos = 0
    for match in LINK_RE.finditer(text):
        parts.append(_inline_no_links(text[pos:match.start()]))
        label = _inline_no_links(match.group(1))
        href = html.escape(rewrite_md_href(match.group(2)), quote=True)
        parts.append(f'<a href="{href}">{label}</a>')
        pos = match.end()
    parts.append(_inline_no_links(text[pos:]))
    return ''.join(parts)


def _inline_no_links(text: str) -> str:
    text = html.escape(text)

    def bold(match: re.Match[str]) -> str:
        return f'<strong>{match.group(1)}</strong>'

    def code(match: re.Match[str]) -> str:
        return f'<code>{match.group(1)}</code>'

    def italic(match: re.Match[str]) -> str:
        return f'<em>{match.group(1)}</em>'

    text = BOLD_RE.sub(bold, text)
    text = CODE_RE.sub(code, text)
    text = ITALIC_RE.sub(italic, text)
    return text


def _flush_paragraph(buf: list[str], out: list[str]) -> None:
    if not buf:
        return
    out.append('<p>' + inline(' '.join(buf)) + '</p>')
    buf.clear()


def _flush_list(items: list[str], ordered: bool, out: list[str]) -> None:
    if not items:
        return
    tag = 'ol' if ordered else 'ul'
    out.append(f'<{tag}>')
    for item in items:
        out.append(f'<li>{inline(item)}</li>')
    out.append(f'</{tag}>')
    items.clear()


def _is_table_row(line: str) -> bool:
    return line.startswith('|') and line.endswith('|')


def _is_table_sep(line: str) -> bool:
    if not _is_table_row(line):
        return False
    cells = [c.strip() for c in line.strip('|').split('|')]
    return bool(cells) and all(re.fullmatch(r':?-{3,}:?', c or '') for c in cells)


def _table_cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip('|').split('|')]


def markdown_to_html(source: str) -> str:
    lines = source.replace('\r\n', '\n').split('\n')
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    ordered = False
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            _flush_paragraph(paragraph, out)
            _flush_list(list_items, ordered, out)
            i += 1
            continue
        if _is_table_row(stripped) and i + 1 < len(lines) and _is_table_sep(lines[i + 1].strip()):
            _flush_paragraph(paragraph, out)
            _flush_list(list_items, ordered, out)
            headers = _table_cells(stripped)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and _is_table_row(lines[i].strip()):
                rows.append(_table_cells(lines[i].strip()))
                i += 1
            out.append('<table><thead><tr>')
            for cell in headers:
                out.append(f'<th>{inline(cell)}</th>')
            out.append('</tr></thead><tbody>')
            for row in rows:
                out.append('<tr>')
                for cell in row:
                    out.append(f'<td>{inline(cell)}</td>')
                out.append('</tr>')
            out.append('</tbody></table>')
            continue
        heading = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        if heading:
            _flush_paragraph(paragraph, out)
            _flush_list(list_items, ordered, out)
            level = len(heading.group(1))
            out.append(f'<h{level}>{inline(heading.group(2))}</h{level}>')
            i += 1
            continue
        bullet = re.match(r'^[-*]\s+(.*)$', stripped)
        if bullet:
            _flush_paragraph(paragraph, out)
            if list_items and ordered:
                _flush_list(list_items, ordered, out)
            ordered = False
            list_items.append(bullet.group(1))
            i += 1
            continue
        number = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if number:
            _flush_paragraph(paragraph, out)
            if list_items and not ordered:
                _flush_list(list_items, ordered, out)
            ordered = True
            list_items.append(number.group(2))
            i += 1
            continue
        _flush_list(list_items, ordered, out)
        paragraph.append(stripped)
        i += 1
    _flush_paragraph(paragraph, out)
    _flush_list(list_items, ordered, out)
    return '\n'.join(out)
