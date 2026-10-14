#!/usr/bin/env python3
"""Corpus statistics and analytics generator for BD-ExamQ.
Extracts distribution metrics, Bloom's cognitive level breakdowns,
chapter coverage, and linguistic characteristics across questions.
"""

import sys
import json
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_all_records(source_path: Path) -> List[Dict[str, Any]]:
    records = []
    if source_path.is_file():
        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    elif source_path.is_dir():
        for file_path in source_path.glob("*.jsonl"):
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
    return records


def compute_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_q = len(records)
    exams = Counter(r.get("exam", "Unknown") for r in records)
    boards = Counter(r.get("board", "Unknown") for r in records)
    years = Counter(r.get("year", "Unknown") for r in records)
    subjects = Counter(r.get("subject", "Unknown") for r in records)
    q_types = Counter(r.get("question_type") or r.get("q_type", "Unknown") for r in records)
    chapters = Counter(f"{r.get('subject', 'General')} - {r.get('chapter_id') or r.get('chapter', 'Unassigned')}" for r in records)
    
    # Cognitive domain stats (including sub-parts for CQs)
    cognitive_levels = Counter()
    total_subparts = 0
    total_marks = 0.0
    stem_lengths = []
    has_image_count = 0

    for r in records:
        total_marks += float(r.get("marks") or 0.0)
        if r.get("has_image"):
            has_image_count += 1
            
        stem = r.get("stem") or r.get("text_bn") or r.get("question_text") or ""
        if stem:
            stem_lengths.append(len(stem.split()))

        # If CQ, count subparts
        sub_parts = r.get("sub_questions") or r.get("sub_parts")
        if sub_parts:
            for sp in sub_parts:
                total_subparts += 1
                cog = sp.get("cognitive_domain") or sp.get("part") or "unspecified"
                cognitive_levels[cog] += 1
        else:
            bloom = r.get("bloom_level") or "unspecified"
            cognitive_levels[bloom] += 1

    avg_stem_words = sum(stem_lengths) / len(stem_lengths) if stem_lengths else 0

    return {
        "total_questions": total_q,
        "total_subparts": total_subparts,
        "total_marks": total_marks,
        "has_image_percentage": (has_image_count / total_q) * 100 if total_q else 0,
        "avg_words_per_question": round(avg_stem_words, 2),
        "exam_distribution": dict(exams),
        "board_distribution": dict(boards),
        "year_distribution": dict(sorted(years.items())),
        "subject_distribution": dict(subjects),
        "question_type_distribution": dict(q_types),
        "cognitive_domain_distribution": dict(cognitive_levels),
        "top_chapters": dict(chapters.most_common(10))
    }


def print_report(stats: Dict[str, Any]):
    print("=" * 60)
    print("      📊 BD-ExamQ CORPUS DESCRIPTIVE STATISTICS")
    print("=" * 60)
    print(f"Total Question Records : {stats['total_questions']}")
    print(f"Total Sub-Questions (CQ): {stats['total_subparts']}")
    print(f"Total Marks Represented: {stats['total_marks']:.0f}")
    print(f"Questions with Diagrams: {stats['has_image_percentage']:.1f}%")
    print(f"Avg. Bangla Words/Stem : {stats['avg_words_per_question']}")
    
    print("\n--- Exam Level Distribution ---")
    for k, v in stats["exam_distribution"].items():
        print(f"  • {str(k):15}: {v:5d} ({v/stats['total_questions']*100:.1f}%)")

    print("\n--- Question Type Breakdown ---")
    for k, v in stats["question_type_distribution"].items():
        print(f"  • {str(k):15}: {v:5d} ({v/stats['total_questions']*100:.1f}%)")

    print("\n--- Board Distribution ---")
    for k, v in sorted(stats["board_distribution"].items(), key=lambda x: -x[1]):
        print(f"  • {str(k):18}: {v:5d}")

    print("\n--- Subject Distribution ---")
    for k, v in sorted(stats["subject_distribution"].items(), key=lambda x: -x[1])[:20]:
        print(f"  • {str(k):25}: {v:5d}")

    print("\n--- Cognitive Domain (Bloom's Taxonomy / Subparts) Distribution ---")
    for k, v in sorted(stats["cognitive_domain_distribution"].items(), key=lambda x: -x[1])[:10]:
        print(f"  • {str(k):18}: {v:5d}")

    print("\n--- Top Chapters Examined ---")
    for k, v in sorted(stats["top_chapters"].items(), key=lambda x: -x[1])[:15]:
        print(f"  • {str(k):35}: {v:5d} questions")
    print("=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BD-ExamQ Corpus Statistics Generator")
    parser.add_argument(
        "--file",
        default=str(PROJECT_ROOT / "data" / "processed" / "questions.jsonl"),
        help="Path to questions.jsonl or samples directory"
    )
    args = parser.parse_args()

    target_path = Path(args.file)
    if not target_path.exists():
        target_path = PROJECT_ROOT / "data" / "samples"

    records = load_all_records(target_path)
    if not records:
        print(f"No records found to analyze at {target_path}.")
        sys.exit(1)
    stats = compute_statistics(records)
    print_report(stats)


if __name__ == "__main__":
    main()
