# AGENTS.md

This file provides repository-specific guidance for agents working on Faded
Balancer DCTL.

## Project overview

Faded Balancer is a DaVinci Resolve DCTL for inspecting and balancing RGB
channels in faded film scans. The main implementation is
`FadedBalancerDCTL.dctl`; installers, documentation, and read-only validation
tools live alongside it.

## Authoritative processing pipeline

The per-pixel pipeline order is fixed:

1. Assisted two-point faded-channel recovery
2. Embedded preset pass
3. Global Offset/Lift/Gamma/Gain pass
4. Fade Correction
5. Per-channel Offset/Lift/Gamma/Gain pass
6. Optional Rec.709-weighted luma preservation for the per-channel pass
7. Tonally weighted channel matrix
8. Tonally weighted min/max channel mixing
9. Simultaneous channel replacement from one source snapshot
10. Channel removal
11. Channel isolation preview
12. Optional diagnostic log preview

Do not reorder these stages without treating the change as grade-affecting.
Recovery picker samples are in the DCTL input domain and must remain before all
other grading operations.

## Source of truth

- `FadedBalancerDCTL.dctl` is the implementation and preset authority. Its ten
  `PRESET_EASTMAN1` through `PRESET_EASTMAN10` blocks are the actual presets.
- `presets/presets.json` is only a deprecation pointer for historical links. Do
  not restore an external preset list or synchronize values into it.
- `docs/presets_companion.md` documents the visible preset labels and behavior.
- `tools/validate_presets.py` derives UI ranges and preset values directly from
  the DCTL, then checks selector/block count, numeric validity, enum mappings,
  and documentation coverage.

## DCTL coding standards

- Use float operations and avoid accidental type narrowing.
- Keep branching in the per-pixel transform modest and predictable.
- Preserve existing parameter identifiers when changing a visible label so old
  grades remain compatible.
- Treat below-black, super-white, negative, NaN, and infinite values
  defensively; a neutral control path should not destroy valid extended-range
  values.
- Precompute constants or shared masks rather than repeating expensive math.
- Distinguish diagnostic previews from delivery transforms in naming and docs.

## Parameter and preset changes

When changing UI parameters or embedded presets:

1. Keep the UI declaration, tooltip, local transform copy, and actual use in
   sync.
2. Update `docs/presets_companion.md` when a selector label or recipe changes.
3. Update `README.md`, `docs/FAQ.md`, or other feature documentation when the
   user-visible behavior changes.
4. Run the source and numerical checks below.

Do not edit `presets/presets.json` to represent preset values.

## Testing

Run from the repository root:

```bash
python3 tools/validate_presets.py
python3 tools/test_range_recovery.py
python3 tools/test_dctl_pipeline.py
```

The Python suites mirror DCTL math but do not replace a Resolve host test. For
release candidates, install the exact packaged DCTL at:

`/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`

Then refresh Resolve's DCTL list and smoke-test neutral defaults, both recovery
pickers, affected controls, and representative faded footage.

## Release preparation

- Use `tools/build_mac_installer.sh` and the Windows installer workflow to build
  artifacts from the same final DCTL source.
- Use `tools/create_releases.sh` only when the requested action includes
  publishing a GitHub release.
- Verify packaged payload hashes and version strings before tagging.
- Installer signing/notarization and Resolve host coverage are separate release
  gates; do not claim them from source-level tests alone.
