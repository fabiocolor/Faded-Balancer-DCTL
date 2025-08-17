# Faded Balancer — FAQ for Colorists & Restoration Artists

This short FAQ explains what `FadedBalancerOFX.dctl` does, when to use it, and practical tips for working with faded chromogenic film scans. For in-depth technical background or maintainer-only notes, contact the project owner.

Q: What is FadedBalancer?
A: A single-file DCTL shader that helps rebalance color and recover midtone contrast in faded film scans. It offers presets for common faded stocks plus global and per-channel controls so you can target neutral drift (commonly magenta/pink casts) and recover natural-looking neutrals.

Q: When should I use it?
A: Use it on scanned film or archival footage that shows color casts, lifted blacks, or low midtone contrast typical of aged chromogenic prints. It is designed as a corrective pass — try it early in your pipeline on a copy of the scan.

Q: What do the main controls do (in plain terms)?
- Fade Correction: gentle contrast + saturation recovery tuned for faded material.
- Preserve Luminance: keeps perceived brightness stable after per-channel work (useful when rebalancing neutrals).
- Global / Per-Channel (Offset, Shadows, Midtones, Highlights): familiar lift/gamma/gain controls; per-channel midtone exponents are useful to counter unequal dye loss.
- Mixing / Replace / Remove: deterministic operations to composite or mute channels safely (e.g., remove a noisy channel).

Q: Quick workflow tip
1. Pick a preset if you know the stock (presets are suggestions).
2. Set fade correction to taste for midtone contrast.
3. Use per-channel offsets or midtones to align neutral patches (eye or scope).
4. Enable Preserve Luminance if neutral rebalancing changes apparent brightness.

Q: Safety & best practices
- Work nondestructively; preserve originals.
- Avoid extreme boosts in dark shadows to limit noise amplification.
- Keep midtone exponents within reasonable ranges (small adjustments first).

Q: How do I install and test?
- Copy `FadedBalancerOFX.dctl` into Resolve's LUT/DCTL folder and restart Resolve.
- On a neutral chart or known gray patch, verify the neutral axis moves toward neutral without clipping.

Q: Want deeper rationale?
- Maintainer-only background research is private; contact the project owner for access.

### Quick visual checklist (use scopes)
Follow these quick checks after you make adjustments to confirm a safe correction:

- Neutrals: On vectorscope and RGB parade, neutral patches should align near the neutral axis and show roughly equal R/G/B amplitudes in midtones.
- Luma preservation: If `Preserve Luminance` is enabled, overall perceived brightness (monitor or waveform) should remain similar before/after per-channel tweaks.
- Shadows: Check parade shadows for noise spikes after aggressive boosts — reduce shadow gain if noise is amplified.
- Highlights: Use the Cineon inspection toggle to ensure highlights do not clip in log space before committing stronger highlight boosts.
