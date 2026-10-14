#!/usr/bin/env python3
"""
BD-ExamQ PDF Question Extractor
================================
Extracts and structures questions from downloaded BD board exam PDFs.

Workflow:
  1. Reads PDFs from data/raw/pdfs/
  2. Extracts text (via pdfplumber or PyMuPDF with OCR fallback)
  3. Parses MCQ (MCQ) and Creative Questions (CQ) using heuristics + regex
  4. Outputs structured JSONL to data/processed/questions.jsonl

Usage:
  python scripts/extract_questions_from_pdf.py [--input PATH] [--output PATH] [--exam all|HSC|SSC] [--verbose]
"""

import argparse
import json
import re
import sys
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc
from typing import Optional

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("extractor")

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW_PDF_DIR = ROOT / "data" / "raw" / "pdfs"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_JSONL = PROCESSED_DIR / "questions.jsonl"
MANIFEST_PATH = ROOT / "data" / "raw" / "manifest.json"

# ── Question patterns (Bengali + English) ────────────────────────────────────
# MCQ options: (ক) / (খ) / (গ) / (ঘ) or (a) / (b) / (c) / (d)
MCQ_OPTION_BN = re.compile(r"^\s*[(\[।]?\s*([কখগঘ])\s*[)\]।]?\s*(.+)", re.UNICODE)
MCQ_OPTION_EN = re.compile(r"^\s*[(\[।]?\s*([abcd])\s*[)\]।]?\s*(.+)", re.IGNORECASE)

# CQ sub-questions: a. / b. / c. / d. or ক. / খ. / গ. / ঘ.
CQ_SUB_BN = re.compile(r"^\s*([ক-ঘ])\s*[.)|।]\s*(.+)", re.UNICODE)
CQ_SUB_EN = re.compile(r"^\s*([a-d])\s*[.)|।]\s*(.+)", re.IGNORECASE)

# CQ stem markers
CQ_STEM_MARKERS = re.compile(
    r"(উদ্দীপক|সৃজনশীল|Creative Question|Stimulus|নিচের উদ্দীপক)",
    re.UNICODE | re.IGNORECASE,
)

# Header/Boilerplate filter
HEADER_PAT = re.compile(
    r"(board \d{4}|বোর্ড[- ]\d{4}|subject code|বিষয় কোড|full marks|পূর্ণমান|creative essay|সৃজনশীল প্রশ্ন|read the stems|time[s\s]*—|সময়[-—]|answer any|যে কোনো|দেওয়া আছে)",
    re.IGNORECASE | re.UNICODE,
)

# Generic question numbering: "১।", "1.", "প্রশ্ন ১", starting with 1-9 (never 0)
Q_NUM_BN = re.compile(r"^\s*([১-৯][০-৯]*)\s*[.)|।]\s*(.*)", re.UNICODE)
Q_NUM_EN = re.compile(r"^\s*([1-9]\d*)\s*[.)|।]\s*(.*)")
Q_HEADER = re.compile(r"(প্রশ্ন|Question)\s*[:#।]?\s*([১-৯][০-৯]*|\d+)", re.UNICODE | re.IGNORECASE)


def _bn_digit_to_int(s: str) -> Optional[int]:
    """Convert Bengali digit string to int."""
    bn = "০১২৩৪৫৬৭৮৯"
    try:
        return int("".join(str(bn.index(c)) if c in bn else c for c in s))
    except Exception:
        return None


def stable_id(text: str, source: str, idx: int) -> str:
    h = hashlib.md5(f"{source}|{idx}|{text[:80]}".encode()).hexdigest()[:10]
    return f"Q-{h}"


def try_import_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber
    except ImportError:
        return None


def try_import_pymupdf():
    try:
        import pymupdf  # preferred import name (PyMuPDF >= 1.24)
        return pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # legacy fallback
            return pymupdf
        except ImportError:
            return None


def _try_djvu_txt(pdf_path: Path) -> str:
    """Check for an Archive.org pre-OCR'd _djvu.txt sibling file."""
    djvu = pdf_path.with_suffix('').parent / (pdf_path.stem + "_djvu.txt")
    if djvu.exists():
        log.info(f"  📄 Using pre-OCR'd _djvu.txt: {djvu.name}")
        return djvu.read_text(encoding="utf-8", errors="replace")
    return ""


