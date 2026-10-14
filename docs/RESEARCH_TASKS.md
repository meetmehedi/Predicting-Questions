# BD-ExamQ: Benchmark Research Tasks & Formal Formulation

This document defines the mathematical formulation, experimental setups, baselines, and evaluation metrics for machine learning and natural language processing tasks based on the BD-ExamQ corpus.

---

## Task 1: Next-Year Chapter & Topic Likelihood Forecasting

### Problem Formulation
Given the historical sequence of examination papers $\mathcal{D}_{\le t} = \{Q_y\}_{y=y_{start}}^t$ across education boards $\mathcal{B} = \{b_1, \dots, b_B\}$ and subjects $\mathcal{S}$, predict the probability distribution over chapters $\mathcal{C} = \{c_1, \dots, c_M\}$ that will be examined in year $t+1$:

$$P(c_i \in \text{Paper}_{t+1, b, s} \mid \mathcal{D}_{\le t})$$

### Constraints & Domain Covariates
1. **Syllabus Coverage Constraints:** Board exam committees must adhere to NCTB guidelines requiring coverage across syllabus divisions (e.g., answering at least 1 question from Group A and Group B).
2. **Curriculum Disruptions (Covariates):**
   - 2020 Auto-pass (missing paper).
   - 2021-2023 Short Syllabi (restricted chapter universe).

### Evaluation Metrics
- **Top-$k$ Hit Rate:** Precision / Recall of top-$k$ predicted chapters against ground-truth examined chapters ($k \in \{3, 5\}$).
- **Marks-Weighted Coverage ($\%$):** Percentage of total marks in the target paper accounted for by the predicted top-$k$ chapters.
- **Mean Reciprocal Rank (MRR):** Ranking accuracy of examined chapters.

---

## Task 2: Question Type and Marks-Weight Distribution Prediction

### Problem Formulation
Predict the multivariate distribution of allocated marks across:
1. Cognitive levels (Bloom's Taxonomy): $\mathbf{w}_{\text{bloom}} = [w_{\text{knowledge}}, w_{\text{comp}}, w_{\text{app}}, w_{\text{higher\_order}}]$
2. Chapter mark allocation: $\mathbf{w}_{\text{chapter}} \in \mathbb{R}^M$ where $\sum_{i=1}^M w_i = W_{\text{total}}$.

### Modeling Approaches
- Multi-target regression (Ridge, LightGBM, MLP).
- Dirichlet distribution modeling over normalized mark shares.

### Evaluation Metrics
- **Wasserstein Distance / Earth Mover's Distance (EMD):** Measures divergence between predicted and actual mark allocations.
- **Root Mean Squared Error (RMSE)** and **Mean Absolute Error (MAE)** on per-chapter mark totals.

---

## Task 3: Question-Level Similarity & Cross-Board Migration Retrieval

### Problem Formulation
Analyze the recurrence and migration of question patterns across boards and time. Given a question $q_{t, b_i}$ from year $t$ in Board $b_i$:
1. Retrieve candidate precursor questions $\mathcal{R} \subset \mathcal{D}_{< t}$ from prior years across all boards that exhibit semantic or template equivalence.
2. Predict whether a question asked in Board $A$ in year $t-1$ will be adapted by Board $B$ in year $t$.

### Modeling Approaches
- **Lexical Baselines:** BM25, TF-IDF n-grams over Bengali tokens.
- **Dense Retrieval:** Bengali sentence encoders (BanglaBERT, multilingual E5, sentence-transformers) fine-tuned with triplet loss or contrastive learning.
- **Graph Link Prediction:** Bipartite graph linking questions to underlying concept triplets $(c, t, \text{bloom})$.

### Evaluation Metrics
- **Recall@K ($k \in \{1, 5, 10\}$)**
- **Mean Average Precision (MAP@K)**
- **Normalized Discounted Cumulative Gain (NDCG@K)**

---

## Task 4: NCTB Textbook-Grounded Candidate Question Generation

### Problem Formulation
Given an NCTB textbook section or learning outcome (শিখনফল) $\mathcal{T}_{c, \tau}$ and a target cognitive domain $d \in \{\text{জ্ঞান}, \text{অনুধাবন}, \text{প্রয়োগ}, \text{উচ্চতর দক্ষতা}\}$:
1. Synthesize a plausible exam-grade Creative Question stem and four linked sub-questions $(s, q_a, q_b, q_c, q_d)$.
2. Evaluate synthetic questions against the genuine board paper for that exam cycle.

### Evaluation Protocol
- **Linguistic Quality & Fluency:** Perplexity under Bengali language models, grammar correctness.
- **Semantic Fidelity:** Alignment with NCTB textbook learning outcomes.
- **Discriminative Turing-Style Test:** Domain educators rate whether a question was board-authored or model-generated (Blind human evaluation).
