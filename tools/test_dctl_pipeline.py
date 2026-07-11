#!/usr/bin/env python3
"""Adversarial numerical audit tests for the complete Faded Balancer pipeline."""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DCTL_PATH = ROOT / "FadedBalancerDCTL.dctl"
F32 = np.float32
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)


def signed_pow(value: np.ndarray, exponent: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float32)
    exponent = np.asarray(exponent, dtype=np.float32)
    if np.all(np.abs(exponent - F32(1.0)) <= F32(1e-7)):
        return value.copy()
    with np.errstate(over="ignore", invalid="ignore"):
        magnitude = np.power(np.abs(value), exponent)
    result = np.copysign(magnitude, value).astype(np.float32)
    return np.where(np.isfinite(result), result, value).astype(np.float32)


def lggo(
    rgb: np.ndarray,
    offset: np.ndarray | float = 0.0,
    lift: np.ndarray | float = 0.0,
    gamma: np.ndarray | float = 1.0,
    gain: np.ndarray | float = 1.0,
) -> np.ndarray:
    out = np.asarray(rgb, dtype=np.float32).copy()
    out += np.asarray(offset, dtype=np.float32)
    out += np.asarray(lift, dtype=np.float32)
    out = signed_pow(out, F32(1.0) / np.asarray(gamma, dtype=np.float32))
    out *= np.asarray(gain, dtype=np.float32)
    return out


def fade_correction(rgb: np.ndarray, amount: float) -> np.ndarray:
    out = np.asarray(rgb, dtype=np.float32).copy()
    if amount <= 0.0 or not np.isfinite(amount):
        return out
    a = F32(np.clip(amount, 0.0, 1.0))
    luma = np.sum(out * LUMA, axis=-1, keepdims=True, dtype=np.float32)
    bounded = np.clip(luma, F32(0.0), F32(1.0))
    bounded_contrast = bounded * bounded * (F32(3.0) - F32(2.0) * bounded)
    contrasted = luma + (bounded_contrast - bounded)
    final_luma = luma + a * (contrasted - luma)
    saturation = F32(1.0) + a * a
    out = luma + (out - luma) * saturation
    new_luma = np.sum(out * LUMA, axis=-1, keepdims=True, dtype=np.float32)
    safe = np.abs(new_luma) > F32(1e-9)
    ratio = np.ones_like(new_luma)
    np.divide(final_luma, new_luma, out=ratio, where=safe)
    ratio = np.where(np.isfinite(ratio), ratio, F32(1.0))
    return (out * ratio).astype(np.float32)


def tonal_mask(rgb: np.ndarray, shadows: float, highlights: float) -> np.ndarray:
    image = np.asarray(rgb, dtype=np.float32)
    luma = np.sum(image * LUMA, axis=-1, dtype=np.float32)
    bounded = np.clip(luma, F32(0.0), F32(1.0))
    highlight_mask = bounded * bounded
    shadow_mask = F32(1.0) - highlight_mask
    return np.clip(
        shadow_mask * F32(shadows) + highlight_mask * F32(highlights),
        F32(0.0),
        F32(1.0),
    )


def matrix_mix(
    rgb: np.ndarray,
    coefficients: np.ndarray,
    shadows: float = 1.0,
    highlights: float = 1.0,
    donor: float = 1.0,
) -> np.ndarray:
    image = np.asarray(rgb, dtype=np.float32)
    coeff = np.asarray(coefficients, dtype=np.float32)
    donors = image * F32(donor)
    candidate = image + donors @ coeff.T
    mask = tonal_mask(image, shadows, highlights)[..., None]
    return (image + mask * (candidate - image)).astype(np.float32)


def minmax_mix(
    rgb: np.ndarray,
    darken: tuple[int, int, int] = (-1, -1, -1),
    lighten: tuple[int, int, int] = (-1, -1, -1),
    shadows: float = 1.0,
    highlights: float = 1.0,
    donor: float = 1.0,
) -> np.ndarray:
    image = np.asarray(rgb, dtype=np.float32)
    candidate = image.copy()
    donors = image * F32(donor)
    for target in range(3):
        if darken[target] >= 0:
            candidate[..., target] = np.minimum(
                candidate[..., target], donors[..., darken[target]]
            )
        if lighten[target] >= 0:
            candidate[..., target] = np.maximum(
                candidate[..., target], donors[..., lighten[target]]
            )
    mask = tonal_mask(image, shadows, highlights)[..., None]
    return (image + mask * (candidate - image)).astype(np.float32)


