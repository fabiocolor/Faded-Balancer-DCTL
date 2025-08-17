# Contributing to FadedBalancerOFX

This project is a single-file DaVinci Resolve DCTL plugin (`FadedBalancerOFX.dctl`). The goal of this CONTRIBUTING guide is to give humans the same practical rules and low-risk workflows that agents follow in `.github/copilot-instructions.md`.

Please keep changes small, reversible, and well-documented.

## Quick checklist for PRs
- Update code in `FadedBalancerOFX.dctl` only when necessary.
- Update docs in `docs/` that correspond to behavioral changes (`SPECIFICATION.md`, `API.md`). For developer guidance and tests consult `internal/ARCHIVE_DOCS.md` (private).
- Include before/after screenshots and RGB parade scope images for any visual change.
- Describe behavioral changes and list acceptance tests you used from the internal archive (`internal/ARCHIVE_DOCS.md`).

## DCTL-specific rules (must follow)
- Keep the canonical pipeline order (see `docs/SPECIFICATION.md#authoritative-pipeline`) when making changes.
- UI controls must be declared with `DEFINE_UI_PARAMS` and their variable names must match the names used in `transform()`.
- Float literals must end with `f` (e.g., `0.5f`).
- Use only Resolve/DCTL intrinsics (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, etc.).
- Implement Midtones as a gamma exponent: `out = _powf(in, 1.0f / midtones)` and keep midtones in ~[0.1..3.0].
- Mixing must be pure `_fminf`/`_fmaxf` (no blend weights).
- Preserve Luminance: compute Rec.709 Y before per-channel changes and rescale RGB afterwards to keep Y constant.
- No global final clamp: the plugin intentionally allows values outside [0..1].
- UI limits: Resolve enforces ≤64 controls per UI type — keep counts within that limit.

## Safe, low-risk edits
You may do these without prior approval:
- Fix typos and grammar in `docs/*.md` and UI tooltips.
- Add or expand inline examples or `// TODO` anchors in `FadedBalancerOFX.dctl` and docs.
- Normalize example float literals in docs/comments to include `f` (don’t change runtime constants without approval).
- Add or update short acceptance steps in `docs/TESTS.md` (keep test semantics the same).
- Reformat markdown for readability (don’t change meaning).

## Changes that require owner approval
Obtain approval from the repo owner (see `README.md` for contact) before making:
- Any change to the pipeline order.
- Renaming UI controls or changing numeric ranges in `DEFINE_UI_PARAMS`.
- Adding runtime state, loops with variable bounds, or new intrinsics not known to Resolve.
- Introducing a final global clamp or changing the design that permits out-of-range outputs.

## How to test locally (manual)
1. Copy `FadedBalancerOFX.dctl` to your DaVinci Resolve LUT/DCTL folder:
   - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
   - Windows: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
2. Restart DaVinci Resolve.
3. In the Color page, add a DCTL effect to a node and select `FadedBalancerOFX`.
4. Use scopes (RGB parade, histogram, waveform) to verify behavior described in the private maintainer archive (`internal/ARCHIVE_DOCS.md`).

NOTE: testing is visual/manual; there is no automated build step.

## PR checklist
- [ ] Title: short, descriptive (e.g., `fix: preserve-luma edge-case`)
- [ ] Body: summary, files changed, acceptance tests performed (link to `docs/TESTS.md` steps), and before/after images.
- [ ] Docs updated if public behavior changed.
- [ ] Tag owner / request review from the author listed in `README.md` for any behavioral changes.

## Upstream spec sync
The official Blackmagic Design DCTL reference is vendored at `docs/vendor/bmd-dctl/README.md` (do not modify it directly). When:
- Adding or using a new intrinsic
- Changing the transform function signature (float3 vs float4)
- Adjusting UI macro usage (`DEFINE_UI_PARAMS`, potential tooltips)

You must confirm the construct exists in the upstream spec. If Blackmagic updates their spec and it affects this plugin, add a short note in your PR body: `Upstream spec sync: <YYYY-MM-DD>` describing what changed. Optionally summarize new relevant intrinsics in `docs/vendor/bmd-dctl/summary.md` (create/update) so future contributors have a quick diff without scanning the large upstream file.

If an intrinsic you want is missing upstream, open an issue instead of guessing — unsupported intrinsics can silently fail inside Resolve.

## Contact / owner
- See `README.md` for author/contact information (owner: Fabio Bedoya). Ask the owner for approval when doing anything marked "requires owner approval." 

Thank you for contributing — small, well-documented changes make the project easier to maintain.
