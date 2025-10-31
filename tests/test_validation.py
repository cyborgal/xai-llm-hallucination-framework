import io
import json
import os
import pathlib
import shutil
import importlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES_DIR = ROOT / "examples"

AVAIL_FILE = EXAMPLES_DIR / "availability_sample.json"
CLAIMS_FILE = EXAMPLES_DIR / "claims_sample.jsonl"

# Try to import the project's verification module from either src/ or root.
_verif_mod = None
for mod_name in ("src.verification_algorithm", "verification_algorithm"):
    try:
        _verif_mod = importlib.import_module(mod_name)
        break
    except ModuleNotFoundError:
        continue

if _verif_mod is None:
    pytest.skip("verification_algorithm module not found in src/ or project root", allow_module_level=True)

# Find a callable that validates a single natural-language claim.
VERIFY_FN = None
for candidate in (
    "verify_availability_claim",  # preferred name in our docs
    "verify_claim",               # common alias
    "verify_tool_output"          # older name (expects structured args)
):
    if hasattr(_verif_mod, candidate):
        VERIFY_FN = getattr(_verif_mod, candidate)
        break

if VERIFY_FN is None:
    pytest.skip(
        "No verification function found in verification_algorithm "
        "(expected verify_availability_claim / verify_claim / verify_tool_output)",
        allow_module_level=True
    )

# Optional: if your pipeline shells out to SWI-Prolog, skip if swipl is missing.
if shutil.which("swipl") is None:
    pytest.skip("SWI-Prolog (swipl) not found in PATH; skipping integration tests", allow_module_level=True)


def _load_availability():
    with open(AVAIL_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _iter_claims():
    with open(CLAIMS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


@pytest.mark.parametrize("claim", list(_iter_claims()))
def test_claims_against_sample_availability(claim):
    """
    Integration-ish test: uses your verification function to evaluate each claim line
    against the sample availability. The test expects the function to return a dict
    containing a boolean field indicating validity. We support several common field
    names to keep this test tolerant to small API differences.
    """
    availability = _load_availability()

    # Accept a few result shapes (be lenient to repo variations).
    res = None
    if VERIFY_FN.__name__ == "verify_tool_output":
        # Older signature often expects (tool_result_json, llm_expected_str)
        res = VERIFY_FN(availability, claim["query"])
    else:
        res = VERIFY_FN(availability, claim["query"])

    # Normalize result -> boolean
    if isinstance(res, dict):
        if "valid" in res:
            got = bool(res["valid"])
        elif "is_valid" in res:
            got = bool(res["is_valid"])
        elif "match" in res and isinstance(res["match"], dict) and "valid" in res["match"]:
            got = bool(res["match"]["valid"])
        else:
            raise AssertionError(f"Unrecognized result shape from verifier: {res}")
    else:
        # If the function returns a bare bool, accept it.
        got = bool(res)

    assert got == claim["expected_valid"], f"Claim #{claim['id']} failed: {claim['query']!r}"
