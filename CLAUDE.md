# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DaVinci Resolve DCTL (DaVinci CTL) plugin for balancing RGB channels and correcting faded film scans. The project is primarily composed of:

- **FadedBalancerDCTL.dctl**: The main DCTL plugin file
- **Presets system**: JSON-based configuration for common corrections
- **Documentation**: Comprehensive guides for users and developers

## Architecture

The DCTL implements a fixed processing pipeline with these stages:
1. Preset Application (internal variables only)
2. Global Adjust (Offset/Shadows/Midtones/Highlights)
3. Fade Correction (contrast + saturation recovery)
4. Per-Channel Adjust (RGB individual controls)
5. Optional Preserve Luminance (post per-channel only)
6. Channel Mixer (RGB matrix for highlight boost)
7. Mixing (Darken/Lighten via min/max)
8. Replace (explicit channel copy)
9. Removal (zero out channels)
10. Optional Output to Cineon Log

## Key Files

- `FadedBalancerDCTL.dctl`: Main plugin with UI parameters and transform function
- `presets/presets.json`: Preset definitions (referenced by tools)
- `tools/validate_presets.py`: Validates preset JSON against DCTL parameters
- `tools/create_releases.sh`: Packages release artifacts

## Development Guidelines

### DCTL Coding Standards
- Use `float` operations; avoid type narrowing
- Minimize dynamic branching in pixel loops
- Keep parameter names/defaults synced with presets.json
- Handle NaNs and out-of-gamut values defensively
- Precompute constants to avoid repeated expensive math

### Parameter Synchronization
When modifying parameters in FadedBalancerDCTL.dctl:
- Ensure names match presets/presets.json schema
- Update README.md if UI changes
- Run tools/validate_presets.py to verify consistency
- Update docs/presets_companion.md if preset behavior changes

### Testing
- Use tools/validate_presets.py to validate preset configurations
- Test with sample footage: Archive.org Film BAR 70 Trailers Reel
- Verify installation path: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`

### Release Process
Use tools/create_releases.sh to package the DCTL file for distribution.