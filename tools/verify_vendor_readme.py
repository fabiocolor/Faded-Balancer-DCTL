#!/usr/bin/env python3
"""Verify vendor README authority and compare other docs against it.

This script enforces that `internal/docs/vendor/bmd-dctl/README.md` is the
authoritative vendor source. It searches other docs for key DCTL phrases and
prints a report. It's intended for local dev use or CI integration.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / 'internal' / 'docs' / 'vendor' / 'bmd-dctl' / 'README.md'
DOCS = list((ROOT / 'docs').rglob('*.md')) + list((ROOT / 'internal').rglob('*.md'))

def load(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except Exception:
        return ''

def main():
    if not VENDOR.exists():
        print(f'ERROR: vendor README not found at {VENDOR}')
        return 2

    vendor_txt = load(VENDOR)
    keywords = [
        'transform(', 'DEFINE_UI_PARAMS', 'DEFINE_LUT', 'TRANSITION_PROGRESS',
        '__RESOLVE_VER_MAJOR__', 'RAND(', 'TIMELINE_FRAME_INDEX'
    ]

    print('Vendor README:', VENDOR)
    issues = []
    for doc in DOCS:
        if doc.samefile(VENDOR):
            continue
        text = load(doc)
        matches = [k for k in keywords if k in text and k not in vendor_txt]
        if matches:
            issues.append((doc, matches))

    if not issues:
        print('OK: No docs reference DCTL keywords that are missing from vendor README.')
        return 0

    print('\nFound docs that reference DCTL keywords absent from vendor README:')
    for doc, matches in issues:
        print(f'- {doc}: {matches}')

    print('\nRecommendation: Ensure vendor README is authoritative, or add missing vendor content.')
    return 1

if __name__ == "__main__":
    sys.exit(main())
