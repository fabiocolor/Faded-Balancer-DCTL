# Acceptance Tests

### Test 1: Neutral Fade Correction
**Input:** Magenta faded clip.  
**Operation:** Balance_R=-0.2f, Balance_B=+0.2f.  
**Expected:** Neutral grey scale parade in RGB scopes.

---

### Test 2: Channel Copy
**Input:** Blue channel fully blank.  
**Operation:** Copy Green→Blue.  
**Expected:** Reconstructed blue channel, histogram matches green.

---

### Test 3: Channel Removal
**Input:** Normal clip.  
**Operation:** Remove Red.  
**Expected:** Output only Green + Blue.

---

### Test 4: Section Bypass
**Input:** Clip with all toggles off.  
**Expected:** Exact passthrough, no pixel change.

---

### Test 5: Extreme Gamma
**Input:** Any clip.  
**Operation:** Gamma_R=+1.0f.  
**Expected:** Red channel curve visibly altered, but no values exceed [0,1].

---
# Acceptance Tests

Visual and numerical acceptance tests apply as described.

Note:
- UI behaviors (default values, tooltips, slider limits) verified by Resolve’s inspector.
- Follows same semantics as GainDCTLPlugin and ColorPicker examples.

# Acceptance Tests

## 1. Identity
Defaults → output == input (within float precision).

## 2. Preserve Luma
Adjust Red Highlights=1.2f, Preserve Luminance=1 → Y_post ≈ Y_pre (Δ ≤ 0.001).

## 3. Magenta Fade Fix
Input: Blue ~12% under R/G.  
Action: BlueHighlights=1.12f.  
Expect: R≈G≈B neutralized.

## 4. Darken/Lighten
RedDarkenWith=Green → R_out = _fminf(R,G).  
RedLightenWith=Blue → R_out = _fmaxf(R,B).

## 5. Replace + Remove
copyBlueSource=Red, channelRemovalMode=Remove Blue.  
Result: B = 0.

## 6. Cineon Output
outputToCineon=1.  
Expect: monotonic log encoding per channel, no gamut ops.

# Minimal Acceptance Tests (reference for Copilot)

## 1) Identity
Params: all defaults (preserveLuminance=0, outputToCineon=0)
Expect: out ≈ in (subject to float precision).

## 2) Preserve Luma Check
- Record Y_pre after Fade.
- Apply per-channel tweaks (e.g., redHighlights=1.2f).
- With preserveLuminance=1, Y_post ≈ Y_pre (±1e-3), chroma changes visible.

## 3) Magenta Fade Scenario
Input: neutral swatch where B is ~12% under R/G.
Action: set blueHighlights=1.12f (and/or blueMidtones=0.95f).
Expect: Δ(R−G) small; B approaches R/G without overshoot.

## 4) Darken/Lighten Composites
Set redDarkenWith=With Green, redLightenWith=None.
Expect: R_out = min(R_in, G_in). With Lighten: R_out = max(R_in, G_in).

## 5) Replace Then Remove
Set copyBlueSource=With Red, channelRemovalMode=Remove Blue.
Expect: B becomes R, then zeroed → final B = 0.

## 6) Cineon Output Sanity
Enable outputToCineon=1.
Expect: monotonic encoding per channel; mid-grays compress toward log mid.

