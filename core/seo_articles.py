"""Derive readable summaries and section links from the article's real text."""
import math
import re
from html import escape

from .models import slug_az
from .seo_metadata import plain


def article_context(article):
    headings = []
    used = set()

    def section(match):
        level, attributes, body = match.groups()
        label = plain(body)
        existing = re.search(r'(?:^|\s)id\s*=\s*[\"\']([^\"\']+)[\"\']', attributes, re.I)
        anchor = existing.group(1) if existing else 'bolme-' + (slug_az(label, 70) or 'metn')
        candidate, number = anchor, 2
        while candidate in used:
            candidate = f'{anchor}-{number}'
            number += 1
        used.add(candidate)
        if existing:
            attributes = attributes[:existing.start()] + attributes[existing.end():]
        if label and len(headings) < 30:
            headings.append({'label': label, 'anchor': candidate, 'level': level})
        return f'<h{level}{attributes} id="{escape(candidate, quote=True)}">{body}</h{level}>'

    body = re.sub(r'<h([23])\b([^>]*)>(.*?)</h\1\s*>', section, article.metn, flags=re.I | re.S)
    paragraph = re.search(r'<p\b[^>]*>(.*?)</p\s*>', article.metn, flags=re.I | re.S)
    summary = plain(paragraph.group(1) if paragraph else article.metn, 280)
    return {'article_body': body, 'article_toc': headings,
            'article_summary': summary, 'article_read_minutes': max(1, math.ceil(len(plain(article.metn).split()) / 200))}
