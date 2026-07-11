# Faded Balancer DCTL v1.7.0 Feature Audit

Audit date: 2026-07-11

This audit compares every shipped DCTL feature with the behavior implemented in `FadedBalancerDCTL.dctl`. “Pass” means the implementation supports the revised claim below; it does not mean the control can recover image information that was never captured.

## Verdict by feature

| Feature | Verdict | Honest capability and limit |
| :--- | :--- | :--- |
| Progressive Two-Point Recovery | Pass with limits | Applies a progressive dark offset and black-anchored endpoint gain to one channel. Auto conservatively selects one clear sample outlier. It is sample-assisted, not frame analysis, and cannot restore a flat or clipped record. |
| Recovery Strength / Max Gain | Pass | Strength is a linear blend on the target channel. Max Gain caps expansion while retaining the corrected black anchor; a capped result intentionally misses the requested white endpoint. |
| Presets | Pass with limits | Ten fixed embedded recipes run in the documented order. They do not inspect the frame or move sliders. Eight can request Blue Darken with Green unless Preset Tonal Only is enabled. |
| Global and per-channel Offset | Pass | Adds a constant to the whole RGB signal or selected channel. |
| Global and per-channel Lift | Pass after relabel | This legacy control is additive and mathematically identical to Offset. It is retained for saved-grade compatibility and is no longer claimed to isolate shadows. |
| Global and per-channel Gamma | Pass after correction | Uses signed power, keeps negative input sign, is neutral at `1.0`, and fails safely to the input if a finite calculation would overflow. |
| Global and per-channel Gain | Pass after relabel | Multiplies the whole RGB signal or selected channel. It is no longer claimed to isolate highlights. |
| Fade Correction | Pass after correction | Applies a deterministic Rec.709-luma S-curve within normalized `0..1` plus a progressive chroma increase. It does not analyze damage. The bounded curve no longer folds below-black or super-white luma. |
| Preserve Luminance | Pass within stated scope | Restores Rec.709-weighted luma across the visible per-channel stage only. It is a code-value proxy, not color-space-aware physical luminance, and downstream stages can change it. |
| Additive Channel Matrix | Pass after correction | Adds scaled donor-channel structure through broad tonal weights. Mixing Shadows, Mixing Highlights, and Donor Luminance now affect it. This is an approximation, not reconstruction of missing color. |
| Darken / Lighten | Pass | Selects the lower or higher target/donor value and blends through the tonal weight. If both are enabled for one target, Darken is evaluated first and Lighten second. |
| Mixing Shadows / Highlights | Pass with stated limits | Implements broad overlapping weights, `(1-L²)` and `L²`, from bounded Rec.709-weighted luma. These are not exclusive shadow/highlight keys. |
| Donor Luminance | Pass after clarification | Scales donor code values before matrix and min/max mixing. Despite the retained legacy label, it is not perceptual luminance matching or automatic exposure normalization. |
| Replace | Pass after correction | Copies whole channels. Multiple replacements now read one shared snapshot, so swaps and rotations are simultaneous rather than order-dependent. |
| Removal | Pass | Sets the selected channel, or all channels, to zero for diagnosis. |
| Channel Preview | Pass | Shows the selected processed channel as grayscale after Replace and Removal. |
| Diagnostic Log Preview | Pass after replacement | Compresses positive values with `x / (1 + x)` for inspection and maps non-positive values to zero. It is not Cineon, reversible encoding, color management, or a delivery transform. |
| Default full-float identity | Pass after correction | With Preset None, Recovery Off, neutral controls, and Diagnostic Log Preview off, finite negative, zero, normalized, and super-white RGB pass through unchanged. There is no unconditional final clamp. |

## Defects corrected during the audit

- Neutral legacy Gamma math previously forced negative and zero values to a small positive value.
- Fade Correction previously applied a normalized smoothstep polynomial to unbounded luma and could invert super-whites.
- Matrix mixing ignored its advertised tonal weights and donor scale.
- Multiple Replace controls cascaded in declaration order.
- The Cineon-labelled output was a custom clipped inspection curve, not a Cineon transform.
- Presets could silently override a visible Blue Darken selection.
- The old preset validator crashed because the external JSON file had become a deprecation pointer.
- The release scripts contained CRLF line endings, stale version defaults, wildcard asset selection, and a workflow that could expose a partial release.
- The macOS package builder could serialize a provenance xattr as an AppleDouble `._FadedBalancerDCTL.dctl` payload entry.

