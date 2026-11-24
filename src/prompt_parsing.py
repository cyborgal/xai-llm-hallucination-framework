"""Lightweight scheduling-query classification and claim parsing.

This parser supports the examples released with JEI 25-313. It is not a
general-purpose natural language interpreter or an LLM replacement.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional

DAY_PATTERN = r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"
AMBIG_PATTERN = r"\b(?:morning|afternoon|evening)\b"
TIME_PATTERN = r"(?<!\\w)(?:0?[1-9]|1[0-2])(?::[0-5]\\d)?\\s*[ap]\\.?m\\.?\\b|(?<!\\w)(?:[01]?\\d|2[0-3]):[0-5]\\d(?!\\w)"
RANGE_PATTERN = r"\b(?:between|from)\s+(.+?)\s+(?:and|to|-)\s+(.+?)(?=$|[,?.])"


def _minutes(value: str) -> int:
    match = re.fullmatch(r"\s*(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\.?\s*", value, re.I)
    if match:
        h, m, meridiem = int(match[1]), int(match[2] or 0), match[3].lower()
        if not 1 <= h <= 12 or m > 59:
            raise ValueError(f"Invalid time: {value}")
        return ((h % 12) + (12 if meridiem == "p" else 0)) * 60 + m
    match = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*", value)
    if match:
        h, m = int(match[1]), int(match[2])
        if h <= 23 and m <= 59:
            return h * 60 + m
    raise ValueError(f"Time must include AM/PM or 24-hour HH:MM: {value!r}")


def _times(text: str) -> list[str]:
    result = []
    for match in re.finditer(TIME_PATTERN, text, re.I | re.X):
        try:
            minute = _minutes(match.group())
        except ValueError:
            continue
        result.append(f"{minute // 60:02d}:{minute % 60:02d}")
    return result


@dataclass
class ParsedQuery:
    text: str
    days: list[str]
    exact_times: list[str]
    time_ranges: list[tuple[int, int]]
    ambiguous: list[str]
    complexity: str


def parse_query(text: str) -> ParsedQuery:
    days = [m.group().lower() for m in re.finditer(DAY_PATTERN, text, re.I)]
    ambiguous = [m.group().lower() for m in re.finditer(AMBIG_PATTERN, text, re.I)]
    times = _times(text)
    ranges = []
    m = re.search(RANGE_PATTERN, text, re.I)
    if m:
        left, right = _times(m[1]), _times(m[2])
        if left and right:
            a = int(left[0][:2]) * 60 + int(left[0][3:])
            b = int(right[0][:2]) * 60 + int(right[0][3:])
            ranges.append((min(a, b), max(a, b)))
    if ambiguous:
        complexity = "edge"
    elif len(set(days)) > 1 or ranges or len(times) > 1:
        complexity = "complex"
    elif len(days) == 1 and len(times) == 1:
        complexity = "simple"
    else:
        complexity = "edge"
    return ParsedQuery(text, days, times, ranges, ambiguous, complexity)


def parse_llm_answer(answer: str) -> dict[str, Optional[str]]:
    """Extract one affirmative scheduling slot from an LLM response.

    Negative replies (e.g. 'Friday is unavailable') and replies with more
    than one candidate require a separate semantic evaluator and should
    NOT be interpreted as positive claims.
    """
    if re.search(r"\b(?:not|no|unavailable|booked|cannot|can't)\b", answer, re.I):
        raise ValueError("Negative/uncertain scheduling answer requires semantic evaluation")
    days = [m.group().lower() for m in re.finditer(DAY_PATTERN, answer, re.I)]
    times = _times(answer)
    ambiguities = [m.group().lower() for m in re.finditer(AMBIG_PATTERN, answer, re.I)]
    if len(days) != 1 or len(times) > 1 or (times and ambiguities):
        raise ValueError("A single affirmative day and time/window is required")
    if times:
        return {"day": days[0], "time": times[0], "ambiguous": None}
    if len(ambiguities) == 1:
        return {"day": days[0], "time": None, "ambiguous": ambiguities[0]}
    raise ValueError("Unable to extract an affirmative claim")
