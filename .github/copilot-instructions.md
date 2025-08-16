## Purpose
Give an AI coding agent the concise, repo-specific knowledge needed to edit, test, and extend FadedBalancerOFX.dctl quickly.

## Quick facts
- Single-file DCTL plugin: `FadedBalancerOFX.dctl` (entry: __DEVICE__ float3 transform(...)).
- Primary docs: `docs/SPECIFICATION.md`, `docs/API.md`, `docs/CODING_GUIDE.md`, `docs/TESTS.md`, `docs/EDGECASES.md`, and `README.md`.
- No build system: plugin runs inside DaVinci Resolve. Install by copying `FadedBalancerOFX.dctl` to Resolve LUT/DCTL folder (see README.md Install section).

## Authoritative pipeline (must preserve order)
1. Global controls (Offset, Shadows, Midtones, Highlights)
2. Fade Correction
3. Per-channel controls (R/G/B) — then optional Preserve Luminance (rescales using Rec.709 Y)
4. Mixing (Darken = min, Lighten = max)
5. Replace (copy channel sources)
6. Removal (zero channels)
7. Output (optional Linear 126; Cineon log)

When changing behavior, keep this order. Many tests and docs assume it (see `docs/SPECIFICATION.md`).

## Key conventions & gotchas
- UI controls must be declared with `DEFINE_UI_PARAMS` and match variable names used in `transform()`.
- Float literals must use the `f` suffix (e.g., `0.5f`).
- Use only Resolve/DCTL intrinsics: `_powf`, `_fminf`, `_fmaxf`, `_clampf`, etc.
- Midtones = gamma exponent: implement as `out = _powf(in, 1.0f / midtones)` (see SPECIFICATION). Keep midtones constrained to ~[0.1..3.0].
- Mixing must be pure `_fminf`/`_fmaxf` (no blend weights).
- Preserve Luminance: compute Rec.709 Y before per-channel changes and rescale RGB afterwards to keep Y constant.
- Replace runs after Mix and before Removal; Removal overrides earlier ops.
- No global final clamp by design; plugin intentionally allows values outside [0..1].

## Where to look for examples
- UI patterns and param declarations: search for `DEFINE_UI_PARAMS` inside `FadedBalancerOFX.dctl` and referenced examples in docs (GainDCTLPlugin, ColorPicker notes in `docs/SPECIFICATION.md`).
- Behavioral rules, acceptance tests and edge cases: `docs/TESTS.md` and `docs/EDGECASES.md`.
- Installation and usage: `README.md` (installation path and usage notes).

## Dev / test / debug workflow (manual)
- Edit `FadedBalancerOFX.dctl` in-place. There is no build step.
- To test: copy the `.dctl` into your DaVinci Resolve LUT/DCTL folder (see README), restart Resolve, add a DCTL node and inspect scopes (RGB parade, histogram).
- Acceptance checks are manual visual + numeric scope checks described in `docs/TESTS.md` (Identity, Preserve Luma, Copy/Remove, Darken/Lighten, Cineon output).

## Changes an AI should avoid or treat carefully
- Do not add runtime state, loops with variable bounds, or non-supported intrinsics.
- Avoid adding a final clamp unless the change is explicitly required and documented (spec intentionally avoids final clamp).
- Keep UI count and types within Resolve limits (<= 64 controls per UI type).

## Useful code snippets (copy-paste safe)
- Entry signature: `__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)`
- Midtones example: `float3 out = _powf(inColor, 1.0f / globalMidtones);` (remember `f` suffixes)
- Mix example: `r = _fminf(r, g); // darken` and `r = _fmaxf(r, b); // lighten`

## Files to update when you change behavior
- `FadedBalancerOFX.dctl` (implementation)
- `docs/SPECIFICATION.md` (pipeline and must-haves)
- `docs/API.md` (param names and ranges)
- `docs/CODING_GUIDE.md` (coding patterns and intrinsics)
- `docs/TESTS.md` and `docs/EDGECASES.md` (update acceptance tests and rules)

## When to ask for clarification
- If a change affects the pipeline order, tooltips/UI labels, or numeric ranges, ask the repo owner (author is listed in README) before committing.

## Safe edits an AI can make (low-risk)
These are small, reversible changes an AI may make without prior approval. Prefer edits from the top of the list.

- Fix obvious typos and grammar in docs (`docs/*.md`) and UI tooltips.
- Normalize float literals to include `f` suffix where missing in code comments or examples (do not change runtime constants without owner approval).
- Add or expand inline examples in `FadedBalancerOFX.dctl` (small comment blocks showing `DEFINE_UI_PARAMS` usage or `_powf` example).
- Add `// TODO` anchors or short clarifying comments in `FadedBalancerOFX.dctl` and docs to note areas needing review or tests.
- Update or add short acceptance test steps in `docs/TESTS.md` (visual/numeric steps), keeping original test semantics.
- Reformat markdown for readability (wrap long lines, fix heading levels) but don't alter meaning.

Avoid these without explicit owner approval:

- Changing the processing pipeline order (Global → Fade → Per-channel → Mix → Replace → Removal → Output).
- Renaming UI controls or changing numeric ranges in `DEFINE_UI_PARAMS`.
- Adding runtime state, loops with variable bounds, or unsupported intrinsics.
- Introducing a final global clamp or changing the no-clamp design choice.

---
If you'd like, I can tighten any section or add a short checklist of quick edits an AI can make safely (small refactors, add assertions to docs, or add more code examples).
