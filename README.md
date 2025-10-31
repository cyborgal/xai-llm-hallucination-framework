# Query Complexity & Tool-Use Hallucinations in LLM Scheduling — Code

This repository supports a **hypothesis-driven** study of how **query complexity** affects **tool-use hallucinations** in large language models (LLMs) during appointment scheduling, and how an XAI pipeline (logic validation + interpretability) detects and explains errors.

> **Hypothesis (study context)**  
> Increasing query complexity (multi-day or ambiguous time ranges) **increases** tool-use hallucinations due to misinterpretation of structured availability data.  
> The code here provides the logic-validation core and parsing utilities used to test that hypothesis.

---

## What’s here

- `src/prompt_parsing.py` — Classifies queries (simple/complex/edge) and extracts constraints (days, exact times, ranges, and ambiguous terms like “morning”).
- `src/verification_algorithm.py` — Converts availability JSON to Prolog **facts**, loads static **validation rules**, and verifies an LLM’s claim via SWI-Prolog; returns a JSON-friendly verdict.
- `src/xai_agent_loop_pseudocode.txt` — High-level loop used in the manuscript (generation → tool → validation → XAI → optional refeed).
- `src/dynamic_prolog_prompt.txt` — If you need to emit Prolog from an LLM, instructs it to output **facts only** and then include the static rules (no auto “closest-match” logic).

- `prolog/validation_rules.pl` — **Unified** Prolog rules used in the primary analyses (static). Handles exact times and ambiguous windows (e.g., morning = 09:00–12:00).
- `prolog/example_facts_and_query.pl` — Tiny demo asserting a couple of `available_slot/4` facts and running the decision predicate for quick sanity checks.

- `examples/availability_sample.json` — Sample availability (Thu 09:00–12:00; Fri 13:00–16:00) used in tests.
- `examples/claims_sample.jsonl` — Example queries with expected validity labels for integration testing.

- `tests/test_validation.py` — Integration test that loads the samples, calls the verifier, and asserts agreement with expected labels (auto-skips if `swipl` is missing).
