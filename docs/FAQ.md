# Faded Balancer DCTL - FAQ

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="BACKGROUND_FILM_FADING.md">Background & Science</a> •
  <a href="presets_companion.md">Presets Companion</a>
</p>

---

### Frequently Asked Questions

**Why don't the UI sliders move when I select a preset?**

> This is a current limitation of the DCTL format, which does not allow an effect to modify its own UI sliders.
> 
> However, this limitation results in a non-destructive workflow. Presets operate on temporary internal variables, leaving your existing slider adjustments untouched. This allows you to apply and toggle presets without losing your manual settings. The preset is applied *before* your slider adjustments in the image processing pipeline.
> 
> A future version of this tool as a native OpenFX plugin may overcome this limitation and have the sliders update when a preset is selected.

**What does the `Preserve Luminance` checkbox do?**

> It automatically renormalizes the image's luminance *after* any per-channel adjustments have been made. This helps maintain a consistent overall exposure while you correct specific color casts. Note that global adjustments will still affect the final brightness.

**When should I use the `Output to Cineon Log` option?**

> This is a diagnostic tool designed to help you balance channels safely. By converting the output to a Cineon-like log profile, it allows you to inspect the image for channel imbalances and potential clipping in the highlights or shadows before it happens. It is not intended as a final color space transform for delivery.
> 
> Imagine a waveform monitor. A standard output might clip, losing detail in the brightest parts of the image. The Cineon Log output compresses the dynamic range, so you can see all the detail.
> 
> ```
>      Clipped Highlights (Standard View)         Preserved Highlights (Cineon Log View)
> 1023 |--------------------^^^^^^^----|        1023 |--------------------------------|
>      |                   /           |             |                                |
>  768 |------------------/------------|         768 |--------------------/\----------|
>      |                 /             |             |                   /  \         |
>  512 |----------------/--------------|         512 |------------------/----\--------|
>      |                /              |             |                 /      \       |
>  256 |---------------/---------------|         256 |----------------/--------\------|
>      |              /                |             |               /          \     |
>    0 |-------------/-----------------|           0 |--------------/------------\---|
> 
> ```
> In the "Clipped" example, the waveform hits the top and flattens, indicating lost detail. In the "Log" view, the entire waveform is visible, allowing for more precise adjustments.


**My image looks worse after applying a preset. What should I do?**

> Presets are intended as starting points, not one-click solutions. If a preset doesn't produce the desired result, switch back to "None" and begin with manual adjustments. A good starting workflow is to use the "Fade Correction" slider first, then fine-tune the balance using the per-channel `Midtones` controls.

**What is the difference between Channel Mixing and Channel Replacement?**

> **Mixing** combines channels using `min` (Darken) or `max` (Lighten) composite operations. For example, `Red = min(Red, Green)` will darken the red channel wherever it is brighter than the green channel. This is useful for subtle corrections.
>
> **Replacement** completely overwrites the pixel values of one channel with another (e.g., `Red -> Green` makes the red channel's data identical to the green channel's). This is a more aggressive tool, best used for correcting severe color casts where one channel is almost entirely gone.

**How do the new shadow/highlight mixing controls work? (v1.6.0)**

> The **🎭 Mixing Shadows** and **🎭 Mixing Highlights** sliders control where darken/lighten operations take effect in the image. Set to `1.0` for full effect in that tonal range, `0.0` for no effect.
>
> **Example:** If blue is damaged only in shadows, set "Blue Darken With Green", then "Mixing Shadows = 1.0" and "Mixing Highlights = 0.0". This repairs blue shadows using green data while leaving highlights untouched.
>
> This is perfect for film restoration where damage often occurs in specific tonal ranges.

**What does Channel Preview do? (v1.6.0)**

> **👁️ Channel Preview** lets you isolate individual channels (Red Only, Green Only, Blue Only) to inspect damage without using keyboard shortcuts. Essential for film restoration workflow to see exactly which channels need repair. Set back to "Normal" for standard color view.

---

<p align="center">
  <a href="../README.md">Back to Home</a>
</p>
