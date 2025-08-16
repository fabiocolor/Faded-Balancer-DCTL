{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww25100\viewh26880\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # Project Requirements Document \'97 FadedBalancerOFX.dctl\
\
## Purpose\
Film scans often suffer from magenta fading (blue channel loss).  \
The goal of this DCTL is to provide colorists with deterministic, GPU-accelerated tools inside Resolve to rebalance channels quickly, without introducing new color information or relying on LUTs.\
\
## Target Users\
- Film restoration technicians\
- Colorists working in DaVinci Resolve\
- Archivists requiring reproducible and transparent tools\
\
## Goals\
- Deliver a Transform DCTL (Resolve 19.1+ compatible).\
- Provide intuitive UI controls (sliders, checkboxes, combos).\
- Keep the tool fast and deterministic (real-time playback on GPU).\
- Allow recovery of faded scans while preserving archival integrity.\
\
## Functional Requirements\
1. **Global Controls**: Offset, Shadows, Midtones (gamma), Highlights (gain).\
2. **Fade Correction**: single scalar to counteract magenta bias.\
3. **Per-Channel Controls**: Offset, Shadows, Midtones, Highlights for R/G/B.\
4. **Preserve Luminance**: checkbox to normalize Y after per-channel ops.\
5. **Mix**: Darken/Lighten per channel using min/max composites.\
6. **Replace**: copy a channel from another.\
7. **Removal**: zero one or more channels.\
8. **Output Option**: Cineon log encoding per channel.\
9. **UI Constraints**: controls defined with `DEFINE_UI_PARAMS`; \uc0\u8804 64 per UI type.\
10. **Math Constraints**: use only Resolve DCTL intrinsics (e.g. `_powf`, `_fminf`, `_fmaxf`, `_clampf`).\
\
## Non-Functional Requirements\
- **Performance**: must run in real time (single-pass per pixel).\
- **Portability**: works under CUDA, OpenCL, Metal (cross-GPU).\
- **Clarity**: UI labels match function; optional tooltips explain purpose.\
- **Maintainability**: code commented per stage with reference to spec.\
\
## Non-Goals\
- No AI inference.\
- No LUT baking.\
- No gamut remapping or creative colorization.\
\
## Success Criteria\
- Default values \uc0\u8594  identity transform (input \u8776  output).\
- Neutral grays restored in faded scans with minor adjustments.\
- Preserve Luminance maintains Y within \'b10.001.\
- Cineon output produces monotonic log encoding per channel.\
\
## References\
- BMD official DCTL documentation (syntax, UI controls, intrinsics).\
- GainDCTLPlugin.dctl (UI slider usage).\
- ColorPicker.dctl (tooltip and color picker usage).\
\
\
| Requirement ID | Description              | User Story                                                                 | Expected Behavior/Outcome                                                                                          |\
|----------------|--------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|\
| FR001          | Global Controls          | As a colorist, I want global controls (offset, shadows, midtones, highlights) so I can adjust the whole image easily. | The system should apply additive and multiplicative changes to all channels uniformly, following gamma for midtones. |\
| FR002          | Fade Correction          | As a colorist, I want a single fade slider to counteract magenta casts, so I can quickly neutralize faded scans.     | The system should bias the blue channel relative to red/green to reduce magenta appearance.                         |\
| FR003          | Per-Channel Adjustments  | As a colorist, I want per-channel offset/shadow/midtone/highlight controls, so I can correct specific channel imbalances. | The system should apply each adjustment to the respective channel only, preserving independence.                     |\
| FR004          | Preserve Luminance       | As a colorist, I want a toggle to preserve overall luminance when changing channels, so brightness stays consistent. | The system should normalize luma (Rec.709) after per-channel ops to match pre-adjustment luminance.                  |\
| FR005          | Darken/Lighten Mix       | As a colorist, I want to darken or lighten a channel against another, so I can control cross-channel relationships. | The system should apply `_fminf` or `_fmaxf` to the chosen channels, per user selection.                            |\
| FR006          | Channel Replace          | As a colorist, I want to replace one channel with another, so I can quickly rebuild missing or damaged channels.     | The system should copy the source channel\'92s values into the target channel, after Mix and before Removal.            |\
| FR007          | Channel Removal          | As a colorist, I want to remove a channel entirely, so I can isolate or test images without it.                      | The system should zero the chosen channel(s) at the final stage, overriding prior operations.                        |\
| FR008          | Cineon Output Option     | As a colorist, I want to output Cineon log values, so I can inspect film-like encoding without LUTs.                 | The system should encode linear RGB into Cineon log per channel if the option is enabled.                            |\
| FR009          | UI Controls & Tooltips   | As a user, I want clear UI labels and tooltips, so I know what each control does.                                   | All controls must be defined with `DEFINE_UI_PARAMS` and may include `DEFINE_UI_TOOLTIP` (per Resolve 19.1+).        |\
| FR010          | Performance Constraints  | As a user, I want real-time playback, so I can grade interactively.                                                | The system should run in a single-pass GPU shader, using only Resolve\'92s supported intrinsics.                        |\
\
---\
\
## Notes\
- Follows Resolve DCTL conventions (`DEFINE_UI_PARAMS`, `_powf`, `_fminf`, `_fmaxf`, etc.).  \
- Mirrors examples from **GainDCTLPlugin.dctl** (sliders/checkboxes) and **ColorPicker.dctl** (tooltips).  \
- Requirement IDs are stable anchors for specs, tests, and commits.  }

# Project Requirements Document (PRD)  
**Project:** FadedBalancerOFX.dctl  
**Owner:** Fabio Bedoya  
**Goal:** Provide a Resolve OFX tool for balancing faded film scans through per-channel controls, channel operations, and preservation-oriented workflows.

---

## 1. Problem Statement
Film stocks often fade (commonly toward magenta), making restoration difficult. Current tools are either too generic or too destructive. We need a lightweight, reproducible solution tailored to film restoration workflows.

---

## 2. Users & Expected Outcomes

| User Type                | Goal                                                                 | Expected Outcome                                                                 |
|---------------------------|----------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Film restoration techs    | Quickly rebalance faded footage (magenta/blue/green shifts).         | Corrected neutral balance while preserving texture and grain.                    |
| Colorists                | Fine-tune per-channel lift/gamma/gain/offset.                        | Flexible control over channel curves within Resolve.                             |
| Archivists               | Apply corrections non-destructively in workflows.                    | Archival-safe balance for digitized footage.                                     |
| Researchers              | Test chroma behavior of faded stocks in controlled ways.             | Repeatable experiments with consistent results.                                  |

---

## 3. Success Metrics
- ✅ All operations reversible in Resolve.
- ✅ Full per-channel control with normalized ranges.
- ✅ Separate UI sections for balance, copy, and removal.
- ✅ Handles edge cases (channel loss, extreme fades).
- ✅ Lightweight (no external libraries).

---

## 4. Deliverables
- One DCTL plugin (`FadedBalancerOFX.dctl`).
- Documentation set:
  - SPECIFICATION.md
  - API.md
  - EDGECASES.md
  - TESTS.md
  - CODING_GUIDE.md

---