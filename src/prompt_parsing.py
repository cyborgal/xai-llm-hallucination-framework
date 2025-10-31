"""
Parses scheduling queries and classifies complexity:
- simple: one explicit day + one explicit exact time
- complex: multi-day OR explicit time range
- edge: ambiguous phrases (e.g., morning/evening) or insufficient structure
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

DAY_PAT = r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
TIME_PAT = r"(\d{1,2}):?(\d{2})\s*(am|pm)?"
AMBIG_PAT = r"\b(morning|afternoon|evening)\b"
RANGE_PAT = r"(between|from)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(and|to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?"

def _normalize_ampm(h:int, ampm:str|None) -> Tuple[int,int]:
    if ampm is None:
        return h, 0
    a = ampm.lower()
    if a == "am":
        return (0 if h == 12 else h), 0
    if a == "pm":
        return (12 if h == 12 else h + 12), 0
    return h, 0

def _to_minutes(h:int, m:int, ampm:Optional[str]) -> int:
    if ampm:
        H, _ = _normalize_ampm(h, ampm)
        return H * 60 + m
    return h * 60 + m

@dataclass
class ParsedQuery:
    text: str
    days: List[str]
    exact_times: List[str]            # “HH:MM” 24h
    time_ranges: List[Tuple[int,int]] # [(start_min, end_min)]
    ambiguous: List[str]              # ["morning", ...]
    complexity: str                   # "simple" | "complex" | "edge"

def classify_complexity(days, exact_times, time_ranges, ambiguous) -> str:
    if ambiguous:
        return "edge"
    multi_day = len(set(days)) > 1
    has_range = len(time_ranges) > 0
    if multi_day or has_range:
        return "complex"
    if len(days) == 1 and len(exact_times) == 1:
        return "simple"
    if len(days) == 0 or (len(exact_times) + len(time_ranges) + len(ambiguous) == 0):
        return "edge"
    return "complex"

def _extract_days(text: str) -> List[str]:
    return [m.group(1).lower() for m in re.finditer(DAY_PAT, text, flags=re.I)]

def _extract_ambiguous(text:str) -> List[str]:
    return [m.group(1).lower() for m in re.finditer(AMBIG_PAT, text, flags=re.I)]

def _extract_exact_times(text: str) -> List[str]:
    times = []
    for m in re.finditer(TIME_PAT, text, flags=re.I):
        hh = int(m.group(1))
        mm = int(m.group(2))
        ampm = m.group(3)
        mins = _to_minutes(hh, mm, ampm)
        times.append(f"{mins//60:02d}:{mins%60:02d}")
    return times

def _extract_ranges(text:str) -> List[Tuple[int,int]]:
    ranges = []
    for m in re.finditer(RANGE_PAT, text, flags=re.I):
        h1 = int(m.group(2)); m1 = int(m.group(3) or 0); a1 = m.group(4)
        h2 = int(m.group(6)); m2 = int(m.group(7) or 0); a2 = m.group(8)
        start = _to_minutes(h1, m1, a1)
        end   = _to_minutes(h2, m2, a2)
        if end < start:
            start, end = end, start
        ranges.append((start, end))
    return ranges

def parse_query(text:str) -> ParsedQuery:
    days = _extract_days(text)
    ambiguous = _extract_ambiguous(text)
    ranges = _extract_ranges(text)
    exact = _extract_exact_times(text)
    complexity = classify_complexity(days, exact, ranges, ambiguous)
    return ParsedQuery(
        text=text,
        days=days,
        exact_times=exact,
        time_ranges=ranges,
        ambiguous=ambiguous,
        complexity=complexity,
    )

PROMPT_TEMPLATE = (
    "You are a scheduling assistant. Use tools when needed. "
    "Format:\n"
    "Answer: <final answer>\n"
    "Evidence: <availability lines supporting the answer>\n"
)

def parse_llm_answer(answer:str) -> Dict[str, str]:
    day = None
    mday = re.search(DAY_PAT, answer, flags=re.I)
    if mday: day = mday.group(1).lower()

    time = None
    mt = re.search(TIME_PAT, answer, flags=re.I)
    if mt:
        hh = int(mt.group(1)); mm = int(mt.group(2)); ampm = mt.group(3)
        tmin = _to_minutes(hh, mm, ampm)
        time = f"{tmin//60:02d}:{tmin%60:02d}"

    ambiguous = None
    ma = re.search(AMBIG_PAT, answer, flags=re.I)
    if ma: ambiguous = ma.group(1).lower()

    return {"day": day, "time": time, "ambiguous": ambiguous}
