#!/usr/bin/env python3
"""Baseline prediction models for BD-ExamQ.
Implements the 3 foundational baselines formulated in idea.md:
1. Historical Chapter Frequency Baseline
2. Recency Heuristic ('Not Asked Recently' rotation hypothesis)
3. First-order Markov Transition Model

Evaluates on test year using:
- Top-k Chapter Hit Rate (Top-3, Top-5)
- Marks-Weighted Coverage (%)
"""

import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any, Set, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class ChapterFrequencyModel:
    """Ranks chapters strictly by their historical occurrence frequency in training data."""
    def __init__(self):
        self.counts = Counter()

    def fit(self, train_records: List[Dict[str, Any]]):
        self.counts = Counter(r["chapter_id"] for r in train_records if "chapter_id" in r)

    def predict(self, k: int = 5) -> List[str]:
        return [ch for ch, _ in self.counts.most_common(k)]


class RecencyHeuristicModel:
    """Hypothesis: Exam question setters tend to rotate out topics examined in year (t-1)
    and prioritize chapters that were NOT tested recently.
    """
    def __init__(self):
        self.all_known_chapters: Set[str] = set()
        self.year_chapters = defaultdict(set)

    def fit(self, train_records: List[Dict[str, Any]]):
        for r in train_records:
            ch = r.get("chapter_id")
            yr = r.get("year")
            if ch and yr:
                self.all_known_chapters.add(ch)
                self.year_chapters[yr].add(ch)

    def predict(self, prev_year: int, k: int = 5) -> List[str]:
        prev_chapters = self.year_chapters.get(prev_year, set())
        # Prioritize chapters not in previous year
        not_asked_recently = [ch for ch in sorted(self.all_known_chapters) if ch not in prev_chapters]
        asked_recently = [ch for ch in sorted(self.all_known_chapters) if ch in prev_chapters]
        # Combine: not asked first, followed by asked
        ranked = not_asked_recently + asked_recently
        return ranked[:k]


class MarkovTransitionModel:
    """Models transition probability P(Chapter_t | Chapter_{t-1}) based on sequential yearly board sets."""
    def __init__(self):
        self.transition_counts = defaultdict(Counter)
        self.prior_counts = Counter()

    def fit(self, train_records: List[Dict[str, Any]]):
        # Group by board and subject across consecutive years
        board_subject_years = defaultdict(lambda: defaultdict(set))
        for r in train_records:
            b = r.get("board")
            s = r.get("subject")
            y = r.get("year")
            ch = r.get("chapter_id")
            if b and s and y and ch:
                board_subject_years[(b, s)][y].add(ch)
                self.prior_counts[ch] += 1

        for (b, s), year_dict in board_subject_years.items():
            years = sorted(year_dict.keys())
            for i in range(len(years) - 1):
                y_curr = years[i]
                y_next = years[i + 1]
                if y_next - y_curr <= 2:  # allow 1 or 2 year step
                    for ch_curr in year_dict[y_curr]:
                        for ch_next in year_dict[y_next]:
                            self.transition_counts[ch_curr][ch_next] += 1

    def predict(self, prev_chapters: Set[str], k: int = 5) -> List[str]:
        candidate_scores = Counter()
        for ch in prev_chapters:
            for nxt_ch, count in self.transition_counts[ch].items():
                candidate_scores[nxt_ch] += count

        # If sparse, smooth with prior
        for ch, count in self.prior_counts.items():
            candidate_scores[ch] += 0.1 * count

        return [ch for ch, _ in candidate_scores.most_common(k)]


