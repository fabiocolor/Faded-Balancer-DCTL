<!--
 PR template for FadedBalancerOFX
 Keeps PR descriptions consistent and includes the quick pre-review checklist from the coding guide.
-->

<!-- Title: start with `fix:` `feat:` `docs:` `chore:` etc. -->
<!-- Write a short descriptive title above when creating the PR -->

## Summary
Describe the change in 1-2 sentences.

## Acceptance tests performed
- List manual verification steps and scope screenshots (parade/histogram) if visual.

## Pre-review mini-check (required)
Quick items to verify before requesting review. See the full reviewer checklist in the private maintainer archive `internal/ARCHIVE_DOCS.md`.

- [ ] `DEFINE_UI_PARAMS` names are used in `transform()` (or copied to `_l` locals).
- [ ] Pipeline order preserved (see `docs/SPECIFICATION.md#authoritative-pipeline`) and Preserve Luminance behavior verified if used.
- [ ] Float literals use `f` suffix; midtones are in safe range (~0.1f..3.0f).
- [ ] Mix uses `_fminf`/`_fmaxf` and no final global clamp was added.

## Files changed
- List key files changed and why.

## Notes for reviewer
- Any special notes (preset expectations, backward compatibility, owner approval required?).
