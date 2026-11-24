"""Public-validator regression tests. Run: python -m pytest -q"""
import json
import pathlib
import shutil
import pytest

from src.prompt_parsing import parse_llm_answer, parse_query
from src.verification_algorithm import facts_from_availability, normalize_availability, verify_claim

ROOT = pathlib.Path(__file__).resolve().parents[1]
SAMPLE = json.loads((ROOT / "examples/availability_sample.json").read_text())


def test_sample_schema_is_normalized():
    assert normalize_availability(SAMPLE) == {
        "thursday": ["09:00-12:00"], "friday": ["13:00-16:00"]
    }


def test_facts_prolog_module_qualified():
    text = facts_from_availability(SAMPLE)
    assert 'validation_rules:available_slot("-", thursday, "09:00", 540, 720).' in text
    assert 'validation_rules:available_slot("-", friday, "13:00", 780, 960).' in text


@pytest.mark.parametrize("query,kind", [
    ("Is Thursday at 10:15 AM available?", "simple"),
    ("Can we meet Thursday or Friday at 10:00 AM?", "complex"),
    ("Can we meet Thursday morning?", "edge"),
    ("Can we meet Thursday between 10:00 AM and 11:00 AM?", "complex"),
])
def test_query_classification(query, kind):
    assert parse_query(query).complexity == kind


def test_parse_affirmative_slot():
    assert parse_llm_answer("Yes, Friday at 1:30 PM is available") == {
        "day": "friday", "time": "13:30", "ambiguous": None
    }


def test_reject_negative_claim():
    with pytest.raises(ValueError, match="Negative"):
        parse_llm_answer("No, Friday at 9:30 AM is unavailable")


def test_bad_availability_rejected():
    with pytest.raises(ValueError):
        facts_from_availability({"Thursday": ["25:00-27:00"]})


@pytest.mark.skipif(shutil.which("swipl") is None, reason="SWI-Prolog not installed")
@pytest.mark.parametrize("claim,expected", [
    ({"day": "friday", "time": "13:30"}, True),
    ({"day": "friday", "time": "09:30"}, False),
    ({"day": "thursday", "time": "11:00"}, True),
    ({"day": "thursday", "time": "12:00"}, False),
    ({"day": "thursday", "ambiguous": "morning"}, True),
    ({"day": "friday", "ambiguous": "morning"}, False),
])
def test_prolog_integration(claim, expected):
    outcome = verify_claim(SAMPLE, claim)
    assert outcome["is_valid"] is expected
    assert isinstance(outcome["reason"], str)
