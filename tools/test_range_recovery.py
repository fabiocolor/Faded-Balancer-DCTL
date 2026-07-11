#!/usr/bin/env python3
"""Numerical regression tests for progressive two-point channel recovery."""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Callable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DCTL_PATH = ROOT / "FadedBalancerDCTL.dctl"
F32 = np.float32

MODE_OFF = 0
MODE_AUTO = 1
MODE_RED = 2
MODE_GREEN = 3
MODE_BLUE = 4
NO_TARGET = -1

EPS = F32(1e-6)
DETECT_THRESHOLD = F32(0.02)
UNIQUE_MARGIN = F32(1e-6)


def _channel(value: np.ndarray, channel: int) -> np.ndarray:
    return value[..., channel]


def _other_mean(value: np.ndarray, channel: int) -> np.ndarray:
    peers = [index for index in range(3) if index != channel]
    return F32(0.5) * (value[..., peers[0]] + value[..., peers[1]])


def _sample_finite(sample: np.ndarray) -> bool:
    return bool(np.isfinite(sample).all())


def _dark_sample_ready(dark: np.ndarray) -> bool:
    return _sample_finite(dark) and bool(np.max(np.abs(dark)) > EPS)


def _bright_sample_ready(bright: np.ndarray) -> bool:
    return _sample_finite(bright) and bool(np.max(np.abs(bright - F32(1.0))) > EPS)


def _samples_valid(dark: np.ndarray, bright: np.ndarray) -> bool:
    return bool(
        _sample_finite(dark)
        and _sample_finite(bright)
        and np.all((bright - dark) > EPS)
    )


def _dark_candidate_score(dark: np.ndarray, channel: int) -> float:
    peers = [index for index in range(3) if index != channel]
    peer_min = F32(np.minimum(dark[peers[0]], dark[peers[1]]))
    peer_max = F32(np.maximum(dark[peers[0]], dark[peers[1]]))
    target = F32(dark[channel])
    return float(F32(np.maximum(F32(0.0), np.maximum(peer_min - target, target - peer_max))))


def dark_target(dark: np.ndarray) -> int:
    dark = np.asarray(dark, dtype=np.float32)
    if not _dark_sample_ready(dark):
        return NO_TARGET
    scores = np.array(
        [_dark_candidate_score(dark, channel) for channel in range(3)],
        dtype=np.float32,
    )
    winner = int(np.argmax(scores))
    peers = [index for index in range(3) if index != winner]
    if (
        scores[winner] > DETECT_THRESHOLD
        and scores[winner] > scores[peers[0]] + UNIQUE_MARGIN
        and scores[winner] > scores[peers[1]] + UNIQUE_MARGIN
    ):
        return winner
    return NO_TARGET


def _candidate_score(dark: np.ndarray, bright: np.ndarray, channel: int) -> float:
    span = bright - dark
    target_span = F32(span[channel])
    reference_span = F32(_other_mean(bright, channel) - _other_mean(dark, channel))
    if target_span <= EPS or reference_span <= EPS:
        return 0.0
    peers = [index for index in range(3) if index != channel]
    peer_span_min = F32(np.minimum(span[peers[0]], span[peers[1]]))
    peer_dark_min = F32(np.minimum(dark[peers[0]], dark[peers[1]]))
    peer_bright_min = F32(np.minimum(bright[peers[0]], bright[peers[1]]))
    span_margin = F32(F32(peer_span_min - target_span) / reference_span)
    dark_margin = F32(F32(peer_dark_min - dark[channel]) / reference_span)
    bright_margin = F32(F32(peer_bright_min - bright[channel]) / reference_span)
    level_margin = F32(np.minimum(dark_margin, bright_margin))
    return float(F32(np.maximum(F32(0.0), np.maximum(span_margin, level_margin))))


def auto_target(dark: np.ndarray, bright: np.ndarray) -> int:
    dark = np.asarray(dark, dtype=np.float32)
    bright = np.asarray(bright, dtype=np.float32)
    if not _samples_valid(dark, bright):
        return NO_TARGET
    scores = np.array(
        [_candidate_score(dark, bright, channel) for channel in range(3)],
        dtype=np.float32,
    )
    winner = int(np.argmax(scores))
    peers = [index for index in range(3) if index != winner]
    if (
        scores[winner] > DETECT_THRESHOLD
        and scores[winner] > scores[peers[0]] + UNIQUE_MARGIN
        and scores[winner] > scores[peers[1]] + UNIQUE_MARGIN
    ):
        return winner
    return NO_TARGET


