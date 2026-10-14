"""Utility script to export QuestionRecord and ExamPaper Pydantic schemas to standard JSON Schema."""
import json
from pathlib import Path
from schema.models import QuestionRecord, ExamPaper


def export_schemas():
    output_dir = Path(__file__).resolve().parent
    
    question_schema = QuestionRecord.model_json_schema()
    question_schema_path = output_dir / "question_schema.json"
    with open(question_schema_path, "w", encoding="utf-8") as f:
        json.dump(question_schema, f, indent=2, ensure_ascii=False)
    print(f"Exported question schema to {question_schema_path}")

    paper_schema = ExamPaper.model_json_schema()
    paper_schema_path = output_dir / "exam_paper_schema.json"
    with open(paper_schema_path, "w", encoding="utf-8") as f:
        json.dump(paper_schema, f, indent=2, ensure_ascii=False)
    print(f"Exported exam paper schema to {paper_schema_path}")


if __name__ == "__main__":
    export_schemas()
