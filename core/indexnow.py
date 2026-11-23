import os
import json
import logging
import threading
from urllib.parse import urljoin
from typing import Iterable, List
import requests
from django.conf import settings
from django.http import HttpResponse, Http404

logger = logging.getLogger(__name__)

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
DEFAULT_HOST = "prousta.az"


def get_indexnow_key() -> str:
    """IndexNow API açarını settings və ya mühit dəyişənindən götürür."""
    return getattr(settings, 'INDEXNOW_KEY', os.getenv('INDEXNOW_KEY', '')).strip()


def indexnow_key_view(request, key: str):
    """
    IndexNow açarının doğrulanması üçün HTTP endpoint:
    GET /<key>.txt -> cavab: <key>
    """
    configured_key = get_indexnow_key()
    if not configured_key or key != configured_key:
        raise Http404("Not Found")
    return HttpResponse(configured_key, content_type="text/plain; charset=utf-8")


def _send_payload(host: str, key: str, url_list: List[str]):
    key_location = f"https://{host}/{key}.txt"
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": url_list,
    }
    try:
        resp = requests.post(
            INDEXNOW_ENDPOINT,
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(payload),
            timeout=8,
        )
        if resp.status_code in (200, 202):
            logger.info("IndexNow submitted %d URLs successfully (status: %d)", len(url_list), resp.status_code)
        else:
            logger.warning("IndexNow submission returned status %d: %s", resp.status_code, resp.text[:200])
    except Exception as exc:
        logger.warning("IndexNow submission failed: %s", exc)


def submit_urls_now(urls: Iterable[str], async_mode: bool = True):
    """
    Verilmiş URL siyahısını (və ya tək URL-i) IndexNow endpointinə göndərir.
    async_mode=True olduqda arxa planda (thread-də) işləyir ki, sorğu ləngiməsin.
    """
    key = get_indexnow_key()
    if not key:
        return

    host = getattr(settings, 'CANONICAL_HOST', DEFAULT_HOST)
    base = f"https://{host}"

    clean_urls = []
    for u in urls:
        if not u:
            continue
        if u.startswith("http://") or u.startswith("https://"):
            clean_urls.append(u)
        else:
            clean_urls.append(urljoin(base, u))

    # Təkrarları silək
    clean_urls = list(dict.fromkeys(clean_urls))
    if not clean_urls:
        return

    if async_mode:
        t = threading.Thread(target=_send_payload, args=(host, key, clean_urls), daemon=True)
        t.start()
    else:
        _send_payload(host, key, clean_urls)
