<p align="center">
  <a href="../README.md">Home</a> •
  <a href="BACKGROUND_FILM_FADING.md">Background & Science</a> •
  <a href="presets_companion.md">Presets Companion</a> •
  <a href="FAQ.md">FAQ</a>
</p>

# Fading Behavior of Chromogenic Film Stocks (Kodak Eastman Color vs. Fuji Color)

This public background summary covers observed fading behaviors of chromogenic photographic prints and practical correction approaches used in digital restoration workflows. It is intended as a technical reference for users and contributors; for vendor-specific archival guidance consult vendor technical publications or archival conservation specialists.

## Background: Chromogenic Dyes and Fade Phenomena

Chromogenic color films create images using three organic dye layers—cyan, magenta, and yellow—produced by color coupler chemistry. Over time these dyes are susceptible to chemical breakdown. Fading can occur as:

- Dark fading: slow dye decay while stored (accelerated by heat and humidity).
- Light fading: dye bleaching from projection or exposure to light.

Visually, fading reduces contrast and image density (a washed-out look). Because the three dyes fade at different rates the color balance shifts: neutrals commonly drift toward pink/magenta in aged chromogenic prints. This magenta/pink cast typically indicates disproportionate cyan loss; remaining magenta and yellow layers dominate, producing a red/blue bias in the scanned image.

Historically, some Kodak Eastman prints from the 1950s–1970s are especially prone to early cyan loss and visible magenta casts within a decade under normal conditions. Early Fuji prints (pre-1983) fared somewhat better but could still exhibit purple-like shifts when faded. Both vendors introduced "low-fade" stocks in the early 1980s (Kodak LPP ~1982, Fuji improvements ~1983) that substantially improved cyan stability; post-1983 prints are far less likely to show severe dye-driven color shifts over decades.

Storage conditions dramatically influence fade rates: higher temperature and humidity accelerate fading (for example, fading at ~30 °C can be orders of magnitude faster than at ~7 °C). While manufacturer lab data can predict long lifetimes for low-fade stock under cold storage, archives commonly observe faster degradation due to variable real-world storage conditions.

## Colorimetric Characteristics of Fading

Unequal dye loss skews the neutral gray axis. In CIELAB space, faded neutrals from older Eastman prints typically shift toward positive a* (magenta) and sometimes slightly negative b* (blue bias). Densitometrically, the maximum optical density of each layer drops with time: blacks lift and overall contrast flattens.

Operationally, faded film often shows too much red and blue relative to green (R and B > G). Correction strategies therefore aim to restore R ≈ G ≈ B for neutral patches, typically by reducing R and B or boosting G (or a mixture), depending on tonal zone and the chosen method.

## Quantitative & Kinetic Models

First-order kinetics (exponential decay) is a useful starting model for dye fading:

   D_i(t) = D_i(0) * e^{-k_i t}

where D_i is optical density for dye i (C/M/Y) and k_i is a dye-specific fade rate constant (dependent on chemistry and storage). In practice, some stocks show a multi-phase decay (faster initial loss followed by a slower phase), which can be modeled with multi-exponential fits, but the single-exponential model provides a practical foundation.

Experimental datapoints from older stocks show substantial cyan decay over decades (e.g., ΔD ≈ 0.4 loss over 18 years for certain early 1970s Eastman prints at moderate storage temperatures), whereas magenta decay is often much smaller in the same timeframe. These differences translate to per-dye correction factors F_i ~= 1 / remaining_fraction_i (e.g., remaining cyan 30% → F_C ≈ 3.33).

Expressed in RGB/transmittance terms, fading may be approximated by per-channel changes over time (in practice it's simpler to work in optical density and convert back to RGB when needed). The primary takeaway: unequal k_i produce divergence of R, G, B, causing neutral drift.

## Practical, Invertible Correction Strategies (GPU-friendly)

The following methods are ordered from physically grounded to empirical; each is invertible and feasible in a shader with care.

1) Log-Density Domain Correction

   - Convert linearized RGB (assumed transmittance-like) to optical density: D = -log10(max(RGB, eps)).
   - Scale dye-associated densities by user/estimated factors: D' = F * D (per channel or via dye matrix).
   - Convert back: RGB' = 10^{-D'}.

   Pros: physically interpretable and invertible; cons: requires dye ↔ RGB mapping and more expensive math (log/pow) on GPU.

