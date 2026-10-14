#!/usr/bin/env python3
"""Temporal dataset splitter for BD-ExamQ.
Ensures rigorous chronological partitioning (Train: years <= t_train, Val: t_val, Test: t_test)
to prevent temporal leakage from future examination papers.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def split_by_year(
    records: List[Dict[str, Any]],
    train_end_year: int,
    test_year: int
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Splits records into train, validation (optional interim), and test sets chronologically."""
    train = []
    val = []
    test = []

    for r in records:
        y = r.get("year", 0)
        if y <= train_end_year:
            train.append(r)
        elif y < test_year:
            val.append(r)
        elif y == test_year:
            test.append(r)

    return train, val, test


def main():
    parser = argparse.ArgumentParser(description="Chronological splitter for BD-ExamQ")
    parser.add_argument("--train-until", type=int, default=2017, help="Last year included in training split")
    parser.add_argument("--test-year", type=int, default=2023, help="Year used for test split (evaluation)")
    parser.add_argument("--input", type=str, default="data/processed/questions.jsonl", help="Input JSONL file or directory")
    parser.add_argument("--output-dir", type=str, default="data/splits", help="Directory to save split files")
    args = parser.parse_args()

    input_path = PROJECT_ROOT / args.input
    output_path = PROJECT_ROOT / args.output_dir
    output_path.mkdir(parents=True, exist_ok=True)

    records = []
    if input_path.is_file():
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
    elif input_path.is_dir():
        for fp in input_path.glob("*.jsonl"):
            with open(fp, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))

    train, val, test = split_by_year(records, args.train_until, args.test_year)

    print(f"📊 Chronological Splitting Configuration:")
    print(f"   Train (<= {args.train_until}): {len(train)} records")
    print(f"   Validation ({args.train_until+1}..{args.test_year-1}): {len(val)} records")
    print(f"   Test (== {args.test_year}): {len(test)} records")

    for name, split_data in [("train.jsonl", train), ("val.jsonl", val), ("test.jsonl", test)]:
        out_file = output_path / name
        with open(out_file, "w", encoding="utf-8") as f:
            for item in split_data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"   Saved {name} -> {out_file.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
