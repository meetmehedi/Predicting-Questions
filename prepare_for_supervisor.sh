#!/usr/bin/env bash
# ============================================================
#  prepare_for_supervisor.sh
#  BD-ExamQ Corpus Report — Full Build Script
#  Usage:  bash prepare_for_supervisor.sh
# ============================================================

set -euo pipefail

# ── Colours ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}  ✅  $1${NC}"; }
warn() { echo -e "${YELLOW}  ⚠️   $1${NC}"; }
err()  { echo -e "${RED}  ❌  $1${NC}"; exit 1; }
step() { echo -e "\n${CYAN}${BOLD}━━━  $1  ━━━${NC}"; }

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/docs"
PDF_FILE="$DOCS_DIR/BD_ExamQ_Corpus_Report.pdf"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${CYAN}║   BD-ExamQ  ·  Supervisor Report Build Script   ║${NC}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════╝${NC}"

# ── STEP 0: Sanity checks ─────────────────────────────────────
step "STEP 0 — Checking environment"
command -v python3    >/dev/null 2>&1 || err "python3 not found"
command -v pdflatex   >/dev/null 2>&1 || err "pdflatex not found (install MacTeX)"
python3 -c "import matplotlib, numpy" 2>/dev/null \
    || err "matplotlib/numpy missing  →  pip install matplotlib numpy"
ok "All dependencies present"

# ── STEP 1: Generate figures ──────────────────────────────────
step "STEP 1 — Generating figures  (gen_figures.py)"
cd "$DOCS_DIR"
python3 gen_figures.py

for fig in figs/fig1_cq_anatomy.pdf figs/fig2_pipeline.pdf \
           figs/fig3_corpus_dynamics.pdf figs/fig4_system_architecture.pdf; do
    [[ -f "$fig" ]] && ok "$(basename $fig)" || err "Missing: $fig"
done
ok "All 4 figures generated"

# ── STEP 2: Compile LaTeX (Pass 1) ───────────────────────────
step "STEP 2 — LaTeX compile  (Pass 1 / 2)"
pdflatex -interaction=nonstopmode -halt-on-error BD_ExamQ_Corpus_Report.tex \
    > /tmp/latex_pass1.txt 2>&1 \
    || { grep -A3 "^!" /tmp/latex_pass1.txt; err "LaTeX Pass 1 failed"; }
ok "Pass 1 complete"

# ── STEP 3: Compile LaTeX (Pass 2) ───────────────────────────
step "STEP 3 — LaTeX compile  (Pass 2 / 2 — cross-references)"
pdflatex -interaction=nonstopmode -halt-on-error BD_ExamQ_Corpus_Report.tex \
    > /tmp/latex_pass2.txt 2>&1 \
    || { grep -A3 "^!" /tmp/latex_pass2.txt; err "LaTeX Pass 2 failed"; }
ok "Pass 2 complete — cross-references resolved"

# ── STEP 4: Citation audit ────────────────────────────────────
step "STEP 4 — Reference & citation audit"
python3 - <<'PYEOF'
import re, sys
with open("BD_ExamQ_Corpus_Report.tex") as f:
    tex = f.read()
cited_raw = re.findall(r'\\cite{([^}]+)}', tex)
cited   = {k.strip() for g in cited_raw for k in g.split(',')}
defined = set(re.findall(r'\\bibitem{([^}]+)}', tex))
missing = cited - defined
orphans = defined - cited
fail = False
if missing:
    for k in sorted(missing): print(f"  ❌  MISSING bibitem: {k}")
    fail = True
if orphans:
    for k in sorted(orphans): print(f"  ⚠️   Defined but not cited: {k}")
else:
    print(f"  ✅  All {len(defined)} references defined and cited")
with open("BD_ExamQ_Corpus_Report.log") as lf:
    log = lf.read()
undef = re.findall(r"Citation `([^']+)' on page", log)
if undef:
    for u in undef: print(f"  ⚠️   Undefined in log: {u}")
else:
    print(f"  ✅  No undefined citation warnings in log")
sys.exit(1 if fail else 0)
PYEOF
ok "Reference audit passed"

# ── STEP 5: Math-mode check ───────────────────────────────────
step "STEP 5 — Equation / math-mode check"
MERR=$(grep -c "Missing \$ inserted\|Runaway argument" \
       BD_ExamQ_Corpus_Report.log 2>/dev/null || echo 0)
[ "$MERR" -gt 0 ] && warn "$MERR math-mode issue(s) — review log" \
                     || ok "No math-mode errors detected"

# ── STEP 6: Verify PDF ────────────────────────────────────────
step "STEP 6 — PDF verification"
[[ -f "$PDF_FILE" ]] || err "PDF not found!"
SIZE=$(du -sh "$PDF_FILE" | cut -f1)
PAGE_COUNT=$(grep "Output written" BD_ExamQ_Corpus_Report.log \
             | grep -oE '[0-9]+ page' | grep -oE '[0-9]+' || echo "?")
ok "PDF ready: BD_ExamQ_Corpus_Report.pdf  ($SIZE,  $PAGE_COUNT pages)"

# ── STEP 7: Page previews ─────────────────────────────────────
step "STEP 7 — Generating page previews"
if command -v pdftoppm >/dev/null 2>&1; then
    pdftoppm -r 150 -png BD_ExamQ_Corpus_Report.pdf page_prev
    COUNT=$(ls page_prev-*.png 2>/dev/null | wc -l | tr -d ' ')
    ok "$COUNT page preview PNGs generated"
else
    warn "pdftoppm not available — skipping previews"
fi

# ── STEP 8: Open PDF ──────────────────────────────────────────
step "STEP 8 — Opening PDF"
open "$PDF_FILE" 2>/dev/null && ok "PDF opened in default viewer" \
    || warn "Could not auto-open — open manually:\n       $PDF_FILE"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║       🎓  Report is ready for supervisor!        ║${NC}"
echo -e "${GREEN}${BOLD}║                                                  ║${NC}"
echo -e "${GREEN}${BOLD}║  📄  docs/BD_ExamQ_Corpus_Report.pdf             ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""
