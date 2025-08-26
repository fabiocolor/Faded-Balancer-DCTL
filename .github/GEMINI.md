# Gemini Code Assistant Context

## Project Overview

This project is a DaVinci Resolve DCTL (DaVinci CTL) script called `FadedBalancerOFX`. Its purpose is to provide a tool for colorists and restoration artists to correct and rebalance color in scanned film footage that has suffered from dye fading, which typically manifests as a magenta color cast.

The core of the project is the `FadedBalancerOFX.dctl` file, which is a C-like script that defines the image processing pipeline and the user interface within DaVinci Resolve.

The project also includes extensive documentation, presets, and a validation tool.

### Key Technologies

*   **DaVinci CTL:** A C-like language for creating custom color transformations in DaVinci Resolve.
*   **Python:** Used for the preset validation script.
*   **JSON:** Previously used for presets, but now deprecated in favor of hardcoded presets in the DCTL file.

### Architecture

The project is centered around the `FadedBalancerOFX.dctl` file. This file contains:

*   UI definitions for the controls in DaVinci Resolve.
*   The image processing pipeline, which includes:
    *   Preset application
    *   Global and per-channel color adjustments (Offset, Shadows, Midtones, Highlights)
    *   A "Fade Correction" algorithm to restore contrast and saturation.
    *   Channel mixing and replacement.
    *   An optional output to a Cineon log profile for inspection.
*   Hardcoded presets for different fading scenarios.

The `docs` directory contains detailed information on the theory behind the tool, usage instructions, and a guide to the presets.

The `tools` directory contains a Python script for validating the presets.

## Building and Running

This is not a typical software project with a build process. The `FadedBalancerOFX.dctl` file is used directly by DaVinci Resolve.

### Installation

1.  Copy the `FadedBalancerOFX.dctl` file to the DaVinci Resolve LUT folder:
    *   **macOS:** `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
    *   **Windows:** `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
2.  Restart DaVinci Resolve.
3.  The DCTL will be available as an effect in the Color page.

### Running the Validation Tool

The preset validation tool can be run from the command line:

```bash
python3 tools/validate_presets.py presets/presets.json
```

**Note:** The `presets.json` file is currently deprecated, so this script may not be directly useful without modification.

## Development Conventions

*   **DCTL:** The DCTL code is well-commented and follows a clear structure. UI definitions are at the top, followed by helper functions and the main `transform` function.
*   **Presets:** Presets are now hardcoded within the `FadedBalancerOFX.dctl` file. This is a change from previous versions where they were loaded from an external JSON file.
*   **Documentation:** The project has a strong emphasis on documentation, with separate files for the scientific background, presets, and frequently asked questions.
*   **Validation:** The `validate_presets.py` script suggests a practice of validating presets against the allowed UI ranges.