def recover_two_point(
    rgb: np.ndarray,
    dark: np.ndarray,
    bright: np.ndarray,
    mode: int = MODE_OFF,
    strength: float = 1.0,
    maximum_gain: float = 4.0,
) -> np.ndarray:
    image = np.asarray(rgb, dtype=np.float32)
    output = image.copy()
    if mode == MODE_OFF or strength <= 0.0:
        return output

    dark = np.asarray(dark, dtype=np.float32)
    bright = np.asarray(bright, dtype=np.float32)
    controls = np.r_[dark, bright, F32(strength), F32(maximum_gain)]
    if not np.isfinite(controls).all() or not _dark_sample_ready(dark):
        return output

    bright_ready = _bright_sample_ready(bright)
    if bright_ready and not _samples_valid(dark, bright):
        return output

    if mode == MODE_AUTO:
        channel = auto_target(dark, bright) if bright_ready else dark_target(dark)
    else:
        channel = mode - 2
    if channel not in (0, 1, 2):
        return output

    target_black = dark[channel]
    reference_black = _other_mean(dark, channel)
    blend = F32(np.clip(strength, 0.0, 1.0))
    original = output[..., channel].copy()
    dark_offset = reference_black - target_black
    dark_corrected = original + dark_offset
    mapped = dark_corrected

    if bright_ready:
        target_white = bright[channel]
        reference_white = _other_mean(bright, channel)
        corrected_target_white = target_white + dark_offset
        corrected_target_span = corrected_target_white - reference_black
        reference_span = reference_white - reference_black
        if corrected_target_span <= EPS or reference_span <= EPS:
            return output

        raw_gain = reference_span / corrected_target_span
        if not np.isfinite(raw_gain) or raw_gain <= 0.0:
            return output
        gain_limit = F32(np.clip(maximum_gain, 1.0, 8.0))
        gain = np.minimum(raw_gain, gain_limit)
        mapped = reference_black + (dark_corrected - reference_black) * gain

    recovered = original + blend * (mapped - original)
    recovered = np.where(np.isfinite(recovered) | ~np.isfinite(original), recovered, original)
    output[..., channel] = recovered
    return output


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _close(actual: np.ndarray | float, expected: np.ndarray | float, tolerance: float = 2e-6) -> None:
    _require(
        bool(np.allclose(actual, expected, rtol=0.0, atol=tolerance)),
        f"expected {expected!r}, got {actual!r}",
    )


def test_source_contract() -> str:
    source = DCTL_PATH.read_text()
    required = (
        "FadedBalancerDCTL v1.7.0",
        "⚫ Step 1 Dark Neutral, DCTLUI_COLOR_PICKER, 0.0f, 0.0f, 0.0f",
        "⚪ Step 2 Bright Neutral, DCTLUI_COLOR_PICKER, 1.0f, 1.0f, 1.0f",
        "__DEVICE__ int recoveryDarkSampleReady",
        "__DEVICE__ int recoveryBrightSampleReady",
        "__DEVICE__ int recoveryDarkTargetChannel",
        "__DEVICE__ int recoveryTargetChannel",
        "__DEVICE__ float3 applyRangeRecovery",
        "float threshold = 0.02f;",
        "float correctedTargetWhite = targetWhite + darkOffset;",
        "(darkCorrectedValue - referenceBlack) * gain",
        "rangeRecoveryDark.r, rangeRecoveryDark.g, rangeRecoveryDark.b",
        "rangeRecoveryBright.r, rangeRecoveryBright.g, rangeRecoveryBright.b",
        "rangeRecoveryMode, rangeRecoveryStrength, rangeRecoveryMaxGain",
    )
    for snippet in required:
        _require(snippet in source, f"missing source contract: {snippet}")
    _require(not re.search(r"#define\s+RR_", source), "new combo identifiers must remain bare")
    stage = source.index("// --- 0. Assisted two-point faded-channel recovery")
    presets = source.index("// --- PRESET PRE-TRANSFORM")
    _require(stage < presets, "range recovery must run before presets")
    return "progressive pickers, concatenated math, host-safe combo, and Stage 0 ordering match"