## Compatibility decisions

- Existing parameter identifiers and enum values are retained for saved Resolve grades.
- Lift and Gain math is unchanged; only the visible Shadows/Highlights terminology was corrected.
- Preset Tonal Only is an unchecked opt-out. A live saved-node upgrade showed that Resolve initializes a newly introduced checkbox to zero, so unchecked preserves the historical preset mixing request.
- Matrix mask/donor integration, simultaneous Replace, signed Gamma, safe Fade Correction, and Diagnostic Log Preview intentionally correct prior behavior.

## Validation evidence

- `python3 tools/test_range_recovery.py`: 18/18 passed.
- `python3 tools/test_dctl_pipeline.py`: 11/11 passed, including randomized finite-output cases.
- `python3 tools/validate_presets.py presets/presets.json`: ten selectors and ten embedded blocks, zero errors and zero warnings.
- The exact source and validation set also passed natively on Ubuntu 24.04 with Python 3.12.3 and NumPy 2.2.6: Recovery 18/18, complete pipeline 11/11, and preset validation with zero errors or warnings. This is headless validation of the numerical mirrors and source contracts, not Resolve execution.
- DaVinci Resolve Studio 20.3.3 on macOS/Metal compiled the final source on actual faded footage. Auto Recovery retained the existing dark and bright samples, the corrected labels and compatibility opt-out appeared, and no DCTL error was reported.
- DaVinci Resolve Studio 20.3.2.9 on Windows 11 Pro for Workstations compiled the same source on an NVIDIA GeForce RTX 3090 with driver 610.62. Resolve's log recorded automatic compute selection defaulting to CUDA and `Selected compute API: CUDA`; no DCTL build error appeared.
- On that Windows/CUDA host, Auto Recovery rendered the synthetic red-compacted fixture pixel-for-pixel identical to its clean 8-bit reference: maximum and mean error were both zero across 6,220,800 RGB channel values. Resetting Step 2 left the Step 1 black-point correction active, and restoring Step 2 changed only red from the dark-only render.
- Windows 16-bit TIFF renders of actual faded footage confirmed the same concatenation. The bright step changed 1,062,377 red values relative to the dark-only stage while changing zero green or blue values. Effect-off versus effect-on green and blue differed only by a one-code render-rounding decrement in fewer than 0.2% of their values.
- A final Windows/CUDA release-gate smoke used 16-bit PNG renders. Neutral defaults and effect bypass produced byte-identical files. With Red from G at `0.5`, the additive matrix changed red and left green/blue unchanged; setting both tonal weights to zero returned an exact identity, while Donor Luminance `0.1` versus `3.0` produced different red-only magnitudes. Red Darken with Green passed the same weight-disable and donor-magnitude checks for the min/max path.
- The release source, both locally installed macOS DCTL paths, and the Windows Resolve LUT copy matched SHA-256 `d5a0c2e2adedd5318fc4beb0b4d6330e7b57d9aafbadc52ce2da824f4ea70390` at validation time.
- The macOS 1.7.0 package was built locally, contained exactly one DCTL payload with the same hash, and contained no AppleDouble payload entry.

The hash is evidence for this audited working tree, not a permanent public release checksum. Recompute it after any source change.

## Remaining release gates and product limits

- The Windows Resolve/CUDA runtime gate is closed for the tested RTX 3090 configuration. AMD/OpenCL and Linux-in-Resolve remain untested and must not be inferred from that pass.
- The available Linux validation host is Ubuntu 24.04 with an RTX A4000 and NVIDIA driver 580.159.03. Its headless numerical validation passed, but DaVinci Resolve is not installed there. Installing and configuring Resolve was outside this audit, so no Linux DCTL compilation or GPU-render claim is made.
- Inno Setup is not installed on the tested Windows host. The tag workflow performs the Windows installer build, but that installer build has not been reproduced locally there.
- The Windows installer is unsigned. The macOS package is unsigned and not notarized; the install guide documents the resulting operating-system warnings.
- Winget can lag behind the GitHub release and must be updated after the raw 1.7.0 installer is public.
- No Transform DCTL can perform reliable cached full-frame histogram analysis inside this per-pixel implementation. A future OFX can add frame analysis, temporal stability, neutral-region proposals, and shot-level state; the DCTL remains deliberately operator-assisted.
- The DCTL performs no color-space conversion. Recovery samples and all creative controls operate on the RGB code values entering the node.

No tag, GitHub release, push, or Winget update is part of this audit document.
