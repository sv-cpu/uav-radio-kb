"""Сборка статического HTML-сайта для просмотра базы знаний."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import pathlib
import re
import shutil
import sys

from scripts.markdown_html import markdown_to_html
from scripts.validate import ROOT, SECTIONS, read_article, validate

SECTION_TITLES = {
    '01-radio-fundamentals': 'Основы радиосвязи',
    '02-wave-propagation': 'Распространение радиоволн',
    '03-antennas': 'Антенны',
    '04-radio-hardware': 'Радиооборудование',
    '05-control-links': 'Каналы управления',
    '06-video-links': 'Видеоканалы',
    '07-telemetry': 'Телеметрия',
    '08-calculations': 'Расчёты',
    '09-diagnostics': 'Диагностика',
    '10-interference': 'Помехи и совместимость',
    '11-standards': 'Стандарты и нормативы',
    '12-field-cases': 'Полевые случаи',
    '13-equipment': 'Карточки оборудования',
}

STATUS_LABEL = {
    'verified': 'проверено',
    'needs_review': 'на ревью',
    'draft': 'черновик',
    'deprecated': 'устарело',
}

CSS = """
:root {
  --bg: #10161c;
  --bg-elev: #171f28;
  --muted: #9aa8b5;
  --line: #2a3642;
  --accent: #d08a45;
  --accent-2: #5ec2b7;
  --ok: #6fbf7a;
  --warn: #d4b15a;
  --draft: #8ea0b0;
  --danger: #c77b7b;
  --serif: "Literata", "Iowan Old Style", "Palatino Linotype", Palatino, serif;
  --sans: "Manrope", "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, monospace;
  --max: 68rem;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  min-height: 100vh;
  color: #e8eef4;
  font-family: var(--sans);
  background:
    radial-gradient(1200px 500px at 10% -10%, rgba(208,138,69,0.18), transparent 55%),
    radial-gradient(900px 420px at 100% 0%, rgba(94,194,183,0.12), transparent 50%),
    linear-gradient(180deg, #0d1217 0%, var(--bg) 40%, #0c1116 100%);
}
a { color: var(--accent-2); text-decoration-thickness: 1px; text-underline-offset: 0.18em; }
a:hover { color: #9fe0d8; }
.wrap { width: min(var(--max), calc(100% - 2rem)); margin: 0 auto; }
.top {
  position: sticky; top: 0; z-index: 5;
  backdrop-filter: blur(10px);
  background: rgba(13,18,23,0.82);
  border-bottom: 1px solid rgba(42,54,66,0.9);
}
.top-inner {
  display: flex; align-items: center; justify-content: space-between;
  gap: 1rem; padding: 0.85rem 0;
}
.brand {
  color: #f3f6f8; font-weight: 700; letter-spacing: 0.02em;
  text-decoration: none; font-size: 1.02rem;
}
.brand span { color: var(--accent); }
.nav-links { display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.92rem; }
.nav-links a { color: var(--muted); text-decoration: none; }
.nav-links a:hover { color: #f3f6f8; }
.hero {
  padding: 2.6rem 0 1.6rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.6rem;
}
.hero .eyebrow {
  color: var(--accent); text-transform: uppercase; letter-spacing: 0.14em;
  font-size: 0.75rem; font-weight: 700; margin: 0 0 0.7rem;
}
.hero h1 {
  font-family: var(--serif); font-weight: 600; font-size: clamp(1.8rem, 4vw, 2.6rem);
  line-height: 1.15; margin: 0 0 0.8rem; max-width: 20ch;
}
.hero p { color: var(--muted); max-width: 42rem; margin: 0; font-size: 1.05rem; }
.layout {
  display: grid; grid-template-columns: 16rem minmax(0, 1fr); gap: 1.5rem;
  padding-bottom: 3rem;
}
@media (max-width: 860px) {
  .layout { grid-template-columns: 1fr; }
  .side { position: static !important; }
}
.side {
  position: sticky; top: 4.2rem; align-self: start;
  background: rgba(23,31,40,0.72); border: 1px solid var(--line);
  border-radius: 0.7rem; padding: 0.9rem 0.95rem;
  max-height: calc(100vh - 5rem); overflow: auto;
}
.side h2 {
  margin: 0 0 0.65rem; font-size: 0.78rem; text-transform: uppercase;
  letter-spacing: 0.12em; color: var(--muted); font-weight: 700;
}
.side ol { list-style: none; margin: 0; padding: 0; }
.side li { margin: 0; }
.side a {
  display: block; padding: 0.38rem 0.45rem; border-radius: 0.4rem;
  color: #d7e0e8; text-decoration: none; font-size: 0.92rem;
}
.side a:hover, .side a[aria-current="page"] {
  background: rgba(208,138,69,0.14); color: #fff;
}
.side .count { color: var(--muted); font-size: 0.8rem; margin-left: 0.25rem; }
.main { min-width: 0; }
.section-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr)); gap: 0.85rem;
}
.section-tile {
  display: block; padding: 1rem 1rem 1.1rem; border-radius: 0.7rem;
  border: 1px solid var(--line); background: rgba(23,31,40,0.65);
  text-decoration: none; color: inherit;
  transition: border-color 0.2s ease, transform 0.2s ease;
}
.section-tile:hover { border-color: rgba(208,138,69,0.55); transform: translateY(-1px); }
.section-tile strong {
  display: block; font-family: var(--serif); font-size: 1.15rem; margin-bottom: 0.35rem;
}
.section-tile .meta { color: var(--muted); font-size: 0.88rem; }
.article-list { list-style: none; margin: 0; padding: 0; }
.article-list li {
  border-top: 1px solid var(--line); padding: 0.85rem 0;
  display: grid; gap: 0.35rem;
}
.article-list a.title {
  color: #f2f6fa; text-decoration: none; font-size: 1.05rem; font-weight: 600;
}
.article-list a.title:hover { color: var(--accent-2); }
.article-list .summary { color: var(--muted); margin: 0; font-size: 0.95rem; }
.badge {
  display: inline-block; border-radius: 0.3rem; padding: 0.12rem 0.45rem;
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase;
}
.badge.verified { background: rgba(111,191,122,0.18); color: var(--ok); }
.badge.needs_review { background: rgba(212,177,90,0.18); color: var(--warn); }
.badge.draft { background: rgba(142,160,176,0.18); color: var(--draft); }
.badge.deprecated { background: rgba(199,123,123,0.18); color: var(--danger); }
.badge.planned { background: rgba(94,194,183,0.12); color: #8fd4cc; }
.article {
  background: rgba(23,31,40,0.55); border: 1px solid var(--line);
  border-radius: 0.8rem; padding: 1.25rem 1.25rem 1.6rem;
}
.article-meta {
  display: flex; flex-wrap: wrap; gap: 0.55rem; align-items: center;
  margin: 0 0 1rem; color: var(--muted); font-size: 0.9rem;
}
.article .body {
  font-family: var(--serif); font-size: 1.08rem; line-height: 1.65; color: #e9eef3;
}
.article .body h1, .article .body h2, .article .body h3, .article .body h4 {
  font-family: var(--sans); line-height: 1.25; color: #f7fafc;
}
.article .body h1 { font-size: 1.7rem; margin-top: 0; }
.article .body h2 { font-size: 1.28rem; margin-top: 1.6rem; }
.article .body h3 { font-size: 1.1rem; margin-top: 1.3rem; }
.article .body p { margin: 0.75rem 0; }
.article .body code {
  font-family: var(--mono); font-size: 0.9em;
  background: rgba(0,0,0,0.28); padding: 0.08rem 0.28rem; border-radius: 0.25rem;
}
.article .body table {
  width: 100%; border-collapse: collapse; margin: 1rem 0; font-family: var(--sans);
  font-size: 0.95rem;
}
.article .body th, .article .body td {
  border: 1px solid var(--line); padding: 0.5rem 0.55rem; vertical-align: top;
}
.article .body th { background: rgba(0,0,0,0.25); text-align: left; }
.article .body ul, .article .body ol { padding-left: 1.25rem; }
.related {
  margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid var(--line);
}
.related h2 {
  font-size: 0.95rem; margin: 0 0 0.5rem; color: var(--muted);
  text-transform: uppercase; letter-spacing: 0.08em;
}
.related ul { margin: 0; padding-left: 1.1rem; }
.planned-list { margin: 1rem 0 0; padding: 0; list-style: none; }
.planned-list li {
  color: var(--muted); padding: 0.45rem 0; border-top: 1px dashed var(--line);
  font-size: 0.95rem;
}
.footer {
  border-top: 1px solid var(--line); color: var(--muted);
  padding: 1.25rem 0 2rem; font-size: 0.88rem;
}
.notice {
  margin: 0 0 1.2rem; padding: 0.75rem 0.9rem; border-radius: 0.55rem;
  border: 1px solid rgba(208,138,69,0.35); background: rgba(208,138,69,0.08);
  color: #f0d2b0; font-size: 0.92rem;
}
"""


def escape(text: str) -> str:
    return html.escape(text, quote=True)


def site_href(base: str, target: str) -> str:
    """Ссылка от корня сайта. base — '' или '/repo'; target без ведущего /."""
    target = target.lstrip('/')
    root = base.rstrip('/') if base else ''
    return f'{root}/{target}'


def page_shell(
    title: str,
    body: str,
    *,
    base: str,
    current_section: str | None,
    sections: list[tuple[str, str, int]],
) -> str:
    nav = []
    for sid, stitle, count in sections:
        href = site_href(base, f'{sid}/index.html')
        current = ' aria-current="page"' if sid == current_section else ''
        nav.append(
            f'<li><a href="{escape(href)}"{current}>{escape(stitle)}'
            f'<span class="count">({count})</span></a></li>'
        )
    built = dt.date.today().isoformat()
    root = site_href(base, 'index.html')
    css = site_href(base, 'assets/site.css')
    plan = site_href(base, 'plan.html')
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Literata:opsz,wght@7..72,500;7..72,600&family=Manrope:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{escape(css)}">
</head>
<body>
<header class="top"><div class="wrap top-inner">
  <a class="brand" href="{escape(root)}">UAV Radio <span>KB</span></a>
  <nav class="nav-links">
    <a href="{escape(root)}">Разделы</a>
    <a href="{escape(plan)}">План 65</a>
  </nav>
</div></header>
<div class="wrap layout">
<aside class="side"><h2>Разделы</h2><ol>{''.join(nav)}</ol></aside>
<main class="main">{body}</main>
</div>
<footer class="wrap footer">
  Обзорная HTML-версия для проверки. Материалы — только для просмотра;
  копирование без разрешения запрещено. Сборка: {built}.
</footer>
</body>
</html>
"""


def load_articles(root: pathlib.Path):
    articles = []
    by_id = {}
    for path in sorted((root / 'docs').rglob('*.md')):
        if path.name == 'index.md':
            continue
        meta, body = read_article(path)
        item = {
            'path': path,
            'meta': meta,
            'body': body,
            'section': meta['section'],
            'slug': path.stem,
            'rel_html': f"{meta['section']}/{path.stem}.html",
        }
        articles.append(item)
        by_id[meta['id']] = item
    return articles, by_id


def parse_plan(root: pathlib.Path) -> list[tuple[str, str]]:
    text = (root / 'reports/article-plan.md').read_text(encoding='utf-8')
    items = []
    for match in re.finditer(r'^- \*\*(\d+\.\d+)\*\* (.+)\.\s*$', text, re.M):
        items.append((match.group(1), match.group(2).rstrip('.')))
    return items


def section_number(section_id: str) -> str:
    return str(int(section_id.split('-', 1)[0]))


def _articles_label(count: int) -> str:
    mod10 = count % 10
    mod100 = count % 100
    if mod10 == 1 and mod100 != 11:
        word = 'статья'
    elif 2 <= mod10 <= 4 and not 12 <= mod100 <= 14:
        word = 'статьи'
    else:
        word = 'статей'
    return f'{count} {word} на сайте'


def build(root: pathlib.Path, output: pathlib.Path, base_url: str = '') -> int:
    errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    if output.exists():
        shutil.rmtree(output)
    assets = output / 'assets'
    assets.mkdir(parents=True)
    (assets / 'site.css').write_text(CSS, encoding='utf-8')

    base = base_url.rstrip('/')
    articles, by_id = load_articles(root)
    counts = {sid: 0 for sid in sorted(SECTIONS)}
    for article in articles:
        counts[article['section']] += 1
    section_nav = [(sid, SECTION_TITLES[sid], counts[sid]) for sid in sorted(SECTIONS)]

    tiles = []
    for sid, title, count in section_nav:
        href = site_href(base, f'{sid}/index.html')
        tiles.append(
            f'<a class="section-tile" href="{escape(href)}">'
            f'<strong>{escape(section_number(sid) + ". " + title)}</strong>'
            f'<div class="meta">{escape(_articles_label(count))}</div></a>'
        )
    home_body = f"""
<section class="hero">
  <p class="eyebrow">Обзор для проверки</p>
  <h1>Инженерная база знаний по радиосвязи БПЛА</h1>
  <p>Разделы и статьи из репозитория. Статусы: проверено, на ревью, черновик.
  Это HTML-витрина для чтения, не нормативный документ и не основной RAG.</p>
</section>
<p class="notice">Собственные материалы доступны только для просмотра. Копирование и
переиспользование без письменного разрешения правообладателя не допускаются.</p>
<section class="section-grid">{''.join(tiles)}</section>
"""
    (output / 'index.html').write_text(
        page_shell('UAV Radio KB', home_body, base=base, current_section=None, sections=section_nav),
        encoding='utf-8', newline='\n',
    )

    plan_items = parse_plan(root)
    plan_lis = ''.join(
        f'<li><span class="badge planned">{escape(num)}</span> {escape(title)}</li>'
        for num, title in plan_items
    )
    plan_body = f"""
<section class="hero">
  <p class="eyebrow">План первой версии</p>
  <h1>65 согласованных материалов</h1>
  <p>Наличие пункта в плане не означает готовности статьи. Фактические файлы
  и статусы смотрите в разделах.</p>
</section>
<ul class="planned-list">{plan_lis}</ul>
"""
    (output / 'plan.html').write_text(
        page_shell('План статей — UAV Radio KB', plan_body, base=base,
                   current_section=None, sections=section_nav),
        encoding='utf-8', newline='\n',
    )

    for sid in sorted(SECTIONS):
        section_dir = output / sid
        section_dir.mkdir(parents=True, exist_ok=True)
        section_articles = [a for a in articles if a['section'] == sid]
        index_path = root / 'docs' / sid / 'index.md'
        intro = ''
        if index_path.is_file():
            raw = index_path.read_text(encoding='utf-8')
            body_md = re.sub(r'^# .*\n+', '', raw, count=1)
            intro = f'<div class="body">{markdown_to_html(body_md)}</div>'
        lis = []
        for article in section_articles:
            meta = article['meta']
            status = meta['status']
            lis.append(
                f'<li><div><span class="badge {escape(status)}">'
                f'{escape(STATUS_LABEL.get(status, status))}</span></div>'
                f'<a class="title" href="{escape(site_href(base, article["rel_html"]))}">'
                f'{escape(meta["title"])}</a>'
                f'<p class="summary">{escape(meta["summary"])}</p></li>'
            )
        empty = ''
        if not section_articles:
            empty = (
                '<p class="summary">В этом разделе пока нет подготовленных статей. '
                f'См. <a href="{escape(site_href(base, "plan.html"))}">план</a>.</p>'
            )
        section_body = f"""
<section class="hero">
  <p class="eyebrow">Раздел {escape(section_number(sid))}</p>
  <h1>{escape(SECTION_TITLES[sid])}</h1>
</section>
{intro}
<ul class="article-list">{''.join(lis)}</ul>
{empty}
"""
        (section_dir / 'index.html').write_text(
            page_shell(
                f'{SECTION_TITLES[sid]} — UAV Radio KB',
                section_body,
                base=base,
                current_section=sid,
                sections=section_nav,
            ),
            encoding='utf-8',
            newline='\n',
        )

        for article in section_articles:
            meta = article['meta']
            body_html = markdown_to_html(article['body'])
            related = []
            for rid in meta.get('related', []):
                target = by_id.get(rid)
                if not target:
                    continue
                href = site_href(base, target['rel_html'])
                related.append(
                    f'<li><a href="{escape(href)}">{escape(target["meta"]["title"])}</a></li>'
                )
            related_block = ''
            if related:
                related_block = (
                    '<section class="related"><h2>Связанные статьи</h2><ul>'
                    + ''.join(related)
                    + '</ul></section>'
                )
            art_body = f"""
<article class="article">
  <div class="article-meta">
    <span class="badge {escape(meta['status'])}">
      {escape(STATUS_LABEL.get(meta['status'], meta['status']))}
    </span>
    <span>{escape(meta['type'])}</span>
    <span>обновлено {escape(meta['updated_at'])}</span>
  </div>
  <div class="body">{body_html}</div>
  {related_block}
</article>
"""
            (section_dir / f'{article["slug"]}.html').write_text(
                page_shell(
                    f'{meta["title"]} — UAV Radio KB',
                    art_body,
                    base=base,
                    current_section=sid,
                    sections=section_nav,
                ),
                encoding='utf-8',
                newline='\n',
            )

    # .nojekyll so GitHub Pages serves as-is
    (output / '.nojekyll').write_text('', encoding='utf-8')
    return len(articles)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build static review site')
    parser.add_argument('--output', type=pathlib.Path, default=ROOT / 'build/site')
    parser.add_argument(
        '--base-url',
        default='',
        help='Prefix for GitHub Pages project site, e.g. /uav-radio-kb',
    )
    args = parser.parse_args(argv)
    try:
        count = build(ROOT, args.output, base_url=args.base_url)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f'Built site with {count} articles at {args.output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
