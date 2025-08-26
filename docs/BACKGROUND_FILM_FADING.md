# Fading Behavior of Chromogenic Film Stocks

Technical summary for restoration work: observed fading patterns in chromogenic prints and practical, invertible correction approaches suitable for DCTL workflows. For vendor archival policy or storage guidance, consult vendor publications and conservation specialists.

## Background: Chromogenic Dyes and Fade Phenomena

Chromogenic color films form images from three dye layers—cyan, magenta, yellow—via color‑coupler chemistry. Dyes decay over time due to:

- Dark fading: slow dye decay while stored (accelerated by heat and humidity).
- Light fading: dye bleaching from projection or exposure to light.

Effects: reduced density/contrast and cross‑channel imbalance. Neutrals often shift magenta due to cyan loss, yielding red/blue dominance in scans.

Historic note: some Eastman prints (1950s–1970s) show early cyan loss and magenta casts; pre‑1983 Fuji prints can shift purple. Low‑fade stocks (Kodak LPP ~1982; Fuji ~1983) improved stability.

Storage matters: higher temperature/humidity accelerates fading (orders of magnitude faster around 30 °C vs 7 °C). Real collections often degrade faster than lab predictions.

## Colorimetric Characteristics of Fading

Unequal dye loss skews the neutral axis. In CIELAB, neutrals shift toward +a* (magenta) and sometimes −b* (blue). Densities drop; blacks lift; contrast flattens. Operationally R,B > G; aim to restore R ≈ G ≈ B on neutrals by reducing R/B or boosting G, per‑tone.

## Quantitative & Kinetic Models

First‑order kinetics approximate dye fading: D_i(t)=D_i(0)·e^{−k_i t}, with dye‑specific rates k_i. Older stocks show larger cyan loss over decades (e.g., ΔD≈0.4), suggesting correction factors F_i≈1/remaining_fraction_i. Practically: unequal k_i → R,G,B divergence → neutral drift.

## Practical, Invertible Correction Strategies (GPU-friendly)

Invertible methods suitable for GPU/DCTL, ordered from physical to empirical:

1) Log-Density Domain Correction

   - Convert linearized RGB (assumed transmittance-like) to optical density: D = -log10(max(RGB, eps)).
   - Scale dye-associated densities by user/estimated factors: D' = F * D (per channel or via dye matrix).
   - Convert back: RGB' = 10^{-D'}.

   Pros: physically interpretable/invertible. Cons: requires dye↔RGB mapping; log/pow cost.

2) Power-Law (Per-Channel Gamma / Exponent)

   - Simpler approximation: apply per-channel exponentials: R' = pow(R, F_C), etc., where F_C is chosen to rebalance neutrals.
   - Fast and easily implemented in shader code using safe pow guards.

   Pros: cheap, effective. Cons: less exact; add midtone weighting to avoid extreme tone issues.

3) 3×3 Color Matrix / Per-Channel Gain-Bias

   - Apply a diagonal or full 3×3 matrix to rebalance channels (fast: three dot-products per pixel).
   - Can be combined with offsets (lift) to adjust shadows.

   Pros: very fast, invertible. Cons: uniform across tones; weaker when fade is strongly tonal.

4) Channel Tone Curves / 1D LUTs

   - Per-channel 1D LUTs or polynomial curves calibrated to reference patches (e.g., China Girl) allow non-linear, monotonic correction tuned per-tone.
   - Useful to restore contrast alongside color.

   Pros: precise, invertible if monotonic. Cons: needs anchors; careful smoothing required.

Practical recipe: estimate coarse F_i from neutral patches; apply per‑channel gain+exponent; refine with gentle per‑channel curves/LUT for residuals.

## Examples & Practical Notes

Example: cyan 30% remaining (F_C≈3.33), magenta 80% (F_M≈1.25), yellow 50% (F_Y≈2.0). In log density: scale by F_i; in power‑law: use similar exponents with midtone weighting.

## Guardrails & Validation

- State input color space (scene‑linear vs log) and convert explicitly.
- Guard pow/log (e.g., eps≈1e‑6) to avoid NaNs; cap extreme boosts.
- Prefer midtone weighting; keep blocks bypassable and mixable (0–100%).
- Validate neutrals (a*≈0, b*≈0), density range (no clipping), and approximate round‑trip invertibility.

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
