"""Reviewed-by-code service briefs; editorial guidance, not provider claims."""
import hashlib
import json
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent


@lru_cache(maxsize=1)
def catalog():
    result = {}
    for path in sorted((ROOT / 'data').glob('*.json')):
        entries = json.loads(path.read_text(encoding='utf-8'))
        overlap = result.keys() & entries.keys()
        if overlap:
            raise ValueError(f'Duplicate service briefs: {sorted(overlap)}')
        result.update(entries)
    return result


@lru_cache(maxsize=1)
def legacy():
    return json.loads((ROOT / 'legacy_fingerprints.json').read_text(encoding='utf-8'))


def fingerprint(text):
    return hashlib.sha256(' '.join(text.split()).encode()).hexdigest()


def get_content(category):
    slug = category if isinstance(category, str) else category.slug
    content = catalog().get(slug)
    if content and not isinstance(category, str):
        names = legacy()['names'].get(slug, [content['name']])
        if category.ad not in names:
            return None  # Preserve a category repurposed by its editor.
    return content


def metadata_value(category, field):
    stored = getattr(category, field, '') or ''
    content = get_content(category)
    if content and (not stored.strip() or fingerprint(stored) in legacy()[field]):
        return content['heading'] + ' | Prousta.az' if field == 'seo_title' else content['description']
    return stored


class _Blocks(HTMLParser):
    """Locate top-level blocks without reserializing or altering custom HTML."""
    void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.stack, self.ranges = [], []
        self.feed(source)
        self.close()

    def position(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if not self.stack:
            self.start = self.position()
        if tag not in self.void:
            self.stack.append(tag)
        elif not self.stack:
            self.ranges.append((self.start, self.position() + len(self.get_starttag_text())))

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            if not self.stack:
                end = self.source.find('>', self.position())
                if end >= 0:
                    self.ranges.append((self.start, end + 1))


def additional_html(category):
    text = category.seo_metn
    if not text or not get_content(category):
        return text
    known = set(legacy()['html_blocks'])
    parser = _Blocks(text)
    pieces, cursor = [], 0
    for start, end in parser.ranges:
        pieces.append(text[cursor:start])
        if fingerprint(text[start:end]) not in known:
            pieces.append(text[start:end])
        cursor = end
    pieces.append(text[cursor:])
    return ''.join(pieces).strip()
