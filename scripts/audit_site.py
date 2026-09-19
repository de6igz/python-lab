"""Проверка локальных ссылок/ресурсов и отсутствия CDN в HTML/CSS."""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.external_assets = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for field in ('src', 'href'):
            value = attrs.get(field)
            if not value:
                continue
            if tag in ('script', 'img', 'iframe', 'source') or tag == 'link' and attrs.get('rel') in ('stylesheet', 'preload'):
                if value.startswith(('https://', 'http://', '//')):
                    self.external_assets.append(value)
            self.refs.append(value)


def audit(root):
    root = Path(root).resolve()
    documents = {}
    errors = []
    for path in root.rglob('*.html'):
        parser = Links()
        parser.feed(path.read_text())
        documents[path] = parser
        errors.extend(f'{path.relative_to(root)}: CDN resource {v}' for v in parser.external_assets)
    for path, parser in documents.items():
        for ref in parser.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc or ref.startswith('/'):
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= 'index.html'
            if not target.exists():
                errors.append(f'{path.relative_to(root)}: missing {ref}')
            elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
                errors.append(f'{path.relative_to(root)}: missing anchor {ref}')
    for path in root.rglob('*.css'):
        if re.search(r'url\(\s*[\"\x27]?(?:https?:)?//', path.read_text()):
            errors.append(f'{path.relative_to(root)}: external CSS asset')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'audit OK: {len(documents)} HTML files, no missing local links or external HTML/CSS assets')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('site', type=Path)
    audit(parser.parse_args().site)
