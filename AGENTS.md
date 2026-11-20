# Faded Balancer DCTL

Environment context: read `00_INDEX/CORE_ENVIRONMENT_GUIDE.md` in the Obsidian vault (local path in ~/OBSIDIAN_AGENT_START.md).

A single-file DCTL for rebalancing faded film scans. There is no build: the host loads `FadedBalancerDCTL.dctl` directly. This repo needs no GPU jobs; if it ever does, use CWC as described in `CWC.md`.

## Layout
- `FadedBalancerDCTL.dctl`: all logic, UI parameters and the embedded presets (authoritative).
- `presets/presets.json`: deprecation pointer only. Do not reintroduce generated preset JSON.
- `docs/`: user docs. `internal/`: maintainer spec (including code style), helpers and vendor headers; never link it publicly. `tools/`: checks and release scripts.

## Rules
- Pipeline order is fixed: presets → global → fade correction → per-channel → optional preserve luminance → mixing → replace → removal → optional log preview.
- Follow the code style in the maintainer spec.
- No final hard clamp; preserve below-black and super-white values.
- Keep parameter identifiers and enum values stable so saved grades still load. Keep labels and defaults in sync with README and docs.

## Checks
- Run the pipeline and range-recovery tests in `tools/` and, when presets change, the preset validator.
- Manual host check: default settings are identity on a neutral patch; per-channel moves show the expected parade response. The reference test footage is named in `docs/`.
- Commits use the existing conventional style. Add before/after frames under `assets/` for behaviour changes.
