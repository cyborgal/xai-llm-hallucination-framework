# Explainable AI Framework for LLM Scheduling Hallucinations

**Public code supporting the published research paper:**  
Baelyn Thantron and Gopal Gupta, [*An explainable AI framework for studying query complexity and hallucinations in LLM scheduling tasks*](https://emerginginvestigators.org/articles/25-313/pdf), *Journal of Emerging Investigators* (2026). DOI: [10.59720/25-313](https://doi.org/10.59720/25-313).

The study investigates whether more complex appointment-scheduling queries produce more tool-use hallucinations and explores logic-based validation and explainability for diagnosing those errors.

**November 2026 update:** The research publication was finalized in November 2026. The public repository was updated in November to align the released validation utilities, test cases, and documentation with the final manuscript.

## Published findings

The article reports testing 9,999 scheduling queries: hallucination rates of **10.2% (simple)**, **14.8% (complex)**, and **18.5% (edge)**. In a 500-query paired feedback experiment, reported hallucinations fell from **16.8% to 4.6%** after Prolog corrective feedback. These are results **reported in the publication**, not reconstructed from public sample data.

## Public implementation

| Component | File |
| --- | --- |
| Classify scheduling query complexity | `src/prompt_parsing.py` |
| Transform structured calendar availability into Prolog facts | `src/verification_algorithm.py` |
| Logic-based time and window validation | `prolog/validation_rules.pl` |
| Representative availability example | `examples/availability_sample.json` |
| Regression and integration tests | `tests/test_validation.py` |
| Runnable public validator demonstration | `scripts/demo_validator.py` |
| Reanalyze **real supplied** trial and paired-feedback logs | `scripts/analyze_trials.py` |
| Original study workflow schematic | `src/xai_agent_loop_pseudocode.txt` |

## Run the included validator

Requirements: **Python 3.11+**, **SWI-Prolog 9.x** (`swipl` on PATH), and pytest.

```bash
python -m pip install pytest
python -m pytest -q
python -m scripts.demo_validator
```

The demo validates a Thursday morning slot and Friday afternoon slot against representative calendar data. CI runs the same test suite with SWI-Prolog installed.

For a detailed **paper-to-code methodology map**, original-data requirements, and instructions for analyzing real study logs, see **[REPRODUCIBILITY.md](REPRODUCIBILITY.md)**.

### Scope

The published research involves GPT-4o/LangChain runs, Prolog, LIME, attention visualizations, and a corrective-feedback experiment. The public code provides a tested **deterministic validation subset and reusable analysis utilities**, not the complete historical experiment corpus or LLM/XAI outputs. Reproducing the paper's exact numerical findings requires original experiment records and explanation artifacts. No missing results have been synthesized for this release.

## Citation

Thantron, B., & Gupta, G. (2026). *An explainable AI framework for studying query complexity and hallucinations in LLM scheduling tasks*. Journal of Emerging Investigators. https://doi.org/10.59720/25-313
