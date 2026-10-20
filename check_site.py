"""Project-local, dependency-free checks of the published reader artifacts."""
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import json
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.entries = []
        self.quotes = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'details' and 'entry' in attrs.get('class', '').split():
            self.entries.append(attrs['id'])
        if attrs.get('data-field') == 'quote':
            self.quotes.append(tag)


def parse(path):
    doc = Document()
    doc.feed(path.read_text())
    assert len(doc.ids) == len(set(doc.ids)), f'Duplicate HTML IDs: {path.name}'
    return doc


def check():
    sources = json.loads((ROOT / 'sources.json').read_text())
    expected = {'ref-' + source['id'] for source in sources}
    reader = parse(ROOT / 'index.html')
    periods = json.loads((ROOT / 'historical_periods.json').read_text())['entries']
    assert set(periods) == {source['id'] for source in sources}
    for sid, period in periods.items():
        assert period['label'] and period['basis'], f'Missing historical scope: {sid}'
    assert len(expected) == 57
    assert set(reader.entries) == expected, 'Reader references differ from the source records'
    assert len(reader.quotes) == 57, 'Reader must include all 57 excerpts'
    markdown = (ROOT / 'wanderjahre-annotated-bibliography.md').read_text()
    assert set(re.findall(r'<a id="(ref-[^"]+)"', markdown)) == expected
    expected_urls = set(re.findall(r'\]\((https?://[^)]+)\)', markdown))
    assert expected_urls <= set(reader.links), 'Reader lost reference URLs'
    documents = {}
    for name in ('index.html', 'wanderjahre.html'):
        document = parse(ROOT / name)
        documents[name] = document
        for url in document.links:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            destination = ROOT / unquote(parts.path) if parts.path else ROOT / name
            assert destination.is_file(), f'{name}: missing local target {url}'
            if parts.fragment:
                target = unquote(parts.fragment)
                if destination.suffix == '.html':
                    assert target in parse(destination).ids, f'{name}: missing anchor {url}'
                elif destination.suffix == '.md':
                    assert f'id="{target}"' in destination.read_text(), f'Missing Markdown anchor: {url}'
    for name in ('LICENSE', 'CONTENT-LICENSE.md', 'NOTICE.md', 'reader-assets/OFL.txt', '.nojekyll'):
        assert (ROOT / name).is_file(), f'Missing distribution file: {name}'
    print(f'PASS: 57 entries, 57 excerpts, {len(expected_urls)} reference URLs, local links and anchors')


if __name__ == '__main__':
    check()
