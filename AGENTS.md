# Repository Guidelines

## Project Structure & Modules
- `FadedBalancerOFX.dctl`: Core DCTL plugin (authoritative logic and presets).
- `docs/`: User docs (FAQ, presets companion, background notes).
- `assets/{before,after}/`: Example frames for README/PRs.
- `presets/presets.json`: Placeholder only; presets now live in `FadedBalancerOFX.dctl`.
- `tools/validate_presets.py`: Read‑only sanity checker for external preset JSON.
- `internal/`: Maintainer notes and vendor references. Do not link publicly.

## Build, Test, Dev Commands
- Install (Resolve): copy `FadedBalancerOFX.dctl` to your LUT folder
  - macOS: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
  - Windows: `C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT\\`
- Validate presets JSON (if editing external examples):
  - `python3 tools/validate_presets.py presets/presets.json`
- Local run: open Resolve, add DCTL effect, select `FadedBalancerOFX`.

## Coding Style & Naming
- Match current DCTL style: 4‑space indent, `//` comments, vendor intrinsics only (`_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_log10f`).
- Float literals must use `f` suffix (e.g., `0.1f`).
- Preserve the pipeline order exactly (preset → global → fade → per‑channel → preserve‑luma → mix → replace → removal → optional Cineon).
- UI params use concise identifiers (e.g., `globalMidtones`); internal locals use `_l` or `p_` prefixes when appropriate.
- No final hard clamp; output may exceed [0,1] by design.

## Testing Guidelines
- Manual in Resolve (baseline):
  - Identity: default UI on neutral patch → output ≈ input.
  - Simple correction: tweak `blueHighlights` and verify parade moves toward neutral.
  - Verify options: Preserve Luminance behavior; Cineon Log inspection mode.
- Visual docs: place frames in `assets/before/` and `assets/after/` and reference in PR.

## Commit & Pull Requests
- Commits: prefer conventional style seen in history (e.g., `feat:`, `fix:`, `docs:`, `chore:`; also `DCTL:` when touching shader logic). Imperative, concise subjects.
- PR checklist:
  - Describe behavior change and acceptance steps performed in Resolve.
  - Include before/after images and note any UI label/tooltip updates.
  - Confirm: pipeline order unchanged; vendor intrinsics; `f` suffixes; default identity holds; preset validator (if used) passes.
  - Link related issues and note any migration notes for users.

## Security & Notes
- Do not surface files under `internal/` in public docs.
- Keep `.env` and private data out of examples.
- Do not reintroduce auto‑generated preset JSON; authoritative presets live in `FadedBalancerOFX.dctl`.
