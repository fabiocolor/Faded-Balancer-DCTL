# Preset Companion (Simple Guide)

These 10 presets are gentle starting points for common faded film situations. Pick one that feels closest, then fine‑tune the sliders. Presets never overwrite your actual UI values; they only set temporary internal copies.

Quick meanings:
- "Red Compress" entries: calm down red mids/highs where cyan dye faded.
- "Balanced" / "Neutral" entries: light shaping only.
- "Heavy Red Crush": strong rescue for severe red imbalance (use sparingly; watch scopes).
- "Neg Offset Blue Cut": slight overall dip plus blue shadow reduction to tame cool noise.
- "Highlight Lift Blue Shadow": lifts highlights while gently pulling blue shadows down.

Preset list (1 → 10):
1. Red Compress Mid – everyday mild red mid control.
2. Balanced Aggregate – safe neutral baseline.
3. Red Compress Hi Lift – mild red compress with a modest highlight lift.
4. Red Comp Blue Tweak – adds a tiny blue shadow dip.
5. Heavy Red Crush – strong red mid compression + highlight gain (watch clipping).
6. Mild Corrective – small overall tidy with softer highlights.
7. Neutral Red Mid Tweak – near neutral, light red mid compression.
8. Strong Red Compress – deeper red compression for tougher fades.
9. Neg Offset Blue Cut – slight negative offset plus blue shadow suppression.
10. Highlight Lift Blue Shadow – gentle highlight lift + softened blue shadows (safer variant).

How to choose:
- Start with 2 (Balanced) if unsure.
- If image is very magenta: try 1, 3, or 8.
- If highlights feel dull: try 3 or 10.
- If blue shadows are noisy or cool: 4, 9, or 10.
- If red layer almost gone: 5 (then refine carefully).

After picking:
1. Nudge Fade Correction (0.10–0.30 typical) for a subtle contrast/color lift.
2. Toggle Preserve Luminance if color moves changed overall brightness too much.
3. Adjust per‑channel Midtones first before heavy offset or highlight moves.
4. Use min (Darken) mixes only if a channel spikes compared to others.

Checklist before moving on:
- Parade looks neutral (grays sit together).
- Highlights not clipping (enable Cineon view to inspect).
- Skin / memory colors feel natural after small tweaks.
- Blue noise acceptable (if not, pick a preset with blue darken).

That’s it. Keep it gentle; this tool is for clean rescue, not stylized looks.

Doc version: matches shader v1.4.0.

## Share your preset (short)

If you have a preset that helps others, please share it. Preferred submission: email **info@fabiocolor.com** with subject "Preset submission: <your preset name>" and attach one of the following minimal items:

- `preset.txt` — plain text containing the minimal submission fields below (recommended), or
- `ui.png` — full DCTL UI screenshot showing numeric values.

Optional but helpful: `before.png` and `after.png` (small, cropped) and a tiny scope (RGB parade).

Minimal submission (copy/paste into email or an issue):
- Preset name:
- Author / handle (optional):
- Short description:
- Tested shader / Resolve version:
- Key UI values (only values changed from defaults):
	- Fade Correction:
	- Preserve Luminance: <true|false>
	- Global Offset (R,G,B):
	- Global Shadows (R,G,B):
	- Global Midtones (scalar or R,G,B):
	- Global Highlights (R,G,B):
   
License / consent
- Include a short line giving permission to include the preset in the repository (recommended: CC0 / Public Domain), or specify preferred attribution.
	Example: "I consent to inclusion under CC0 (public domain)" or "Include with attribution: @username".