def test_disabled_and_default_identity() -> str:
    rng = np.random.default_rng(1)
    image = rng.uniform(-2.0, 4.0, (17, 23, 3)).astype(np.float32)
    bad = np.array([np.nan, 1.0, 0.0], dtype=np.float32)
    off = recover_two_point(image, bad, bad, mode=MODE_OFF)
    zero = recover_two_point(
        image,
        np.zeros(3, dtype=np.float32),
        np.ones(3, dtype=np.float32),
        mode=MODE_AUTO,
        strength=0.0,
    )
    neutral = recover_two_point(
        image,
        np.zeros(3, dtype=np.float32),
        np.ones(3, dtype=np.float32),
        mode=MODE_AUTO,
    )
    _require(np.array_equal(off, image), "Off is not bitwise identity")
    _require(np.array_equal(zero, image), "Strength 0 is not bitwise identity")
    _require(np.array_equal(neutral, image), "default equal spans should not choose a target")
    return "Off, Strength 0, and default neutral samples are exact identities"


def test_dark_sample_gives_immediate_preview() -> str:
    dark = np.array([140.0, 37.0, 50.0], dtype=np.float32) / F32(255.0)
    bright_unset = np.ones(3, dtype=np.float32)
    pixels = np.array(
        [[140.0, 37.0, 50.0], [194.0, 191.0, 188.0]],
        dtype=np.float32,
    ) / F32(255.0)
    _require(dark_target(dark) == 0, "dark-only Auto did not select red")
    output = recover_two_point(pixels, dark, bright_unset, mode=MODE_AUTO)
    dark_peer_mean = F32((37.0 + 50.0) / (2.0 * 255.0))
    delta = F32((43.5 - 140.0) / 255.0)
    _close(output[0, 0], dark_peer_mean)
    _close(output[:, 0], pixels[:, 0] + delta)
    _require(np.array_equal(output[:, 1:], pixels[:, 1:]), "dark preview changed peer channels")
    return "Step 1 immediately selects red and applies the constant dark offset"


def test_dark_preview_auto_is_conservative() -> str:
    bright_unset = np.ones(3, dtype=np.float32)
    ambiguous = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    pixel = np.array([0.4, 0.5, 0.6], dtype=np.float32)
    _require(dark_target(ambiguous) == NO_TARGET, "tied dark extremes selected a target")
    output = recover_two_point(pixel, ambiguous, bright_unset, mode=MODE_AUTO)
    _require(np.array_equal(output, pixel), "ambiguous dark-only Auto changed the pixel")

    dominant = np.array([0.55, 0.15, 0.19], dtype=np.float32)
    for shift in range(3):
        d = np.roll(dominant, shift)
        expected = shift
        _require(dark_target(d) == expected, f"wrong dark-only target for shift {shift}")
    return "dark-only Auto rejects ties and identifies one clear RGB outlier symmetrically"


def test_full_recovery_concatenates_dark_then_bright() -> str:
    dark = np.array([140.0, 37.0, 50.0], dtype=np.float32) / F32(255.0)
    bright = np.array([194.0, 191.0, 188.0], dtype=np.float32) / F32(255.0)
    pixels = np.stack((dark, bright), axis=0)
    output = recover_two_point(pixels, dark, bright, mode=MODE_AUTO)

    channel = 0
    reference_black = F32(_other_mean(dark, channel))
    reference_white = F32(_other_mean(bright, channel))
    dark_offset = F32(reference_black - dark[channel])
    stage_one = pixels.copy()
    stage_one[:, channel] += dark_offset
    corrected_bright = F32(bright[channel] + dark_offset)
    gain = F32((reference_white - reference_black) / (corrected_bright - reference_black))
    expected = stage_one.copy()
    expected[:, channel] = reference_black + (
        stage_one[:, channel] - reference_black
    ) * gain

    _close(output, expected)
    _close(output[0, channel], reference_black)
    _close(output[1, channel], reference_white)
    _close(gain, F32(146.0 / 54.0))
    return "raw bright picker is dark-corrected internally; both OBSESSION anchors concatenate exactly"


