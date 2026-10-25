from django import template
from core.seo_metadata import build_metadata

register = template.Library()


@register.inclusion_tag('partials/seo_head.html', takes_context=True)
def seo_head(context):
    metadata = build_metadata(context)
    return {'seo': metadata, 'GOOGLE_SITE_VERIFICATION': context.get('GOOGLE_SITE_VERIFICATION', ''),
            'YANDEX_VERIFICATION': context.get('YANDEX_VERIFICATION', '')}
