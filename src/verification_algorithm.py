"""
Builds Prolog FACTS from availability JSON, loads static rules
(prolog/validation_rules.pl), and validates an LLM claim.

verify_claim(availability, claim_dict) -> dict
  availability: {"Thursday": ["09:00-12:00"], "Friday": ["13:00-16:00"], ...}
  claim_dict:   {"day":"friday","time":"13:30"} or {"day":"friday","ambiguous":"morning"}
"""

from __future__ import annotations
import json
import os
import re
import subprocess
import tempfile
from typing import Dict, Any, List

def facts_from_availability(availability: Dict[str, List[str]]) -> str:
    lines = []
    for day_name, spans in availability.items():
        day_atom = day_name.lower()
        for span in spans:
            span = span.replace("–", "-").replace("—", "-")
            m = re.match(r"\s*(\d{2}):(\d{2})\s*-\s*(\d{2}):(\d{2})\s*$", span)
            if not m:
                raise ValueError(f"Bad span format: {span}")
            sH,sM,eH,eM = map(int, m.groups())
            start = 60*sH + sM
            end   = 60*eH + eM
            label = f"{sH:02d}:{sM:02d}"
            lines.append(f"available_slot('-', {day_atom}, \"{label}\", {start}, {end}).")
    return "\n".join(lines) + "\n"

def _build_prolog_source(facts: str, claim: Dict[str, Any]) -> str:
    header = ":- ensure_loaded('prolog/validation_rules.pl').\n\n"
    body = facts + "\n"

    day = claim.get("day")
    time = claim.get("time")
    ambiguous = claim.get("ambiguous")

    if day and time:
        q = f"validate_answer({day}, exact_time(\"{time}\"), Verdict, Reason), json_out(Verdict, Reason)."
    elif day and ambiguous:
        q = f"validate_answer({day}, ambiguous({ambiguous}), Verdict, Reason), json_out(Verdict, Reason)."
    else:
        q = "json_out(error, 'claim missing day/time or ambiguous window')."

    main = f":- initialization(({q}), main).\n"
    return header + body + main

def run_swipl(src: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        pl_path = os.path.join(td, "tmp_validate.pl")
        with open(pl_path, "w", encoding="utf-8") as f:
            f.write(src)
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cmd = ["swipl", "-q", "-f", pl_path, "-g", "true", "-t", "halt"]
        cp = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        out = cp.stdout.strip()
        if cp.returncode != 0 and not out:
            raise RuntimeError(f"SWI-Prolog error: {cp.stderr}")
        return out

def verify_claim(availability: Dict[str, List[str]], claim: Dict[str, Any]) -> Dict[str, Any]:
    facts = facts_from_availability(availability)
    src = _build_prolog_source(facts, claim)
    raw = run_swipl(src)
    try:
        return json.loads(raw)
    except Exception:
        return {"is_valid": False, "reason": f"Prolog returned: {raw}"}