def test_random_single_dctl_matches_two_stage_oracle() -> str:
    rng = np.random.default_rng(122)
    for _ in range(300):
        channel = int(rng.integers(0, 3))
        peers = [index for index in range(3) if index != channel]
        dark = rng.uniform(0.02, 0.25, 3).astype(np.float32)
        peer_spans = rng.uniform(0.4, 0.75, 2).astype(np.float32)
        target_span = F32(rng.uniform(0.15, float(np.min(peer_spans)) * 0.8))
        bright = dark.copy()
        bright[peers[0]] += peer_spans[0]
        bright[peers[1]] += peer_spans[1]
        bright[channel] += target_span
        pixels = rng.uniform(-0.5, 1.5, (17, 3)).astype(np.float32)

        reference_black = F32(_other_mean(dark, channel))
        reference_white = F32(_other_mean(bright, channel))
        dark_offset = F32(reference_black - dark[channel])
        stage_one = pixels.copy()
        stage_one[:, channel] += dark_offset
        corrected_bright = F32(bright[channel] + dark_offset)
        gain = F32((reference_white - reference_black) / (corrected_bright - reference_black))
        maximum_gain = float(max(F32(1.0), gain + F32(0.25)))
        oracle = stage_one.copy()
        oracle[:, channel] = reference_black + (
            stage_one[:, channel] - reference_black
        ) * gain

        output = recover_two_point(
            pixels, dark, bright, channel + 2, 1.0, maximum_gain
        )
        _close(output, oracle, tolerance=3e-6)
    return "300 random RGB cases match explicit dark-offset then pivoted-white composition"


def test_host_fixture_recovers_red() -> str:
    dark = np.array([0.1875, 0.125, 0.125], dtype=np.float32)
    bright = np.array([0.5625, 0.875, 0.875], dtype=np.float32)
    damaged = np.array([[0.1875, 0.125, 0.125], [0.375, 0.5, 0.5], [0.5625, 0.875, 0.875]], dtype=np.float32)
    expected = np.array([[0.125, 0.125, 0.125], [0.5, 0.5, 0.5], [0.875, 0.875, 0.875]], dtype=np.float32)
    _require(auto_target(dark, bright) == 0, "Auto did not select red")
    output = recover_two_point(damaged, dark, bright, mode=MODE_AUTO)
    _close(output, expected)
    return "Auto selects red; dark/mid/bright map to 0.125/0.500/0.875"


def test_auto_channel_permutations() -> str:
    dark = np.array([0.1875, 0.125, 0.125], dtype=np.float32)
    bright = np.array([0.5625, 0.875, 0.875], dtype=np.float32)
    pixel = np.array([0.375, 0.5, 0.5], dtype=np.float32)
    for shift in range(3):
        d = np.roll(dark, shift)
        b = np.roll(bright, shift)
        p = np.roll(pixel, shift)
        target = shift
        _require(auto_target(d, b) == target, f"wrong Auto target for shift {shift}")
        output = recover_two_point(p, d, b, mode=MODE_AUTO)
        _close(output[target], 0.5)
        for channel in range(3):
            if channel != target:
                _require(output[channel] == p[channel], "non-target channel changed")
    return "Auto recovers compacted red, green, and blue symmetrically"


def test_offset_low_channel() -> str:
    dark = np.array([0.02, 0.10, 0.10], dtype=np.float32)
    bright = np.array([0.82, 0.90, 0.90], dtype=np.float32)
    pixel = np.array([0.42, 0.50, 0.50], dtype=np.float32)
    _require(auto_target(dark, bright) == 0, "offset-low channel was not detected")
    output = recover_two_point(pixel, dark, bright, mode=MODE_AUTO)
    _close(output, np.array([0.50, 0.50, 0.50], dtype=np.float32))
    return "equal-span red shifted low is lifted by 0.08"


def test_ambiguous_auto_is_identity() -> str:
    fixtures = (
        (np.array([0.1, 0.1, 0.1]), np.array([0.9, 0.9, 0.9])),
        (np.array([0.18, 0.18, 0.1]), np.array([0.50, 0.50, 0.9])),
        (np.array([0.1, 0.1, 0.1]), np.array([0.95, 0.8, 0.8])),
        (np.array([0.1, 0.1, 0.1]), np.array([0.884, 0.9, 0.9])),
    )
    pixel = np.array([0.3, 0.4, 0.5], dtype=np.float32)
    for dark, bright in fixtures:
        dark = dark.astype(np.float32)
        bright = bright.astype(np.float32)
        _require(auto_target(dark, bright) == NO_TARGET, "ambiguous samples selected a target")
        output = recover_two_point(pixel, dark, bright, mode=MODE_AUTO)
        _require(np.array_equal(output, pixel), "ambiguous Auto changed the pixel")
    return "ties, two damaged channels, an expanded channel, and <2% drift are rejected"


