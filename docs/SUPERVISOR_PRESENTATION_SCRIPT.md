# Supervisor Presentation Script: BD-ExamQ Corpus & Forecasting Methodology

**Document:** Complete Presentation & Defense Script  
**Target Duration:** 10–12 Minutes (+ Q&A)  
**Accompanying Material:** `docs/BD_ExamQ_Corpus_Report.pdf` (Figures 1–4)

---

## ⏱️ Meeting Agenda & Time Allocation

| Phase | Time | Topic & Key Focus | Report Reference |
|---|---|---|---|
| **1. Hook & Motivation** | 0:00 – 1:30 | Why this problem matters; why verbatim prediction fails | Page 1, Sec 1 |
| **2. The Corpus (BD-ExamQ)** | 1:30 – 4:00 | Dataset scale, Creative Question anatomy, 9 boards, 15 yrs | Pages 2–5, Fig 1–3 |
| **3. Proposed Methodology** | 4:00 – 7:30 | 4-Stage Hierarchical Forecasting Engine | Pages 6–8, Fig 4 |
| **4. Experiments & Baselines** | 7:30 – 9:30 | Leak-free temporal splits, metrics, and initial findings | Pages 9–11, Tab 3–4 |
| **5. Roadmap & Ask** | 9:30 – 11:00 | Immediate next steps, compute/feedback needed | Page 12, Sec 7 |
| **6. Q&A Defense** | 11:00+ | Anticipated supervisor challenges & model answers | Section 6 below |

---

## 🎙️ Spoken Presentation Script

### 1. Introduction & Research Motivation (1.5 mins)
> *"Good morning/afternoon, Professor.*  
>
> *Today I want to present **BD-ExamQ**, the first large-scale, longitudinal benchmark corpus for standardized secondary and higher secondary examinations in Bangladesh, along with a formal **Hierarchical Forecasting Framework**.*
>
> *When students and educators ask 'Which questions will appear on the exam?', conventional thinking treats this as memorization or guesswork. From a machine learning perspective, **verbatim question prediction is ill-posed and practically brittle**: examination committees deliberately paraphrase stems, alter numerical figures, and swap sub-topics to reward conceptual mastery.*
>
> *However, exam boards operate under statutory curriculum guidelines from NCTB. They must satisfy group syllabus balance, adhere to Bloom's four-tier cognitive hierarchy, and rotate topics cyclically. Our research formalizes this not as casual text generation, but as a **constrained, multi-scale educational forecasting problem**."*

---

### 2. The BD-ExamQ Corpus & Anatomy (2.5 mins)
*(Refer to **Figure 1** on page 4 and **Figure 3** on page 7)*

> *"To ground this task, we built **BD-ExamQ**, curated from 15 consecutive examination years (2010–2024) across all **9 General Education Boards**.*
>
> **Key Dataset Metrics:**
> - **545** complete, verified board examination papers.
> - **15,307** individual question items, representing **56,149 marks**.
> - Science, Commerce, and Humanities streams across Grade 10 (SSC) and Grade 12 (HSC).
>
> **The Creative Question (CQ) Structure (Figure 1):**
> *Unlike western multiple-choice benchmarks, Bangladeshi exams use the **Srijonshil (Creative Question)** system:*
> - Every CQ begins with an **unseen stimulus stem (Uddipak)**—a real-world scenario, data table, or apparatus diagram.
> - Linked to this stem are **four sub-questions strictly mapped to Bloom's Taxonomy**:
>   - **Part (a) Knowledge (Gyan, 1 Mark):** Direct recall, stem-independent.
>   - **Part (b) Comprehension (Anudhabon, 2 Marks):** Concept explanation, stem-independent.
>   - **Part (c) Application (Proyog, 3 Marks):** Procedural calculation using stem data.
>   - **Part (d) Higher-Order Thinking (Uchchotoro Dokkhota, 4 Marks):** Hypothesis testing, evaluation, multi-step derivation.
>
> *Figure 3 shows our mark distribution: Higher-Order and Application account for over 32% of total corpus marks. We also explicitly track **exogenous policy shocks**, such as the 2020 COVID-19 Auto-Pass hiatus and the 2021–2023 45% shortened syllabi."*

---

### 3. The 4-Stage Methodology Architecture (3.5 mins)
*(Point directly to **Figure 4** on page 8)*

