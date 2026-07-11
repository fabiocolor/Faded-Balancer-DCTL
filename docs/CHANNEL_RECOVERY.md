# Progressive Two-Point Faded-Channel Recovery

Progressive Two-Point Recovery repositions or expands one RGB channel from operator-selected neutral dark and bright samples. It is intended for a faded scan in which one channel still contains useful tonal structure but its black level, white level, or total span no longer follows the other two channels.

This is assisted endpoint matching, not full-frame automatic analysis. A per-pixel Transform DCTL has no practical once-per-frame histogram or cached scene state. The operator supplies two samples; the DCTL performs a deterministic correction for every pixel.

The setup is progressive. The dark sample produces an immediate black-point correction. The bright sample then completes the range stretch around that corrected black point.

## Calculation

For selected target channel `T`, the two non-target channels provide averaged reference endpoints:

```text
reference black = mean(other two channels in Dark Neutral Sample)
reference white = mean(other two channels in Bright Neutral Sample)

dark offset = reference black - target black
dark-corrected T = input T + dark offset
dark-corrected target white = target white + dark offset

gain = (reference white - reference black)
     / (dark-corrected target white - reference black)

recovered T = reference black
            + (dark-corrected T - reference black) * gain
```

The denominator simplifies to `target white - target black`; the expanded form above shows the intended sequence. Resolve supplies both picker values in the DCTL node-input domain, so the DCTL applies the dark offset to the stored bright value internally before calculating gain.

At full Recovery Strength, when Recovery Max Gain does not limit the gain, the **recovery stage's affine result** is mathematically the same as applying its dark offset and endpoint gain in sequence. This does not promise that two complete Faded Balancer nodes will match one: a literal two-node chain would also repeat presets, global controls, Fade Correction, mixing, and every other enabled stage.

**Recovery Strength** blends the affine result with the original target channel. **Recovery Max Gain** limits range expansion to reduce noise, grain, banding, and quantization amplification. When the limit engages, the reference black remains anchored but the requested white match is intentionally not reached.

The recovery stage does not copy donor pixels and does not clamp its result to `0..1`. It preserves the target channel's surviving spatial structure. It cannot recreate structure that is flat, clipped, or absent.

## Controls

- **Recovery Target:** `Off`, `Auto`, `Red`, `Green`, or `Blue`. `Off` is the backward-compatible default.
- **Step 1 Dark Neutral:** Pick a representative neutral dark area that is not crushed or clipped. While the bright picker is still at its reset value, this aligns only the dark endpoint.
- **Step 2 Bright Neutral:** Pick a representative neutral bright area that is not specular or clipped. This completes the black-anchored stretch.
- **Recovery Strength:** Blend from the original target channel at `0` to the calculated correction at `1`.
- **Recovery Max Gain:** Upper limit for expansion, from `1.0` to `8.0`; default `4.0`.

Resolve groups DCTL controls by control type rather than strictly preserving declaration order. Recovery Strength and Recovery Max Gain appear with the sliders, while Recovery Target and the two color pickers appear with combo-box and picker controls.

## What Auto actually detects

`Auto` is conservative and sample-driven:

- **After Step 1:** it makes a provisional choice only if one sampled dark-channel value lies clearly outside the interval formed by the other two. The absolute outlier must exceed the internal `0.02` threshold and be unique.
- **After Step 2:** it reassesses all three channels and selects one only if it is uniquely narrower than both peers or consistently lower at both sampled endpoints. Scores are normalized against the two-channel reference span and must exceed `0.02`.
- **Ambiguity:** ties, weak differences, naturally colored samples, and conflicting evidence return identity.

Because the Step 1 choice has less evidence, the selected channel can change when Step 2 is supplied. That is expected. Choose Red, Green, or Blue explicitly when inspection or film knowledge already identifies the damaged record.

Two neutral samples cannot prove whether a difference comes from dye fading, scene color, scanner response, mixed illumination, or filtration. `Auto` is a cautious convenience, not a damage classifier.

## Recommended workflow

1. Decide where the DCTL belongs in the node pipeline. Recovery samples always describe the RGB values entering this DCTL.
2. Set Preset to `None` while evaluating the endpoints.
3. Reset both recovery pickers if reusing a node. Dark resets to black and Bright resets to white.
4. Use Channel Preview and scopes to confirm that the suspected channel still contains tonal detail.
5. Select `Auto`, or choose Red, Green, or Blue explicitly.
6. Pick an unclipped neutral dark area with Step 1 Dark Neutral. The rendered image shows the black-point correction immediately.
7. Pick an unclipped neutral bright area with Step 2 Bright Neutral. The rendered image shows the full black-anchored stretch.
8. Reduce Recovery Strength if the match is visually excessive.
9. Lower Recovery Max Gain if noise, grain, quantization, or banding becomes prominent.
10. Continue with presets or manual controls, remembering that every later stage sees the recovered image.

The two samples should be under the same illumination and preferably represent the same neutral material family. Avoid colored shadows, skin unless known neutral, specular highlights, flare with a color tint, and any area clipped in one or more channels.

## Why the picker values do not concatenate visibly

The bright picker's displayed RGB remains the raw node-input sample. A DCTL UI control cannot read an intermediate pixel from its own transform or overwrite its own picker value. The rendered calculation still concatenates Step 1 internally.

Use two serial DCTL nodes only when you specifically need the second picker's **visible UI readout** to come from an already processed node, or when you intentionally want to split the wider processing pipeline between nodes. One node is sufficient for the recovery-stage endpoint math.

## Fail-closed behavior

The recovery stage returns the original pixel when:

- Recovery Target is `Off` or Recovery Strength is zero.
- The dark picker remains at its all-zero reset value.
- A sample or control needed for the calculation is non-finite.
- Auto cannot identify one unique channel for the current step.
- After Step 2, any channel's bright sample is not above its dark sample.
- The target or reference span is flat, reversed, or too close to zero.
- The calculated gain is non-positive or non-finite.

Explicit channel selection bypasses only Auto's ambiguity test. It does not bypass sample validation.

The all-zero dark and all-one bright defaults also act as setup sentinels. Those exact RGB triples are unsuitable recovery samples because they represent clipped endpoints, so treating them as “not picked” is intentional.

## Full-float and working-domain behavior

Recovery is an affine calculation on the DCTL's input RGB values. It does not assume that output must remain in `0..1`, and it applies no clamp. Negative and super-white pixel values remain representable when the calculation is finite.

The DCTL does not know the input color space. Log, scene-linear, and display-referred values give different numerical endpoint relationships. For best results:

- sample and render in the same node-input domain;
- keep both endpoints unclipped in all channels;
- judge whether matching code-value endpoints is appropriate for that encoding; and
- leave color-space conversion, gamut mapping, and legal-range handling to dedicated nodes.

Faded Balancer DCTL v1.7.0 targets DaVinci Resolve 19.1 or later.

## Numerical validation

Run:

```bash
python3 tools/test_range_recovery.py
```

The suite checks disabled identity, immediate dark preview, automatic and explicit selection, the sequential affine composition, endpoint mapping, shifted-low channels, ambiguity rejection, strength, maximum gain, invalid samples, non-finite controls, full-float behavior, RGB permutations, and randomized safety cases.
