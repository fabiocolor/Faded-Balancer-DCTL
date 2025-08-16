---

# 📄 EDGECASES.md (Rules)

```markdown
# Edge Cases & Rules

1. **Channel Loss**  
   - If a channel is fully faded, use `Copy` before applying balance.

2. **Double Toggle**  
   - If both Copy and Remove are active for the same channel, *Removal wins*.

3. **Extreme Input Values**  
   - Clamp all outputs to [0,1].

4. **Neutralization First**  
   - Auto black/white pickers (future) must apply before any other adjustments.

5. **Disabled Sections**  
   - Disabled toggles must fully bypass that section.

---
---

## 📄 `EDGECASES.md` (update)
```md
# Edge Cases

- UI parameters must remain within ranges set in `DEFINE_UI_PARAMS`.
- Sliders default and step sizes follow BMD conventions (see GainDCTLPlugin).
- Tooltips (optional) are only supported in Resolve 19.1+ (see ColorPicker example).
- Max controls: 64 per UI type, enforced by Resolve.

---

## 📄 `EDGECASES.md`
```md
# Edge Cases & Rules

- **Pipeline is fixed**: Global → Fade → Per-Channel (+Preserve Luma) → Mix → Replace → Removal → Output.  
- **Preserve Luminance**: applied only after per-channel ops, not global or later stages.  
- **Midtones**: constrain to [0.1..3.0] → prevents unstable `_powf`.  
- **No final clamp**: allow values outside [0..1], handled by grading later.  
- **Mix conflicts**: each Darken/Lighten acts independently. Implementation: `_fminf`/`_fmaxf`.  
- **Replace conflicts**: process R→G→B in fixed order to avoid recursion.  
- **Removal precedence**: Removal zeroes channels after Replace regardless of earlier settings.  
- **Cineon output**: applied last, per-channel only.  
- **UI Limits**: ≤64 controls per type.  
- **Float literals**: must end with `f` (e.g., `0.5f`).  

# Edge Cases & Determinism

- **Order is fixed**: Global → Fade → Per-Channel (→ Pres. Luma) → Mix → Replace → Removal → Output.
- **Preserve Luminance** only normalizes after per-channel; it does not affect Global or later stages.
- **Midtones extremes**: keep within [0.1..3.0] to avoid unstable pow().
- **No final clamp**: values may exceed [0..1] by design; grading downstream must handle ranges.
- **Mix conflicts**: multiple Darken/Lighten selections apply independently on each channel (pure min/max).
- **Replace conflicts**: each channel has at most one source; process order is R→G→B in code to remain stable.
- **Removal precedence**: Removal zeroes channels after Replace regardless of earlier settings.
- **Cineon output**: applied last; no gamut or matrix transforms, per-channel only.