def evaluate_predictions(predicted_chapters: List[str], test_records: List[Dict[str, Any]]) -> Dict[str, float]:
    actual_chapters = {r["chapter_id"] for r in test_records if "chapter_id" in r}
    if not actual_chapters:
        return {"hit_rate": 0.0, "marks_coverage": 0.0}

    pred_set = set(predicted_chapters)
    hits = actual_chapters.intersection(pred_set)
    hit_rate = len(hits) / len(actual_chapters)

    # Marks-weighted coverage
    total_test_marks = sum(r.get("marks", 0.0) for r in test_records)
    covered_marks = sum(r.get("marks", 0.0) for r in test_records if r.get("chapter_id") in pred_set)
    marks_coverage = (covered_marks / total_test_marks * 100) if total_test_marks > 0 else 0.0

    return {
        "hit_rate": hit_rate,
        "marks_coverage": marks_coverage,
        "actual_count": len(actual_chapters),
        "predicted_count": len(predicted_chapters),
        "hits": len(hits)
    }


def main():
    parser = argparse.ArgumentParser(description="BD-ExamQ Baseline Prediction Experiments")
    parser.add_argument("--train-until", type=int, default=2022, help="Train cutoff year")
    parser.add_argument("--test-year", type=int, default=2023, help="Evaluation test year")
    parser.add_argument("--top-k", type=int, default=4, help="Top-k chapters to predict")
    args = parser.parse_args()

    samples_dir = PROJECT_ROOT / "data" / "samples"
    records = []
    for fp in samples_dir.glob("*.jsonl"):
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    train = [r for r in records if r.get("year", 0) <= args.train_until]
    test = [r for r in records if r.get("year", 0) == args.test_year]

    print("=" * 65)
    print(f"   🎯 BD-ExamQ TOPIC PREDICTION BASELINE EXPERIMENTS")
    print("=" * 65)
    print(f"Training set: <= {args.train_until} ({len(train)} questions)")
    print(f"Testing set : == {args.test_year} ({len(test)} questions)")
    print(f"Predicting Top-{args.top_k} chapters per model\n")

    actual_test_chapters = sorted(list({r["chapter_id"] for r in test}))
    print(f"Actual Chapters in {args.test_year} Exam: {actual_test_chapters}")
    print("-" * 65)

    # 1. Frequency Baseline
    freq_model = ChapterFrequencyModel()
    freq_model.fit(train)
    freq_preds = freq_model.predict(k=args.top_k)
    freq_eval = evaluate_predictions(freq_preds, test)

    print(f"1. Chapter Frequency Baseline:")
    print(f"   Predicted Chapters : {freq_preds}")
    print(f"   Chapter Hit Rate   : {freq_eval['hits']}/{freq_eval['actual_count']} ({freq_eval['hit_rate']*100:.1f}%)")
    print(f"   Marks-Weighted Cov : {freq_eval['marks_coverage']:.1f}%\n")

    # 2. Recency Heuristic
    rec_model = RecencyHeuristicModel()
    rec_model.fit(train)
    rec_preds = rec_model.predict(prev_year=args.train_until, k=args.top_k)
    rec_eval = evaluate_predictions(rec_preds, test)

    print(f"2. Recency Heuristic ('Not Asked in {args.train_until}'):")
    print(f"   Predicted Chapters : {rec_preds}")
    print(f"   Chapter Hit Rate   : {rec_eval['hits']}/{rec_eval['actual_count']} ({rec_eval['hit_rate']*100:.1f}%)")
    print(f"   Marks-Weighted Cov : {rec_eval['marks_coverage']:.1f}%\n")

    # 3. Markov Model
    prev_year_chapters = {r["chapter_id"] for r in train if r.get("year") == args.train_until}
    markov_model = MarkovTransitionModel()
    markov_model.fit(train)
    markov_preds = markov_model.predict(prev_year_chapters, k=args.top_k)
    markov_eval = evaluate_predictions(markov_preds, test)

    print(f"3. First-Order Markov Transition Model:")
    print(f"   Predicted Chapters : {markov_preds}")
    print(f"   Chapter Hit Rate   : {markov_eval['hits']}/{markov_eval['actual_count']} ({markov_eval['hit_rate']*100:.1f}%)")
    print(f"   Marks-Weighted Cov : {markov_eval['marks_coverage']:.1f}%")
    print("=" * 65)


if __name__ == "__main__":
    main()
