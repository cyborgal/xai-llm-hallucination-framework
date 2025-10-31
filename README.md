# Query complexity increases tool-use hallucinations in LLM scheduling tasks — Code & Repro

This repository contains code supporting the manuscript’s hypothesis-driven study of how **query complexity** affects **tool-use hallucinations** in large language models (LLMs) during appointment scheduling, and how an **XAI-integrated** pipeline (Prolog validation, LIME, attention maps) detects and explains errors.

## What’s here
- `src/prompt_parsing.py` — Classifies queries (simple/complex/edge), extracts day/time constraints (including ambiguous terms like “morning”).
- `src/verification_algorithm.py` — Converts availability JSON to Prolog **facts**, loads static **validation rules**, and verifies LLM claims against ground truth using SWI-Prolog.
- `src/xai_agent_loop_pseudocode.txt` — High-level loop used in the manuscript (generation → tool → validation → XAI → optional refeed).
- `src/dynamic_prolog_prompt.txt` — If you must generate Prolog dynamically, instructs the LLM to emit **facts only** and then include the static rules (no auto “closest-match”).
- `prolog/validation_rules.pl` — **Unified** Prolog rules used in primary analyses (static). Handles exact times and ambiguous windows (e.g., morning = 09:00–12:00).
- `prolog/optimized_prolog.pl`, `prolog/full_prolog.pl` — **Compatibility shims** that load `validation_rules.pl`. (Legacy logic like “closest match” is **not used**.)
- `analysis/make_figures.py` — Generates Figures 2–5 exactly as in the paper:
  - Fig 2 uses **±1 SE** error bars (not SD).
  - Fig 5 shows **before/after** rates with 95% CI and a **McNemar χ²(1)** line (continuity correction) based on **b=67, c=6**.

## Reproducing figures
```bash
# Option A: conda
conda create -n xai-llm python=3.11 -y
conda activate xai-llm
pip install -r requirements.txt

# Option B: plain pip
python -m venv .venv && source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# Generate figures (PNG + TIFF) to ./figs
python analysis/make_figures.py
