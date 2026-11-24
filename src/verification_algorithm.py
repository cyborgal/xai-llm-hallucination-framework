"""Deterministic validation of structured scheduling availability with SWI-Prolog.

This is the *public validation component* of the published study, not the
unreleased GPT-4o experiment runner. Inputs use the example JSON schema in
examples/availability_sample.json and structured claims from parse_llm_answer.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import tempfile
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
RULES = ROOT / "prolog" / "validation_rules.pl"
DAY_NAMES = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
TIME = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _minutes(value: str) -> int:
    m = TIME.fullmatch(value)
    if not m:
        raise ValueError(f"Invalid 24-hour HH:MM time: {value!r}")
    return int(m[1]) * 60 + int(m[2])


def normalize_availability(value: dict[str, Any]) -> dict[str, list[str]]:
    """Accept either documented sample 'slots' schema or day-to-spans mapping."""
    if "slots" in value:
        result: dict[str, list[str]] = {}
        for item in value["slots"]:
            day = str(item["day"]).lower()
            if day not in DAY_NAMES:
                raise ValueError(f"Unknown weekday: {day}")
            for window in item["windows"]:
                start, end = window["start"], window["end"]
                _minutes(start)
                _minutes(end)
                result.setdefault(day, []).append(f"{start}-{end}")
        return result
    result = {}
    for day_name, spans in value.items():
        day = day_name.lower()
        if day not in DAY_NAMES:
            raise ValueError(f"Unknown weekday: {day}")
        result[day] = list(spans)
    return result


def facts_from_availability(value: dict[str, Any]) -> str:
    lines: list[str] = []
    for day, spans in normalize_availability(value).items():
        for span in spans:
            parts = re.split(r"\s*[-–—]\s*", span)
            if len(parts) != 2:
                raise ValueError(f"Bad availability interval: {span!r}")
            start, end = map(_minutes, parts)
            if not start < end:
                raise ValueError(f"Invalid availability interval: {span!r}")
            # Module qualification makes facts visible to the module predicates.
            lines.append(f'validation_rules:available_slot("-", {day}, "{parts[0]}", {start}, {end}).')
    return "\n".join(lines) + "\n"


def verify_claim(availability: dict[str, Any], claim: dict[str, Any]) -> dict[str, Any]:
    """Return is_valid and reason, checking an *affirmative* scheduling claim.

    Missing day/time is rejected rather than silently treated as unavailable.
    This does not verify negative natural-language claims without extra parsing.
    """
    day = claim.get("day")
    time = claim.get("time")
    ambiguous = claim.get("ambiguous")
    if day not in DAY_NAMES or bool(time) == bool(ambiguous):
        raise ValueError("Claim needs a valid lower-case day and exactly one of time/ambiguous")
    if time:
        _minutes(time)
        request = f'exact_time("{time}")'
    else:
        if ambiguous not in ("morning", "afternoon", "evening"):
            raise ValueError("Unknown ambiguous time window")
        request = f"ambiguous({ambiguous})"
    if shutil.which("swipl") is None:
        raise RuntimeError("SWI-Prolog is required; install swipl and retry")

    rules_path = str(RULES.resolve()).replace("\\", "/").replace("'", "''")
    prolog_source = (
        f":- use_module('{rules_path}').\n"
        + facts_from_availability(availability)
        + f":- initialization((validation_rules:validate_answer({day}, {request}, V, R), "
        + "validation_rules:json_out(V, R)), main).\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "validation_run.pl"
        script.write_text(prolog_source, encoding="utf-8")
        proc = subprocess.run(
            ["swipl", "-q", "-f", str(script), "-t", "halt"],
            cwd=ROOT, capture_output=True, text=True, timeout=20, check=False,
        )
    if proc.returncode != 0:
        raise RuntimeError(f"SWI-Prolog failed: {proc.stderr.strip()}")
    try:
        result = json.loads(proc.stdout.strip())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid Prolog JSON output: {proc.stdout!r}") from exc
    if not isinstance(result.get("is_valid"), bool):
        raise RuntimeError(f"Unexpected Prolog verdict: {result!r}")
    return result
