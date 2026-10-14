#!/usr/bin/env python3
"""Export utilities for BD-ExamQ.
Converts nested JSONL records into:
1. Flattened CSV format suitable for spreadsheets / pandas / R.
2. Hugging Face Datasets compatible JSON structure.
"""

import sys
import json
import csv
from pathlib import Path
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def flatten_record_for_csv(record: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens a QuestionRecord into a 1-row tabular structure."""
    # Handle CQ sub-questions from both schemas
    subs = record.get("sub_questions") or []
    subparts = record.get("sub_parts") or []
    
    sub_ka, sub_kha, sub_ga, sub_gha = "", "", "", ""
    if subs:
        for s in subs:
            p = str(s.get("part", "")).lower()
            txt = s.get("text", "")
            if p in ["a", "ক"]:
                sub_ka = txt
            elif p in ["b", "খ"]:
                sub_kha = txt
            elif p in ["c", "গ"]:
                sub_ga = txt
            elif p in ["d", "ঘ"]:
                sub_gha = txt
    elif subparts:
        for sp in subparts:
            p = sp.get("part")
            txt = sp.get("text_bn", "")
            if p in ["a", "ক"]:
                sub_ka = txt
            elif p in ["b", "খ"]:
                sub_kha = txt
            elif p in ["c", "গ"]:
                sub_ga = txt
            elif p in ["d", "ঘ"]:
                sub_gha = txt

    # Handle MCQ options
    opts = record.get("options") or []
    opt_ka, opt_kha, opt_ga, opt_gha = "", "", "", ""
    if opts and isinstance(opts[0], str):
        if len(opts) > 0: opt_ka = opts[0]
        if len(opts) > 1: opt_kha = opts[1]
        if len(opts) > 2: opt_ga = opts[2]
        if len(opts) > 3: opt_gha = opts[3]
    elif opts and isinstance(opts[0], dict):
        opt_ka = next((op.get("text_bn", "") for op in opts if op.get("label") in ["ক", "a"]), "")
        opt_kha = next((op.get("text_bn", "") for op in opts if op.get("label") in ["খ", "b"]), "")
        opt_ga = next((op.get("text_bn", "") for op in opts if op.get("label") in ["গ", "c"]), "")
        opt_gha = next((op.get("text_bn", "") for op in opts if op.get("label") in ["ঘ", "d"]), "")

    return {
        "id": record.get("id"),
        "exam": record.get("exam"),
        "year": record.get("year"),
        "board": record.get("board"),
        "subject": record.get("subject"),
        "paper": record.get("paper", ""),
        "question_type": record.get("question_type") or record.get("q_type", ""),
        "marks": record.get("marks", 0),
        "stem": record.get("stem") or record.get("text_bn") or record.get("question_text") or "",
        "sub_a_ka": sub_ka,
        "sub_b_kha": sub_kha,
        "sub_c_ga": sub_ga,
        "sub_d_gha": sub_gha,
        "mcq_opt_a": opt_ka,
        "mcq_opt_b": opt_kha,
        "mcq_opt_c": opt_ga,
        "mcq_opt_d": opt_gha,
        "chapter": record.get("chapter") or record.get("chapter_id", ""),
        "topic": record.get("topic") or record.get("topic_id", ""),
        "source_file": record.get("source_file", ""),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Export BD-ExamQ corpus to CSV")
    parser.add_argument("--input", default="data/processed/questions.jsonl", help="Input JSONL file")
    parser.add_argument("--output", default="data/processed/questions.csv", help="Output CSV path")
    args = parser.parse_args()

    input_path = PROJECT_ROOT / args.input
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

    if not records:
        print(f"No records found to export at {input_path}.")
        return

    flattened = [flatten_record_for_csv(r) for r in records]
    fieldnames = list(flattened[0].keys())

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)

    print(f"✅ Exported {len(flattened)} records to CSV: {output_path.relative_to(PROJECT_ROOT)} ({output_path.stat().st_size / 1024 / 1024:.2f} MB)")


if __name__ == "__main__":
    main()
