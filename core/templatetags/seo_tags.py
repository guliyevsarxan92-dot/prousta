from django import template
from core.seo_metadata import build_metadata, service_faq
from core.service_content import get_content, additional_html, source_links
from core.ru_content import category_name_ru, service_brief_ru

register = template.Library()


@register.filter
def ru_cat(category):
    return category_name_ru(category)


@register.inclusion_tag('partials/seo_head.html', takes_context=True)
def seo_head(context):
    metadata = build_metadata(context)
    return {'seo': metadata, 'GOOGLE_SITE_VERIFICATION': context.get('GOOGLE_SITE_VERIFICATION', ''),
            'YANDEX_VERIFICATION': context.get('YANDEX_VERIFICATION', '')}


@register.inclusion_tag('partials/service_guide.html', takes_context=True)
def service_guide(context):
    category = context['aktiv_kategori']
    is_ru = bool(context.get('is_ru'))
    brief = service_brief_ru(category) if is_ru else get_content(category)
    return {'category': category, 'brief': brief, 'is_ru': is_ru,
            **{key: context.get(key) for key in ('priority_service', 'service_provider', 'service_sources', 'service_related')},
            'additional_html': '' if is_ru else additional_html(category),
            'source_links': source_links(category)}


@register.inclusion_tag('partials/service_questions.html', takes_context=True)
def service_questions(context):
    return {'questions': service_faq(context), 'is_ru': bool(context.get('is_ru'))}
