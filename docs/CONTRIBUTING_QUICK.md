# Quick PR Review Checklist

Use this short checklist when reviewing PRs. Copy-paste into the PR body or use as reviewer guidance.

- [ ] Title is descriptive and follows `fix:`, `feat:`, `docs:`, etc.
- [ ] Summary describes behavior changes and lists acceptance tests performed (link to `docs/TESTS.md`).
- [ ] Before/after images attached (PNG) and RGB parade or histogram screenshots included for visual changes.

DCTL-specific checks
- [ ] Pipeline order preserved: Global → Fade → Per-channel (→ Preserve Luma) → Mix (min/max) → Replace → Removal → Output
- [ ] UI params declared with `DEFINE_UI_PARAMS` and names match variables used in `transform()`
- [ ] Float literals in code/examples use `f` suffix where needed (e.g., `0.5f`)
- [ ] Only Resolve intrinsics used (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, etc.)
- [ ] Midtones implemented as gamma (`_powf(in, 1.0f / midtones)`) and within safe range (~0.1..3.0)
- [ ] Mix operations use pure `_fminf`/`_fmaxf` (no blending weights)
- [ ] Preserve Luminance behavior verified when enabled (Y_pre ≈ Y_post within small epsilon)
- [ ] No final global clamp added (allow out-of-range values by design)
- [ ] UI control counts remain within Resolve limits (≤64 per UI type)

Docs & tests
- [ ] Update corresponding docs in `docs/` when changing public behavior (`SPECIFICATION.md`, `API.md`, `CODING_GUIDE.md`, `TESTS.md`, `EDGECASES.md`)
- [ ] Add/adjust acceptance test steps in `docs/TESTS.md` and note which were run

Owner approval required for:
- Any change to pipeline order
- Renaming UI controls or changing numeric ranges in `DEFINE_UI_PARAMS`
- Introducing runtime state, loops with variable bounds, or non-supported intrinsics
- Adding a final global clamp or otherwise changing the no-clamp design

Notes
- Testing is manual — copy `FadedBalancerOFX.dctl` into Resolve LUT/DCTL folder and verify using scopes.
- If in doubt, tag the repo owner (see `README.md`) for a final decision.