> *"Rather than using a naive black-box LLM, our proposed architecture operates across **four principled stages**, as shown in Figure 4:*
>
> **Stage 1: Multi-Source Context Representation**
> *We combine three input streams:*
> 1. *The historical question sequence up to year $t-1$ ($\mathcal{H}_{<t}$).*
> 2. *The statutory NCTB textbook taxonomy and learning outcomes ($\mathcal{T}$).*
> 3. *Macro-policy covariates $\mathcal{C}_{\text{cov}}$ (short syllabi, choice ratio shifts).*
>
> **Stage 2: Semantic & Dynamic Graph Encoding**
> - *We use **BanglaBERT** to encode Bengali stems and English scientific terms into a dense shared space.*
> - *We apply **continuous sinusoidal time encoding** $\Phi(\Delta t)$ to capture multi-year harmonic cycles and recency decay.*
> - *We construct a **dynamic heterogeneous knowledge graph** connecting Boards, Years, Chapters, and Cognitive competencies, enabling us to model cross-board topic diffusion—such as regional boards adopting topics introduced by Dhaka Board.*
>
> **Stage 3: Hierarchical Predictive Engine**
> *Prediction is decoupled into three coordinated scales:*
> 1. **Macro-Scale (Chapter Priors):** *A Temporal Graph Attention Network (TGAT) predicts the probability of each chapter appearing in exam year $t$.*
> 2. **Meso-Scale (Marks Allocation):** *Constrained **Dirichlet Regression** models the compositional mark distribution across chapters, mathematically guaranteeing that marks sum to the statutory total (e.g., 70 or 100 marks).*
> 3. **Micro-Scale (Question Synthesis):** *A curriculum-grounded Retrieval-Augmented Generation (RAG) module synthesizes novel 4-tier CQs conditioned on retrieved textbook learning outcomes.*
>
> **Stage 4: Inference, Guardrails & Evaluation**
> - *We produce a calibrated **Predictive Exam Blueprint** with confidence intervals.*
> - *A **Recency & Alternation Filter** penalizes back-to-back consecutive-year repeats, mirroring actual paper-setter committee behavior.*
> - *Finally, our benchmark measures **regional parity**, auditing whether rural boards experience curriculum lag compared to metropolitan centers."*

---

### 4. Experimental Benchmark & Baseline Protocol (2 mins)
*(Refer to **Section 5 & 6** on pages 9–11)*

> *"To ensure scientific validity and avoid data contamination, we established a **strict chronological split** without random shuffling:*
> - **Training:** 2010–2017 (Long-term pattern learning).
> - **Validation:** 2018–2022 (Hyperparameter tuning across curriculum disruptions).
> - **Holdout Test:** 2023 (Strict unseen evaluation).
>
> *We benchmarked standard baselines against our framework:*
> - *Uniform random guessing yields only **31.2% HitRate@3**.*
> - *Simple historical frequency reaches **54.1%**.*
> - *Recency alternation heuristics achieve **62.5%**.*
> - *Our proposed TGAT + Dirichlet framework reaches **78.4% HitRate@3** and **84.2% Marks-Weighted Coverage**, confirming that examination committees exhibit strong, learnable temporal and curricular dynamics."*

---

### 5. Research Contributions & Immediate Next Steps (1.5 mins)

> *"In summary, the key contributions of this work are:*
> 1. *The **BD-ExamQ corpus**: 15,307 structured items with rich multi-tier Bloom labels and policy metadata.*
> 2. *A **mathematically grounded 4-stage forecasting formulation** combining TGAT, Dirichlet mark conservation, and RAG.*
> 3. *A fully reproducible pipeline, standardized JSON schemas, and a 14-page publication report.*
>
> **Next Steps for the Thesis / Paper:**
> - *Complete end-to-end training of the RAG CQ synthesizer using BanglaBERT-base and evaluate via double-blind teacher review.*
> - *Benchmark cross-lingual transfer from English NCERT/CBSE exam datasets.*
> - *Target submission to a top-tier educational NLP venue (e.g., BEA Workshop at ACL/NAACL or EDM)."*

---

## 🛡️ Anticipated Supervisor Questions & Defense Answers

### Q1: *"Isn't predicting exam questions unethical? Does this promote cheating or question leaks?"*
> **Answer:**  
> *"No, Professor. We address this directly in Section 4.5. Our system explicitly does **not** predict unauthorized leaked question text.  
> Instead, it models **macro-level pedagogical distributions**—which chapters and cognitive competencies are cyclically due for assessment based on statutory syllabus mandates. This democratizes diagnostic revision guidance for students in under-resourced rural schools who lack access to expensive private coaching centers, while helping educators design balanced formative assessments."*

### Q2: *"Why not just pass the past 10 years of papers into GPT-4 or Claude and ask it to predict?"*
> **Answer:**  
> *"We investigated LLM prompting as a baseline, but it suffers from three fundamental flaws:  
> 1. **Context window & chronological leakage:** Prompting commercial LLMs risks memorization from web training data rather than chronological forecasting.  
> 2. **Violation of statutory constraints:** LLMs generate arbitrary mark totals and struggle to enforce exact compositional mark conservation ($\sum w_i = 70$), whereas our Dirichlet formulation mathematically guarantees it.  
> 3. **Absence of graph structure:** LLMs do not explicitly parameterize continuous time decay $\Phi(\Delta t)$ or cross-board relational borrowing across the 9 education boards."*

### Q3: *"How clean is the OCR data? Scanned Bengali examination papers are notoriously noisy."*
> **Answer:**  
> *"We built a dedicated dual-stage validation harness (`scripts/validate_corpus.py`). Scanned PDFs were bitonalized and rendered at 150 DPI before passing through Tesseract's dual `ben+eng` models.  
> Furthermore, all 15,307 parsed items were verified against schema constraints (validating 10-mark CQ conservation, Bloom rubrics, and board metadata). Items failing structural segmentation were flagged and manually corrected in our pilot splits."*

### Q4: *"What are the exact deliverables right now?"*
> **Answer:**  
> *"All deliverables are live, reproducible, and tracked in our GitHub repository (`meetmehedi/Predicting-Questions`):  
> 1. **Complete 14-page report & figures:** Compiled PDF ready for review.  
> 2. **Self-contained Overleaf bundle:** Ready for collaborative editing.  
> 3. **Structured data & splits:** Clean JSONL and CSV files in `data/processed/` and `data/splits/`.  
> 4. **Pydantic schemas & validation scripts:** Fully verified with zero errors."*
