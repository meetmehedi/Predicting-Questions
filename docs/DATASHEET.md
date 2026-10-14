# Datasheet for BD-ExamQ Corpus

*Following the framework proposed by Gebru et al., "Datasheets for Datasets", CACM 2021.*

---

## 1. Motivation

### For what purpose was the dataset created?
BD-ExamQ was created to enable rigorous, academic-grade research in Educational Data Mining (EDM), Natural Language Processing for low-resource languages (Bengali), and Automated Question Generation/Analysis within the context of Bangladesh's national examination system (SSC and HSC). It provides a structured benchmark for analyzing syllabus coverage, topic recurrence patterns, Bloom's cognitive taxonomy balance, and cross-board question migration.

### Who created the dataset and who funded it?
Initiated by educational data science and NLP researchers in Bangladesh.

---

## 2. Composition

### What do the instances represent?
Each instance represents an individual examination question administered in the official Secondary School Certificate (SSC) or Higher Secondary Certificate (HSC) board examinations in Bangladesh. For Creative Questions (CQ), each instance encapsulates the complete stimulus (উদ্দীপক) along with its four constituent sub-questions (ক, খ, গ, ঘ).

### How many instances are there?
- Pilot release: Curated gold-standard records across HSC Physics, HSC ICT, and SSC General Mathematics.
- Full target corpus: >50,000 digitized questions spanning 2010 to present across all 11 education boards.

### What data does each instance contain?
- Metadata: Exam level, year, education board, subject code, paper, set, allocated marks, time.
- Linguistic content: Bengali text, optional English version text, stimulus/stem, LaTeX mathematical/chemical notation, image paths for figures.
- Structured sub-components: 4 sub-parts (CQ) or 4 choices + answer key (MCQ).
- Pedagogical annotations: NCTB chapter ID, topic tags, Bloom's cognitive domain, curriculum phase.
- Quality indicators: OCR confidence score and verification tier.

---

## 3. Collection Process

### How were the data acquired?
Publicly archived past board examination papers released after examination completion by official education boards, educational web portals, and standard NCTB textbooks.

### Did the collection process involve human subjects?
No personal or student data is involved. All examination papers are historical public documents.

---

## 4. Preprocessing and Cleaning

### What preprocessing was performed?
1. Scanned PDFs processed via OCR (Tesseract / high-performance document vision models).
2. Unicode text normalized to NFC format.
3. Mathematical formulas and tables manually transcribed into LaTeX syntax.
4. Pedagogical annotations (Chapter, Topic, Bloom's level) reviewed by domain experts.

---

## 5. Uses

### What tasks is the corpus intended for?
1. Predicting topic and chapter appearance likelihood in future exam cycles (macro forecasting).
2. Cognitive taxonomy classification and question difficulty estimation.
3. Cross-board question similarity detection and paraphrase retrieval.
4. Curriculum-grounded educational question generation.

### What should the corpus NOT be used for?
The corpus is **NOT** designed to facilitate cheating, illegal question leaking, or commercial exploitation. It is strictly for retrospective educational analytics and computational linguistics.

---

## 6. Distribution & Ethics

### How is the dataset distributed?
Distributed as standardized open-source JSON Lines (`.jsonl`) files alongside data validation, analysis, and benchmark scripts.

### Ethical Considerations & Exam Leak Framing
- Examination security is of utmost importance in Bangladesh.
- To prevent misuse or misunderstanding:
  - This research explicitly models **high-level chapter and topic recurrence distributions**, not verbatim question guessing.
  - Board examinations test students on a bounded syllabus; predicting that a fundamental topic (e.g., "Vectors" or "Newtonian Mechanics") will appear on an exam is standard educational forecasting comparable to syllabus blueprint design.
  - The corpus is intended to help teachers, test designers, and curriculum developers identify blind spots, repetitive patterns, and inequities in test design.