def preserve_luma(before: np.ndarray, after: np.ndarray) -> np.ndarray:
    before = np.asarray(before, dtype=np.float32)
    out = np.asarray(after, dtype=np.float32).copy()
    pre = np.sum(before * LUMA, axis=-1, keepdims=True, dtype=np.float32)
    post = np.sum(out * LUMA, axis=-1, keepdims=True, dtype=np.float32)
    safe = np.abs(post) > F32(1e-9)
    ratio = np.ones_like(post)
    np.divide(pre, post, out=ratio, where=safe)
    ratio = np.where(np.isfinite(ratio), ratio, F32(1.0))
    return (out * ratio).astype(np.float32)


def replace_channels(rgb: np.ndarray, sources: tuple[int, int, int]) -> np.ndarray:
    source = np.asarray(rgb, dtype=np.float32)
    out = source.copy()
    for target, donor in enumerate(sources):
        if donor >= 0:
            out[..., target] = source[..., donor]
    return out


def remove_channels(rgb: np.ndarray, mode: int) -> np.ndarray:
    out = np.asarray(rgb, dtype=np.float32).copy()
    if mode in (1, 4):
        out[..., 0] = 0.0
    if mode in (2, 4):
        out[..., 1] = 0.0
    if mode in (3, 4):
        out[..., 2] = 0.0
    return out


def isolate_channel(rgb: np.ndarray, mode: int) -> np.ndarray:
    out = np.asarray(rgb, dtype=np.float32).copy()
    if mode in (1, 2, 3):
        channel = out[..., mode - 1]
        out = np.stack((channel, channel, channel), axis=-1)
    return out


def diagnostic_log(rgb: np.ndarray) -> np.ndarray:
    image = np.asarray(rgb, dtype=np.float32)
    positive = np.maximum(image, F32(0.0))
    return (F32(1.0) - F32(1.0) / (F32(1.0) + positive)).astype(np.float32)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _close(actual: np.ndarray | float, expected: np.ndarray | float, tol: float = 3e-6) -> None:
    _require(
        bool(np.allclose(actual, expected, rtol=0.0, atol=tol)),
        f"expected {expected!r}, got {actual!r}",
    )


def test_source_contract() -> str:
    source = DCTL_PATH.read_text()
    required = (
        "__DEVICE__ float safeSignedPow",
        "__DEVICE__ float mixingTonalMask",
        "float3 matrixDonors = rgb * donorLuminanceAdjust_l;",
        "rgb = _mix(rgb, matrixCandidate, matrixMask);",
        "float3 replaceSource = rgb;",
        "__DEVICE__ float diagnosticLogPreview",
        "🧩 Preset Tonal Only",
        "Legacy additive lift; same response as Offset",
        "not a Cineon or delivery transform",
    )
    for snippet in required:
        _require(snippet in source, f"missing audited source contract: {snippet}")

    identifiers = re.findall(r"DEFINE_UI_PARAMS\(\s*([A-Za-z_]\w*)\s*,", source)
    _require(len(identifiers) >= 46, f"expected at least 46 UI controls, found {len(identifiers)}")
    for identifier in identifiers:
        _require(source.count(identifier) >= 2, f"UI control appears unwired: {identifier}")
    return f"{len(identifiers)} UI controls are wired; audited helpers and honest labels exist"


def test_default_full_float_identity() -> str:
    values = np.array(
        [
            [-4.0, -0.1, 0.0],
            [-1e-7, 1e-7, 0.18],
            [0.25, 0.5, 1.0],
            [1.2, 2.0, 4.0],
        ],
        dtype=np.float32,
    )
    out = lggo(values)
    out = fade_correction(out, 0.0)
    out = lggo(out)
    out = matrix_mix(out, np.zeros((3, 3), dtype=np.float32))
    out = minmax_mix(out)
    out = replace_channels(out, (-1, -1, -1))
    out = remove_channels(out, 0)
    out = isolate_channel(out, 0)
    _require(np.array_equal(out, values), "neutral full pipeline is not bitwise identity")
    return "negative, zero, normalized, and super-white RGB remain bitwise identical"


