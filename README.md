# BD-ExamQ: Bangladesh Secondary & Higher Secondary Board Examination Question Corpus

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Pydantic v2](https://img.shields.io/badge/pydantic-v2-green.svg)](https://docs.pydantic.dev/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

An academic-grade, multimodal research corpus and benchmarking framework designed for analyzing and forecasting examination questions in the **Secondary School Certificate (SSC)** and **Higher Secondary Certificate (HSC)** national board exams of Bangladesh.

---

## 📌 Research Overview

In Bangladesh, national secondary education culminates in centralized board examinations administered across 11 education boards. Predicting examination questions is framed not as predicting exact verbatim sentences, but rather as **probabilistic topic forecasting, cognitive taxonomy balance analysis, and cross-board pattern retrieval**:

1. **Chapter & Topic Forecasting:** Estimating the likelihood distribution $P(\text{Chapter} \mid \text{History})$ that specific syllabus sections will be examined in year $t+1$.
2. **Cognitive Balance (Bloom's Taxonomy):** Quantifying the distribution of marks across Knowledge (জ্ঞান), Comprehension (অনুধাবন), Application (প্রয়োগ), and Higher-Order Thinking (উচ্চতর দক্ষতা).
3. **Cross-Board Question Migration:** Measuring recurrence and semantic similarity between questions from different boards across consecutive examination cycles.
4. **NCTB Textbook Grounding:** Benchmarking question generation models conditioned on official curriculum learning outcomes (শিখনফল).

---

## 📂 Repository Structure

```
.
├── README.md                      # Primary research overview and documentation
├── idea.md                        # Original architectural blueprint & research framing
├── requirements.txt               # Locked dependencies (pydantic, pandas, scikit-learn, etc.)
│
├── schema/                        # Formal data schemas and Pydantic v2 validation models
│   ├── models.py                  # Pydantic models (QuestionRecord, SubQuestion, MCQOption, ExamPaper)
│   ├── export_json_schema.py      # Script generating portable JSON Schemas
│   ├── question_schema.json       # Exported JSON Schema for QuestionRecord
│   └── exam_paper_schema.json     # Exported JSON Schema for complete ExamPaper
│
├── data/
│   ├── metadata/                  # Authoritative education metadata and taxonomy
│   │   ├── boards.json            # Catalog of all 11 BD education boards
│   │   ├── subjects.json          # Subject codes, papers, marks breakdown, practicals
│   │   ├── curriculum_timeline.json # Structural shifts & covariates (CQ rollout, COVID, etc.)
│   │   ├── download_sources.json  # Catalog of verified question PDF download sources
│   │   └── sample_taxonomy.json   # NCTB chapter and topic hierarchy for pilot subjects
│   ├── samples/                   # Curated gold-standard pilot dataset
│   │   ├── hsc_physics_cq.jsonl   # HSC Physics 1st Paper CQs with LaTeX & Bengali
│   │   ├── hsc_ict_cq.jsonl       # HSC ICT Creative Questions
│   │   ├── ssc_math_cq.jsonl      # SSC General Mathematics Creative Questions
│   │   ├── ssc_math_mcq.jsonl     # SSC General Math MCQs (single, completion, context-based)
│   │   └── pilot_corpus.csv       # Tabular flattened CSV export for spreadsheets/pandas
│   └── raw/                       # Storage for raw scanned PDFs and image stimuli
│       ├── manifest.json          # Automated provenance log (SHA256, source URLs, timestamps)
│       ├── pdfs/                  # Downloaded question PDFs organized by Exam/Year/Board
│       └── README.md              # OCR intake conventions and directory guides
│
├── scripts/                       # Tooling, evaluation, and baseline pipeline
│   ├── question_downloader.py     # Automated bot downloading past papers from web & archives
│   ├── validate_corpus.py         # Validates question records against schema and metadata rules
│   ├── corpus_stats.py            # Generates academic corpus analytics & distributions
│   ├── temporal_split.py          # Partitions data chronologically (<= t vs t+1) without leakage
│   ├── baselines.py               # Implements 3 baselines: Frequency, Recency heuristic, Markov model
│   └── data_exporter.py           # Exports JSONL records into flattened CSV & tabular datasets
│
└── docs/                          # Detailed research protocols and methodology documentation
    ├── ANNOTATION_GUIDELINE.md    # Standard Operating Procedure for digitization & annotation
    ├── RESEARCH_TASKS.md          # Formal mathematical formulation of 4 benchmark tasks
    └── DATASHEET.md               # Gebru et al. Datasheet for Datasets & Ethics statement
```

---

## 🚀 Quickstart

### 1. Environment Setup
```bash
# Clone the repository and navigate to project root
cd "Predicting question "

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Past Question Papers via Bot
Use the automated downloading bot to fetch past board exam papers:
```bash
# Launch interactive downloader wizard
python scripts/question_downloader.py --interactive

# Or download verified past papers via CLI arguments:
python scripts/question_downloader.py --exam HSC --subject Physics --max-files 5

# Download SSC papers from specific year and board:
python scripts/question_downloader.py --exam SSC --year 2010 --board Dhaka

# Scrape all PDF question papers from an educational portal URL:
python scripts/question_downloader.py --source scrape_url --url "https://example.com/hsc-physics" --exam HSC
```

### 3. Validate Dataset
Validate JSONL records against structural rules (marks summation, valid boards, subject codes, Bloom's levels):
```bash
python scripts/validate_corpus.py
```

### 3. Compute Corpus Descriptive Statistics
Generate comprehensive distribution metrics, Bloom's domain breakdown, and chapter coverage:
```bash
python scripts/corpus_stats.py
```

### 4. Run Baseline Topic Prediction Experiments
Evaluate the 3 core baselines (Historical Frequency, Recency Heuristic, First-Order Markov Model) using strict temporal splits:
```bash
python scripts/baselines.py --train-until 2022 --test-year 2023 --top-k 4
```

### 5. Export to CSV / Spreadsheets
Flatten nested CQs and MCQs into an Excel-friendly CSV format:
```bash
python scripts/data_exporter.py
```

---

## 📋 Data Record Specification

Every question record contains both raw text and rich pedagogical annotations. Creative Questions (CQ) preserve their internal 4-part hierarchy:

```json
{
  "id": "HSC-2023-DHA-PHY1-CQ-02",
  "exam": "HSC",
  "year": 2023,
  "board": "Dhaka",
  "subject": "Physics",
  "subject_code": "174",
  "paper": "1st",
  "set": "Ka",
  "q_type": "CQ",
  "question_no": 2,
  "marks": 10.0,
  "stem": "চিত্রে একটি নদীর প্রস্থ $d = 500\\text{ m}$। স্রোতের বেগ $u = 3\\text{ km/h}$...",
  "has_image": true,
  "image_paths": ["figures/hsc_2023_dha_phy1_q2.png"],
  "sub_parts": [
    {
      "part": "ক",
      "cognitive_domain": "knowledge",
      "marks": 1,
      "text_bn": "একক ভেক্টর কাকে বলে?",
      "chapter_id": "PHY1-CH02"
    },
    {
      "part": "খ",
      "cognitive_domain": "comprehension",
      "marks": 2,
      "text_bn": "দুটি সমমানের ভেক্টরের লব্ধি এদের যেকোনো একটির সমান হতে পারে কি? ব্যাখ্যা কর।",
      "chapter_id": "PHY1-CH02"
    },
    {
      "part": "গ",
      "cognitive_domain": "application",
      "marks": 3,
      "text_bn": "শান্তনুর নৌকার যাত্রা কোণ $\\alpha_1$ নির্ণয় কর।",
      "chapter_id": "PHY1-CH02"
    },
    {
      "part": "ঘ",
      "cognitive_domain": "higher_order",
      "marks": 4,
      "text_bn": "উদ্দীপকে উল্লেখিত দুই মাঝির মধ্যে কার নদী পার হতে কম সময় লাগবে? গাণিতিক যুক্তি সহ বিশ্লেষণ কর।",
      "chapter_id": "PHY1-CH02"
    }
  ],
  "chapter_id": "PHY1-CH02",
  "chapter_name_bn": "ভেক্টর",
  "topic_id": "PHY1-CH02-TOP02",
  "topic_tags": ["নদী-নৌকা", "লব্ধি বেগ", "ন্যূনতম দূরত্ব"],
  "bloom_level": "mixed",
  "curriculum_phase": "covid_short_2022_2023",
  "ocr_confidence": 0.98,
  "verification_status": "gold_verified"
}
```

---

## 🔬 Benchmark Tasks & Modeling Approaches

| Task | Objective | Primary Metric |
|---|---|---|
| **Task 1: Topic Forecasting** | Predict which chapters will be examined in year $t+1$ | Top-$k$ Hit Rate, Marks Coverage |
| **Task 2: Cognitive Weighting** | Predict marks distribution across Bloom's levels | Earth Mover's Distance (EMD), MAE |
| **Task 3: Cross-Board Similarity** | Retrieve similar/precursor questions across boards | Recall@K, MAP@K, NDCG@K |
| **Task 4: Question Generation** | Synthesize valid CQ/MCQ from textbook sections | Perplexity, Human Expert Evaluation |

See [docs/RESEARCH_TASKS.md](docs/RESEARCH_TASKS.md) for detailed mathematical formulations.

---

## ⚖️ Ethics and Legal Notice

- **Public Good & Educational Research:** This project is intended solely for scientific research in natural language processing, educational assessment design, and curriculum analytics.
- **Anti-Cheat & Anti-Leak Standard:** BD-ExamQ strictly analyzes **retrospective historical patterns** and macro-level topic probabilities. It cannot and should not be used for illicit question prediction or commercial exam tampering.
- For complete disclosures, see [docs/DATASHEET.md](docs/DATASHEET.md).
