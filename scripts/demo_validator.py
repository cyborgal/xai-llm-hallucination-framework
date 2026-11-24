"""Run public Prolog validation on included sample data.
Usage: python -m scripts.demo_validator
Requires SWI-Prolog installed and on PATH.
"""
import json
from pathlib import Path
from src.verification_algorithm import verify_claim

sample = json.loads((Path(__file__).resolve().parents[1] / "examples/availability_sample.json").read_text())
for claim in [
    {"day": "thursday", "time": "10:00"},
    {"day": "friday", "time": "09:30"},
    {"day": "thursday", "ambiguous": "morning"},
]:
    print(json.dumps({"claim": claim, **verify_claim(sample, claim)}))
