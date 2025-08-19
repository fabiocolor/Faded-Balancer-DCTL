#!/usr/bin/env python3
"""Simple preset validator for FadedBalancerOFX presets.

Checks that numeric preset values lie within the UI parameter ranges defined in
`FadedBalancerOFX.dctl` and flags "very extreme" values (configurable).

Usage:
    python3 tools/validate_presets.py presets/presets_auto.json

This script is intentionally read-only and does not modify any files.
"""
import json
import sys
from pathlib import Path

# UI ranges mirrored from DCTL DEFINE_UI_PARAMS
RANGES = {
    'offset': (-0.5, 0.5),
    'shadows': (-0.5, 0.5),
    'midtones': (0.1, 3.0),
    'highlights': (0.1, 3.0),
}

# Extra "extreme" thresholds to surface as warnings (non-blocking)
EXTREME = {
    'midtones_high': 2.5,    # midtones above this are strong
    'highlights_high': 2.0,  # highlights above this are strong
}

def check_preset(preset, index):
    name = preset.get('name', f'Preset_{index:02d}')
    warnings = []
    errors = []

    # Helper to check a channel group
    def check_channel(prefix, channel_name):
        off = preset.get(f'{prefix}Offset', None)
        sh = preset.get(f'{prefix}Shadows', None)
        mi = preset.get(f'{prefix}Midtones', None)
        hi = preset.get(f'{prefix}Highlights', None)
        if off is not None:
            lo, hi_r = RANGES['offset']
            if not (lo <= off <= hi_r):
                errors.append(f"{channel_name} offset {off} out of range [{lo},{hi_r}]")
        if sh is not None:
            lo, hi_r = RANGES['shadows']
            if not (lo <= sh <= hi_r):
                errors.append(f"{channel_name} shadows {sh} out of range [{lo},{hi_r}]")
        if mi is not None:
            lo, hi_r = RANGES['midtones']
            if not (lo <= mi <= hi_r):
                errors.append(f"{channel_name} midtones {mi} out of range [{lo},{hi_r}]")
            elif mi >= EXTREME['midtones_high']:
                warnings.append(f"{channel_name} midtones {mi} is high (>= {EXTREME['midtones_high']})")
        if hi is not None:
            lo, hi_r = RANGES['highlights']
            if not (lo <= hi <= hi_r):
                errors.append(f"{channel_name} highlights {hi} out of range [{lo},{hi_r}]")
            elif hi >= EXTREME['highlights_high']:
                warnings.append(f"{channel_name} highlights {hi} is strong (>= {EXTREME['highlights_high']})")

    check_channel('red', 'Red')
    check_channel('green', 'Green')
    check_channel('blue', 'Blue')

    # Additional checks: fadeCorrection and boolean flags
    fc = preset.get('fadeCorrection', None)
    if fc is not None and not (0.0 <= fc <= 1.0):
        errors.append(f"fadeCorrection {fc} out of [0,1]")

    return name, errors, warnings


def main(argv):
    if len(argv) < 2:
        print('Usage: validate_presets.py <presets.json>')
        return 2
    p = Path(argv[1])
    if not p.exists():
        print(f'File not found: {p}')
        return 2
    data = json.loads(p.read_text())
    total_errors = 0
    total_warnings = 0
    print(f'Validating presets in {p}...')
    for i, preset in enumerate(data):
        name, errors, warnings = check_preset(preset, i)
        if errors or warnings:
            print(f'\n[{i}] {name}')
        for e in errors:
            print(f'  ERROR: {e}')
        for w in warnings:
            print(f'  WARNING: {w}')
        total_errors += len(errors)
        total_warnings += len(warnings)

    print('\nSummary:')
    print(f'  presets scanned: {len(data)}')
    print(f'  total errors: {total_errors}')
    print(f'  total warnings: {total_warnings}')
    if total_errors > 0:
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
