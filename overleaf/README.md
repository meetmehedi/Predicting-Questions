# Overleaf Project: BD-ExamQ Corpus Report

This directory contains the self-contained LaTeX source ready to be uploaded directly to [Overleaf](https://www.overleaf.com/).

## Contents
- **`main.tex`**: The primary LaTeX source file containing all report sections, mathematical formulation, definitions, and self-contained bibliography.
- **`figs/`**: High-resolution vector (`.pdf`) and raster (`.png`) diagrams referenced by `main.tex`:
  - `fig1_cq_anatomy`: Anatomy of a Creative Question (CQ) item.
  - `fig2_pipeline`: Multi-stage digitization & annotation pipeline.
  - `fig3_corpus_dynamics`: Temporal evolution & board distribution.
  - `fig4_system_architecture`: Proposed Question Prediction methodology architecture.

## How to Import into Overleaf

### Option 1: Upload the ZIP file (Recommended - 1 Click)
1. Go to [Overleaf Dashboard](https://www.overleaf.com/project).
2. Click **New Project** $\rightarrow$ **Upload Project**.
3. Select or drag-and-drop the file: `overleaf_project.zip` (located in the repository root).
4. Click **Recompile**. Overleaf will compile the full 14-page report with zero warnings.

### Option 2: Upload Files Manually
1. In Overleaf, create a **Blank Project** (name it e.g. `BD-ExamQ-Report`).
2. Upload `main.tex` to the project root.
3. Create a folder named `figs/` and upload all images from this `figs/` directory into it.
4. Click **Recompile**.