def _run_tesseract_ocr(pdf_path: Path) -> str:
    """Render PDF pages using PyMuPDF and run Tesseract OCR with Bengali + English."""
    import subprocess
    import tempfile
    import os

    tesseract_bin = "/opt/homebrew/bin/tesseract"
    if not os.path.exists(tesseract_bin):
        import shutil
        tesseract_bin = shutil.which("tesseract")
    if not tesseract_bin:
        return ""

    pymupdf = try_import_pymupdf()
    if not pymupdf:
        return ""

    try:
        doc = pymupdf.open(str(pdf_path))
        ocr_pages = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for idx, page in enumerate(doc):
                pix = page.get_pixmap(dpi=150)
                img_path = os.path.join(tmpdir, f"page_{idx}.png")
                pix.save(img_path)
                cmd = [tesseract_bin, img_path, "stdout", "-l", "ben+eng"]
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    ocr_pages.append(f"=== Page {idx+1} ===\n" + res.stdout.strip())
        if ocr_pages:
            log.info(f"  🔍 Tesseract OCR extracted {len(ocr_pages)} pages from {pdf_path.name}")
            return "\n\n".join(ocr_pages)
    except Exception as e:
        log.warning(f"  Tesseract OCR failed on {pdf_path.name}: {e}")
    return ""


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract raw text from PDF.
    Priority: pdfplumber → PyMuPDF → _djvu.txt sibling → Tesseract OCR → give up.
    Handles encrypted/image-only PDFs gracefully.
    """
    def _clean_text_check(t: str) -> str:
        # Strip common watermark URLs/boilerplate
        cleaned = re.sub(r"https?://\S+|www\.\S+|teachingbd\S*", "", t, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", "", cleaned)
        return cleaned

    pdfplumber = try_import_pdfplumber()
    if pdfplumber:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
            text = "\n".join(pages)
            if len(_clean_text_check(text)) > 200:
                log.debug(f"  pdfplumber extracted {len(text)} chars from {pdf_path.name}")
                return text
            else:
                log.info(f"  pdfplumber got only boilerplate/watermarks from {pdf_path.name} — triggering OCR")
        except Exception as e:
            log.warning(f"  pdfplumber failed on {pdf_path.name}: {e}")

    pymupdf = try_import_pymupdf()
    if pymupdf:
        try:
            doc = pymupdf.open(pdf_path)
            if not doc.is_encrypted:
                pages = [doc[i].get_text() for i in range(len(doc))]
                text = "\n".join(pages)
                if len(_clean_text_check(text)) > 200:
                    log.debug(f"  PyMuPDF extracted {len(text)} chars from {pdf_path.name}")
                    return text
        except Exception as e:
            log.warning(f"  PyMuPDF failed on {pdf_path.name}: {e}")

    # Fallback 1: Archive.org pre-OCR'd DjVu text
    djvu_text = _try_djvu_txt(pdf_path)
    if len(_clean_text_check(djvu_text)) > 200:
        return djvu_text

    # Fallback 2: Local Tesseract Bengali+English OCR for scanned board papers
    ocr_text = _run_tesseract_ocr(pdf_path)
    if ocr_text.strip():
        return ocr_text

    log.error(f"  Could not extract text from {pdf_path.name}.")
    return ""


def infer_metadata_from_path(pdf_path: Path) -> dict:
    """
    Infer exam/year/board/subject from folder hierarchy:
    data/raw/pdfs/<EXAM>/<YEAR>/<BOARD>/filename.pdf
    """
    parts = pdf_path.parts
    meta = {"exam": None, "year": None, "board": None, "subject": None}
    try:
        raw_idx = parts.index("pdfs")
        if raw_idx + 1 < len(parts):
            meta["exam"] = parts[raw_idx + 1]
        if raw_idx + 2 < len(parts):
            try:
                meta["year"] = int(parts[raw_idx + 2])
            except ValueError:
                pass
        if raw_idx + 3 < len(parts):
            meta["board"] = parts[raw_idx + 3]
    except ValueError:
        pass

    # Subject from filename
    name = pdf_path.stem.upper()
    subjects = {
        "PHY": "Physics", "CHEM": "Chemistry", "BIO": "Biology",
        "MATH": "Mathematics", "ICT": "ICT", "ENG": "English",
        "BAN": "Bengali", "BANGLA": "Bengali",
    }
    for key, val in subjects.items():
        if key in name:
            meta["subject"] = val
            break

    return meta


def parse_lines_to_questions(lines: list[str], meta: dict, source_file: str) -> list[dict]:
    """
    Heuristic parser: groups lines into question blocks and classifies them into CQ or MCQ.
    Extracts structured stimulus/stem and sub-questions (a, b, c, d) for CQ, and options for MCQ.
    """
    records = []
    current_q_lines = []
    current_type = "unknown"
    q_idx = 0

    def flush(block: list[str]):
        nonlocal q_idx
        text = "\n".join(block).strip()
        if len(text) < 15:
            return

        # Check if block is purely boilerplate/header
        non_header_lines = [l for l in block if not HEADER_PAT.search(l) and not l.startswith("===")]
        if not non_header_lines:
            return

        # Detect CQ sub-questions
        subs = []
        cur_sub_part = None
        cur_sub_text = []

        # Detect MCQ options
        mcq_opts = []

        stem_lines = []

        for line in block:
            m_cq = CQ_SUB_BN.match(line) or CQ_SUB_EN.match(line)
            m_mcq = MCQ_OPTION_BN.match(line) or MCQ_OPTION_EN.match(line)

            # In BD exams, if a line has marks at the end (e.g. "1", "২", "3", "৪") or letters a-d, it's CQ
            has_marks_suffix = bool(re.search(r"[\s\t]+[1-4১-৪][\s\t]*$", line))

            if m_cq and (has_marks_suffix or cur_sub_part is not None or m_cq.group(1).lower() in ["a", "b", "c", "d", "ক", "খ", "গ", "ঘ"]):
                if cur_sub_part:
                    subs.append({"part": cur_sub_part, "text": " ".join(cur_sub_text).strip()})
                cur_sub_part = m_cq.group(1).lower()
                cur_sub_text = [m_cq.group(2).strip()]
            elif cur_sub_part:
                cur_sub_text.append(line)
            else:
                if m_mcq and not has_marks_suffix:
                    mcq_opts.append(m_mcq.group(2).strip())
                stem_lines.append(line)

        if cur_sub_part:
            subs.append({"part": cur_sub_part, "text": " ".join(cur_sub_text).strip()})

        # Classification
        if len(subs) >= 2 or any(s["part"] in ["c", "d", "গ", "ঘ"] for s in subs):
            qtype = "CQ"
        elif len(mcq_opts) >= 3:
            qtype = "MCQ"
        elif CQ_STEM_MARKERS.search(text):
            qtype = "CQ"
        else:
            qtype = "CQ" if len(subs) > 0 else "MCQ"

        q_idx += 1
        stem_text = "\n".join(stem_lines).strip()
        record = {
            "id": stable_id(text, source_file, q_idx),
            "exam": meta.get("exam"),
            "year": meta.get("year"),
            "board": meta.get("board"),
            "subject": meta.get("subject"),
            "paper": meta.get("paper"),
            "question_type": qtype,
            "question_text": text,
            "stem": stem_text if stem_text else text,
            "sub_questions": subs if qtype == "CQ" else [],
            "options": mcq_opts[:4] if qtype == "MCQ" else [],
            "answer": None,
            "marks": 10 if qtype == "CQ" else 1,
            "topic": None,
            "chapter": None,
            "source_file": source_file,
            "extracted_at": datetime.now(UTC).isoformat(),
        }
        records.append(record)

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("==="):
            continue

        # Skip standalone header lines before first question
        if not current_q_lines and HEADER_PAT.search(line):
            continue

        is_q_num = Q_NUM_BN.match(line) or Q_NUM_EN.match(line) or Q_HEADER.match(line)

        if is_q_num:
            if current_q_lines:
                flush(current_q_lines)
            current_q_lines = [line]
        else:
            current_q_lines.append(line)

    if current_q_lines:
        flush(current_q_lines)

    return records


def process_pdf(pdf_path: Path, verbose: bool = False) -> list[dict]:
    """Full pipeline: extract → parse → return structured records."""
    resolved_path = pdf_path.resolve()
    rel_path_str = str(resolved_path.relative_to(ROOT)) if resolved_path.is_relative_to(ROOT) else pdf_path.name
    log.info(f"Processing: {rel_path_str}")
    text = extract_text_from_pdf(pdf_path)
    if not text.strip():
        log.warning(f"  No text extracted from {pdf_path.name} — may need OCR")
        return []

    meta = infer_metadata_from_path(resolved_path)
    if verbose:
        log.info(f"  Metadata: {meta}")

    lines = text.split("\n")
    records = parse_lines_to_questions(lines, meta, rel_path_str)
    log.info(f"  ✓ {len(records)} question blocks found")
    return records


def main():
    parser = argparse.ArgumentParser(description="BD-ExamQ PDF Question Extractor")
    parser.add_argument("--input", default=str(RAW_PDF_DIR), help="PDF input directory")
    parser.add_argument("--output", default=str(OUTPUT_JSONL), help="Output JSONL file")
    parser.add_argument("--exam", default="all", choices=["all", "HSC", "SSC"])
    parser.add_argument("--subject", default="all", help="Filter by subject name")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max PDFs to process (0 = all)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker processes")
    parser.add_argument("--no-resume", action="store_true", help="Do not resume, re-extract everything")
    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.DEBUG)

    input_dir = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Collect PDFs
    input_path = Path(args.input)
    if input_path.is_file():
        pdfs = [input_path]
    else:
        pdfs = sorted(input_path.rglob("*.pdf"))
    if args.exam != "all":
        pdfs = [p for p in pdfs if args.exam in p.parts]
    if args.subject != "all":
        pdfs = [p for p in pdfs if args.subject.lower() in p.stem.lower()]
    if args.limit > 0:
        pdfs = pdfs[: args.limit]

    # Resume support: identify PDFs already extracted
    seen_sources = set()
    existing_records = []
    if not args.no_resume and output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        existing_records.append(rec)
                        if rec.get("source_file"):
                            seen_sources.add(rec["source_file"])
            log.info(f"Loaded {len(existing_records)} existing records from {len(seen_sources)} sources.")
        except Exception as e:
            log.warning(f"Could not read existing output: {e}")

    pending_pdfs = []
    for p in pdfs:
        resolved = p.resolve()
        rel_str = str(resolved.relative_to(ROOT)) if resolved.is_relative_to(ROOT) else p.name
        if rel_str not in seen_sources:
            pending_pdfs.append(p)

    print(f"\n{'='*60}")
    print("  📄 BD-ExamQ PDF Question Extractor")
    print(f"{'='*60}")
    print(f"  Input       : {input_dir}")
    print(f"  Output      : {output_path}")
    print(f"  Exam        : {args.exam}")
    print(f"  Total PDFs  : {len(pdfs)} found")
    print(f"  Cached PDFs : {len(pdfs) - len(pending_pdfs)} already extracted")
    print(f"  Pending PDFs: {len(pending_pdfs)} to extract (using {args.workers} workers)")
    print(f"{'='*60}\n")

    if not pending_pdfs:
        print("✨ All PDFs are already extracted! Use --no-resume to re-extract.")
    else:
        import concurrent.futures
        from tqdm import tqdm

        new_records = []
        mode = "a" if not args.no_resume and output_path.exists() else "w"
        with open(output_path, mode, encoding="utf-8") as out_f:
            if args.workers > 1 and len(pending_pdfs) > 1:
                with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as executor:
                    future_to_pdf = {executor.submit(process_pdf, p, args.verbose): p for p in pending_pdfs}
                    for future in tqdm(concurrent.futures.as_completed(future_to_pdf), total=len(pending_pdfs), desc="Extracting"):
                        try:
                            recs = future.result()
                            for r in recs:
                                out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
                            out_f.flush()
                            new_records.extend(recs)
                        except Exception as exc:
                            pdf = future_to_pdf[future]
                            log.error(f"Failed processing {pdf.name}: {exc}")
            else:
                for pdf_path in tqdm(pending_pdfs, desc="Extracting"):
                    recs = process_pdf(pdf_path, verbose=args.verbose)
                    for r in recs:
                        out_f.write(json.dumps(r, ensure_ascii=False) + "\n")
                    out_f.flush()
                    new_records.extend(recs)

        existing_records.extend(new_records)

    # Summary
    all_records = existing_records
    exam_counts = {}
    type_counts = {}
    year_counts = {}
    for r in all_records:
        exam_counts[r.get("exam", "?")] = exam_counts.get(r.get("exam", "?"), 0) + 1
        type_counts[r.get("question_type", "?")] = type_counts.get(r.get("question_type", "?"), 0) + 1
        yr = str(r.get("year", "?"))
        year_counts[yr] = year_counts.get(yr, 0) + 1

    print(f"\n{'='*60}")
    print(f"  ✅ Extraction Complete")
    print(f"{'='*60}")
    print(f"  Total questions : {len(all_records)}")
    print(f"  By exam         : {exam_counts}")
    print(f"  By type         : {type_counts}")
    print(f"  By year         : {dict(sorted(year_counts.items()))}")
    print(f"  Output file     : {output_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
