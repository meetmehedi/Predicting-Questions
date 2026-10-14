#!/usr/bin/env python3
"""Corpus validation tool for BD-ExamQ.
Validates question records in JSON/JSONL against Pydantic models and structural rules:
- Schema conformance
- CQ marks summation (ক+খ+গ+ঘ == total marks)
- Valid board names from metadata/boards.json
- Valid subjects from metadata/subjects.json
- OCR confidence bounds
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schema.models import QuestionRecord, ExamPaper


def load_metadata_lookups():
    boards_path = PROJECT_ROOT / "data" / "metadata" / "boards.json"
    subjects_path = PROJECT_ROOT / "data" / "metadata" / "subjects.json"
    
    valid_boards = set()
    if boards_path.exists():
        with open(boards_path, "r", encoding="utf-8") as f:
            valid_boards = {b["name_en"] for b in json.load(f)}
            
    valid_subjects = set()
    if subjects_path.exists():
        with open(subjects_path, "r", encoding="utf-8") as f:
            valid_subjects = {s["subject"] for s in json.load(f)}
            
    return valid_boards, valid_subjects


def validate_file(file_path: Path, valid_boards: set, valid_subjects: set) -> Dict[str, Any]:
    print(f"\n🔍 Validating: {file_path.relative_to(PROJECT_ROOT)}")
    total = 0
    valid_count = 0
    errors: List[Dict[str, Any]] = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                data = json.loads(line)
            except Exception as e:
                errors.append({"line": line_num, "id": "UNKNOWN", "error": f"JSON decode error: {e}"})
                continue

            record_id = data.get("id", f"line_{line_num}")
            
            # Pydantic validation
            try:
                record = QuestionRecord.model_validate(data)
                
                # Metadata consistency check
                if valid_boards and record.board.value not in valid_boards:
                    errors.append({
                        "line": line_num,
                        "id": record_id,
                        "error": f"Board '{record.board.value}' not found in official boards metadata"
                    })
                    continue

                if valid_subjects and record.subject not in valid_subjects:
                    errors.append({
                        "line": line_num,
                        "id": record_id,
                        "error": f"Subject '{record.subject}' not found in official subjects metadata"
                    })
                    continue

                valid_count += 1
            except Exception as e:
                errors.append({"line": line_num, "id": record_id, "error": str(e)})

    return {
        "file": str(file_path.relative_to(PROJECT_ROOT)),
        "total": total,
        "valid": valid_count,
        "errors": errors
    }


def main():
    valid_boards, valid_subjects = load_metadata_lookups()
    samples_dir = PROJECT_ROOT / "data" / "samples"
    
    target_files = list(samples_dir.glob("*.jsonl"))
    if not target_files:
        print("No .jsonl sample files found in data/samples/")
        sys.exit(1)

    all_passed = True
    total_records = 0
    total_valid = 0

    for file_path in target_files:
        result = validate_file(file_path, valid_boards, valid_subjects)
        total_records += result["total"]
        total_valid += result["valid"]

        if result["errors"]:
            all_passed = False
            print(f"❌ Found {len(result['errors'])} errors in {result['file']}:")
            for err in result["errors"]:
                print(f"   [Line {err['line']}] ID: {err['id']} -> {err['error']}")
        else:
            print(f"✅ All {result['valid']}/{result['total']} records valid!")

    print("\n" + "=" * 50)
    print(f"Validation Summary: {total_valid}/{total_records} valid records ({(total_valid/total_records)*100:.1f}%)")
    print("=" * 50)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
