# Quick PR Review Checklist

Use this short checklist when reviewing PRs. Copy-paste into the PR body or use as reviewer guidance.

- [ ] Title is descriptive and follows `fix:`, `feat:`, `docs:`, etc.
- [ ] Summary describes behavior changes and lists acceptance tests performed (link to `docs/TESTS.md`).
- [ ] Before/after images attached (PNG) and RGB parade or histogram screenshots included for visual changes.

DCTL-specific checks
- [ ] Pipeline order preserved (see `docs/SPECIFICATION.md#authoritative-pipeline`).
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

## Lint checklist (one-page)
Use this quick checklist before opening a PR. It replaces a previous repo script and focuses on human-reviewable items.

- UI names
	- [ ] Every `DEFINE_UI_PARAMS` first argument (identifier) is used inside `transform()` or copied into a local `_l` variable.
	- [ ] UI names in `DEFINE_UI_PARAMS` exactly match the symbols referenced in code (case-sensitive).

- Pipeline & behavior
	 - [ ] Pipeline order preserved (see `docs/SPECIFICATION.md#authoritative-pipeline`).
	- [ ] Preserve Luminance (when enabled) rescales using Rec.709 Y (verify Y_pre ≈ Y_post within epsilon).

- Numeric & intrinsics
	- [ ] Float literals use `f` suffix (e.g., `0.5f`).
	- [ ] Midtones used as gamma: implemented as `_powf(in, 1.0f / midtones)` and kept in safe range (~0.1f..3.0f).
	- [ ] Mix uses `_fminf`/`_fmaxf` only (no weighted blends).
	- [ ] Only supported Resolve intrinsics used (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_mix`, `_log10f`, etc.).

- UI & UX
	- [ ] Slider ranges in `DEFINE_UI_PARAMS` match documented ranges in `docs/API.md` (offsets ±0.5f, midtones ~[0.1f..3.0f], fadeCorrection [0..1]).
	- [ ] UI control counts remain within Resolve limits (≤64 per UI type).

- Docs & tests
	- [ ] Update `docs/SPECIFICATION.md`, `docs/API.md`, `docs/TESTS.md`, and `docs/EDGECASES.md` when changing runtime behavior.
	- [ ] Add acceptance test steps to `docs/TESTS.md` describing how the change was validated in Resolve.

If you want automation later, we can add a tiny grep-based pre-commit check that enforces the UI-name rule; for now prefer this human checklist to keep reviews fast.
