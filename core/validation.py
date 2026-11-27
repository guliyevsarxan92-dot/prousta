"""Shared input rules used by both HTML and API entry points."""
import io
import re
import warnings
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import DecimalValidator
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, ImageOps, UnidentifiedImageError
from rest_framework.views import exception_handler
from rest_framework.response import Response


class PasswordLengthValidator:
    def validate(self, password, user=None):
        if len(password) > 128:
            raise ValidationError('Şifrə maksimum 128 simvol ola bilər.')

    def get_help_text(self):
        return 'Şifrə maksimum 128 simvol ola bilər.'


def api_exception_handler(exc, context):
    if isinstance(exc, ValidationError):
        return Response({'error': ' '.join(exc.messages)}, status=400)
    return exception_handler(exc, context)


def money(value, *, minimum=Decimal('0'), maximum=Decimal('99999999.99'), optional=False):
    if optional and (value is None or value == ''):
        return None
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result < minimum or result > maximum:
            raise ValueError
        DecimalValidator(10, 2)(result)
    except (InvalidOperation, ValueError, TypeError, ValidationError):
        raise ValidationError('Məbləğ düzgün deyil və ya icazə verilən həddən kənardır.')
    return result


def phone(value, *, optional=False):
    if optional and not value:
        return ''
    if not isinstance(value, str) or re.search(r'[^\d+\s()\-]', value):
        raise ValidationError('Telefon nömrəsi düzgün deyil.')
    digits = re.sub(r'\D', '', value)
    if len(digits) == 12 and digits.startswith('994'):
        digits = digits[3:]
    elif len(digits) == 10 and digits.startswith('0'):
        digits = digits[1:]
    if len(digits) != 9 or not digits.isascii():
        raise ValidationError('Telefon nömrəsi 9 rəqəmdən ibarət olmalıdır.')
    return '+994' + digits


def text(value, label, maximum, *, minimum=1):
    if not isinstance(value, str):
        raise ValidationError(f'{label} mətn olmalıdır.')
    value = value.strip()
    if not minimum <= len(value) <= maximum:
        raise ValidationError(f'{label}: uzunluq {minimum}–{maximum} simvol olmalıdır.')
    return value


def image_upload(upload, *, max_bytes=5 * 1024 * 1024):
    """Decode, bound memory/CPU, and re-encode all untrusted image bytes."""
    if upload is None or upload.size > max_bytes:
        raise ValidationError('Şəkil tələb olunur və 5 MB-dan böyük ola bilməz.')
    try:
        upload.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(upload) as source:
                if source.format not in {'JPEG', 'PNG', 'WEBP', 'GIF'}:
                    raise ValueError
                width, height = source.size
                if width * height > 20_000_000 or max(width, height) > 10000:
                    raise ValueError
                source.verify()
            upload.seek(0)
            with Image.open(upload) as source:
                im = ImageOps.exif_transpose(source)
                im.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                rgb = Image.new('RGB', im.size, 'white')
                if 'A' in im.getbands():
                    rgb.paste(im.convert('RGB'), mask=im.getchannel('A'))
                else:
                    rgb.paste(im.convert('RGB'))
                output = io.BytesIO()
                rgb.save(output, 'JPEG', quality=85, optimize=True)
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise ValidationError('Etibarlı JPEG, PNG, WebP və ya GIF şəkli yükləyin (maksimum 20 MP).')
    finally:
        upload.seek(0)
    import uuid
    return SimpleUploadedFile(uuid.uuid4().hex + '.jpg', output.getvalue(), content_type='image/jpeg')


def service_areas(value):
    """Seçilmiş xidmət ərazilərini (rayon/qəsəbə slug-larını) yoxlayır və kanonik ardıcıllıqla birləşdirir."""
    import json
    from .locations import LOKASIYALAR

    if value is None or value == '':
        return ''
    items = []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ''
        if stripped.startswith('['):
            try:
                parsed = json.loads(stripped)
                if not isinstance(parsed, list):
                    raise ValueError
                items = parsed
            except ValueError:
                raise ValidationError('Xidmət əraziləri siyahısı düzgün deyil.')
        else:
            items = stripped.split(',')
    elif isinstance(value, (list, tuple, set)):
        for entry in value:
            if entry is None or entry == '':
                continue
            if isinstance(entry, str) and entry.strip().startswith('['):
                try:
                    parsed = json.loads(entry.strip())
                    if not isinstance(parsed, list):
                        raise ValueError
                    items.extend(parsed)
                except ValueError:
                    raise ValidationError('Xidmət əraziləri siyahısı düzgün deyil.')
            elif isinstance(entry, str) and ',' in entry:
                items.extend(entry.split(','))
            else:
                items.append(entry)
    else:
        raise ValidationError('Xidmət əraziləri siyahısı düzgün deyil.')

    chosen = set()
    name_to_slug = {info['ad'].lower(): s for s, info in LOKASIYALAR.items()}
    for raw in items:
        if not isinstance(raw, str):
            raise ValidationError('Seçilmiş xidmət ərazisi düzgün deyil.')
        slug = raw.strip().lower()
        if not slug:
            continue
        slug = name_to_slug.get(slug, slug)
        if slug not in LOKASIYALAR:
            raise ValidationError('Seçilmiş xidmət ərazisi düzgün deyil.')
        chosen.add(slug)
    return ','.join(slug for slug in LOKASIYALAR if slug in chosen)


def extract_service_areas(data, fallback=''):
    if hasattr(data, 'getlist'):
        if 'xidmet_erazileri' in data:
            return service_areas(data.getlist('xidmet_erazileri'))
        return service_areas(fallback)
    if isinstance(data, dict) and 'xidmet_erazileri' in data:
        return service_areas(data.get('xidmet_erazileri'))
    return service_areas(fallback)


def listing_values(data):
    # Import lazily to keep presentation and input validation independent.
    from .content import description_error
    title = text(data.get('bashliq'), 'Başlıq', 200, minimum=5)
    description = text(data.get('acaqlama'), 'Açıqlama', 10000, minimum=15)
    error = description_error(description)
    if error:
        raise ValidationError(error)
    return {'bashliq': title, 'acaqlama': description,
            'qiymet': money(data.get('qiymet'), optional=True),
            'telefon': phone(data.get('telefon')),
            'sheher': text(data.get('sheher', 'Bakı'), 'Şəhər', 100),
            'xidmet_erazileri': extract_service_areas(data)}
