# Acceptance Tests — FadedBalancerOFX

## Quick verify (30s)
A short, practical checklist to validate the plugin quickly for non-technical users.

1. Install the DCTL: copy `FadedBalancerOFX.dctl` to your Resolve LUT/DCTL folder and restart Resolve.
2. Identity check: apply the plugin with default UI values to a neutral patch. Output should match input within floating tolerance (per-channel difference ≲ 1e-4).
3. Simple correction example: on a faded/magenta test image, nudge `blueHighlights` by +0.10 and observe the RGB parade moving toward neutral; if `preserveLuminance` is used, verify Y_post ≈ Y_pre (±1e-3).

Purpose
- Provide a short, reproducible set of manual acceptance tests that verify the plugin's public behavior and invariants. Tests are manual visual + numeric checks using Resolve scopes (RGB parade, histogram, and numeric readouts).

How to run
- Copy `FadedBalancerOFX.dctl` into your Resolve LUT/DCTL folder, restart Resolve, add a DCTL node, and use scopes to inspect results. For each test below, record the numeric scope values where applicable.

Tolerances
- Equality/identity checks use a floating tolerance: ±1e-4 for per-channel comparisons, ±1e-3 for luminance comparisons.

Tests

1) Identity (smoke)
- Setup: all UI controls at default values (preserveLuminance=0, outputToCineon=0).
- Expect: output ≈ input (per-channel difference ≤ 1e-4 across a neutral patch).

2) Preserve Luminance
- Setup: apply a global fade (optional) then record Y_pre = 0.2126*R + 0.7152*G + 0.0722*B.
- Action: apply per-channel edits (e.g., redHighlights=1.2f) with `preserveLuminance=1`.
- Expect: Y_post within ±1e-3 of Y_pre; chroma (R,G,B) may change but luminance preserved.

3) Darken / Lighten composites
- Setup: use a test image with differing channels.
- Action: set redDarkenWith = With Green → observe R_out = min(R_in, G_in). Then test redLightenWith = With Blue → R_out = max(R_in, B_in).
- Expect: per-pixel numeric checks match `_fminf`/`_fmaxf` results.

4) Replace then Removal ordering
- Action: set copyBlueSource = With Red, then set channelRemovalMode = Remove Blue.
- Expect: operation order yields final blue channel = 0 (Replace runs before Removal).

5) Cineon output
- Action: enable `outputToCineon` and inspect per-channel curves and numeric values.
- Expect: values are mapped to a Cineon-style log range; negative inputs clamp to 0.0 before mapping. The mapping is monotonic per-channel.

6) Preset pre-transform behavior
- Setup: choose a non-default `presetMode` and observe behavior.
- Expect: presets apply as pre-transform suggestions to local copies (they do not overwrite UI-controlled variables) and may adjust suggested fade/mix/output flags.

7) Edge behavior: no final clamp
- Setup: apply strong highlights/offsets producing values >1.0.
- Expect: plugin does not apply a final clamp; values may exceed 1.0 in the internal pipeline unless `outputToCineon` is used.

Notes
- If any test fails due to a behavioral change, update `docs/SPECIFICATION.md`, `docs/API.md`, `docs/EDGECASES.md`, and `docs/TESTS.md` together and request owner approval for non-trivial changes.
- These tests are acceptance-level manual checks; automated unit tests are not applicable inside Resolve and require external tooling or mock harnesses.

