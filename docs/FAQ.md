# Faded Balancer DCTL — FAQ

<p align="center">
  <a href="../README.md">Home</a> •
  <a href="CHANNEL_RECOVERY.md">Channel Recovery</a> •
  <a href="BACKGROUND_FILM_FADING.md">Background & Science</a> •
  <a href="presets_companion.md">Presets Companion</a>
</p>

---

### Recovery

**Is two-point recovery automatic white balance?**

Not in the full-frame analysis sense. You supply a representative neutral dark sample and a representative neutral bright sample. The DCTL estimates the damaged channel's reference endpoints from the other two channels and applies an offset-and-gain correction to that one channel.

`Auto` only selects the channel. It does not search the frame for neutral objects, build a histogram, recognize skin, or determine scene illumination. This is an assisted balancing tool designed around what a per-pixel Transform DCTL can calculate reliably.

**Why does the image change after the dark pick, before I choose the bright point?**

That is the progressive part of the workflow. Step 1 aligns the target channel's sampled dark value to the mean of the other two sampled values. Step 2 then stretches around that corrected black point so the bright endpoint also aligns.

**Why does the bright picker's displayed value still look like the original image?**

Resolve supplies both color-picker values from the DCTL node input. A Transform DCTL cannot write its intermediate result back into its own picker UI. Faded Balancer therefore applies the Step 1 offset to the stored bright value internally before calculating Step 2.

At full Recovery Strength, when Recovery Max Gain does not limit the result, this recovery-stage affine math matches applying the dark offset and then the endpoint gain sequentially. It does not mean that two complete Faded Balancer nodes with other active stages will always match one node.

**Why did Auto choose a channel after the dark pick and then change after the bright pick?**

Before Step 2, Auto has only one sample and can make a provisional choice only when one dark-channel value clearly lies outside the other two. After Step 2, it re-evaluates all three channel spans and endpoint levels. The better-supported final choice can differ. Choose Red, Green, or Blue explicitly if you already know the damaged record.

**Why does Auto sometimes do nothing?**

Ambiguity is treated as identity. Two samples cannot reliably distinguish subtle fading from naturally colored scene content. Auto also refuses invalid, reversed, flat, non-finite, or effectively clipped sample spans. Explicit channel selection avoids only the ambiguity check; it cannot make a flat channel recoverable.

**Can recovery restore a completely flat or clipped channel?**

No. A stretch can expand surviving differences, but it cannot invent detail. Recovery Max Gain limits noise, grain, quantization, and banding amplification. Matrix mixing or Replace can borrow structure from another channel, but that is an approximation or substitution—not recovery of the original color record.

**What makes a good sample?**

Choose unclipped, low-chroma areas under the same illumination: one dark but not crushed, one bright but not specular. Avoid colored objects, mixed lighting, reflections, and areas where any RGB channel is flat. Both picker values must represent the DCTL's input domain.

---

### Core grading controls

**What is the difference between Offset, Lift, Gamma, and Gain?**

The actual operation order is:

```text
x = x + Offset + Lift
x = sign(x) * abs(x)^(1 / Gamma)
x = x * Gain
```

- Offset adds a constant to the whole channel.
- Lift is a legacy additive control with the same response as Offset. It is not restricted to shadows; its behavior is retained for compatibility with existing grades.
- Gamma is a sign-preserving power operation. `1.0` is neutral.
- Gain multiplies the whole channel. It is not restricted to highlights.

These definitions apply to both global and individual RGB controls.

**Does Fade Correction examine the image and adapt to the damage?**

No. It is a deterministic per-pixel curve driven only by its slider. It uses Rec.709-weighted luma to apply a smooth contrast nudge within `0..1` and increases chroma progressively. It is useful for washed-out scans, but it does not estimate dye loss or choose a setting automatically.

**What does Preserve Luminance preserve?**

It stores Rec.709-weighted luma immediately before the manual per-channel Offset/Lift/Gamma/Gain pass and rescales RGB immediately afterward. It does not preserve final output brightness across global controls, presets, Fade Correction, matrix or min/max mixing, Replace, Removal, Preview, or Diagnostic Log Preview.

The rescale is skipped when a safe finite ratio cannot be calculated. Large per-channel corrections can also change hue or drive values out of range even when the weighted luma is matched.

**Does the DCTL clamp values to `0..1`?**

There is no final hard clamp. Neutral Gamma preserves sign, active Gamma uses signed power, and recovery can produce below-black or super-white values. Fade Correction keeps its bounded luma curve from folding excursions outside `0..1`.

Some explicit tools are intentionally range-changing: Removal writes zero, Channel Preview duplicates one channel, and Diagnostic Log Preview maps non-positive inputs to zero. A downstream transform, viewer, codec, or node can still clip values even when this DCTL does not.

