## Copilot / AI agent instructions — FadedBalancerOFX (concise)

Purpose: give an AI coding agent the exact, repo-specific facts needed to edit,
test, and extend `FadedBalancerOFX.dctl` safely and quickly.

Quick facts
- Single-file DCTL: `FadedBalancerOFX.dctl` is the canonical source (entry: `__DEVICE__ float3|float4 transform(...)`).
- No build: test by copying the `.dctl` into Resolve's LUT/DCTL folder and restarting Resolve.
- Private maintainer guidance and helper snippets are available to the project owner/maintainers. Contact the repository owner for access to maintainer documentation.

Must-follow rules (do not change without owner approval)
- Pipeline ordering is authoritative; do not change it without owner approval.
- Do not rename or change `DEFINE_UI_PARAMS` identifiers or numeric ranges.
- No runtime state, no variable-bound loops, and only vendor intrinsics (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_log10f`, etc.).
- Always validate any DCTL code or suggestions against the official vendor documentation in `docs/vendor/bmd-dctl/README.md` before applying — that file is authoritative for supported intrinsics, transform signatures, and UI control definitions.

Concrete, copy-paste patterns
- Entry signature example: `__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)`.
- Midtones (gamma): `out = _powf(in, 1.0f / midtones);` (midtones ~ [0.1f..3.0f]).
- Preserve luminance: compute Rec.709 Y `0.2126f*R + 0.7152f*G + 0.0722f*B` before per-channel edits and rescale after when enabled.
- Mixing: use `_fminf` / `_fmaxf` for Darken/Lighten (no weighted blends).
- Use `safe_pow(base, exp)` (clamp base ≥ 1e-9f). Contact the repository owner for maintainer helper snippets.

Files to update together when changing runtime behavior
- `FadedBalancerOFX.dctl` (and notify the repository owner for maintainer notes).

Testing & validation (manual)
- Install test: copy `.dctl` to Resolve LUT/DCTL folder and restart.
- Quick smoke: default UI on a neutral patch should be identity (per-channel diff ≲ 1e-4).
- Functional checks: small midtone edits must move RGB parade predictably; `preserveLuminance` keeps Y within ~1e-3.

PR hints
- Commit messages: concise, e.g. `chore(docs): ...`, `fix(dctl): ...`, `feat(dctl): ...`.
- For behavioral changes include before/after images and scope screenshots in PR descriptions.

If unsure
- If an edit touches pipeline order, UI names/ranges, or output mapping, ask the repo owner (see `README.md`) before committing.

End of concise instructions.