def test_signed_gamma_and_legacy_lift() -> str:
    pixel = np.array([-0.25, 0.25, 1.25], dtype=np.float32)
    gamma = lggo(pixel, gamma=2.0)
    _require(np.isfinite(gamma).all(), "signed gamma generated NaN/Inf")
    _require(gamma[0] < 0.0 and gamma[1] > 0.0, "signed gamma lost channel sign")
    offset = lggo(pixel, offset=0.1)
    lift = lggo(pixel, lift=0.1)
    _require(np.array_equal(offset, lift), "legacy Lift no longer matches documented additive behavior")
    huge = np.array(
        [np.finfo(np.float32).max, -np.finfo(np.float32).max, 1.0],
        dtype=np.float32,
    )
    guarded = lggo(huge, gamma=0.1)
    _require(np.isfinite(guarded).all(), "signed gamma overflow escaped the finite-input guard")
    _require(np.array_equal(guarded[:2], huge[:2]), "overflow guard did not fail safe to input")
    return "Gamma is signed/full-float safe with overflow fallback; legacy Lift remains explicit additive compatibility math"


def test_fade_is_monotonic_and_full_float_safe() -> str:
    values = np.array([-2.0, -1.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0], dtype=np.float32)
    gray = np.stack((values, values, values), axis=1)
    out = fade_correction(gray, 1.0)[:, 0]
    _require(np.isfinite(out).all(), "Fade Correction generated NaN/Inf")
    _require(bool(np.all(np.diff(out) >= 0.0)), "Fade Correction is not monotonic")
    _close(out[values < 0.0], values[values < 0.0])
    _close(out[values > 1.0], values[values > 1.0])
    _close(out[values == 0.5], np.array([0.5], dtype=np.float32))
    return "bounded contrast is monotonic from -2 to 4 and preserves below-black/super-white excursions"


def test_matrix_uses_masks_and_donor() -> str:
    pixel = np.array([0.2, 0.4, 0.8], dtype=np.float32)
    coeff = np.zeros((3, 3), dtype=np.float32)
    coeff[0, 1] = 0.5
    default = matrix_mix(pixel, coeff)
    _close(default, np.array([0.4, 0.4, 0.8], dtype=np.float32))
    donor = matrix_mix(pixel, coeff, donor=2.0)
    _close(donor, np.array([0.6, 0.4, 0.8], dtype=np.float32))
    disabled = matrix_mix(pixel, coeff, shadows=0.0, highlights=0.0, donor=3.0)
    _require(np.array_equal(disabled, pixel), "zero tonal weights did not disable matrix mixing")
    shadow = matrix_mix(pixel, coeff, shadows=1.0, highlights=0.0)
    highlight = matrix_mix(pixel, coeff, shadows=0.0, highlights=1.0)
    _require(not np.array_equal(shadow, highlight), "shadow/highlight matrix weights are disconnected")
    return "matrix coefficients respond to donor scale and both tonal weights"


def test_minmax_uses_masks_and_donor() -> str:
    pixel = np.array([0.8, 0.3, 0.6], dtype=np.float32)
    dark = minmax_mix(pixel, darken=(1, -1, -1))
    _close(dark, np.array([0.3, 0.3, 0.6], dtype=np.float32))
    adjusted = minmax_mix(pixel, darken=(1, -1, -1), donor=2.0)
    _close(adjusted, np.array([0.6, 0.3, 0.6], dtype=np.float32))
    disabled = minmax_mix(
        pixel, darken=(1, -1, -1), shadows=0.0, highlights=0.0
    )
    _require(np.array_equal(disabled, pixel), "zero tonal weights did not disable min/max mixing")
    return "Darken/Lighten donor scaling and tonal weighting match the UI contract"


def test_preserve_luma_scope() -> str:
    before = np.array([[0.2, 0.5, 0.8], [-0.2, 0.1, 0.4]], dtype=np.float32)
    after = lggo(before, offset=np.array([0.2, -0.1, 0.05], dtype=np.float32))
    preserved = preserve_luma(before, after)
    pre_luma = np.sum(before * LUMA, axis=-1)
    post_luma = np.sum(preserved * LUMA, axis=-1)
    _close(post_luma, pre_luma, tol=2e-6)
    return "Rec.709-weighted luma is restored across the per-channel stage, including signed values"


def test_replacements_are_simultaneous() -> str:
    pixel = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    swapped = replace_channels(pixel, (1, 0, -1))
    _close(swapped, np.array([0.2, 0.1, 0.3], dtype=np.float32))
    rotated = replace_channels(pixel, (1, 2, 0))
    _close(rotated, np.array([0.2, 0.3, 0.1], dtype=np.float32))
    return "multi-channel Replace reads one snapshot and supports predictable swaps/rotations"


