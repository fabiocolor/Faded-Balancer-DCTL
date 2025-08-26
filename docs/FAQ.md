# FadedBalancer — FAQ

- What is it: A DCTL for rebalancing RGB in faded film scans; restores neutral balance and midtone contrast.
- When to use: Early in grading on magenta‑shifted, washed‑out, or low‑contrast scans.
- Core controls: Fade Correction; Global+Per‑Channel Offset/Shadows/Midtones/Highlights; Mixing (Darken/Lighten); Replace/Remove; optional Cineon view.

## Quick Workflow
1) Pick a preset close to the target look.
2) Set Fade Correction for midtone contrast.
3) Balance globally, then refine per‑channel.
4) Enable Preserve Luminance if overall brightness drifts.

## Notes for Restoration
- Prefer midtone adjustments to avoid shadow noise amplification.
- Use Mixing/Replace only when a channel dominates (e.g., cyan loss → reduce red mids or borrow green/blue).
- Verify clipping in Cineon view; keep operations invertible where possible.

## Install
- Place `FadedBalancerOFX.dctl` in Resolve’s LUT/DCTL folder and restart.

Contact: info@fabiocolor.com

