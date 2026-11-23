from django import template
from core.seo_metadata import build_metadata, service_faq
from core.service_content import get_content, additional_html, source_links

register = template.Library()


@register.inclusion_tag('partials/seo_head.html', takes_context=True)
def seo_head(context):
    metadata = build_metadata(context)
    return {'seo': metadata, 'GOOGLE_SITE_VERIFICATION': context.get('GOOGLE_SITE_VERIFICATION', ''),
            'YANDEX_VERIFICATION': context.get('YANDEX_VERIFICATION', '')}


@register.inclusion_tag('partials/service_guide.html', takes_context=True)
def service_guide(context):
    category = context['aktiv_kategori']
    return {'category': category, 'brief': get_content(category),
            **{key: context.get(key) for key in ('priority_service', 'service_provider', 'service_sources', 'service_related')},
            'additional_html': additional_html(category), 'source_links': source_links(category)}


@register.inclusion_tag('partials/service_questions.html', takes_context=True)
def service_questions(context):
    return {'questions': service_faq(context)}
