## Purpose
Give an AI coding agent short, actionable knowledge to edit, test, and extend `FadedBalancerOFX.dctl` safely and quickly.

## Quick facts
- Single-file DCTL plugin: `FadedBalancerOFX.dctl` (entry: `__DEVICE__ float3|float4 transform(...)`).
- Primary docs: `docs/SPECIFICATION.md`, `docs/API.md`, `docs/CODING_GUIDE.md`, `docs/TESTS.md`, `docs/EDGECASES.md`, and `README.md`.
- No build system: plugin runs inside DaVinci Resolve. Install by copying `FadedBalancerOFX.dctl` to Resolve LUT/DCTL folder (see README.md Install section).

## Resolve LUT / DCTL common install locations (check your Resolve version)
- macOS (user): `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/DCTL`
- macOS (system): `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/DCTL`
- Windows (user): `C:\Users\<you>\AppData\Roaming\Blackmagic Design\DaVinci Resolve\LUT\DCTL` (or `%APPDATA%\Blackmagic Design\DaVinci Resolve\LUT\DCTL`)
- Windows (system): `C:\ProgramData\Blackmagic Design\DaVinci Resolve\LUT\DCTL`
- Linux (typical installs): `/opt/resolve/share/resolve/LUT/DCTL` or check `~/.local/share/DaVinciResolve` depending on distro and install method

Always verify the exact folder for your Resolve version — or consult `docs/vendor/bmd-dctl/README.md` (authoritative vendor guidance bundled in this repo).

## What matters (high level)
- The repo is a single-pass per-pixel transformer (shader-like). The DCTL is source-of-truth: behavior, UI params and helpers live in `FadedBalancerOFX.dctl`.
- Pipeline order is canonical; see `docs/SPECIFICATION.md#authoritative-pipeline` for the full, authoritative order and rules.
- ALWAYS open and reference `docs/vendor/bmd-dctl/README.md` when correcting code or generating new DCTL: it documents supported intrinsics, entry signatures, and UI control forms that must be followed.

## Developer workflow (concrete steps)
1. Edit `FadedBalancerOFX.dctl` in-place. Keep `DEFINE_UI_PARAMS(...)` names and the variables in `transform()` consistent.
2. Quick local checks: ensure float literals have `f` suffix (e.g., `0.001f`) and only vendor intrinsics are used (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_log10f`, etc.).
3. Manual test: copy `.dctl` to Resolve LUT/DCTL folder, restart Resolve, add a DCTL node, and use RGB parade/histogram and numeric readouts as described in `docs/TESTS.md`.

## Project-specific conventions & examples
- UI params: declared with `DEFINE_UI_PARAMS` and must match names referenced inside `transform()`.
  Example: if `DEFINE_UI_PARAMS` declares `float globalMidtones`, `transform()` must use `globalMidtones`.
- Midtones = gamma exponent. Use: `out = _powf(in, 1.0f / midtones);` (keep midtones roughly in [0.1..3.0]).
- Preserve luminance: compute Rec.709 Y (0.2126 * R + 0.7152 * G + 0.0722 * B) before per-channel edits and rescale RGB afterward to restore Y.
- Mixing: implement Darken/Lighten purely with `_fminf` / `_fmaxf` (no weighted blends).
- No final clamp: the plugin intentionally allows values outside [0..1]; do not add a global `_clampf` unless requested.
- Helpers in the code: `safe_pow(...)` (domain guard), `applyLGGO(...)` (Offset→Shadows→Midtones→Highlights), `linearToCineon(...)` — refer to their implementations for correct usage.

## Changes an AI should avoid without approval
- Do not change pipeline order, rename UI controls, or change numeric ranges in `DEFINE_UI_PARAMS` without owner approval.
- Do not introduce runtime state, variable-bound loops, or non-vendor intrinsics.
- Do not add a final global clamp (design choice).

## Files to update together when changing behavior
- `FadedBalancerOFX.dctl`
- `docs/SPECIFICATION.md`, `docs/API.md`, `docs/CODING_GUIDE.md`, `docs/TESTS.md`, `docs/EDGECASES.md`

## Good small edits an AI may make
- Fix grammar/typos in docs, normalize `f` suffixes in comments, add short inline examples or `// TODO` anchors, and improve doc clarity.

## When to ask for clarification
- Ask the repo owner (see `README.md`) before modifying pipeline order, UI labels/ranges, or output mapping behavior (Cineon/Linear handling).
