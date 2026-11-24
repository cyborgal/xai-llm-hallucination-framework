# Reproducibility and source provenance

This repository accompanies [Thantron & Gupta, *Journal of Emerging Investigators* 9 (2026), DOI: 10.59720/25-313](https://emerginginvestigators.org/articles/25-313/pdf).

## What is runnable here

The public release implements the **deterministic availability-validation portion**: sample scheduling availability, normalization into Prolog facts, exact-time/window validation, query classification, a Python-to-SWI-Prolog interface, regression tests, and statistics utilities for externally supplied original model logs.

- Requires Python 3.11+, SWI-Prolog 9.x, and pytest (for tests).
- `python -m pip install pytest`
- `python -m pytest -q`
- `python -m scripts.demo_validator`

GitHub Actions installs SWI-Prolog and runs these tests. A passing test means the public validator works on its documented examples. **It does not independently reproduce the published GPT-4o experimental results.**

## Correspondence with the published study

| Published component | Public artifact | Reproduction status |
| --- | --- | --- |
| Generated queries, grouped simple/complex/edge | `src/prompt_parsing.py`, example queries | Illustrative parser, not the original 9,999-query corpus |
| Calendar tool response | `examples/availability_sample.json` | Representative fixed availability |
| Logic validation with Prolog | `prolog/validation_rules.pl`, `src/verification_algorithm.py` | Runnable released implementation |
| GPT-4o / LangChain scheduling agent | `src/xai_agent_loop_pseudocode.txt` | Workflow schematic; original generation code and API logs not included |
| LIME local feature importance | Described in paper | Original perturbation/model outputs and explanatory code not included |
| Attention heatmaps | Figures 3–4 in paper | Original attention inputs/attribution data and scripts not included |
| 9,999-query categorization and statistical tests | `scripts/analyze_trials.py` | Can analyze real, appropriately formatted logs; study logs not included |
| Paired 500-trial Prolog-refeeding experiment | `scripts/analyze_trials.py --paired` | Can analyze original paired outcomes if supplied; response-generation logs not included |

The published paper reports 10.2%, 14.8%, and 18.5% hallucinations across categories, plus a reduction from 16.8% to 4.6% in a 500-query refeeding experiment. Those are **published reported results**, not outputs generated from the public sample files. This repository does not fabricate the underlying observations.

### Important interpretation boundaries

The released validator checks whether a **single affirmative availability claim** is supported by the tool output. It does not infer truth values from arbitrary free-form *negative* answers or multi-slot answers. Those require a separate semantic evaluator grounded in the original LLM logs. The parser intentionally rejects negative/ambiguous cases rather than mislabeling them.

The paper discusses attention visualizations alongside GPT-4o. Public GPT-4o API responses do not generally expose internal transformer attention tensors; consequently, the published heatmaps cannot be regenerated from the public GPT-4o API alone. Their provenance and any surrogate-model methodology must be established from the original lab artifacts rather than inferred from this repo.

Likewise, a changed schedule, model version, prompt, sampling seed, temperature, tool output, or query corpus constitutes a **new experiment**, not replication of the historical numerical results.

## Analyzing original logs (if available)

Supply a CSV with unique `query_id`, `category` (simple/complex/edge), and `is_hallucination` (0/1 or true/false). Then run:

```bash
python -m scripts.analyze_trials path/to/original_trials.csv
```

For the paired refeeding study, add a second CSV containing `query_id`, `before_hallucination`, and `after_hallucination`:

```bash
python -m scripts.analyze_trials path/to/original_trials.csv --paired path/to/original_refeed.csv
```

The tool calculates proportions, nonparametric percentile-bootstrap confidence intervals (1,000 resamples; fixed seed), two-sided pooled two-proportion z-tests, and continuity-corrected McNemar chi-square tests. Outputs reflect the supplied observations; they are not guaranteed to equal the paper unless the original data and analysis choices match.

## Next steps to reproduce the entire paper

To independently reproduce the original study end to end, the original lab would need to provide: (1) exact generated 9,999-query corpus and calendar responses; (2) actual LLM output logs, prompts, configurations, and API/tool integration; (3) outcome labels and decision rules for affirmative, negative, and multi-slot replies; (4) LIME perturbations/model outputs and visualization scripts; (5) provenance and inputs for the attention heatmaps; and (6) the 500 original paired feedback trials. These should be published only with necessary privacy, permission, and API-key review.

The public repo intentionally distinguishes the accessible validation utilities from unpublished experiment artifacts so readers can judge the scope of verification accurately.