2) Power-Law (Per-Channel Gamma / Exponent)

   - Simpler approximation: apply per-channel exponentials: R' = pow(R, F_C), etc., where F_C is chosen to rebalance neutrals.
   - Fast and easily implemented in shader code using safe pow guards.

   Pros: cheap and effective for many cases; cons: less physically exact and may misbehave in extreme shadows/highlights without midtone weighting.

3) 3×3 Color Matrix / Per-Channel Gain-Bias

   - Apply a diagonal or full 3×3 matrix to rebalance channels (fast: three dot-products per pixel).
   - Can be combined with offsets (lift) to adjust shadows.

   Pros: extremely fast, invertible; cons: uniform across tonal range — may underperform when fade is strongly tonal.

4) Channel Tone Curves / 1D LUTs

   - Per-channel 1D LUTs or polynomial curves calibrated to reference patches (e.g., China Girl) allow non-linear, monotonic correction tuned per-tone.
   - Useful to restore contrast alongside color.

   Pros: precise tonal control and invertible if monotonic; cons: requires anchors (patches) to design LUTs and careful smoothing to avoid artifacts.

In practice, combined approaches are common: estimate coarse F_i from neutral patches (border, leader, or chart), apply per-channel gain+exponent in the shader, and refine with gentle per-channel curves or a LUT for residuals.

## Examples & Practical Notes

Example: Severe Eastman fade where cyan is 30% remaining (F_C ≈ 3.33), magenta 80% rem (F_M ≈ 1.25), yellow 50% rem (F_Y ≈ 2.0). In log-domain that suggests multiplying channel densities by those factors; in a power-law approximation use exponents near these values with midtone weighting to avoid shadow clipping.

Restoration case studies often derive F_i from reference neutral patches (black leader or gray steps) and then apply density-domain or exponent corrections. These workflows are consistent with archival practice and offer a good balance between speed and fidelity for DCTL use.

## Guardrails & UX Guidance

- Always document assumed input color space (scene-linear vs log). Convert explicitly when necessary.
- Use domain guards for pow/log to avoid NaNs (e.g., clamp to small eps like 1e-6).
- Cap extreme boosts and consider midtone weighting to avoid noise amplification in shadows.
- Keep all corrective blocks optionally bypassable and parameterized by mix strength (0–100%).

## Validation & Acceptance Cues

- Neutral re-alignment: neutral test patches should move toward a*=0, b*=0 (CIELAB) within a small tolerance after correction.
- Contrast: recovered density range should increase without causing clipping; compare histograms/scopes pre/post.
- Round-trip: when feasible, ensure inverse mapping approximately restores the input (useful for testing invertibility).

## References

Chatterjee, S., Trumpy, G., Lindblom, B., & Hardeberg, J. Y. (2023). Digital unfading of chromogenic film informed by its spectral densities. Journal of Imaging, 9(1), 20. https://doi.org/10.3390/jimaging9010020

European Broadcasting Union. (1990). EBU Technical Recommendation 3285: Preservation and reproduction of colour photographic images. Geneva, Switzerland: European Broadcasting Union. (Consult EBU archives for the official text.)

Eastman Kodak Company. (1982). Low-fade color print film (Eastman LPP) [Technical publication]. Rochester, NY: Eastman Kodak Company. (Vendor technical note — consult Kodak archival publications.)

Image Permanence Institute. (1993). IPI storage guide for acetate film. Rochester, NY: Image Permanence Institute, Rochester Institute of Technology. (See IPI publications: https://www.imagepermanenceinstitute.org/)

Trumpy, G., Lindblom, B., & Hardeberg, J. Y. (2022). Spectral analysis of faded chromogenic film dyes for archival restoration. In Proceedings of the IS&T Color and Imaging Conference (pp. 305–310). (IS&T proceedings — consult conference archives or IS&T digital library.)

Fuji Photo Film Co., Ltd. (1983). Introduction of improved low-fade Fujicolor print stock [Technical notes]. Tokyo, Japan: Fuji Photo Film Co., Ltd. (Vendor technical note — consult Fujifilm archival publications.)

---

### Supporting / Contextual References

Christie, R. M., & Mackay, H. (2008). The chemistry of photographic color image formation and dye stability. Coloration Technology, 124(4), 203–210. https://doi.org/10.1111/j.1478-4408.2008.00152.x

Wilhelm, H. (1993). The permanence and care of color photographs. Grinnell, IA: Preservation Publishing Company.