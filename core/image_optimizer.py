import io
from PIL import Image, ImageOps
from django.core.files.uploadedfile import InMemoryUploadedFile


def optimize_cloudinary_url(url, transform='f_auto,q_auto'):
    """
    Cloudinary şəkil URL-lərinə avtomatik müasir format (WebP/AVIF) və 
    ağıllı sıxılma (q_auto) əlavə edir.
    Əgər şəkil lokal fayl sistemindədirsə (Cloudinary deyilsə), URL-i toxunulmaz saxlayır.
    """
    if not url:
        return ''
    
    url_str = str(url)
    if '/image/upload/' in url_str:
        parts = url_str.split('/image/upload/', 1)
        sub = parts[1]
        # Artıq transformasiya varsa, təkrar əlavə etmə
        if sub.startswith(('f_auto', 'w_', 'q_', 'c_')):
            return url_str
        return f"{parts[0]}/image/upload/{transform}/{sub}"
    
    return url_str


def get_card_image_url(url):
    """Ana səhifə və axtarış kartları üçün yüngül WebP URL (~15-25 KB)."""
    return optimize_cloudinary_url(url, 'f_auto,q_auto,w_500,c_limit')


def get_detail_image_url(url):
    """Elan daxili əsas şəkil üçün Full HD keyfiyyətli WebP URL (~60-90 KB)."""
    return optimize_cloudinary_url(url, 'f_auto,q_auto,w_1200,c_limit')


def get_thumb_image_url(url):
    """Qalereya kiçik ikonları üçün URL (~5-10 KB)."""
    return optimize_cloudinary_url(url, 'f_auto,q_auto,w_160,c_limit')


def compress_uploaded_image(uploaded_file, max_size=(1600, 1600), quality=85):
    """
    İstifadəçinin yüklədiyi şəkli (telefon kamerasından çıxan 5-10MB fotoları)
    yaddaşda avtomatik 1600px həddinə endirir və keyfiyyəti itirmədən yüngülləşdirir.
    """
    if not uploaded_file:
        return uploaded_file

    try:
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)

        im = Image.open(uploaded_file)
        # EXIF orientation (telefon şəkillərinin yan çevrilməsinin qarşısını almaq üçün)
        im = ImageOps.exif_transpose(im)

        if getattr(im, 'format', None) in ('GIF', 'SVG'):
            if hasattr(uploaded_file, 'seek'):
                uploaded_file.seek(0)
            return uploaded_file

        if im.mode in ('RGBA', 'LA', 'P'):
            im = im.convert('RGB')

        im.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        im.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)

        fname = getattr(uploaded_file, 'name', 'photo.jpg')
        base_name = fname.rsplit('.', 1)[0]
        new_name = f"{base_name}.jpg"

        return InMemoryUploadedFile(
            file=output,
            field_name=getattr(uploaded_file, 'field_name', None),
            name=new_name,
            content_type='image/jpeg',
            size=output.getbuffer().nbytes,
            charset=None
        )
    except Exception:
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(0)
        return uploaded_file
