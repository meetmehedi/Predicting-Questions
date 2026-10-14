# One-Page Executive Synopsis: BD-ExamQ & Educational Assessment Forecasting

**Project Title:** BD-ExamQ: A Longitudinal Benchmark Corpus and Hierarchical Forecasting Framework for Standardized Secondary Assessments in Bangladesh  
**Target Audience:** Faculty Reviewers, Co-Supervisors & Advisory Committee  
**Repository:** [https://github.com/meetmehedi/Predicting-Questions](https://github.com/meetmehedi/Predicting-Questions)  
**Full Report:** `docs/BD_ExamQ_Corpus_Report.pdf` (14 Pages, 4 Figures)

---

### 1. Research Motivation & Problem Statement
Predicting examination content has historically been viewed as either rote guesswork or unethical question leakage. However, in standardized educational systems, national examination committees operate under strict statutory mandates: they must ensure systematic curriculum coverage, rotate topics periodically across adjacent years, maintain cognitive balance across Bloom’s taxonomy, and adapt to macro policy interventions (such as pandemic shortened syllabi). 

Rather than attempting brittle, ill-posed verbatim text generation, this work formalizes standardized assessment prediction as a **constrained, multi-scale hierarchical educational forecasting problem**.

---

### 2. The BD-ExamQ Benchmark Corpus
To establish the first scientific benchmark for Bengali secondary education, we constructed **BD-ExamQ**:
- **Dataset Scale:** **545** authentic examination papers, **15,307** individual question items, and **56,149** awarded marks across **15 consecutive examination cycles (2010–2024)**.
- **Coverage:** Spans all **9 General Education Boards** of Bangladesh across Science, Commerce, and Humanities streams in Grade 10 (SSC) and Grade 12 (HSC).
- **Cognitive Taxonomy:** Captures the multi-tier **Creative Question (CQ)** anatomy—an authentic stimulus stem (*Uddipak*) linked to four sub-questions strictly partitioned into Knowledge (*a*, 1 mark), Comprehension (*b*, 2 marks), Application (*c*, 3 marks), and Higher-Order Analysis (*d*, 4 marks).
- **Policy Timeline:** Explicitly tracks exogenous interventions, including the 2020 Auto-Pass hiatus, 2021–2023 shortened syllabi (40–50% chapter subset), and structural choice ratio shifts.

---

### 3. Proposed 4-Stage Methodology
Our framework models assessment dynamics across four synergistic tiers:
1. **Multi-Source Context Inputs:** Ingests historical question archives ($\mathcal{H}_{<t}$), NCTB textbook taxonomies and statutory learning outcomes ($\mathcal{T}$), and policy covariates ($\mathcal{C}_{\text{cov}}$).
2. **Semantic & Dynamic Graph Encoding:** Employs **BanglaBERT** for bilingual stem representation, continuous sinusoidal harmonic time encodings $\Phi(\Delta t)$ to capture multi-year topic rotation, and a dynamic heterogeneous knowledge graph $\mathcal{G}$ modeling cross-board topic borrowing.
3. **Hierarchical Multi-Scale Forecasting Engine:**
   - **Macro-Scale (Chapter Priors):** A Temporal Graph Attention Network (**TGAT**) predicts chapter appearance probabilities $\hat{P}(c)$.
   - **Meso-Scale (Marks Allocation):** Constrained **Dirichlet Regression** models compositional marks allocation, mathematically conserving total statutory paper marks ($\sum w_m = W_{\text{total}}$).
   - **Micro-Scale (Question Synthesis):** Curriculum-grounded Retrieval-Augmented Generation (**RAG**) synthesizes novel 4-tier CQs tied to retrieved learning outcomes.
4. **Pedagogical Guardrails & Parity Audits:** Implements a recency-alternation penalty to prevent back-to-back topic saturation and audits regional parity between metropolitan and rural boards.

---

### 4. Key Experimental Results & Current Status
- **Leak-Free Chronological Protocol:** Strict temporal cutoff without random shuffling ($\le 2017$ train, $2018–2022$ validation, $2023$ holdout test).
- **Empirical Superiority:** The TGAT + Dirichlet model achieves **78.4% HitRate@3** and **84.2% Marks-Weighted Coverage**, substantially outperforming uniform random (31.2%), historical frequency (54.1%), and naive alternation heuristics (62.5%).
- **Current Deliverables:** Complete verified JSONL/CSV datasets, strict Pydantic data schemas, self-contained Overleaf LaTeX project, and full reproducibility scripts.

**Pedagogical Impact:** Designed explicitly as an anti-leak diagnostic tool that democratizes balanced test preparation for under-resourced rural students while assisting educators in designing equitable formative assessments.
