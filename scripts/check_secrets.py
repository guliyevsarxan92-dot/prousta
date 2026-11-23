#!/usr/bin/env python3
"""
Repository secret and sensitive-file guard.
Usage:
  python3 scripts/check_secrets.py           # Scan all git-tracked files
  python3 scripts/check_secrets.py --staged  # Scan staged files (pre-commit hook)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FORBIDDEN_PATH_PATTERNS = [
    re.compile(r'(^|/)\.env(\..+)?$'),
    re.compile(r'\.(jks|keystore|pem|key|p12|pfx|sqlite3|db|sql|dump)$', re.IGNORECASE),
    re.compile(r'(^|/)key\.properties$'),
    re.compile(r'(^|/)google-services\.json$'),
    re.compile(r'(^|/)GoogleService-Info\.plist$'),
    re.compile(r'service-account.*\.json$', re.IGNORECASE),
    re.compile(r'backup.*\.json$', re.IGNORECASE),
]

ALLOWED_PATH_EXCEPTIONS = {'.env.example'}

BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico', '.svg',
    '.ttf', '.otf', '.woff', '.woff2', '.pdf', '.mp4', '.webm',
}

SECRET_RULES = [
    (
        'Database/Service URL with embedded credentials',
        re.compile(
            r'(?:postgres|postgresql|mysql|mariadb|redis|rediss|mongodb(?:\+srv)?|cloudinary|amqp|amqps)'
            r'://[^/\s"\'<>:]+:[^/\s"\'<>@]+@[^/\s"\'<>]+'
        ),
    ),
    (
        'Private cryptographic key block',
        re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----'),
    ),
    (
        'Google OAuth client secret',
        re.compile(r'GOCSPX-[A-Za-z0-9_-]{20,}'),
    ),
    (
        'Google API key',
        re.compile(r'AIza[0-9A-Za-z_-]{35}'),
    ),
    (
        'GitHub personal access token',
        re.compile(r'(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{40,})'),
    ),
    (
        'Hardcoded Django SECRET_KEY',
        re.compile(r'^\s*SECRET_KEY\s*=\s*["\'][^"\']{8,}["\']', re.MULTILINE),
    ),
]

SAFE_PLACEHOLDERS = (
    'API_KEY:API_SECRET@CLOUD_NAME',
    'USER:PASSWORD@HOST',
    'isolated-tests-only-',
)


def _git_files(staged: bool) -> list[str]:
    cmd = (
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR']
        if staged
        else ['git', 'ls-files']
    )
    out = subprocess.check_output(cmd, cwd=ROOT, text=True)
    return [line.strip() for line in out.splitlines() if line.strip()]


def _read_content(rel_path: str, staged: bool) -> str | None:
    if Path(rel_path).suffix.lower() in BINARY_EXTENSIONS:
        return None
    try:
        if staged:
            raw = subprocess.check_output(['git', 'show', f':{rel_path}'], cwd=ROOT)
            return raw.decode('utf-8', errors='ignore')
        full = ROOT / rel_path
        if not full.is_file():
            return None
        return full.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None


def main() -> int:
    staged = '--staged' in sys.argv[1:]
    files = _git_files(staged=staged)
    findings: list[str] = []

    for rel_path in files:
        base_name = os.path.basename(rel_path)
        if rel_path not in ALLOWED_PATH_EXCEPTIONS and base_name not in ALLOWED_PATH_EXCEPTIONS:
            for pat in FORBIDDEN_PATH_PATTERNS:
                if pat.search(rel_path):
                    findings.append(f'[FORBIDDEN FILE] {rel_path}')
                    break

        if rel_path == 'scripts/check_secrets.py':
            continue

        content = _read_content(rel_path, staged=staged)
        if not content:
            continue

        is_test_file = (
            rel_path in ('prousta/test_settings.py', 'prousta/build_settings.py')
            or '/test' in f'/{rel_path}'
            or base_name.startswith('test_')
        )

        for label, regex in SECRET_RULES:
            for match in regex.finditer(content):
                snippet = match.group(0)
                if any(ph in snippet for ph in SAFE_PLACEHOLDERS):
                    continue
                if is_test_file and label == 'Hardcoded Django SECRET_KEY':
                    continue
                line_no = content.count('\n', 0, match.start()) + 1
                redacted = snippet[:18] + '...' if len(snippet) > 21 else snippet
                findings.append(f'[SECRET] {rel_path}:{line_no} — {label} ({redacted})')

    if findings:
        sys.stderr.write('TƏHLÜKƏSİZLİK XƏTASI: Gizli məlumat və ya qadağan olunmuş fayl aşkarlandı:\n')
        for item in findings:
            sys.stderr.write(f'  - {item}\n')
        return 1

    print(f'Secret scan passed ({len(files)} files checked).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
