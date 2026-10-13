"""
core/watermark.py
Şəkillərdə filiqran (watermark), kənar platformaların loqoları (tap.az, lalafo, turbo.az və s.)
və su nişanlarının avtomatik aşkarlanması modulu.
Xarici C/C++ və ya OCR asılılığı olmadan, saf Python və Pillow ilə yüksək sürətli işləyir.
"""

import math
from PIL import Image

# Qadağan olunmuş kənar platforma adları və filiqran açar sözləri
FORBIDDEN_KEYWORDS = [
    'tap.az', 'tap_az', 'tapaz', 'tap-az',
    'lalafo',
    'turbo.az', 'turboaz', 'turbo_az',
    'bina.az', 'binaaz', 'bina_az',
    'boss.az', 'bossaz', 'boss_az',
    'watermark', 'water-mark', 'water_mark',
    'filigran', 'filiqran',
    'su-nisani', 'su_nisani', 'sunisani',
    'shutterstock', 'gettyimages', 'istockphoto', 'depositphotos',
]


def filigran_yoxla(file_obj, filename=None):
    """
    Yüklənmiş şəkil faylını filiqran və ya kənar platforma loqosu üçün yoxlayır.
    
    Qaytarır:
        (True, xeta_mesaji)  - Filiqran və ya kənar loqo aşkar edildikdə
        (False, '')          - Şəkil təmiz olduqda
    """
    fname = (filename or getattr(file_obj, 'name', '') or '').lower()

    # 1. Fayl adında kənar platforma və ya filiqran açar sözləri
    for kw in FORBIDDEN_KEYWORDS:
        if kw in fname:
            return True, f"Fayl adında kənar platforma və ya filiqran izi aşkar edildi ({kw})"

    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

        im = Image.open(file_obj)

        # 2. Şəkil metadatasında (EXIF, IPTC, PNG info) kənar sayt izi
        meta_str = ''
        try:
            exif = im.getexif()
            if exif:
                for k, v in exif.items():
                    meta_str += f" {v}".lower()
        except Exception:
            pass

        if hasattr(im, 'info') and isinstance(im.info, dict):
            for k, v in im.info.items():
                meta_str += f" {v}".lower()

        for kw in FORBIDDEN_KEYWORDS:
            if kw in meta_str:
                return True, f"Şəkil məlumatlarında (metadata/EXIF) filiqran aşkar edildi ({kw})"

        # 3. Şəklin künclərində və kənarlarında loqo/filiqran nişanının vizual təhlili
        w, h = im.size
        # Minimum analiz ölçüsü (çox kiçik şəkillər onsuz da standartdan kənardır)
        if w >= 150 and h >= 100:
            corners = [
                ('Aşağı-Sağ', im.crop((int(w * 0.68), int(h * 0.80), w, h))),
                ('Aşağı-Sol', im.crop((0, int(h * 0.80), int(w * 0.32), h))),
                ('Yuxarı-Sağ', im.crop((int(w * 0.68), 0, w, int(h * 0.20)))),
                ('Aşağı-Mərkəz', im.crop((int(w * 0.34), int(h * 0.82), int(w * 0.66), h))),
            ]

            for corner_name, crop in corners:
                crop_rgb = crop.convert('RGB')
                cw, ch = crop_rgb.size
                if cw < 40 or ch < 20:
                    continue
                pix = crop_rgb.load()

                pts_orange = []
                pts_red = []
                pts_green = []
                pts_dark = []
                pts_white = []

                for y in range(ch):
                    for x in range(cw):
                        r, g, b = pix[x, y]
                        # Tap.az narıncı loqo nişanı (#ff5a00 / #f9593a)
                        if r > 200 and 40 <= g <= 135 and b <= 50 and (r - g) >= 80:
                            pts_orange.append((x, y, r, g, b))
                        # Lalafo qırmızı loqo nişanı (#e60050)
                        elif r > 190 and g <= 50 and 50 <= b <= 130:
                            pts_red.append((x, y, r, g, b))
                        # Lalafo yaşıl loqo nişanı (#00b86b)
                        elif g > 160 and r <= 60 and 60 <= b <= 140:
                            pts_green.append((x, y, r, g, b))
                        # Tünd filiqran paneli (kontrastlı yazı ilə)
                        elif r <= 45 and g <= 45 and b <= 45 and abs(r - g) < 15 and abs(g - b) < 15:
                            pts_dark.append((x, y, r, g, b))
                        # Ağ filiqran paneli (tünd yazı ilə)
                        elif r >= 235 and g >= 235 and b >= 235 and abs(r - g) < 15 and abs(g - b) < 15:
                            pts_white.append((x, y, r, g, b))

                badges = [
                    ('tap.az narıncı loqo nişanı', pts_orange, None),
                    ('lalafo qırmızı loqo nişanı', pts_red, None),
                    ('lalafo yaşıl loqo nişanı', pts_green, None),
                    ('tünd filiqran paneli', pts_dark, 'dark'),
                    ('ağ filiqran paneli', pts_white, 'white'),
                ]

                for name, pts, b_type in badges:
                    if len(pts) < 180:
                        continue
                    xs = [p[0] for p in pts]
                    ys = [p[1] for p in pts]
                    x_min, x_max = min(xs), max(xs)
                    y_min, y_max = min(ys), max(ys)
                    bw = x_max - x_min + 1
                    bh = y_max - y_min + 1
                    aspect = bw / max(bh, 1)
                    fill = len(pts) / (bw * bh)

                    # Tünd və ya ağ panellər bütün küncü bürüməməlidir (təbii kölgə olmamalıdır)
                    if b_type:
                        if bw > int(cw * 0.80) or bh > int(ch * 0.65):
                            continue

                    # Nişan qutusu parametrləri (üfüqi düzbucaqlı, sıx rəng doluluğu)
                    if 45 <= bw <= int(cw * 0.85) and 14 <= bh <= int(ch * 0.65) and 1.4 <= aspect <= 7.0 and fill >= 0.45:
                        r_vals = [p[2] for p in pts]
                        g_vals = [p[3] for p in pts]
                        b_vals = [p[4] for p in pts]
                        r_mean = sum(r_vals) / len(pts)
                        g_mean = sum(g_vals) / len(pts)
                        b_mean = sum(b_vals) / len(pts)
                        std_avg = (
                            math.sqrt(sum((v - r_mean) ** 2 for v in r_vals) / len(pts)) +
                            math.sqrt(sum((v - g_mean) ** 2 for v in g_vals) / len(pts)) +
                            math.sqrt(sum((v - b_mean) ** 2 for v in b_vals) / len(pts))
                        ) / 3.0

                        # Sintetik düz rəng tonu (loqo/badge standartı)
                        if std_avg < 14:
                            if b_type == 'dark':
                                bright_count = 0
                                for sy in range(y_min, y_max + 1):
                                    for sx in range(x_min, x_max + 1):
                                        sr, sg, sb = pix[sx, sy]
                                        if sr > 165 and sg > 165 and sb > 165:
                                            bright_count += 1
                                if bright_count < 25:
                                    continue
                            elif b_type == 'white':
                                dark_count = 0
                                for sy in range(y_min, y_max + 1):
                                    for sx in range(x_min, x_max + 1):
                                        sr, sg, sb = pix[sx, sy]
                                        if sr < 85 and sg < 85 and sb < 85:
                                            dark_count += 1
                                if dark_count < 25:
                                    continue
                            return True, f"Şəkildə {name} ({corner_name} hissəsində) aşkar edildi"

    except Exception:
        # Fayl oxuma xətası baş verərsə digər validasiyalara mane olmamaq üçün susuruq
        pass
    finally:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)

    return False, ''
