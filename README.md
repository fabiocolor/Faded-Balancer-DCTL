# FadedBalancerOFX

![Release](https://img.shields.io/github/v/release/fabiocolor/Faded-Balancer-DCTL?include_prereleases&sort=semver)
![License](https://img.shields.io/badge/license-MIT-green)
[![Donate](https://img.shields.io/badge/donate-PayPal-blue.svg)](https://paypal.me/fabiocolor)

<p align="center">
  <a href="docs/BACKGROUND_FILM_FADING.md">Background & Science</a> •
  <a href="docs/presets_companion.md">Presets Companion</a> •
  <a href="docs/FAQ.md">FAQ</a> •
  <a href="https://github.com/fabiocolor/Faded-Balancer-DCTL/releases">Releases</a>
</p>

A DaVinci Resolve DCTL OFX plugin for balancing RGB channels in faded film scans. It provides controlled per‑channel adjustment, mixing, and inspection tools suited to archival restoration work.

---

### Releases

Versions are tracked on the GitHub Releases page. See release notes for changes and downloadable artifacts.

---

### Features

- **Fade correction:** Gentle contrast/saturation recovery for faded prints (see `docs/BACKGROUND_FILM_FADING.md`).
- **Global & per‑channel balance:** Offset/Shadows/Midtones/Highlights controls; tuned for restoration workflows.
- **Preserve luminance:** Optional luma re‑normalization after per‑channel stage.
- **Channel mixing:** Darken/Lighten via min/max; deterministic and invertible.
- **Replace / removal:** Replace a channel from another, or mute channels for checks.
- **Cineon inspection:** Optional linear→Cineon log viewing transform (inspection only).
- **Presets:** Non‑destructive starting points (see `docs/presets_companion.md`).

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

### Examples

Example frames are available under `assets/before/` and `assets/after/`.

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

- Set Fade Correction for a modest midtone contrast/color lift.
- Balance globally, then refine with per‑channel controls (R/G/B).
- Use Mixing/Replace for strong channel dominance (e.g., cyan loss → reduce red mids or borrow green/blue).
- Presets: choose the closest, then refine; switching to None restores baseline.

### Workflow Notes

- Enable Cineon view to check clipping without altering grade context.
- Prefer midtone adjustments for red bias; large shadow lifts amplify noise.
- Apply a preset, evaluate scopes, then fine‑tune midtones before heavy shadow/highlight moves.

For common questions and troubleshooting, see the FAQ: `docs/FAQ.md`.

### Video Demonstration

For a visual guide on how to use the plugin, check out the video tutorial below:

[![FadedBalancerOFX Video Tutorial](https://img.youtube.com/vi/ATPkq5BHs-A/maxresdefault.jpg)](https://youtu.be/ATPkq5BHs-A)

---

### Documentation & License

- Background & science: `docs/BACKGROUND_FILM_FADING.md`.
- Presets companion: `docs/presets_companion.md`.
- FAQ: `docs/FAQ.md`.

License: [MIT](LICENSE)

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