def test_manual_target_and_peer_average() -> str:
    dark = np.array([0.10, 0.18, 0.22], dtype=np.float32)
    bright = np.array([0.40, 0.76, 0.84], dtype=np.float32)
    pixels = np.array([[0.10, 0.4, 0.5], [0.25, 0.4, 0.5], [0.40, 0.4, 0.5]], dtype=np.float32)
    output = recover_two_point(pixels, dark, bright, mode=MODE_RED)
    _close(output[:, 0], np.array([0.20, 0.50, 0.80], dtype=np.float32))
    _require(np.array_equal(output[:, 1:], pixels[:, 1:]), "manual red changed peers")
    return "unequal peers average to black 0.20, white 0.80, gain 2.0"


def test_strength_is_linear() -> str:
    dark = np.array([0.10, 0.18, 0.22], dtype=np.float32)
    bright = np.array([0.40, 0.76, 0.84], dtype=np.float32)
    pixel = np.array([0.25, 0.4, 0.5], dtype=np.float32)
    expected = {0.25: 0.3125, 0.5: 0.375, 1.0: 0.5}
    for strength, red in expected.items():
        output = recover_two_point(pixel, dark, bright, MODE_RED, strength)
        _close(output[0], red)
    return "Strength produces exact 25%, 50%, and 100% interpolation"


def test_maximum_gain_black_anchor() -> str:
    dark = np.array([0.05, 0.10, 0.10], dtype=np.float32)
    bright = np.array([0.15, 0.90, 0.90], dtype=np.float32)
    pixels = np.array([[0.05, 0.2, 0.2], [0.10, 0.2, 0.2], [0.15, 0.2, 0.2]], dtype=np.float32)
    output = recover_two_point(pixels, dark, bright, MODE_RED, 1.0, 4.0)
    _close(output[:, 0], np.array([0.10, 0.30, 0.50], dtype=np.float32))
    return "8x request is capped at 4x while the black anchor remains exact"


def test_invalid_samples_fail_closed() -> str:
    image = np.array([0.3, 0.4, 0.5], dtype=np.float32)
    fixtures = (
        (np.array([0.1, 0.1, 0.1]), np.array([0.1, 0.9, 0.9])),
        (np.array([0.2, 0.1, 0.1]), np.array([0.1, 0.9, 0.9])),
        (np.array([0.1, 0.9, 0.1]), np.array([0.2, 0.8, 0.9])),
    )
    for dark, bright in fixtures:
        output = recover_two_point(image, dark.astype(np.float32), bright.astype(np.float32), MODE_RED)
        _require(np.array_equal(output, image), "invalid samples changed output")
    return "flat target and reversed target/peer spans are exact identities"


def test_nonfinite_controls_fail_closed() -> str:
    image = np.array([0.3, 0.4, 0.5], dtype=np.float32)
    dark = np.array([0.1, 0.1, 0.1], dtype=np.float32)
    bright = np.array([0.4, 0.9, 0.9], dtype=np.float32)
    for field, value in (("dark", np.nan), ("bright", np.inf)):
        d = dark.copy()
        b = bright.copy()
        (d if field == "dark" else b)[0] = value
        output = recover_two_point(image, d, b, MODE_RED)
        _require(np.array_equal(output, image), "nonfinite picker changed output")
    for strength, maximum_gain in ((np.nan, 4.0), (1.0, np.inf)):
        output = recover_two_point(image, dark, bright, MODE_RED, strength, maximum_gain)
        _require(np.array_equal(output, image), "nonfinite scalar changed output")
    return "NaN/Inf picker and scalar controls fail to identity"


