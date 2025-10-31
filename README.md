# Query Complexity & Tool-Use Hallucinations in LLM Scheduling — Code

This repository supports a **hypothesis-driven** study of how **query complexity** affects **tool-use hallucinations** in large language models (LLMs) during appointment scheduling, and how an XAI pipeline (logic validation + interpretability) detects and explains errors.

> **Hypothesis (study context)**  
> Increasing query complexity (multi-day or ambiguous time ranges) **increases** tool-use hallucinations due to misinterpretation of structured availability data.  
> The code here provides the logic-validation core and parsing utilities used to test that hypothesis.

---

## Repository Structure

- `src/prompt_parsing.py` — Parses user queries and classifies complexity (`simple` / `complex` / `edge`); extracts days, exact times, time ranges, and ambiguous phrases.
- `src/verification_algorithm.py` — Converts availability JSON into **Prolog facts**, loads static rules, and verifies an LLM claim via SWI-Prolog; returns a JSON verdict with reason.
- `src/xai_agent_loop_pseudocode.txt` — High-level control flow showing how responses are generated, validated with logic, and logged for interpretability analysis.
- `src/dynamic_prolog_prompt.txt` — Instructions for emitting **facts** only and loading **static** rules (no new rules inlined).
- `prolog/validation_rules.pl` — Static Prolog rules for exact-time validation and ambiguous windows (e.g., morning/afternoon/evening).
- `prolog/optimized_prolog.pl`, `prolog/full_prolog.pl` — Minimal modules that load the same static rules (entry points).
- `requirements.txt` — Python dependencies for analysis utilities used around the validator.

> **Note:** This repository focuses on the **logic-validation and parsing** components described in the manuscript. It intentionally does **not** document figure generation here.
