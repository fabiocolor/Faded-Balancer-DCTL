# Project Requirements Document (PRD) — FadedBalancerOFX.dctl

Purpose
-------
Provide a compact, deterministic DCTL (Resolve 19.1+) to help colorists and archivists rebalance faded film scans (common magenta/blue channel shifts) using per-channel corrective controls. The plugin must be safe for archival workflows (no destructive remapping) and easy to inspect in Resolve.

Scope & Non-Goals
------------------
- Scope: a single Transform DCTL (no external tools) implementing global and per-channel adjustments, fade correction, min/max mixing, channel replace/removal, and optional per-channel Cineon output for inspection.
- Non-goals: no AI inference, no LUT baking as a required workflow, and no color-gamut remapping or creative grading by default.

Target users
------------
- Film restoration technicians, colorists in Resolve, archivists, and researchers needing repeatable experiments.

High-level goals
----------------
- Deterministic, GPU-friendly pixel transform (single-pass per pixel).
- Clear, minimal UI surface (sliders, combos, checkboxes) matching `DEFINE_UI_PARAMS` usage.
- Preserve ability to inspect intermediate states (no hidden final clamp by default).

Functional requirements (short)
------------------------------
- FR001 Global controls: Offset, Shadows, Midtones (gamma), Highlights.
- FR002 Fade correction: single scalar mix to nudge contrast/saturation for faded scans.
- FR003 Per-channel controls: Offset, Shadows, Midtones, Highlights for R/G/B.
- FR004 Preserve Luminance: optional toggle that rescales RGB to keep Rec.709 Y after per-channel stage.
- FR005 Mix: per-channel Darken/Lighten implemented as pure `_fminf` / `_fmaxf` operations.
- FR006 Replace: copy a channel from another (runs after Mix, before Removal).
- FR007 Removal: zero selected channels (runs last and overrides previous ops).
- FR008 Output: `outputToCineon` toggles per-channel linear→Cineon mapping for inspection.

Non-functional requirements
---------------------------
- Performance: single-pass, no dynamic loops with variable bounds; use Resolve intrinsics only.
- Portability: compatible with Resolve's GPU backends (CUDA/OpenCL/Metal) per vendor docs.
- Usability: UI labels and optional `DEFINE_UI_TOOLTIP` help explain controls.
- Maintainability: code organized by pipeline stage and documented in `docs/CODING_GUIDE.md`.

Edge cases & invariants
------------------------
- Pipeline order is authoritative and must not change; see `docs/SPECIFICATION.md#authoritative-pipeline` for the canonical order and invariants.
- Preserve Luminance affects only the Per-channel stage and rescales using Rec.709 coefficients.
- Midtones are gamma parameters; clamp/use safe pow (e.g., `safe_pow` with base >= 1e-9f). Keep midtones within ~[0.1f..3.0f].
- No final global clamp: outputs may leave [0..1] unless `outputToCineon` is enabled.
- Presets (if present) are pre-transform suggestions applied to local copies and must not overwrite UI variables directly.

Success criteria
----------------
- Default UI yields identity transform by default.
- Plugin corrects typical faded-magenta/blue scans with small UI adjustments.
- Tests in `docs/TESTS.md` pass for identity, preserve-luma, mix/replace, removal, and Cineon output behaviors.

Deliverables
------------
- `FadedBalancerOFX.dctl` (single source file)
- Docs: `docs/SPECIFICATION.md`, `docs/API.md`, `docs/EDGECASES.md`, `docs/TESTS.md`, `docs/CODING_GUIDE.md`.

References
----------
- `docs/vendor/bmd-dctl/README.md` (vendor DCTL rules and UI types).
- `FadedBalancerOFX.dctl` (implementation — single source of truth).
- `docs/CODING_GUIDE.md`, `docs/API.md`, `docs/EDGECASES.md` (project docs).

Change control
--------------
- Any change that alters pipeline order, public UI names/ranges, or core behaviors must be accompanied by updates to `docs/SPECIFICATION.md`, `docs/API.md`, `docs/TESTS.md`, and `docs/EDGECASES.md`, and requires owner approval before merging.

Notes
-----
- Keep the PRD concise — detailed developer guidance belongs in `docs/CODING_GUIDE.md` and examples in `docs/TESTS.md`.