def test_full_float_is_not_clipped() -> str:
    dark = np.array([0.20, 0.10, 0.10], dtype=np.float32)
    bright = np.array([0.50, 0.70, 0.70], dtype=np.float32)
    red = np.array([-1.0, 0.0, 0.5, 1.0, 2.0], dtype=np.float32)
    image = np.stack((red, np.full_like(red, 0.4), np.full_like(red, 0.4)), axis=1)
    output = recover_two_point(image, dark, bright, MODE_RED)
    _close(output[:, 0], np.array([-2.3, -0.3, 0.7, 1.7, 3.7], dtype=np.float32))
    _require(float(output[:, 0].min()) < 0.0 and float(output[:, 0].max()) > 1.0, "output was clipped")
    return "recovery itself preserves negative and super-white values"


def test_random_endpoint_mapping() -> str:
    rng = np.random.default_rng(12)
    for _ in range(200):
        dark = rng.uniform(-0.2, 0.3, 3).astype(np.float32)
        spans = rng.uniform(0.1, 0.8, 3).astype(np.float32)
        bright = dark + spans
        channel = int(rng.integers(0, 3))
        reference_span = float(_other_mean(bright, channel) - _other_mean(dark, channel))
        target_span = float(spans[channel])
        maximum_gain = max(1.0, reference_span / target_span + 0.25)
        mode = channel + 2
        endpoints = np.stack((dark, bright), axis=0)
        output = recover_two_point(endpoints, dark, bright, mode, 1.0, maximum_gain)
        _close(output[0, channel], _other_mean(dark, channel))
        _close(output[1, channel], _other_mean(bright, channel))
        peers = [index for index in range(3) if index != channel]
        _require(np.array_equal(output[:, peers], endpoints[:, peers]), "random case changed peers")
    return "200 random uncapped cases map both endpoints and preserve peers"


def test_random_finite_safety() -> str:
    rng = np.random.default_rng(21)
    for _ in range(300):
        dark = rng.uniform(-1.0, 1.0, 3).astype(np.float32)
        bright = dark + rng.uniform(1e-5, 4.0, 3).astype(np.float32)
        image = rng.uniform(-16.0, 16.0, (8, 3)).astype(np.float32)
        mode = int(rng.integers(MODE_AUTO, MODE_BLUE + 1))
        output = recover_two_point(
            image,
            dark,
            bright,
            mode,
            float(rng.uniform(0.0, 1.0)),
            float(rng.uniform(1.0, 8.0)),
        )
        _require(np.isfinite(output).all(), "finite random input generated NaN/Inf")
    return "300 random full-float cases remain finite"


Test = Callable[[], str]
TESTS: tuple[tuple[str, Test], ...] = (
    ("source contract", test_source_contract),
    ("disabled/default identity", test_disabled_and_default_identity),
    ("immediate dark preview", test_dark_sample_gives_immediate_preview),
    ("dark preview Auto", test_dark_preview_auto_is_conservative),
    ("concatenated OBSESSION", test_full_recovery_concatenates_dark_then_bright),
    ("random sequential oracle", test_random_single_dctl_matches_two_stage_oracle),
    ("controlled red recovery", test_host_fixture_recovers_red),
    ("channel permutations", test_auto_channel_permutations),
    ("offset-low detection", test_offset_low_channel),
    ("ambiguous Auto", test_ambiguous_auto_is_identity),
    ("manual target/peer mean", test_manual_target_and_peer_average),
    ("strength response", test_strength_is_linear),
    ("maximum gain", test_maximum_gain_black_anchor),
    ("invalid samples", test_invalid_samples_fail_closed),
    ("nonfinite controls", test_nonfinite_controls_fail_closed),
    ("full-float recovery", test_full_float_is_not_clipped),
    ("random endpoint mapping", test_random_endpoint_mapping),
    ("random finite safety", test_random_finite_safety),
)


def main() -> int:
    failures: list[tuple[str, str]] = []
    print(f"Range Recovery numerical tests: {DCTL_PATH}")
    for name, test in TESTS:
        started = time.perf_counter()
        try:
            detail = test()
        except Exception as exc:
            elapsed = (time.perf_counter() - started) * 1000.0
            failures.append((name, str(exc)))
            print(f"FAIL  {name:<28} {elapsed:7.1f} ms  {exc}")
        else:
            elapsed = (time.perf_counter() - started) * 1000.0
            print(f"PASS  {name:<28} {elapsed:7.1f} ms  {detail}")

    print(f"\nSummary: {len(TESTS) - len(failures)}/{len(TESTS)} passed")
    if failures:
        for name, detail in failures:
            print(f"  {name}: {detail}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
