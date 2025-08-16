# Edge Cases & Rules

This file lists deterministic rules and edge-case behaviors contributors must preserve when editing `FadedBalancerOFX`.

Rules
- Pipeline is fixed: Global → Fade → Per-Channel (→ Preserve Luminance) → Mix → Replace → Removal → Output.
- Preserve Luminance only applies after per-channel adjustments; it does not affect Global or later stages.
- Midtones must be constrained to a safe range (~0.1f..3.0f) to avoid unstable `_powf` behavior.
- No final global clamp: outputs may lie outside [0.0f, 1.0f] by design; downstream grading is expected to handle ranges.
- If both Copy (Replace) and Remove are active for the same channel, Removal takes precedence.
- Replace should be implemented with a fixed order (e.g., R→G→B) to avoid recursive sourcing.
- Mixing uses pure `_fminf` / `_fmaxf` operations; no blending weights are permitted.
- UI constraints: keep controls ≤64 per UI type; respect ranges declared in `DEFINE_UI_PARAMS`.

Notes
- When changing behavior that affects any of the above rules (pipeline order, UI ranges, or intrinsics), update `docs/SPECIFICATION.md`, `docs/TESTS.md`, and `CONTRIBUTING.md`, and request owner approval for non-trivial changes.

