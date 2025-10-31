# Query Complexity & Tool-Use Hallucinations in LLM Scheduling — Code

This repository supports a **hypothesis-driven** study of how **query complexity** affects **tool-use hallucinations** in large language models (LLMs) during appointment scheduling, and how an XAI pipeline (logic validation + interpretability) detects and explains errors.

> **Hypothesis (study context)**  
> Increasing query complexity (multi-day or ambiguous time ranges) **increases** tool-use hallucinations due to misinterpretation of structured availability data.  
> The code here provides the logic-validation core and parsing utilities used to test that hypothesis.

---

## Repository Structure
.
├── examples/
│   ├── availability_sample.json      # Sample availability data (Thu 09–12, Fri 13–16)
│   └── claims_sample.jsonl           # Example user queries with expected validity labels
├── prolog/
│   ├── example_facts_and_query.pl    # Tiny demo: asserts a few facts + query predicate
│   └── validation_rules.pl           # Static rules: exact-time & ambiguous-window logic
├── src/
│   ├── dynamic_prolog_prompt.txt     # If you ever emit facts from an LLM, use this prompt
│   ├── prompt_parsing.py             # Token/phrase extraction & complexity classification
│   ├── verification_algorithm.py     # Python→Prolog adapter + single-claim verification
│   └── xai_agent_loop_pseudocode.txt # High-level flow (generate→verify→log/explain)
├── tests/
│   └── test_validation.py            # Integration-ish tests against the sample data
└── README.md
