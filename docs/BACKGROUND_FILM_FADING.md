# Faded Balancer DCTL - Background & Science

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="presets_companion.md">Presets Companion</a> •
  <a href="FAQ.md">FAQ</a>
</p>

---

### The Science of Film Fading

This document provides a brief, practical overview of why color film fades and the strategies Faded Balancer DCTL employs to correct it.

### How Color Film Works

Most color motion picture film is **chromogenic**, meaning it creates color through a chemical process. A prominent example of this is the **Eastman Color** process, developed by Kodak in 1950. This process uses a multilayer film (an Integral Tripack) where three key layers, each sensitive to a primary color of light, are exposed in a standard camera.

During development, a process called **dye-coupling** occurs. A special developing agent combines with color-forming couplers in each layer to create dyes of the complementary color. The concentration of the dye is proportional to the amount of silver in the image, and the silver is removed later in the process.

The following diagram illustrates the structure of Eastman Color Print Film Type 5381, showing the different emulsion layers.

![Structure of Eastman Color Print Film](../assets/diagrams/Craig_Eastman-Color_1953-plate-2b.png)
*Source: Craig Eastman (1953), Plate 2b. More historical diagrams can be found in the Eastman Color gallery on [filmcolors.org](https://filmcolors.org/galleries/eastmancolor-illustrations/).*

| Light Sensitivity | Forms Dye |
| :---: | :---: |
| 🔵 Blue | 🟡 Yellow |
| 🟢 Green | 🟣 Magenta |
| 🔴 Red | 🇨🇳 Cyan |

These three dyes (Cyan, Magenta, Yellow) are organic and inherently unstable. Over time, they chemically break down, causing the image to fade and shift in color.

### The "Magenta Cast" Problem

While all dyes are unstable, the dyes in Eastman Color film stock, particularly from the 1950s to the early 1980s, were known for their chemical instability. The **cyan and yellow dyes are notoriously less stable** than the magenta dye. As they deteriorate at a faster rate, the image loses its blue and green information, leaving the more stable magenta dye to dominate the color balance.

This phenomenon is especially common in certain film stocks, such as the **Eastman Color Print Film** widely used for theatrical distribution prints during that era. The result is a characteristic **strong red or magenta cast**, often referred to as the "pink fade." It wasn't until the early 1980s that more stable "Low Fade" stocks were introduced.

This is the single most common type of color degradation in archival film, and it is the primary problem Faded Balancer DCTL is designed to solve.

**Example of Faded Film with a Magenta Cast:**
![Captain Scene Before](../assets/before/captain_before.png)

### Corrective Strategies in Faded Balancer DCTL

Because the original dye information is permanently lost from the film, a true restoration of the original colors is impossible. Instead, the goal is to **re-balance the remaining color channels** to achieve a neutral, believable image. This process is a form of digital approximation, using the remaining data to make an informed "guess" at the intended look.

#### 1. Reduce the Dominant Channel
The most direct approach is to reduce the strength of the red channel to bring it back in line with the green and blue channels.
> - **Tools:** The per-channel `Red` sliders (Shadows, Midtones, Highlights) and several presets (`Strong Red Compress`, `Red Compress Mid`) are designed for this purpose.

#### 2. Channel Mixing & Replacement
In severe cases, the red channel may be too noisy, clipped, or degraded to be useful on its own. In these situations, we can "borrow" information from a healthier channel.
> - **Mixing:** Operations like `Red = min(Red, Green)` can effectively darken the red channel where it appears unnaturally bright, reducing the color cast.
> - **Replacement:** A more drastic step, `Red -> Green`, replaces the red channel's data entirely with the green channel's. This is highly effective at removing the cast but will alter the scene's original color palette.

#### 3. The Fade Correction Algorithm
The `Fade Correction` slider is an adaptive tool that analyzes the image to intelligently boost contrast and saturation.
> - **Purpose:** It is designed to counteract the washed-out, low-contrast look that is typical of faded film. It serves as an excellent first step before making fine-tuned manual adjustments to individual color channels.

---

<p align="center">
  <a href="../README.md">Back to Home</a>
</p>
