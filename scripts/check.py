#!/usr/bin/env python3
"""Check links, fragments, metadata and public assets before publishing."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json

ROOT = Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links, self.h1, self.images = path, [], [], 0, 0
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'img': self.images += 1
        for attr in ['href', 'src']:
            if attr in a: self.links.append(a[attr])

def main():
    docs = {p.name: Document(p) for p in ROOT.glob('*.html')}
    errors, checked = [], 0
    for name, doc in docs.items():
        if len(doc.ids) != len(set(doc.ids)): errors.append(f'{name}: duplicate element ID')
        if doc.h1 != 1: errors.append(f'{name}: expected one main heading')
        if doc.images: errors.append(f'{name}: unexpected image')
        for link in doc.links:
            url = urlparse(link)
            if url.scheme or url.netloc: continue
            target = ROOT / unquote(url.path or name)
            if target.is_dir(): target /= 'index.html'
            if not target.exists(): errors.append(f'{name}: missing {link}')
            elif url.fragment and target.suffix == '.html':
                if unquote(url.fragment) not in docs[target.name].ids:
                    errors.append(f'{name}: missing fragment {link}')
            checked += 1
        # JSON-LD must be parseable and represent complete, public data.
        text = doc.path.read_text()
        start = text.index('<script type="application/ld+json">') + len('<script type="application/ld+json">')
        end = text.index('</script>', start)
        graph = json.loads(text[start:end])
        if graph['@context'] != 'https://schema.org': errors.append(f'{name}: unexpected schema context')
    for path in (ROOT / 'data').glob('*.json'):
        json.loads(path.read_text())
    version = json.loads((ROOT / 'version.json').read_text())['version']
    assert len(version) == 16 and all(c in '0123456789abcdef' for c in version), 'Invalid site version'
    for doc in docs.values():
        text = doc.path.read_text()
        assert f'<meta name="site-version" content="{version}">' in text, 'Page and release versions differ'
        assert 'src="assets/site.js?v=' in text, 'Unversioned site script'
    records = json.loads((ROOT / 'data/publications.json').read_text())
    assert len(records) == len({p['id'] for p in records}), 'Duplicate publication record'
    assert {'paper-' + p['id'] for p in records} == {id for id in docs['research.html'].ids if id.startswith('paper-')}, 'Research page omits or duplicates publication records'
    assert next(p for p in records if p['id'] == 'fuss-catalan')['status'] == 'Work in progress'
    assert not any((ROOT / 'assets').glob('*.jpg')), 'Portrait asset remains'
    assert all((ROOT / f).exists() for f in ['llms.txt', 'llms-full.txt', 'sitemap.xml', 'robots.txt', 'data/profile.json'])
    for path in list(ROOT.glob('*.html')) + list(ROOT.glob('*.md')) + list((ROOT/'data').glob('*.json')):
        text = path.read_text()
        if '/Users/' in text or 'Van Ooststraat' in text or '+32 487' in text:
            errors.append(f'{path.name}: private source detail in public content')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(docs)} pages, {checked} local links/assets, unique anchors, JSON-LD, data exports, no portrait or private application details.')

if __name__ == '__main__':
    main()
