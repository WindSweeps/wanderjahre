"""Project-specific HTML view of the existing verified annotation records.

The existing build_annotations.py supplies the data, titles and reading paths.
build.py renders the older survey, so this view extends the annotation builder
instead of replacing either document or introducing a client-side framework.
"""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit
import base64
import re

P = Path(__file__).parent


def link(label, url, cls=''):
    if urlsplit(url).scheme not in ('', 'https', 'http'):
        raise ValueError(f'Unsupported link: {url}')
    external = ' target="_blank" rel="noopener noreferrer"' if url.startswith('http') else ''
    return f'<a class="{cls}" href="{escape(url, quote=True)}"{external}>{escape(label)}</a>'


def rich(text):
    """Preserve the source records' inline Markdown links, escape all other text."""
    pieces = []
    start = 0
    for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text):
        pieces.extend([escape(text[start:match.start()]), link(match[1], match[2])])
        start = match.end()
    return ''.join(pieces) + escape(text[start:])


def build_site(sources, notes, titles, groups, intro):
    import json
    periods = json.loads((P / 'historical_periods.json').read_text())['entries']
    assert set(periods) == {s['id'] for s in sources}
    by_id = {x['id']: x for x in notes}
    css = (P / 'reader.css').read_text()
    js = (P / 'reader.js').read_text()
    font = base64.b64encode((P / 'reader-assets/UnifrakturCook-Bold.ttf').read_bytes()).decode()
    licence = (P / 'reader-assets/OFL.txt').read_text().replace('--', '—')
    css = f'@font-face{{font-family:UnifrakturCook;src:url(data:font/ttf;base64,{font}) format("truetype");font-weight:700;font-display:swap}}\n' + css
    routes = []
    for line in intro.splitlines():
        if line.startswith('| ') and '[H' in line or line.startswith('| ') and ('[C' in line or '[R' in line):
            question, refs, purpose = [x.strip() for x in line.strip('|').split('|')]
            routes.append(f'<li><p>{escape(question)}</p><div class="route-refs">{rich(refs)}</div><p class="muted">{escape(purpose)}</p></li>')
    nav = []
    sections = []
    chronology = []
    for s in sorted(sources, key=lambda s: (periods[s['id']]['sort_year'] is None, periods[s['id']]['sort_year'] or 0, s['id'][0], int(s['id'][1:]))):
        sid = s['id']
        period = periods[sid]
        chronology.append(f'<li data-for="ref-{sid}"><a href="#ref-{sid}" title="{escape(period["basis"], quote=True)}"><span class="chronology-date">{escape(period["label"])}</span><span class="chronology-title"><span>{sid}</span> {escape(titles[sid])}</span></a></li>')
    timeline = f'''<aside class="chronology" aria-label="按研究历史时间排序的资料索引"><details class="chronology-directory" open><summary>历史时间 <span class="chronology-count">57 条</span></summary><div class="chronology-body"><p class="chronology-note">按研究对象或史料事件的年代排列。约略时期按起点定位；跨期研究单列。</p><ol>{''.join(chronology)}</ol></div></details></aside>'''
    for prefix, label in groups:
        subset = [s for s in sources if s['id'].startswith(prefix)]
        nav.append(f'<details class="index-group" {"open" if prefix == "H" else ""}><summary><span>{prefix} · {escape(label)}</span><span class="count">{len(subset)}</span></summary><ol>')
        entries = []
        for s in subset:
            sid = s['id']
            a = by_id[sid]
            qurl = a.get('quote_url') or a.get('source_url') or s['url']
            nav.append(f'<li data-for="ref-{sid}">{link(sid + "　" + titles[sid], "#ref-" + sid)}</li>')
            links = [("资料主页 ↗", s['url']), ("引文出处 ↗", qurl)]
            seen = {s['url'], qurl}
            for title, url in s.get('extra', []) + a.get('extra_urls', []):
                if url not in seen:
                    links.append((title + ' ↗', url))
                    seen.add(url)
            heading = '可确认的信息与待核问题' if sid in ('H11', 'A11', 'A17') else '重要观点'
            warning = '<span class="limited">仅书目 · 未取得正文</span>' if sid in ('H11', 'A11') else ''
            bibliographic = f'<p class="bibliographic">{rich(s["locator"])}</p>' if s.get('locator') else ''
            entries.append(f'''<details class="entry" id="ref-{sid}" data-group="{prefix}" {"open" if sid == "H1" else ""}>
<summary><span class="entry-id">{sid}</span><span class="entry-heading"><span class="entry-title">{escape(titles[sid])}</span><span class="entry-meta">{escape(s['author'])} · 出版／编订：{escape(str(s['year']))}</span><span class="research-period">研究时段：{escape(periods[sid]['label'])}</span>{warning}</span><span class="expand-mark" aria-hidden="true"></span></summary>
<div class="entry-body">
<p class="source-title" data-field="title">{link(s['title'], s['url'])}</p>{bibliographic}
<dl class="reading-scope"><dt>实际阅读范围</dt><dd data-field="read_scope">{rich(a['read_scope'])}</dd></dl>
<section class="entry-section"><h3>内容大意</h3><p data-field="summary">{rich(a['summary'])}</p></section>
<section class="entry-section"><h3>{heading}</h3><ul class="points">{''.join('<li>' + rich(t) + '</li>' for t in a['points'])}</ul></section>
<figure class="quotation"><figcaption>原文短摘 <span>· {escape(a['quote_kind'])}</span></figcaption><blockquote data-field="quote">{escape(a['quote'])}</blockquote><p class="translation" data-field="translation"><span class="label">中文译解</span>{rich(a['translation'])}</p><p class="quote-location"><span data-field="locator">{rich(a['locator'])}</span> {link('查看原文 ↗', qurl)}</p></figure>
<section class="entry-section inquiry"><h3>追问与用途</h3><p data-field="use">{rich(a['use'])}</p></section>
<dl class="boundary"><dt>证据边界</dt><dd data-field="limits">{rich(a['limits'])}</dd></dl>
<footer class="entry-links">{''.join(link(title, url) for title, url in links)}{link('研究综述中的 ' + sid, 'wanderjahre.html#ref-' + sid)}{link('本条链接', '#ref-' + sid, 'permalink')}</footer>
</div></details>''')
        nav.append('</ol></details>')
        sections.append(f'<section class="reference-group" data-group="{prefix}" id="group-{prefix}"><h2><span>{prefix}</span> {escape(label)}<small>{len(subset)} 条</small></h2>{"".join(entries)}</section>')
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Wanderjahre 文献导读：57条资料的摘要、观点、原文与译解，附出处、证据边界与批判性追问。"><meta name="theme-color" content="#f3eddf"><title>Wanderjahre · 文献导读</title><style>{css}</style></head>
<body><a class="skip-link" href="#reading">跳到文献正文</a>
<header class="masthead"><div class="masthead-inner"><a class="wordmark" href="#top" lang="de">Wanderjahre</a><h1>文献导读</h1><nav aria-label="文档导航"><a href="wanderjahre.html">研究综述</a><a href="wanderjahre-annotated-bibliography.md" download>下载 Markdown</a><button type="button" data-print hidden>打印</button></nav></div></header>
<div class="layout" id="top"><aside class="sidebar" aria-label="文献索引"><details class="directory" open><summary>文献目录 <span>57 条</span></summary><div class="directory-body">{''.join(nav)}<p class="sidebar-note">核心时段 1350—1650<br>制度、艺术与跨地域比较</p></div></details></aside>
{timeline}
<main id="reading" tabindex="-1"><div class="reader-heading"><p>文艺复兴前后的工匠游历</p><span>57 条参考资料</span></div>
<div class="reader-tools" hidden><div class="search-line"><label class="sr-only" for="reader-search">搜索编号、作者、题名或正文</label><input id="reader-search" type="search" placeholder="搜索编号、作者、题名或正文…" autocomplete="off" spellcheck="false"><button id="clear-search" type="button" hidden>清除</button></div><div class="tool-row"><label class="sr-only" for="group-filter">资料分组</label><select id="group-filter"><option value="all">全部资料</option>{''.join(f'<option value="{k}">{k} · {escape(v)}</option>' for k,v in groups)}</select><button type="button" id="toggle-entries" aria-expanded="false">展开全部</button></div><p id="result-count" class="result-count" aria-live="polite">显示全部 57 条</p></div>
<div class="reading-notes"><details class="reading-note"><summary>阅读说明与证据边界</summary><div><p>以下为已有导读的网页呈现。文献核读记录日期为 2026年10月7日；网页整理日期为 2026年10月20日。</p><p>每条保留实际阅读范围、原文类型与定位。“追问与用途”为本次调研的分析，译文为译解；均不冒充作者原话。编号沿用原调研，跳号保留。</p><p>H11、A11未取得实质正文；A4短摘为章节题名；A7依据馆方图录介绍；A17依据抄本编目。A5是Stewart的书评，不能归为Luber原话。详情在对应条目中注明。</p><p>书目、摘要和局部精读不等于全文通读。此页转换保留原有资料判断，未重新核查全部外部网页。</p></div></details><details class="reading-note"><summary>按问题并读</summary><ol class="reading-routes">{''.join(routes)}</ol></details></div>
<div id="empty-state" hidden><h2>没有找到匹配资料</h2><p>试试作者姓氏、资料编号，或缩短关键词。</p><button type="button" id="reset-filters">清除全部筛选</button></div>
{''.join(sections)}
<footer class="reader-footer"><p>Wanderjahre · 参考资料导读</p><p><a href="wanderjahre-annotated-bibliography.md" download>导读 Markdown</a> · <a href="wanderjahre.md" download>研究综述 Markdown</a> · <a href="#top">回到开头 ↑</a></p></footer>
</main></div><script>{js}</script>
<!-- Font copyright and licence, retained with the unmodified embedded font:\n{licence}\n--></body></html>'''
    (P / 'index.html').write_text(html)
    return len(html.encode())
