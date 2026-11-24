"""Analyze recorded binary outcomes from *actual* experiment logs.

This module does not contain simulated study results. It accepts an original
CSV with columns: query_id, category, is_hallucination. Optional paired
re-feeding results use: query_id, before_hallucination, after_hallucination.

Usage:
  python -m scripts.analyze_trials trials.csv
  python -m scripts.analyze_trials trials.csv --paired refeed.csv
"""
from __future__ import annotations
import argparse
import csv
import math
import random
from collections import defaultdict


def parse_bool(s: str) -> bool:
    text = str(s).strip().lower()
    if text in ("1", "true", "yes"):
        return True
    if text in ("0", "false", "no"):
        return False
    raise ValueError(f"Expected boolean field, got {s!r}")


def read_trials(path: str) -> dict[str, list[bool]]:
    by_category: dict[str, list[bool]] = defaultdict(list)
    with open(path, encoding="utf-8", newline="") as f:
        rows = csv.DictReader(f)
        required = {"query_id", "category", "is_hallucination"}
        if not required.issubset(rows.fieldnames or []):
            raise ValueError(f"Required columns: {sorted(required)}")
        seen = set()
        for row in rows:
            if row["query_id"] in seen:
                raise ValueError(f"Duplicate trial id: {row['query_id']}")
            seen.add(row["query_id"])
            category = row["category"].lower().strip()
            if category not in {"simple", "complex", "edge"}:
                raise ValueError(f"Unknown category: {category}")
            by_category[category].append(parse_bool(row["is_hallucination"]))
    return by_category


def bootstrap_ci(samples: list[bool], n_boot: int = 1000, seed: int = 2025) -> tuple[float, float]:
    if not samples:
        raise ValueError("Empty sample")
    random_state = random.Random(seed)
    n = len(samples)
    estimates = sorted(
        sum(samples[random_state.randrange(n)] for _ in range(n)) / n
        for _ in range(n_boot)
    )
    return estimates[int(n_boot * 0.025)], estimates[min(n_boot - 1, int(n_boot * 0.975))]


def two_proportion_z(a: list[bool], b: list[bool]) -> tuple[float, float]:
    x1, x2 = sum(a), sum(b)
    n1, n2 = len(a), len(b)
    pooled = (x1 + x2) / (n1 + n2)
    denominator = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    if not denominator:
        raise ValueError("No variance for z-test")
    z = (x1 / n1 - x2 / n2) / denominator
    p = math.erfc(abs(z) / math.sqrt(2))
    return z, p


def paired_stats(path: str) -> dict[str, float | int]:
    before, after = [], []
    seen = set()
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expected = {"query_id", "before_hallucination", "after_hallucination"}
        if not expected.issubset(reader.fieldnames or []):
            raise ValueError(f"Required columns: {sorted(expected)}")
        for row in reader:
            if row["query_id"] in seen:
                raise ValueError(f"Duplicate paired trial id: {row['query_id']}")
            seen.add(row["query_id"])
            before.append(parse_bool(row["before_hallucination"]))
            after.append(parse_bool(row["after_hallucination"]))
    if not before:
        raise ValueError("No paired trials supplied")
    improved = sum(a and not b for a, b in zip(before, after))
    worsened = sum(not a and b for a, b in zip(before, after))
    discordant = improved + worsened
    if discordant:
        statistic = max(0, abs(improved - worsened) - 1) ** 2 / discordant
        p = math.erfc(math.sqrt(statistic / 2))
    else:
        statistic, p = 0.0, 1.0
    return dict(n=len(before), before_pct=100 * sum(before) / len(before),
                after_pct=100 * sum(after) / len(after),
                improved=improved, worsened=worsened,
                mcnemar_continuity_chisq=statistic, p_value=p)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trials", help="CSV of original query outcomes")
    parser.add_argument("--paired", help="Optional paired outcomes CSV")
    args = parser.parse_args()
    groups = read_trials(args.trials)
    for category in ("simple", "complex", "edge"):
        values = groups.get(category, [])
        if not values:
            print(f"{category}: no data")
            continue
        low, high = bootstrap_ci(values)
        print(f"{category}: n={len(values)} hallucinations={sum(values)}, "
              f"rate={100*sum(values)/len(values):.2f}% "
              f"bootstrap 95% CI=[{low*100:.2f}%, {high*100:.2f}%]")
    for a, b in (("simple", "complex"), ("complex", "edge"), ("simple", "edge")):
        if groups.get(a) and groups.get(b):
            z, p = two_proportion_z(groups[a], groups[b])
            print(f"{a} vs {b}: z={z:.3f}, two-sided p={p:.4g} (Bonferroni alpha=0.0167)")
    if args.paired:
        print("Paired refeeding:", paired_stats(args.paired))


if __name__ == "__main__":
    main()
