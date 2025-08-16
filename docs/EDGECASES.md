# Edge Cases & Rules

This file lists deterministic rules and edge-case behaviors contributors must preserve when editing `FadedBalancerOFX`.

Rules
- Pipeline is canonical; see `docs/SPECIFICATION.md#authoritative-pipeline` for the authoritative pipeline and invariants.
- Preserve Luminance only applies after per-channel adjustments; it does not affect Global or later stages.
- Midtones must be constrained to a safe range (~0.1f..3.0f) to avoid unstable `_powf` behavior.
- No final global clamp: outputs may lie outside [0.0f, 1.0f] by design; downstream grading is expected to handle ranges.
- If both Copy (Replace) and Remove are active for the same channel, Removal takes precedence.
- Replace should be implemented with a fixed order (e.g., R→G→B) to avoid recursive sourcing.
- Mixing uses pure `_fminf` / `_fmaxf` operations; no blending weights are permitted.
- UI constraints: keep controls ≤64 per UI type; respect ranges declared in `DEFINE_UI_PARAMS`.
 - Presets are pre-transform suggestions applied to local copies only and must not overwrite the UI-controlled variables; presets run before Global adjustments and may suggest local changes to mixing/copy/output flags.
 - Alpha handling: when using a float4 `transform()` signature the plugin preserves the input alpha (`p_A`) and does not modify it; avoid changing alpha behavior without explicit tests.
 - safe_pow / domain guards: pow usage must clamp small/negative bases (the DCTL uses `safe_pow(x,y)` which clamps base to ~1e-9f) to avoid NaNs/infinite results on GPU.
 - Cineon encoding: `linearToCineon` clamps negative inputs to 0.0 and maps results into [0.0,1.0] for inspection. This per-channel encoding is not a global final clamp and is only applied when `outputToCineon` is enabled.
 - Slider precision: the DCTL defines float slider steps (e.g., `0.001f`); UIs should support the documented precision in `docs/API.md`.


Notes
- When changing behavior that affects any of the above rules (pipeline order, UI ranges, intrinsics, preset semantics, or alpha handling), update `docs/SPECIFICATION.md`, `docs/TESTS.md`, and `docs/CONTRIBUTING_QUICK.md` (and root `CONTRIBUTING.md` if applicable), and request owner approval for non-trivial changes.

