#!/usr/bin/env python3
"""Validate the presets embedded in ``FadedBalancerDCTL.dctl``.

The DCTL is the only authoritative preset source.  ``presets/presets.json`` is
kept as a deprecation pointer for old links and is deliberately not a preset
database.

The validator checks:

* the ten preset selector entries and their ten implementation blocks;
* every embedded preset numeric against the live DCTL slider range;
* finite UI defaults, bounds, steps, and preset values;
* combo-box value/label mappings where the symbols are locally defined; and
* one documentation heading for every visible preset label.

Usage::

    python3 tools/validate_presets.py
    python3 tools/validate_presets.py presets/presets.json

This script is read-only and uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DCTL = ROOT / "FadedBalancerDCTL.dctl"
DEFAULT_MANIFEST = ROOT / "presets" / "presets.json"
DEFAULT_DOCS = ROOT / "docs" / "presets_companion.md"

PRESET_COUNT = 10
PRESET_SYMBOLS = tuple(f"PRESET_EASTMAN{index}" for index in range(1, 11))
PRESET_NUMERIC_FIELDS = (
    "p_globalOffset",
    "p_globalShadows",
    "p_globalMidtones",
    "p_globalHighlights",
    "p_redOffset",
    "p_redShadows",
    "p_redMidtones",
    "p_redHighlights",
    "p_greenOffset",
    "p_greenShadows",
    "p_greenMidtones",
    "p_greenHighlights",
    "p_blueOffset",
    "p_blueShadows",
    "p_blueMidtones",
    "p_blueHighlights",
)

FLOAT_LITERAL = re.compile(
    r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?[fF]?$"
)


@dataclass(frozen=True)
class Slider:
    identifier: str
    default: float
    minimum: float
    maximum: float
    step: float


@dataclass(frozen=True)
class Combo:
    identifier: str
    default: int
    symbols: tuple[str, ...]
    labels: tuple[str, ...]


@dataclass
class Results:
    errors: list[str]
    warnings: list[str]
    notes: list[str]

    @classmethod
    def create(cls) -> "Results":
        return cls(errors=[], warnings=[], notes=[])

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)


def strip_comments(text: str) -> str:
    """Remove DCTL/C comments while preserving strings and line boundaries."""

    text = re.sub(r"/\*.*?\*/", lambda match: "\n" * match.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def split_top_level(text: str) -> list[str]:
    """Split a macro argument list without splitting nested braces/parens."""

    parts: list[str] = []
    start = 0
    paren_depth = 0
    brace_depth = 0
    in_string = False
    escaped = False

    for index, character in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue

        if character == '"':
            in_string = True
        elif character == "(":
            paren_depth += 1
        elif character == ")":
            paren_depth -= 1
        elif character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth -= 1
        elif character == "," and paren_depth == 0 and brace_depth == 0:
            parts.append(text[start:index].strip())
            start = index + 1

    parts.append(text[start:].strip())
    return parts


def extract_macro_calls(text: str, macro: str) -> list[str]:
    """Return the contents of every balanced ``MACRO(...)`` invocation."""

    calls: list[str] = []
    marker = f"{macro}("
    cursor = 0

    while True:
        start = text.find(marker, cursor)
        if start < 0:
            return calls

        body_start = start + len(marker)
        depth = 1
        in_string = False
        escaped = False
        index = body_start

        while index < len(text) and depth:
            character = text[index]
            if in_string:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == '"':
                    in_string = False
            elif character == '"':
                in_string = True
            elif character == "(":
                depth += 1
            elif character == ")":
                depth -= 1
            index += 1

        if depth:
            raise ValueError(f"unterminated {macro} invocation at byte {start}")

        calls.append(text[body_start : index - 1])
        cursor = index


def extract_braced_block(text: str, opening_brace: int) -> str:
    depth = 0
    for index in range(opening_brace, len(text)):
        character = text[index]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[opening_brace + 1 : index]
    raise ValueError(f"unterminated block at byte {opening_brace}")


def parse_brace_list(token: str) -> tuple[str, ...]:
    token = token.strip()
    if not (token.startswith("{") and token.endswith("}")):
        raise ValueError(f"expected brace list, got {token!r}")
    return tuple(part.strip() for part in split_top_level(token[1:-1]))


def parse_float(token: str) -> float:
    token = token.strip()
    if not FLOAT_LITERAL.fullmatch(token):
        raise ValueError(f"not a numeric literal: {token!r}")
    value = float(token.rstrip("fF"))
    if not math.isfinite(value):
        raise ValueError(f"non-finite numeric literal: {token!r}")
    return value


def parse_integer(token: str) -> int:
    value = parse_float(token)
    if not value.is_integer():
        raise ValueError(f"not an integer literal: {token!r}")
    return int(value)


def parse_defines(text: str) -> dict[str, int]:
    return {
        name: int(value)
        for name, value in re.findall(
            r"^\s*#define\s+([A-Za-z_]\w*)\s+([+-]?\d+)\s*$",
            strip_comments(text),
            flags=re.M,
        )
    }


def parse_ui(
    text: str, results: Results
) -> tuple[dict[str, Slider], dict[str, Combo], dict[str, int]]:
    sliders: dict[str, Slider] = {}
    combos: dict[str, Combo] = {}
    checkboxes: dict[str, int] = {}
    seen: set[str] = set()

    try:
        calls = extract_macro_calls(strip_comments(text), "DEFINE_UI_PARAMS")
    except ValueError as exc:
        results.error(str(exc))
        return sliders, combos, checkboxes

    for call in calls:
        parts = split_top_level(call)
        if len(parts) < 3:
            results.error(f"malformed DEFINE_UI_PARAMS call: {call!r}")
            continue

        identifier = parts[0]
        control_type = parts[2]
        if identifier in seen:
            results.error(f"duplicate UI parameter identifier: {identifier}")
            continue
        seen.add(identifier)

        try:
            if control_type == "DCTLUI_SLIDER_FLOAT":
                if len(parts) != 7:
                    raise ValueError(f"expected 7 arguments, found {len(parts)}")
                slider = Slider(
                    identifier=identifier,
                    default=parse_float(parts[3]),
                    minimum=parse_float(parts[4]),
                    maximum=parse_float(parts[5]),
                    step=parse_float(parts[6]),
                )
                sliders[identifier] = slider
                if slider.minimum > slider.maximum:
                    results.error(f"{identifier}: minimum exceeds maximum")
                if not slider.minimum <= slider.default <= slider.maximum:
                    results.error(
                        f"{identifier}: default {slider.default:g} outside "
                        f"[{slider.minimum:g}, {slider.maximum:g}]"
                    )
                if slider.step <= 0.0:
                    results.error(f"{identifier}: step must be positive")

            elif control_type == "DCTLUI_COMBO_BOX":
                if len(parts) != 6:
                    raise ValueError(f"expected 6 arguments, found {len(parts)}")
                combos[identifier] = Combo(
                    identifier=identifier,
                    default=parse_integer(parts[3]),
                    symbols=parse_brace_list(parts[4]),
                    labels=parse_brace_list(parts[5]),
                )

            elif control_type == "DCTLUI_CHECK_BOX":
                if len(parts) != 4:
                    raise ValueError(f"expected 4 arguments, found {len(parts)}")
                value = parse_integer(parts[3])
                checkboxes[identifier] = value
                if value not in (0, 1):
                    results.error(f"{identifier}: checkbox default must be 0 or 1")

            elif control_type == "DCTLUI_COLOR_PICKER":
                if len(parts) != 6:
                    raise ValueError(f"expected 6 arguments, found {len(parts)}")
                for component in parts[3:]:
                    parse_float(component)

            else:
                results.warning(f"{identifier}: unvalidated UI type {control_type}")
        except ValueError as exc:
            results.error(f"{identifier}: {exc}")

    if not calls:
        results.error("no DEFINE_UI_PARAMS calls found")
    return sliders, combos, checkboxes


def validate_combos(
    combos: dict[str, Combo], defines: dict[str, int], results: Results
) -> None:
    unresolved: list[str] = []

    for combo in combos.values():
        if not combo.symbols or len(combo.symbols) != len(combo.labels):
            results.error(
                f"{combo.identifier}: {len(combo.symbols)} enum values but "
                f"{len(combo.labels)} labels"
            )
            continue
        if len(set(combo.symbols)) != len(combo.symbols):
            results.error(f"{combo.identifier}: duplicate enum symbols")
        if len(set(combo.labels)) != len(combo.labels):
            results.error(f"{combo.identifier}: duplicate visible labels")

        resolved = [defines.get(symbol) for symbol in combo.symbols]
        resolved_count = sum(value is not None for value in resolved)
        if resolved_count == len(resolved):
            values = [int(value) for value in resolved if value is not None]
            if values != list(range(len(values))):
                results.error(
                    f"{combo.identifier}: enum values {values} must map in order "
                    f"to 0..{len(values) - 1}"
                )
            if combo.default not in values:
                results.error(
                    f"{combo.identifier}: default {combo.default} is not an enum value"
                )
        elif resolved_count:
            missing = [
                symbol for symbol, value in zip(combo.symbols, resolved) if value is None
            ]
            results.error(
                f"{combo.identifier}: only some enum symbols resolve; missing "
                + ", ".join(missing)
            )
        else:
            # Resolve can emit bare enum identifiers for a combo.  Their numeric
            # values are not visible to this source-only validator, but the
            # default still has to be a valid option index.
            if not 0 <= combo.default < len(combo.symbols):
                results.error(
                    f"{combo.identifier}: default index {combo.default} outside "
                    f"0..{len(combo.symbols) - 1}"
                )
            unresolved.append(combo.identifier)

    if unresolved:
        results.note(
            "Resolve-generated combo symbols checked by order/arity only: "
            + ", ".join(unresolved)
        )


def find_preset_blocks(text: str, results: Results) -> dict[str, str]:
    clean = strip_comments(text)
    pattern = re.compile(
        r"\bif\s*\(\s*presetMode\s*==\s*(PRESET_EASTMAN\d+)\s*\)\s*\{"
    )
    blocks: dict[str, str] = {}

    for match in pattern.finditer(clean):
        symbol = match.group(1)
        if symbol in blocks:
            results.error(f"duplicate implementation block for {symbol}")
            continue
        try:
            blocks[symbol] = extract_braced_block(clean, match.end() - 1)
        except ValueError as exc:
            results.error(f"{symbol}: {exc}")

    found = set(blocks)
    expected = set(PRESET_SYMBOLS)
    for symbol in sorted(expected - found):
        results.error(f"missing implementation block for {symbol}")
    for symbol in sorted(found - expected):
        results.error(f"unexpected implementation block for {symbol}")
    if len(blocks) != PRESET_COUNT:
        results.error(
            f"expected exactly {PRESET_COUNT} preset blocks, found {len(blocks)}"
        )
    return blocks


def validate_preset_selector(
    combos: dict[str, Combo], defines: dict[str, int], results: Results
) -> tuple[str, ...]:
    selector = combos.get("presetMode")
    if selector is None:
        results.error("missing presetMode combo selector")
        return ()

    expected_symbols = ("PRESET_NONE",) + PRESET_SYMBOLS
    if selector.symbols != expected_symbols:
        results.error(
            "presetMode enum order must be PRESET_NONE followed by "
            "PRESET_EASTMAN1..PRESET_EASTMAN10"
        )
    if len(selector.labels) != PRESET_COUNT + 1:
        results.error(
            f"presetMode must expose None plus exactly {PRESET_COUNT} presets; "
            f"found {len(selector.labels)} labels"
        )
    elif selector.labels[0] != "None":
        results.error("presetMode first visible label must be None")

    values = tuple(defines.get(symbol) for symbol in expected_symbols)
    if all(value is not None for value in values):
        if values != tuple(range(PRESET_COUNT + 1)):
            results.error("preset enum defines must map exactly to 0..10")

    return selector.labels[1:]


def validate_preset_blocks(
    blocks: dict[str, str],
    sliders: dict[str, Slider],
    combos: dict[str, Combo],
    results: Results,
) -> None:
    allowed_assignments = set(PRESET_NUMERIC_FIELDS) | {"p_blueDarkenWith"}
    blue_mix_symbols = set(combos.get("blueDarkenWith", Combo("", 0, (), ())).symbols)

    for symbol in PRESET_SYMBOLS:
        block = blocks.get(symbol)
        if block is None:
            continue

        if not re.search(r"\bpreset_applied\s*=\s*1\s*;", block):
            results.error(f"{symbol}: does not set preset_applied = 1")

        assignments: dict[str, str] = {}
        for name, expression in re.findall(
            r"\b(p_[A-Za-z_]\w*)\s*=\s*([^;]+);", block
        ):
            if name in assignments:
                results.error(f"{symbol}: duplicate assignment to {name}")
            assignments[name] = expression.strip()

        unknown = sorted(set(assignments) - allowed_assignments)
        for name in unknown:
            results.error(f"{symbol}: unknown preset field {name}")

        for field in PRESET_NUMERIC_FIELDS:
            if field not in assignments:
                results.error(f"{symbol}: missing assignment to {field}")
                continue

            try:
                value = parse_float(assignments[field])
            except ValueError as exc:
                results.error(f"{symbol} {field}: {exc}")
                continue

            ui_identifier = field.removeprefix("p_")
            slider = sliders.get(ui_identifier)
            if slider is None:
                results.error(
                    f"{symbol} {field}: no matching slider {ui_identifier}"
                )
            elif not slider.minimum <= value <= slider.maximum:
                results.error(
                    f"{symbol} {field}={value:g} outside {ui_identifier} range "
                    f"[{slider.minimum:g}, {slider.maximum:g}]"
                )

        mix_expression = assignments.get("p_blueDarkenWith")
        if mix_expression is not None and mix_expression not in blue_mix_symbols:
            results.error(
                f"{symbol}: p_blueDarkenWith uses {mix_expression!r}, which is "
                "not an option in blueDarkenWith"
            )


def normalise_heading(text: str) -> str:
    heading = text.strip().rstrip("#").strip()
    while len(heading) >= 4 and heading.startswith("**") and heading.endswith("**"):
        heading = heading[2:-2].strip()
    return heading


def validate_docs(path: Path, labels: Iterable[str], results: Results) -> None:
    if not path.is_file():
        results.error(f"preset documentation not found: {path}")
        return

    headings = [
        normalise_heading(match.group(1))
        for match in re.finditer(
            r"^#{2,6}\s+(.+?)\s*$", path.read_text(encoding="utf-8"), re.M
        )
    ]
    for label in labels:
        count = headings.count(label)
        if count == 0:
            results.error(f"docs: no heading for preset {label!r}")
        elif count > 1:
            results.error(f"docs: duplicate headings for preset {label!r}")


def validate_manifest(path: Path, results: Results) -> None:
    if not path.is_file():
        results.error(f"preset deprecation manifest not found: {path}")
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        results.error(f"cannot read {path}: {exc}")
        return

    if isinstance(data, list):
        results.error(
            f"{path}: external preset lists are deprecated; embedded DCTL "
            "preset blocks are authoritative"
        )
        return
    if not isinstance(data, dict) or not isinstance(data.get("deprecation"), dict):
        results.error(f"{path}: expected a deprecation object")
        return

    message = data["deprecation"].get("message")
    if not isinstance(message, str) or not message.strip():
        results.error(f"{path}: deprecation.message must be a non-empty string")
        return
    lowered = message.lower()
    if "authoritative" not in lowered or "fadedbalancerdctl.dctl" not in lowered:
        results.error(
            f"{path}: deprecation message must point to authoritative "
            "FadedBalancerDCTL.dctl presets"
        )
    else:
        results.note("deprecated presets/presets.json pointer accepted")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate presets embedded in FadedBalancerDCTL.dctl"
    )
    parser.add_argument(
        "manifest",
        nargs="?",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="deprecated preset JSON pointer (default: presets/presets.json)",
    )
    parser.add_argument(
        "--dctl",
        type=Path,
        default=DEFAULT_DCTL,
        help="DCTL source containing authoritative presets",
    )
    parser.add_argument(
        "--docs",
        type=Path,
        default=DEFAULT_DOCS,
        help="preset companion Markdown used for coverage checks",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = Results.create()

    if not args.dctl.is_file():
        print(f"ERROR: DCTL source not found: {args.dctl}")
        return 2

    try:
        source = args.dctl.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: cannot read {args.dctl}: {exc}")
        return 2

    defines = parse_defines(source)
    sliders, combos, _checkboxes = parse_ui(source, results)
    validate_combos(combos, defines, results)
    labels = validate_preset_selector(combos, defines, results)
    blocks = find_preset_blocks(source, results)
    validate_preset_blocks(blocks, sliders, combos, results)
    validate_docs(args.docs, labels, results)
    validate_manifest(args.manifest, results)

    version_match = re.search(r"FadedBalancerDCTL\s+v([^\s]+)", source)
    print("Faded Balancer embedded preset validation")
    print(f"  DCTL: {args.dctl}")
    if version_match:
        print(f"  source version: {version_match.group(1)}")
    print(f"  selector presets: {len(labels)}")
    print(f"  implementation blocks: {len(blocks)}")
    print(f"  sliders checked: {len(sliders)}")
    print(f"  combo boxes checked: {len(combos)}")

    for message in results.notes:
        print(f"  NOTE: {message}")
    for message in results.warnings:
        print(f"  WARNING: {message}")
    for message in results.errors:
        print(f"  ERROR: {message}")

    print(
        f"Summary: {len(results.errors)} error(s), "
        f"{len(results.warnings)} warning(s)"
    )
    return 1 if results.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
