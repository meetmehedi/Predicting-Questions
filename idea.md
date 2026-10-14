Here's a design for an academic-grade corpus covering both HSC and SSC, all subjects.

## Framing the research question

"Predicting questions" is hard to defend as stated, because exact questions rarely repeat. Papers in this area usually predict at a coarser level, which is also easier to evaluate:

1. **Topic/chapter prediction:** which chapters or topics will be examined next year?
2. **Question-type and marks-weight prediction:** how will marks be distributed?
3. **Question-level similarity:** how closely will new questions resemble past ones (paraphrase, template reuse)?
4. **Question generation:** generate plausible questions from the NCTB textbook, then test them against the real paper.

I'd suggest 1 and 3 as the core, with 4 as an extension.

## Corpus components

| Layer | Content | Likely source |
|---|---|---|
| Questions | Past papers, 2010 to the latest year, all boards (Dhaka, Chattogram, Rajshahi, Cumilla, Jashore, Barishal, Sylhet, Dinajpur, Mymensingh, Madrasah, Technical) | Board websites, education portals, archives |
| Textbooks | NCTB books by class, subject, and edition | NCTB website |
| Syllabus and rules | Syllabus documents, marks distribution, pattern circulars, short-syllabus notices | NCTB, Ministry of Education, board notices |
| Metadata | Year, board, exam, subject, paper, set, marks, time | Derived |
| Annotations | Chapter/topic label, question type (MCQ, creative/CQ, short), cognitive level (Bloom's) | Manual and semi-automatic |

## Suggested record schema

Each question gets one row with these fields: `id`, `exam` (SSC/HSC), `year`, `board`, `subject`, `paper`, `set`, `q_type`, `marks`, `text_bn`, `text_en` (if applicable), `stem` (for creative questions), `sub_parts` (knowledge, comprehension, application, higher-order), `chapter_id`, `topic_id`, `bloom_level`, `source_url`, and `ocr_confidence`.

Creative questions (CQ) should be stored as a stem plus four linked sub-questions, not flattened, since the structure is itself a research variable.

## Main challenges to plan for

- **Bangla OCR quality:** many sources are scanned PDFs, so you'll need OCR (Tesseract with Bangla models or a stronger alternative) plus a manually verified sample to report error rates.
- **Structural shifts:** the CQ system was introduced in stages, there were COVID-era disruptions (2020 and 2021 cancelled or altered exams, 2022 short syllabus), and there is the ongoing curriculum transition. Treat these as covariates, not noise, and check the exact details against official notices.
- **Coverage gaps:** older papers and some boards are patchy online. Document the missingness explicitly.
- **Copyright and permissions:** board papers are public, but redistribution terms are unclear. Plan to release metadata plus scripts, or seek permission from the boards, rather than assuming you can republish the text.
- **Leak and ethics concerns:** question leaks are a serious issue in Bangladesh. Framing the work as topic-level analysis and stating that explicitly in the paper will help with ethics review and public reception.

## Evaluation design

- Use **temporal splits** (train on years up to *t*, test on *t+1*) to avoid leakage from future papers.
- **Baselines:** frequency by chapter, a "not asked recently" recency heuristic, and a simple Markov model, before any neural model.
- **Metrics:** top-k chapter hit rate, marks-weighted coverage, and for similarity, embedding-based or BM25 retrieval recall.

## Suggested phases

1. **Pilot:** 3 to 4 subjects, 2 boards, 5 years, to test the schema, OCR, and annotation guidelines.
2. **Scale-up:** all boards and subjects, with the annotation protocol and inter-annotator agreement (Cohen's kappa) on a double-labelled subset.
3. **Analysis and baselines:** descriptive statistics, then the prediction experiments.
4. **Release:** datasheet for the dataset, the schema, and the scripts.

Next, I can write the annotation guidelines and chapter taxonomy template, draft the schema as a ready-to-use spreadsheet or JSON, or outline the paper's literature review and related work. Which would you like first?