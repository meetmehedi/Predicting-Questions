# BD-ExamQ: Question Digitization and Annotation Guidelines

This document outlines the standard operating procedure (SOP) for digitizing, OCR-correcting, and annotating Secondary School Certificate (SSC) and Higher Secondary Certificate (HSC) board examination question papers in Bangladesh.

---

## 1. Corpus Hierarchy and Units of Analysis

Each question is treated as an autonomous unit:
- **Creative Question (CQ / সৃজনশীল প্রশ্ন):** Stored as **one record** containing an optional stimulus (`stem`) and **four linked sub-questions** (`sub_parts`: ক, খ, গ, ঘ). Do **not** split CQs into separate rows, because the semantic dependency between the stem and sub-parts (গ and ঘ) is an explicit research variable.
- **Multiple Choice Question (MCQ / বহুনির্বাচনী প্রশ্ন):** Stored as **one record** with `text_bn`, 4 choices (`options`), and the target `answer_key`. Context-based grouped MCQs must preserve the shared `stem`.
- **Traditional / Short Question:** Stored with question text and allotted marks.

---

## 2. Bangla OCR Clean-up & Text Formatting

Scanned question papers often yield degraded OCR outputs from Tesseract or other engines. Annotators must adhere to the following normalization guidelines:

### 2.1 Bengali Conjuncts (যুক্তবর্ণ) & Unicode Normalization
- All text **must** be normalized to standard **Unicode NFC** (Canonical Decomposition, followed by Canonical Composition).
- Correct typical OCR misrecognitions:
  - `ড়`, `ঢ়`, `য়` confused with `র`, `ড`, `ঢ`, `য`
  - Dari (`।` U+0964) confused with exclamation mark (`!`) or English vertical bar (`|`)
  - Bengali digits (`০`, `১`, `২`, `৩`, `৪`, `৫`, `৬`, `৭`, `৮`, `৯`) must be preserved in questions where they represent official numbering, but mathematical expressions should follow standard LaTeX.

### 2.2 Mathematical Expressions & Scientific Notation
- All mathematical equations, chemical formulas, and physical units must be wrapped in **LaTeX notation**:
  - Inline formulas: `$v = u + at$`, `$E = mc^2$`, `$\\frac{y^3 + ky^2 - 4}{y - 2}$`
  - Units: Use `\\text{}` inside math mode, e.g., `$10\\text{ ms}^{-2}$`, `$500\\text{ kg}$`
  - Chemical symbols: `$\\text{H}_2\\text{SO}_4$`, `$\\text{Fe}^{3+}$`

### 2.3 Diagrams, Figures & Multimodal Stimuli
- If a question includes a circuit diagram, geometric figure, graph, or flowchart:
  - Set `has_image: true`
  - Crop the diagram tightly from the high-resolution scan (300+ DPI) and save to `data/figures/{exam}_{year}_{board}_{subject}_{q_no}.png`.
  - Add the relative path to `image_paths`.
  - In `stem`, describe the diagram in brackets if an official text caption exists: `[চিত্রে প্রদর্শিত বর্তনী অনুসারে...]`.

---

## 3. Creative Question (CQ) Sub-Part Annotation

Every CQ must be annotated according to the NCTB Creative Question policy:

| Part | Name (Bengali) | Bloom's Cognitive Domain | Allotted Marks | Dependency on Stem (উদ্দীপক) |
|---|---|---|---|---|
| **ক** | জ্ঞানমূলক (Knowledge) | `knowledge` | 1 mark | Independent of the stem (direct textbook definition/fact). |
| **খ** | অনুধাবনমূলক (Comprehension) | `comprehension` | 2 marks | Generally independent of the stem (conceptual explanation). |
| **গ** | প্রয়োগমূলক (Application) | `application` | 3 marks | **Directly dependent on the stem** (calculation, execution). |
| **ঘ** | উচ্চতর দক্ষতামূলক (Higher Order) | `higher_order` | 4 marks | **Directly dependent on the stem** (synthesis, evaluation, justification). |

> **Note on Exceptions:** In SSC Mathematics and select subjects, marks are split as ক = 2, খ = 4, ঘ = 4 (sum = 10). Always set `marks` in each sub-part so that `sum(sub_parts.marks) == question.marks`.

---

## 4. NCTB Chapter & Topic Mapping

1. **Chapter ID (`chapter_id`):**
   - Look up the official NCTB textbook chapter from `data/metadata/sample_taxonomy.json`.
   - Format: `{SUBJECT_CODE}-CH{XX}`, e.g., `PHY1-CH02` (Physics 1st Paper, Chapter 2: Vectors).
2. **Multi-Chapter Questions (সংকর উদ্দীপক):**
   - If (গ) is from Chapter 2 and (ঘ) is from Chapter 4, set the primary `chapter_id` to the chapter governing the main stimulus / sub-part (ঘ), and annotate sub-part specific chapters inside `sub_parts[i].chapter_id`.
3. **Topic Tags (`topic_tags`):**
   - Supply 2 to 5 canonical keywords in Bengali describing core concepts (e.g. `["নদী-নৌকা", "লব্ধি বেগ", "সামান্তরিক সূত্র"]`).

---

## 5. Quality Control & Double-Annotation Protocol

To establish academic validity and report inter-annotator agreement in published papers:
1. **Double-Annotation Subset:** 10% of all digitized papers must be independently annotated by two domain experts.
2. **Agreement Metrics:**
   - **Chapter classification:** Report Cohen's Kappa ($\kappa$). Target threshold $\kappa \ge 0.85$.
   - **Topic classification:** Report macro-averaged F1 and Cohen's Kappa.
   - **OCR Word Error Rate (WER):** Sample 1,000 words per board/year and report Character Error Rate (CER) and Word Error Rate (WER) against raw OCR.
3. **Adjudication:** A third senior domain reviewer resolves any discrepancies between Annotator A and Annotator B.
