from django import template
from core.image_optimizer import (
    optimize_cloudinary_url,
    get_card_image_url,
    get_detail_image_url,
    get_thumb_image_url,
)

register = template.Library()


@register.filter(name='absolute_media')
def absolute_media(url):
    if not url:
        return ''
    value = str(url)
    if value.startswith(('https://', 'http://')):
        return value
    from core.seo import SITE_URL
    return SITE_URL + '/' + value.lstrip('/')


@register.filter(name='cld_opt')
def cld_opt(image_or_url, transform='f_auto,q_auto'):
    """Şəkil obyektini və ya URL-i optimallaşdırır."""
    if not image_or_url:
        return ''
    url = getattr(image_or_url, 'url', str(image_or_url))
    return optimize_cloudinary_url(url, transform)


@register.filter(name='cld_card')
def cld_card(image_or_url):
    """Kartlar üçün optimallaşdırılmış WebP URL (~15-25 KB)."""
    if not image_or_url:
        return ''
    url = getattr(image_or_url, 'url', str(image_or_url))
    return get_card_image_url(url)


@register.filter(name='cld_detail')
def cld_detail(image_or_url):
    """Elan daxili əsas şəkil üçün Full HD keyfiyyətli WebP URL."""
    if not image_or_url:
        return ''
    url = getattr(image_or_url, 'url', str(image_or_url))
    return get_detail_image_url(url)


@register.filter(name='cld_thumb')
def cld_thumb(image_or_url):
    """Qalereya kiçik thumbnail-ləri üçün WebP URL."""
    if not image_or_url:
        return ''
    url = getattr(image_or_url, 'url', str(image_or_url))
    return get_thumb_image_url(url)
