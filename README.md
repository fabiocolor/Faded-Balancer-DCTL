# FadedBalancerOFX

![Version](https://img.shields.io/badge/version-v1.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![Donate](https://img.shields.io/badge/donate-PayPal-blue.svg)](https://paypal.me/fabiocolor)

<p align="center">
  <a href="docs/BACKGROUND_FILM_FADING.md">Background & Science</a> •
  <a href="docs/presets_companion.md">Presets Companion</a> •
  <a href="docs/FAQ.md">FAQ</a>
</p>

A DaVinci Resolve DCTL OFX plugin for balancing RGB channels and correcting faded film scans. It provides accessible and flexible tools for channel adjustment, mixing, and restoration preparation.

---

### Version

**Current: v1.4.0** (previous public base was v1.3.0; earlier versions in `previous_versions/`)

#### What's New in v1.4.0
- Added non-destructive preset system (10 starter corrective presets; toggling back to None restores baseline UI state).
- Internal pipeline clarified (see Pipeline section) – ordering unchanged from spec; presets occur before global stage.
- Minor doc clarifications; no processing math changes versus v1.3.0.

#### What's New in v1.3.0
- Added `Preserve Luminance` (⚖) – normalizes luma after per-channel stage only (global adjustments still shift exposure).
- Renamed channel "Copy" operations to clearer **Replace** (e.g. "Replace Red → With Green").
- Locked processing order: Global → Fade Correction → Per-Channel → Mixing → Replace → Removal → Output.
- Consolidated UI/label/icon overhaul (option text simplification, Darken/Lighten composite combos, consistent icon set, duplicate definitions removed).

#### What's New in v1.2.0
- Removed final hard clamp to preserve full floating-point range during grading.
- Added `Output to Cineon Log` checkbox to inspect and balance channels safely without clipping.
- Added per-channel Offset controls (Red/Green/Blue) for finer pre-lift channel alignment.

---

### Features

 -   **Film Fade Correction:** A dedicated tool to correct faded footage by adaptively enhancing contrast and saturation (see `docs/BACKGROUND_FILM_FADING.md` for background and correction strategies).
-   **Global & Per-Channel Balance:** Adjust Lift, Gamma, and Gain for all channels together or individually.
-   **Preserve Luminance (⚖):** Optional re-normalization of luma after per-channel adjustments.
-   **Channel Mixing:** Min/Max composites (e.g., `Red = min(Red, Green)` or `Blue = max(Blue, Green)`), deterministic and invertible.
-   **Channel Replace & Removal:** Replace a channel's data with another or remove a channel entirely (previously labeled Copy).
-   **Optional Cineon Output:** Linear → Cineon-like log inspection mode (not a color managed export transform).
 -   **Presets (v1.4.0):** Non-destructive internal presets that modify only temporary variables; UI slider values remain untouched. See `docs/presets_companion.md` for preset descriptions and guidance.

### Pipeline (Canonical Order)
1. Preset application (internal temporary variables only)
2. Global Adjust (Offset / Shadows / Midtones / Highlights)
3. Fade Correction (contrast + saturation nudge)
4. Per-Channel Adjust (R/G/B)
5. Optional Preserve Luminance (post per-channel only)
6. Mixing (Darken / Lighten via min/max)
7. Replace (explicit channel copy)
8. Removal (zero out channels)
9. Optional Output to Cineon Log

Identity: defaults with preset=None produce output ≈ input (floating point tolerance). Do not reorder without spec update.

---

### Before & After

Here are a few examples showcasing the plugin's effectiveness in correcting faded film scans.

**Example 1: Captain Scene**

| Before | After |
| :---: | :---: |
| ![Captain Scene Before](assets/before/captain_before.png) | ![Captain Scene After](assets/after/captain_after.png) |

**Example 2: Beach Scene**

| Before | After |
| :---: | :---: |
| ![Beach Scene Before](assets/before/beach_before.png) | ![Beach Scene After](assets/after/beach_after.png) |

**Example 3: Table Scene**

| Before | After |
| :---: | :---: |
| ![Table Scene Before](assets/before/table_before.png) | ![Table Scene After](assets/after/table_after.png) |

**Example 4: Boy Scene**

| Before | After |
| :---: | :---: |
| ![Boy Scene Before](assets/before/boy_before.png) | ![Boy Scene After](assets/after/boy_after.png) |

**Example 5: Night Scene**

| Before | After |
| :---: | :---: |
| ![Night Scene Before](assets/before/night_before.png) | ![Night Scene After](assets/after/night_after.png) |

---

### Intended Use

FadedBalancerOFX is designed for archivists, restoration specialists, and anyone working with digitally scanned film that exhibits dye fading or other channel imbalances. While it cannot restore lost color information, it provides the essential tools to neutralize color casts and prepare footage for further restoration work.

---

### Installation

1.  Download `FadedBalancerOFX.dctl`.
2.  Place it in your DaVinci Resolve LUT folder:
	-   **Windows:** `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\LUT\`
	-   **macOS:** `/Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/`
3.  Restart DaVinci Resolve.
4.  In the Color page, add a "DCTL" effect to a node and select `FadedBalancerOFX` from the dropdown menu.

---

### Usage

-   **Fade Correction:** Start with the "Fade Correction" slider to globally improve contrast and saturation.
-   **Channel Balance:** Use the "Global" sliders for overall adjustments, then fine-tune with the individual Red, Green, and Blue controls.
-   **Channel Mixing/Replace:** Use these tools to manage severe color casts. For example, on a film where the cyan dye has faded (leaving a red cast), you can mix or replace the green or blue channels into the red channel to neutralize the image.
-   **Presets (v1.4.0+):** Pick the closest corrective starting point, then refine. Switching back to None returns to baseline instantly (non-destructive).

### Workflow Recommendations

To achieve the best results and preserve maximum image fidelity, consider the following workflow:

*   **Prevent Clipping:** Enable the `Output to Cineon Log` checkbox to verify there is no highlight or shadow clipping in your image.
*   **Avoid Clipping in Red Channel:** When dealing with significant red channel imbalances (common in faded film), it is often better to use the `Red Midtones` control for the primary correction. Using `Red Shadows` (lift) can sometimes crush shadow detail, whereas adjusting the midtones offers a gentler re-balance.
*   **Use Presets Conservatively:** Apply a preset, evaluate scopes, then refine with per-channel midtones before heavy shadow or highlight changes.

For common questions and troubleshooting, see the FAQ: `docs/FAQ.md`.

### Video Demonstration

For a visual guide on how to use the plugin, check out the video tutorial below:

[![FadedBalancerOFX Video Tutorial](https://img.youtube.com/vi/ATPkq5BHs-A/maxresdefault.jpg)](https://youtu.be/ATPkq5BHs-A)

---

### License

## Documentation

- Background & science: `docs/BACKGROUND_FILM_FADING.md` — technical summary of chromogenic dye fading and practical correction approaches.
- Presets companion: `docs/presets_companion.md` — detailed descriptions of included presets and recommended starting points.
- FAQ: `docs/FAQ.md` — common questions, troubleshooting, and user tips.

[MIT License](LICENSE)

---

### Credits

Developed by Fabio Bedoya.

---

### Contact

- **Email:** [info@fabiocolor.com](mailto:info@fabiocolor.com)
- **Instagram:** [@fabiocolor](https://www.instagram.com/fabiocolor)
- **LinkedIn:** [Fabio Bedoya](https://www.linkedin.com/in/fabiobedoya/)
- **YouTube:** [@fabiocolor](https://www.youtube.com/@fabiocolor)

---

### Acknowledgements

The "Film Fade Correction" feature was partially inspired by insights from the following paper, which provided a valuable foundation for the approach used:

-   Trumpy, G., Flueckiger, B., & Goeth, A. (2023). *Digital Unfading of Chromogenic Film Informed by Its Spectral Densities*. [Link to paper](https://ntnuopen.ntnu.no/ntnu-xmlui/handle/11250/3101572)

---

### Support the Project

If you find this plugin useful and would like to support its ongoing development, please consider making a donation. Your support is greatly appreciated!

[Donate via PayPal](https://paypal.me/fabiocolor)