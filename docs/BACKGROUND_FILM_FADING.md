# Film Fading — Practical Background



## What Fading Is (brief)
- Chromogenic color prints use three dye layers: cyan, magenta, yellow.
- Dyes decay with time, temperature/humidity, and light exposure.
- Typical result: reduced density/contrast and a magenta cast from cyan loss.

## How It Appears on Scans
- Image looks pink/magenta; midtones feel flat; blacks are lifted.
- Parade scope: red and blue sit higher than green (R,B > G) through midtones.
- Neutrals drift off gray; highlights can clip early if corrected aggressively.

## Quick Assessment
1) Identify a neutral patch (border, gray step, leader if present).
2) Check the parade: are R and B tracking above G across midtones?
3) Toggle Cineon view (log inspection) to assess highlight/shadow headroom.
4) Note where the shift is strongest (shadows, mids, or highlights).

## Correction Strategy (using FadedBalancerOFX)
1) Preset: select the closest preset as a starting point.
2) Fade Correction: apply a modest lift (typical 0.10–0.30) for midtone contrast/saturation.
3) Global: make small offset/highlight adjustments to place the image.
4) Per‑channel: target midtones first (especially red) to neutralize magenta; add green where needed rather than only cutting red.
5) Preserve Luminance: enable if color moves shift overall brightness.
6) Mixing (Darken/Lighten): calm spikes by taking min/max of channels; use sparingly.
7) Replace/Removal: borrow/mute channels only for checks or severe dye loss.
8) Cineon view: use for inspection; disable before final evaluation/exports.

## Guardrails
- Work in float; avoid clipping while shaping midtones.
- Prefer midtone moves over large shadow lifts (noise amplification).
- Keep changes modest and monotonic; avoid strong toggling between boosts/cuts.
- State and convert input color space explicitly (scene‑linear vs log) when needed.

## Common Cases (quick cues)
- Classic magenta shift: slightly reduce red midtones or boost green midtones; add a small blue darken in noisy/cool shadows.
- Dull highlights: small global highlight scale and/or use presets 3 or 10.
- Severe red dominance: use a “Red Compress” preset (1 or 8), then refine midtones; watch clipping.

## Validation Checklist
- Neutrals align (parade channels converge; a*≈0, b*≈0 if measured).
- Restored density range without clipping (check with Cineon view).
- Memory colors (skin, foliage) look plausible after small tweaks.

## Further Reading (optional)
- Digital “unfading” of chromogenic film: Trumpy et al., 2023 (open access summary).
- EBU Tech 3285: preservation of colour photographic images (overview guidance).
- Image Permanence Institute (IPI): practical storage and stability resources.