def test_removal_and_preview() -> str:
    pixel = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    _close(remove_channels(pixel, 1), np.array([0.0, 0.2, 0.3], dtype=np.float32))
    _close(remove_channels(pixel, 4), np.zeros(3, dtype=np.float32))
    _close(isolate_channel(pixel, 2), np.array([0.2, 0.2, 0.2], dtype=np.float32))
    return "Removal zeros the selected channels and Preview produces grayscale channel isolation"


def test_diagnostic_log_is_honest_and_monotonic() -> str:
    values = np.array([-2.0, 0.0, 0.1, 1.0, 4.0, 100.0], dtype=np.float32)
    gray = np.stack((values, values, values), axis=1)
    out = diagnostic_log(gray)[:, 0]
    _require(np.isfinite(out).all(), "diagnostic log generated NaN/Inf")
    _require(bool(np.all(np.diff(out) >= 0.0)), "diagnostic log is not monotonic")
    _close(out[0], 0.0)
    _close(out[1], 0.0)
    _close(out[3], 0.5)
    _require(0.9 < out[-1] < 1.0, "large positive value was hard-clipped")
    return "preview is monotonic positive compression, maps 1 to 0.5, and is explicitly non-Cineon"


def test_random_pipeline_finite() -> str:
    rng = np.random.default_rng(170)
    for _ in range(300):
        image = rng.uniform(-4.0, 4.0, (31, 3)).astype(np.float32)
        out = lggo(
            image,
            rng.uniform(-0.5, 0.5, 3).astype(np.float32),
            rng.uniform(-0.5, 0.5, 3).astype(np.float32),
            rng.uniform(0.1, 3.0, 3).astype(np.float32),
            rng.uniform(0.1, 3.0, 3).astype(np.float32),
        )
        out = fade_correction(out, float(rng.uniform(0.0, 1.0)))
        before_channels = out.copy()
        out = lggo(
            out,
            rng.uniform(-0.5, 0.5, 3).astype(np.float32),
            rng.uniform(-0.5, 0.5, 3).astype(np.float32),
            rng.uniform(0.1, 3.0, 3).astype(np.float32),
            rng.uniform(0.1, 3.0, 3).astype(np.float32),
        )
        if rng.integers(0, 2):
            out = preserve_luma(before_channels, out)
        coeff = rng.uniform(-2.0, 2.0, (3, 3)).astype(np.float32)
        np.fill_diagonal(coeff, 0.0)
        shadows, highlights = rng.uniform(0.0, 1.0, 2)
        donor = float(rng.uniform(0.1, 3.0))
        out = matrix_mix(out, coeff, float(shadows), float(highlights), donor)
        out = minmax_mix(out, shadows=float(shadows), highlights=float(highlights), donor=donor)
        out = replace_channels(out, (-1, -1, -1))
        _require(np.isfinite(out).all(), "finite randomized controls generated NaN/Inf")
    return "300 randomized full-float pipelines remain finite"


Test = Callable[[], str]
TESTS: tuple[tuple[str, Test], ...] = (
    ("source/UI contract", test_source_contract),
    ("default full-float identity", test_default_full_float_identity),
    ("signed Gamma and legacy Lift", test_signed_gamma_and_legacy_lift),
    ("Fade full-float safety", test_fade_is_monotonic_and_full_float_safe),
    ("matrix masks/donor", test_matrix_uses_masks_and_donor),
    ("minmax masks/donor", test_minmax_uses_masks_and_donor),
    ("Preserve Luminance scope", test_preserve_luma_scope),
    ("simultaneous Replace", test_replacements_are_simultaneous),
    ("Removal and Preview", test_removal_and_preview),
    ("diagnostic log", test_diagnostic_log_is_honest_and_monotonic),
    ("random full pipeline", test_random_pipeline_finite),
)


def main() -> int:
    failures: list[tuple[str, str]] = []
    print(f"DCTL pipeline audit tests: {DCTL_PATH}")
    for name, test in TESTS:
        started = time.perf_counter()
        try:
            detail = test()
        except Exception as exc:
            elapsed = (time.perf_counter() - started) * 1000.0
            failures.append((name, str(exc)))
            print(f"FAIL  {name:<30} {elapsed:7.1f} ms  {exc}")
        else:
            elapsed = (time.perf_counter() - started) * 1000.0
            print(f"PASS  {name:<30} {elapsed:7.1f} ms  {detail}")
    print(f"\nSummary: {len(TESTS) - len(failures)}/{len(TESTS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
