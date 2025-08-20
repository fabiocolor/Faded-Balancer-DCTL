# Copilot Project Instructions — Faded-Balancer-OFX

Purpose: Enable AI coding agents to safely extend / maintain the DCTL plugin without breaking the deterministic GPU pipeline or leaking maintainer‑only docs.

## Big Picture
- Single DCTL shader: `FadedBalancerOFX.dctl` (v1.x). Pipeline (do NOT reorder): presets → global → fadeCorrection → per‑channel (+ optional luminance preserve) → mixing (darken/lighten) → replace → removal → optional Cineon output.
- Presets are non‑destructive: they only modify local `p_` variables before the main user stages. They must never overwrite UI parameter values directly.
- Private maintainer docs live in `internal/`; do not surface their raw content in user‑facing changes. Public guidance stays in `README.md` + `docs/`.

## Key Conventions
- Float literals ALWAYS `f` suffixed (GPU safety). Use vendor intrinsics only: `_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_mix`, `_log10f`.
- Helper naming: `safe_pow`, `applyLGGO`, `applyFadeCorrection`, `linearToCineon`. Keep helpers pure, side‑effect free. Add new helpers above `transform()` and document briefly.
- UI params defined with `DEFINE_UI_PARAMS` in grouped sections (Global / Per‑channel / Mixing / Replace / Removal / Output). Preserve ordering to avoid shifting existing Resolve layouts.
- Combo boxes: enum value list and label list counts MUST match exactly. Follow existing enum naming pattern (e.g. `CR_FROM_GREEN`).
- New stage logic goes in its rightful numbered section comment; never insert between preset application and global stage unless architecture updated in SPEC.

## Adding / Modifying Features
- Bump version comment header (e.g. to v1.5.0) and copy previous file into `previous_versions/` before edits.
- When adding a preset: create new `PRESET_*` constant, extend combo list (IDs contiguous), add logic block that sets only local `p_` variables. Avoid altering defaults of existing presets.
- When adding a UI control: append to the appropriate section; update tooltips if user‑facing. Respect float step granularity (currently `0.001f`). Leave unused headroom for future controls.
- Preserve luminance logic: only rescales after per‑channel stage. If extending, keep pre/post luma capture pattern intact.
- Mixing (darken/lighten) ONLY uses min/max on local copies; do not introduce average or non‑deterministic ops without clear justification.

## Safety / Validation
- Quick self‑test: with all defaults (and no preset) output ≈ input (identity). Small tolerance differences only from float math.
- After preset changes: ensure selecting a preset then toggling back to "None" returns to original look (since UI values never changed).
- Avoid NaNs: clamp inputs in any new pow/log with same `safe_pow` pattern (epsilon `1e-9f`).

## Tooling & CI
- Python helper: `tools/verify_vendor_readme.py` (run locally: `python3 tools/verify_vendor_readme.py`) ensures vendor keyword coverage.
- GitHub Action `verify-vendor-readme.yml` fails PRs that modify `internal/docs/vendor/bmd-dctl/README.md` without label `vendor-docs-update`.
- If you touch that vendor README, add the label and reference the vendor release in the PR body.

## Authoritative Vendor Reference (MANDATORY BEFORE CHANGES)
- Before planning, advising on, or implementing any DCTL-related feature, you MUST first consult the authoritative Blackmagic Design DCTL reference stored under `internal/docs/vendor/bmd-dctl/`. This is the single source of truth for DCTL capabilities (e.g., file access, LUT handling, available functions). Do not rely on general knowledge; always verify against this local documentation.
- Do NOT quote or copy text from vendor docs into public files; only apply the required technical constraints (signatures, intrinsics, limits) inferred from them.
- When uncertain whether an intrinsic / macro / signature is vendor‑supported, STOP and annotate the PR with a short question instead of guessing.
- Record in the PR description: `Vendor check: OK (no new constructs)` or list each newly used intrinsic / macro verified (e.g. `_log10f` already present, etc.).
- If a vendor spec update is needed (new Resolve version), add the `vendor-docs-update` label when touching the vendor README and summarize the delta (e.g. "Added new intrinsic XYZ; bumping helpers").

## PR / Review Checklist (agent)
1. Version bumped & previous version archived.
2. Pipeline order unchanged (unless spec update explicitly required).
3. No leakage of `internal/` content into public docs.
4. New enums: counts & labels aligned; default values safe.
5. Identity & preset non‑destructive behavior verified mentally / via reasoning.
6. Vendor README untouched OR proper label added.

## Examples
- Correct gamma change: `col.x = safe_pow(col.x, 1.0f / midtones.x);` (never raw `_powf` on possibly ≤0 base).
- Preset tweak pattern: inside `if (presetMode == PRESET_EASTMAN11) { preset_applied = 1; p_globalOffset = ...; }`

## Out of Scope
- Do NOT introduce external dependencies or multi‑file refactors; project intentionally single‑file for DCTL portability.

Questions (agent): If ambiguity exists, prefer minimal, reversible changes and leave a concise comment for human review.
