"""Regression tests for real-log statistics functions; these are toy tests, not study data."""
import csv
import pytest

from scripts.analyze_trials import bootstrap_ci, parse_bool, two_proportion_z, paired_stats, read_trials


def test_bool_parser():
    assert parse_bool("true")
    assert not parse_bool("0")
    with pytest.raises(ValueError):
        parse_bool("perhaps")


def test_bootstrap_is_deterministic():
    data = [True, False, True, False]
    assert bootstrap_ci(data, seed=5) == bootstrap_ci(data, seed=5)


def test_two_proportion_returns_probability():
    z, p = two_proportion_z([False] * 8 + [True] * 2, [True] * 8 + [False] * 2)
    assert z < 0
    assert 0 < p < 0.05


def test_paired_statistic(tmp_path):
    file = tmp_path / "paired.csv"
    with file.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["query_id", "before_hallucination", "after_hallucination"])
        w.writerows([("a", 1, 0), ("b", 1, 0), ("c", 0, 1), ("d", 0, 0)])
    result = paired_stats(str(file))
    assert result["improved"] == 2
    assert result["worsened"] == 1
    assert result["before_pct"] == 50.0
    assert result["after_pct"] == 25.0
    assert result["mcnemar_continuity_chisq"] == 0


def test_duplicate_trials_rejected(tmp_path):
    file = tmp_path / "trials.csv"
    file.write_text(
        "query_id,category,is_hallucination\n1,simple,1\n1,complex,0\n"
    )
    with pytest.raises(ValueError, match="Duplicate"):
        read_trials(str(file))