---

### Mixing and channel substitution

**What is the difference between Matrix, Darken/Lighten, and Replace?**

- **Matrix** adds or subtracts a scaled donor channel from a target. `Red from G = 0.2`, for example, forms `R + 0.2G` before tonal blending.
- **Darken/Lighten** chooses the lower or higher of the target and adjusted donor, then applies tonal blending.
- **Replace** overwrites the target with a complete donor channel. Multiple Replace choices are simultaneous and read from the same pre-replacement RGB snapshot.

Matrix and min/max operations can borrow correlated structure. Replace is a complete substitution. None can know the original values of missing or clipped pixels.

**How do Mixing Shadows and Mixing Highlights work?**

They are broad, overlapping weights—not hard tonal ranges. Using Rec.709-weighted luma `L` clamped to `0..1`, the blend amount is:

```text
(1 - L²) * Mixing Shadows + L² * Mixing Highlights
```

Shadows `1` / Highlights `0` is strongest at black and fades smoothly toward white. Shadows `0` / Highlights `1` rises smoothly from black toward white. Both `1` gives full mixing throughout. Intermediate settings combine the two weights.

The luma is calculated from the image entering each mixing stage, so the matrix can affect the luma subsequently seen by the min/max stage.

**What does Donor Luminance do?**

It multiplies donor channels before both additive matrix and min/max mixing. Lower values reduce donor influence; higher values increase it. In the matrix, it scales the added or subtracted donor term. In min/max mixing, it changes the donor value being compared with the target.

It is not a perceptual luminance match, exposure compensation, or automatic normalization.

**Can matrix mixing rebuild a clipped highlight?**

It can add structure from another channel where the channels are sufficiently correlated. That may produce a more plausible target channel, but it is an approximation. It cannot determine the original spectral response or color from data that no longer exists.

---

### Presets

**Why don't the UI sliders move when I select a preset?**

DCTL code cannot move its own controls. A preset applies a fixed internal Offset/Lift/Gamma/Gain pass before the visible manual controls. Returning to `None` removes that internal pass without overwriting your slider positions.

This is non-destructive to the UI state, not an indication that the preset leaves the image unchanged. Presets are fixed recipes and do not evaluate the current shot.

**What does Preset Tonal Only do?**

Eight presets request `Blue Darken With Green`. With Preset Tonal Only unchecked, that request is used only when the visible Blue Darken selector is `None`; an explicit manual Blue Darken choice wins. Enable the checkbox to use only the preset's Offset/Lift/Gamma/Gain recipe.

Unchecked is the compatibility-preserving default, including when Resolve upgrades a saved node created before this checkbox existed.

Red Comp Blue Tweak and Neutral Red Mid Tweak do not request mixing, so the checkbox has no effect on those presets. See [Presets Companion](presets_companion.md) for every internal recipe.

**My image looks worse after a preset. What should I do?**

Return Preset to `None`, or enable Preset Tonal Only to separate the tonal recipe from its optional channel mix. The presets were derived as starting looks for particular scans. They are neither scene-aware nor guaranteed to preserve hue, luma, or headroom on other material.

---

### Preview, color management, and compatibility

**What does Channel Preview do?**

Red Only, Green Only, or Blue Only duplicates the selected channel into all three outputs, producing a grayscale inspection view. It occurs after Replace and Removal, so it shows their result. Return it to Normal for grading or delivery.

**What is Diagnostic Log Preview?**

It is a simple positive display compression: positive `x` is mapped to `x / (1 + x)`, while zero and negative values map to zero. It can make positive super-white excursions easier to inspect.

It is not Cineon, not a standard log curve, not reversible for non-positive values, and not a color-space or delivery transform. It cannot recover anything clipped before the DCTL. Disable it for normal output.

**Where should the DCTL go in a color-managed pipeline?**

The DCTL performs no color-space conversion and works directly on its node-input RGB values. Put it where those values make sense for the operation you are using, and take both recovery samples in that same domain. Fade Correction is tuned around normalized `0..1` luma; Gamma and channel mixing will look different in log, linear, and display-referred encodings.

There is no universally correct node position for every scan. Verify the channels on scopes, keep samples unclipped, and perform display conversion, gamut mapping, and legal-range handling in dedicated downstream steps.

**Which Resolve versions are supported?**

Faded Balancer DCTL v1.7.0 targets DaVinci Resolve 19.1 or later. Older versions are not supported because the current DCTL uses newer Transform DCTL UI definitions and tooltips.

<p align="center">
  <a href="../README.md">Back to Home</a>
</p>
