# Gemini Project Instructions — Faded-Balancer-OFX

This document provides context for the Gemini AI assistant to understand and interact with the FadedBalancerOFX project.

## Project Overview

FadedBalancerOFX is a DaVinci Resolve DCTL OFX plugin for balancing RGB channels and correcting faded film scans. It provides accessible and flexible tools for channel adjustment, mixing, and restoration preparation.

The core of the project is the DCTL code, written in a C-like language that DaVinci Resolve understands. There are two versions of the DCTL file:

*   `FadedBalancerOFX.dctl`: The main plugin file in English.
*   `FadedBalancerOFX_es.dctl`: A Spanish-localized version of the plugin.

## Key Conventions

*   **Pipeline Order:** The image processing pipeline is fixed and should not be reordered: presets → global → fadeCorrection → per‑channel (+ optional luminance preserve) → mixing (darken/lighten) → replace → removal → optional Cineon output.
*   **Presets:** Presets are non-destructive and only modify local `p_` variables. They must never overwrite UI parameter values directly.
*   **Float Literals:** Float literals must always be `f` suffixed for GPU safety (e.g., `1.0f`).
*   **Vendor Intrinsics:** Use vendor intrinsics only: `_powf`, `_fminf`, `_fmaxf`, `_clampf`, `_mix`, `_log10f`.
*   **UI Parameters:** UI parameters are defined with `DEFINE_UI_PARAMS` in grouped sections. Preserve ordering to avoid shifting existing Resolve layouts.

## Building and Running

This is not a typical code project with a build system. The `.dctl` files are the final product and can be used directly in DaVinci Resolve.

**Installation:**

1.  Download `FadedBalancerOFX.dctl`.
2.  Place it in your DaVinci Resolve LUT folder:
    *   **macOS:** `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
    *   **Windows:** `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
3.  Restart DaVinci Resolve.
4.  In the Color page, add a "DCTL" effect to a node and select `FadedBalancerOFX` from the dropdown menu.

**Validation:**

The project includes Python scripts for validation. To run them, you will need Python 3 installed.

*   `python3 tools/validate_presets.py presets/presets.json`: Validates the presets in `presets/presets.json`.
*   `python3 tools/verify_vendor_readme.py`: Verifies that the internal vendor documentation is the single source of truth for DCTL keywords.

## Authoritative Vendor Reference

All code or doc modifications MUST be compared against the official Blackmagic Design DCTL reference stored under `internal/docs/vendor/bmd-dctl/` before implementation.
