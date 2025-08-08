# XAI-LLM Hallucination Framework Code

This repository contains all code and scripts from the manuscript "Mitigating Tool-Use Hallucinations in LLMs via an XAI-Integrated Framework: A Case Study in Appointment Scheduling". It supports replication of the Prolog reasoning, Python tools, and pseudocode for the scheduling assistant.

## Files
- `xai_agent_loop_pseudocode.txt`: Pseudocode for the XAI-Agent loop processing queries and tools.
- `prompt_parsing.py`: Python code for prompt templates and response parsing.
- `verification_algorithm.py`: Python function for verifying tool outputs with Prolog.
- `optimized_prolog.pl`: Main Prolog code including facts, preferences, time conversion helper, validation rules, and queries.
- `full_prolog.pl`: Additional Prolog rules for finding closest slots.
- `dynamic_prolog_prompt.txt`: Prompt template for GPT-4o to generate dynamic Prolog code.

## Usage
- Python: Run in a Python 3+ environment with libraries like re (standard).
- Prolog: Load .pl files in SWI-Prolog and query as per manuscript (e.g., valid_slot).
- See manuscript Results/Methods for integration details.
