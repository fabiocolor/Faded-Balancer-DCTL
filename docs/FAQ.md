# Faded Balancer — FAQ for Colorists & Restoration Artists

This short FAQ explains what `FadedBalancerOFX.dctl` does, when to use it, and practical tips for working with faded chromogenic film scans. For in-depth, technical background (dye chemistry, kinetics, and archival methods) see the private developer reference `internal/BACKGROUND_FILM_FADING.md`.

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
- Maintainers and restorers can read the private background reference: `internal/BACKGROUND_FILM_FADING.md`.

If you want this FAQ trimmed, extended, or copied into a short README section for end-users, tell me which parts to expand or simplify.
