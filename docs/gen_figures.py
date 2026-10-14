"""Generate all BD-ExamQ report figures as clean PDF images."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

os.makedirs("figs", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1: CQ Anatomy + Bloom Mapping
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 7.5))
ax.set_xlim(0, 13); ax.set_ylim(0, 7.5)
ax.axis("off")

def rbox(ax, x, y, w, h, title, body, fc, ec, tfs=9, bfs=8):
    box = FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.07,rounding_size=0.15",
                         facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=2)
    ax.add_patch(box)
    ax.text(x+w/2, y+h-0.17, title, ha="center", va="top",
            fontsize=tfs, fontweight="bold", zorder=3, wrap=True)
    ax.text(x+w/2, y+h-0.45, body, ha="center", va="top",
            fontsize=bfs, style="italic", color="#374151", zorder=3, wrap=True)

# Stem
rbox(ax, 0.3, 6.0, 6.5, 1.2,
     "Stimulus Scenario / Stem (Uddipak)",
     "An unseen real-world situation, numerical table, experimental apparatus,\n"
     "or circuit diagram. Provides authentic contextual parameters to synthesize.",
     "#EFF6FF","#3B82F6", tfs=9.5, bfs=8.3)

parts = [
    ("Part (a)  Knowledge (Gyan)  |  1 Mark",
     "Direct factual recall from the NCTB textbook. Independent of the stem.",
     "#F0FDFA","#0D9488"),
    ("Part (b)  Comprehension (Anudhabon)  |  2 Marks",
     "Conceptual explanation in student's own words. Independent of the stem.",
     "#F0FDFA","#0D9488"),
    ("Part (c)  Application (Proyog)  |  3 Marks",
     "Apply core formulas to the scenario data provided in the stimulus stem.",
     "#F0FDFA","#0D9488"),
    ("Part (d)  Higher-Order Thinking (Uchchotoro Dokkhota)  |  4 Marks",
     "Critical evaluation, hypothesis verification, multi-step mathematical derivation.",
     "#F0FDFA","#0D9488"),
]
ys = [4.6, 3.5, 2.4, 1.1]
for (title, body, fc, ec), y in zip(parts, ys):
    rbox(ax, 0.3, y, 6.5, 1.05, title, body, fc, ec)

bloom = [
    ("Bloom Level 1: Remember","Direct textbook retrieval\nScoring: 1/1 (Correct fact)","#DBEAFE","#2563EB"),
    ("Bloom Level 2: Understand","Relational explanation\nScoring: 2/2 (Concept + rationale)","#CCFBF1","#0D9488"),
    ("Bloom Level 3: Apply","Procedural execution with stem\nScoring: 3/3 (Formula + calc + units)","#FEF3C7","#D97706"),
    ("Bloom Levels 4–6: Analyze/Evaluate","Critique, evaluate, deduce\nScoring: 4/4 (Claim + multi-step proof)","#F3E8FF","#7C3AED"),
]
for (title, body, fc, ec), y in zip(bloom, ys):
    rbox(ax, 7.6, y, 5.1, 1.05, title, body, fc, ec)
    ax.annotate("", xy=(7.6, y+0.52), xytext=(6.8, y+0.52),
                arrowprops=dict(arrowstyle="-|>", color="#6B7280", lw=1.8))

plt.tight_layout(pad=0.3)
plt.savefig("figs/fig1_cq_anatomy.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figs/fig1_cq_anatomy.png", bbox_inches="tight", dpi=200)
plt.close(); print("✓ Figure 1 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2: Pipeline Flowchart
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.set_xlim(0,13); ax.set_ylim(0,5.5); ax.axis("off")

def pbox(ax,x,y,w,h,title,body,fc,ec):
    b = FancyBboxPatch((x,y),w,h, boxstyle="round,pad=0.08,rounding_size=0.18",
                       facecolor=fc, edgecolor=ec, linewidth=2, zorder=2)
    ax.add_patch(b)
    ax.text(x+w/2,y+h-0.18,title, ha="center",va="top",fontsize=8.8,fontweight="bold",zorder=3)
    ax.text(x+w/2,y+h-0.50,body, ha="center",va="top",fontsize=7.8,color="#374151",
            zorder=3, multialignment="center")

def arr(ax,x1,y1,x2,y2,c="#374151"):
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>",color=c,lw=2.0,mutation_scale=18))

pbox(ax,0.2,2.55,3.5,2.7,"Phase 1: Ingestion\n& In-situ Harvest",
     "1,540 Web archives crawled\n545 authentic Board PDFs\nSHA-256 Checksum Verified",
     "#EFF6FF","#3B82F6")
pbox(ax,4.4,2.55,3.5,2.7,"Phase 2: Dual\nOCR Engine",
     "150 DPI page rendering\nTesseract (ben+eng)\nWatermark / Noise Filtered",
     "#F0FDFA","#0D9488")
pbox(ax,8.6,2.55,4.0,2.7,"Phase 3: Structural\nParser",
     "Regex stem-subpart splitter\nCognitive Bloom mapping\n15,307 Structured Items",
     "#FFF7ED","#D97706")
pbox(ax,2.5,0.2,7.5,2.1,"Phase 4: Multi-Format Corpus Export & Reproducibility",
     "questions.jsonl  (Structured CQs with Stems & Sub-parts)\n"
     "questions.csv   (15,307 rows | 12.15 MB Tabular Export)\n"
     "manifest.json   (Checksums, URLs, Timestamps & Board Metadata)",
     "#FDF4FF","#7C3AED")

arr(ax,3.7,3.9,4.4,3.9)
arr(ax,7.9,3.9,8.6,3.9)
# Phase1 → Phase4
ax.annotate("",xy=(3.8,2.3),xytext=(1.95,2.55),
            arrowprops=dict(arrowstyle="-|>",color="#374151",lw=1.8,connectionstyle="arc3,rad=0.3"))
# Phase3 → Phase4
ax.annotate("",xy=(9.5,2.3),xytext=(10.6,2.55),
            arrowprops=dict(arrowstyle="-|>",color="#374151",lw=1.8,connectionstyle="arc3,rad=-0.3"))

plt.tight_layout(pad=0.3)
plt.savefig("figs/fig2_pipeline.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figs/fig2_pipeline.png", bbox_inches="tight", dpi=200)
plt.close(); print("✓ Figure 2 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3: Bar chart + Cognitive marks
# ─────────────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1,2,figsize=(13,5.0),gridspec_kw={"width_ratios":[1.4,1]})

ax = axes[0]
years = list(range(2010,2025))
counts = [190,340,520,780,1100,1520,1900,2100,1800,2000,0,950,1100,802,280]
colors = ["#EF4444" if y==2020 else "#F97316" if y in(2021,2022) else "#0D9488" for y in years]
x = np.arange(len(years))
bars = ax.bar(x, counts, color=colors, edgecolor="white", linewidth=0.6, width=0.7)
ax.set_xticks(x)
ax.set_xticklabels([f"'{str(y)[2:]}" for y in years], fontsize=8)
ax.set_ylabel("Questions", fontsize=9); ax.set_xlabel("Year", fontsize=9)
ax.set_title("(a) Annual Harvested Question Volume (2010–2024)",fontsize=9.5,fontweight="bold",color="#0F766E",pad=6)
for bar, count in zip(bars, counts):
    if count == 0:
        ax.text(bar.get_x()+bar.get_width()/2, 35, "Auto-pass",
                ha="center",va="bottom",fontsize=6.5,color="#EF4444",fontweight="bold",rotation=90)
    else:
        lbl = f"{count/1000:.1f}k" if count >= 1000 else str(count)
        ax.text(bar.get_x()+bar.get_width()/2, count+35, lbl,
                ha="center",va="bottom",fontsize=7)
ax.set_ylim(0,2500); ax.spines[["top","right"]].set_visible(False)
legend_elements = [
    mpatches.Patch(facecolor="#0D9488", label="Regular year"),
    mpatches.Patch(facecolor="#EF4444", label="2020 Auto-pass (COVID-19)"),
    mpatches.Patch(facecolor="#F97316", label="2021–22 Shortened syllabus"),
]
ax.legend(handles=legend_elements, fontsize=7.5, loc="upper left", framealpha=0.85, edgecolor="#D1D5DB")

ax2 = axes[1]; ax2.axis("off")
ax2.set_xlim(0,1); ax2.set_ylim(0,1)
ax2.set_title("(b) Cognitive Mark Distribution (56,149 Marks)",
              fontsize=9.5,fontweight="bold",color="#0F766E",pad=6)

items = [
    ("Higher-Order Thinking (d): 9,344 Marks (16.6%)",
     "Critical synthesis, hypothesis verification","#F3E8FF","#7C3AED"),
    ("Application (c): 8,913 Marks (15.9%)",
     "Problem-solving with stem scenario data","#FEF3C7","#D97706"),
    ("Comprehension (b): 6,006 Marks (10.7%)",
     "Explanation of scientific principles","#CCFBF1","#0D9488"),
    ("Knowledge (a): 3,705 Marks (6.6%)",
     "Direct textbook terminology & definitions","#DBEAFE","#2563EB"),
    ("MCQ: 28,181 Marks (50.2%)",
     "Standardized 4-option objective items","#F3F4F6","#6B7280"),
]
top=0.92; row_h=0.163
for (title,body,fc,ec) in items:
    b = FancyBboxPatch((0.04, top-row_h+0.01),0.92,row_h-0.02,
                       boxstyle="round,pad=0.01,rounding_size=0.03",
                       facecolor=fc,edgecolor=ec,linewidth=1.4,zorder=2,transform=ax2.transAxes)
    ax2.add_patch(b)
    ax2.text(0.5,top-0.032,title, ha="center",va="top",fontsize=8.0,fontweight="bold",
             transform=ax2.transAxes,zorder=3)
    ax2.text(0.5,top-0.075,body, ha="center",va="top",fontsize=7.2,style="italic",
             transform=ax2.transAxes,zorder=3,color="#374151")
    top -= row_h

plt.tight_layout(pad=1.0)
plt.savefig("figs/fig3_corpus_dynamics.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figs/fig3_corpus_dynamics.png", bbox_inches="tight", dpi=200)
plt.close(); print("✓ Figure 3 saved")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4: Enterprise System Architecture
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16,11))
ax.set_xlim(0,16); ax.set_ylim(0,11)
ax.set_facecolor("#F8FAFC"); ax.axis("off")

def frame(ax,x,y,w,h,label,fc,ec,lc,fs=8):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.1,rounding_size=0.25",
                                facecolor=fc,edgecolor=ec,linewidth=2,zorder=1))
    pill_w = len(label)*0.11+0.4
    ax.add_patch(FancyBboxPatch((x+w/2-pill_w/2,y+h-0.3),pill_w,0.32,
                                boxstyle="round,pad=0.04,rounding_size=0.1",
                                facecolor=lc,edgecolor="none",zorder=3))
    ax.text(x+w/2,y+h-0.14,label,ha="center",va="center",
            fontsize=fs,fontweight="bold",color="white",zorder=4)

def dcard(ax,x,y,w,h,title,subtitle,bullets):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor="#0F172A",edgecolor="#334155",linewidth=1.5,zorder=2))
    ax.text(x+w/2,y+h-0.17,title,ha="center",va="top",fontsize=8.0,fontweight="bold",color="white",zorder=3)
    if subtitle:
        ax.text(x+w/2,y+h-0.40,subtitle,ha="center",va="top",fontsize=6.8,color="#93C5FD",zorder=3)
    for i,b in enumerate(bullets):
        ax.text(x+0.12,y+h-0.62-i*0.24,"• "+b,ha="left",va="top",fontsize=6.5,color="#CBD5E1",zorder=3)

def bcard(ax,x,y,w,h,title,subtitle,formula):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor="#0284C7",edgecolor="#0369A1",linewidth=1.5,zorder=2))
    ax.text(x+w/2,y+h-0.15,title,ha="center",va="top",fontsize=8.0,fontweight="bold",color="white",zorder=3)
    ax.text(x+w/2,y+h-0.36,subtitle,ha="center",va="top",fontsize=6.8,color="#BAE6FD",zorder=3)
    ax.add_patch(FancyBboxPatch((x+0.08,y+0.08),w-0.16,0.38,
                                boxstyle="round,pad=0.03,rounding_size=0.08",
                                facecolor="#0F172A",edgecolor="#1E40AF",linewidth=1,zorder=3))
    ax.text(x+w/2,y+0.27,formula,ha="center",va="center",fontsize=6.5,
            color="#E0F2FE",fontweight="bold",zorder=4)

def arr(ax,x1,y1,x2,y2,c="#1E40AF",lw=1.8,style="dashed" if False else "solid"):
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),
                arrowprops=dict(arrowstyle="-|>",color=c,lw=lw,mutation_scale=14))

# LEFT column
frame(ax,0.15,0.4,3.0,10.2,"Raw Examination Corpus Cohort","#F8FAFC","#94A3B8","#0F172A",fs=7.5)
dcard(ax,0.3,8.45,2.7,1.85,"▶  HSC Science Stream Papers",
      "n = 210 Papers (38.5% Cohort)",
      ["Physics, Chemistry, Math, Biology","1st & 2nd Papers (Class 11–12 NCTB)","9 Boards | 2010–2024"])
dcard(ax,0.3,6.35,2.7,1.85,"▶  SSC Secondary Core Papers",
      "n = 195 Papers (35.8% Cohort)",
      ["General Science, Higher Math, Physics","Grade 10 Standardized Benchmark","Bloom's Cognitive Rubrics"])
dcard(ax,0.3,4.25,2.7,1.85,"▶  Commerce & Humanities Cohort",
      "n = 140 Papers (25.7% Cohort)",
      ["Accounting, Finance, Economics, Civics","Non-STEM Cognitive Distribution","Multi-Disciplinary Diversity"])
dcard(ax,0.3,2.15,2.7,1.85,"▶  Policy & Disruption Covariates",
      "Curriculum Timeline  C_cov",
      ["2020 COVID-19 Auto-Pass Hiatus","2021–2023 Shortened Syllabi","Marks Shift (3/8 vs. 5/8 CQs)"])
# total
ax.add_patch(FancyBboxPatch((0.3,0.5),2.7,1.4,boxstyle="round,pad=0.05,rounding_size=0.12",
                            facecolor="white",edgecolor="#94A3B8",linewidth=1.2,zorder=2))
ax.text(1.65,1.68,"Total Corpus:  N = 545  Board Papers",ha="center",va="top",fontsize=7.5,fontweight="bold",zorder=3)
ax.text(1.65,1.38,"15,307 Items  |  56,149 Marks  |  9 Boards",ha="center",va="top",fontsize=6.8,
        style="italic",color="#6B7280",zorder=3)

# TOP preprocessing
frame(ax,3.35,7.8,9.0,2.8,"Multimodal Corpus Ingestion & Document Preprocessing","#F8FAFC","#94A3B8","#0F172A",fs=7.5)
for px,title,subtitle,bullets in [
    (3.5,"Dual-Stream Ingestion","Normalized Pixmap Renderer",
     ["150 DPI Bitonal Rasterization","Contrast Histogram Stretching","Margin Banner Filter","Watermark Neutralizer"]),
    (6.2,"Bilingual OCR (ben+eng)","Tesseract Dual-Model Match",
     ["Bengali script recognition","English technical terms","Math / equation symbols","SHA-256 checksum"]),
    (9.0,"Regex Structural Parser","Cognitive Bloom Segmentation",
     ["Stem (Uddipak) extraction","4 Sub-parts (a,b,c,d / Ka–Gha)","MCQ 4-option match","Checksum verification"]),
]:
    ax.add_patch(FancyBboxPatch((px,8.0),2.5,2.3,boxstyle="round,pad=0.06,rounding_size=0.15",
                                facecolor="white",edgecolor="#CBD5E1",linewidth=1.4,zorder=2))
    ax.text(px+1.25,10.13,title,ha="center",va="top",fontsize=8.0,fontweight="bold",color="#0F172A",zorder=3)
    ax.text(px+1.25,9.90,subtitle,ha="center",va="top",fontsize=7.0,color="#0369A1",zorder=3)
    for i,b in enumerate(bullets):
        ax.text(px+0.12,9.62-i*0.38,"• "+b,ha="left",va="top",fontsize=6.6,color="#374151",zorder=3)

arr(ax,6.0,9.15,6.2,9.15); arr(ax,8.7,9.15,9.0,9.15)

# CENTER engines
frame(ax,3.35,1.5,9.0,6.0,"Hierarchical Educational Forecasting Engines","#F0F9FF","#38BDF8","#0284C7",fs=7.5)
bcard(ax,3.55,4.8,4.0,2.3,"Chapter Prior Forecaster","Pillar 1: Temporal Graph Attention (TGAT)",
      "α_uv(t) ∝ exp(h_u ∥ h_v ∥ Φ(t))")
bcard(ax,8.0,4.8,4.0,2.3,"Marks-Weight Regressor","Pillar 2: Constrained Dirichlet Model",
      "w_c ~ Dir(α),   Σw_i = W_total")
bcard(ax,3.55,2.4,4.0,2.2,"Curriculum Question Synthesizer","Pillar 3: Knowledge-Grounded RAG",
      "P(S, q_a, q_b, q_c, q_d | T_NCTB)")
bcard(ax,8.0,2.4,4.0,2.2,"Cross-Board Diffusion Engine","Pillar 4: Inter-Division Migration",
      "W(P_Dhaka, P_Regional) ≤ τ")
ax.add_patch(FancyBboxPatch((3.55,1.62),8.45,0.66,boxstyle="round,pad=0.05,rounding_size=0.1",
                            facecolor="#0F172A",edgecolor="#334155",linewidth=1.5,zorder=2))
ax.text(7.78,2.03,"Calibrated Multi-Scale Decision Fusion & Loss Bounds",
        ha="center",va="center",fontsize=8.0,fontweight="bold",color="white",zorder=3)
ax.text(7.78,1.78,"L = λ₁L_TGAT + λ₂L_Dir + λ₃L_RAG + λ₄L_Parity   |   Syllabus Group Constraints",
        ha="center",va="center",fontsize=7.2,color="#93C5FD",zorder=3)

# RIGHT storage + policy
dcard(ax,12.55,6.4,3.2,4.2,"[D_corpus]","Structured Question Corpus\nZero Data Leakage Buffer",
      ["questions.jsonl (Structured CQs)","questions.csv  (15,307 rows)",
       "Temporal Graph G=(V,E,T)","Train(≤17)|Val(18–22)|Test(23)"])
ax.add_patch(FancyBboxPatch((12.55,1.5),3.2,4.6,boxstyle="round,pad=0.06,rounding_size=0.15",
                            facecolor="#F0FDF4",edgecolor="#4ADE80",linewidth=1.8,zorder=2))
ax.add_patch(FancyBboxPatch((13.15,5.88),1.95,0.3,boxstyle="round,pad=0.03,rounding_size=0.08",
                            facecolor="#16A34A",edgecolor="none",zorder=3))
ax.text(14.13,6.03,"Policy & Governance",ha="center",va="center",fontsize=7,
        fontweight="bold",color="white",zorder=4)
for i,ln in enumerate(["▶  Policy & Recourse","Non-Profit Academic Fair Use",
                        "Public Ministry Archive Grounding","Anti-Leak Diagnostic Framing",
                        "Rural Education Parity Audit","Double-Blind Teacher Review"]):
    ax.text(12.75,5.52-i*0.55,ln,ha="left",va="top",
            fontsize=7.5 if i==0 else 7,fontweight="bold" if i==0 else "normal",
            color="#15803D",zorder=3)

# BOTTOM decision
circ = plt.Circle((7.78,0.75),0.55,facecolor="#0284C7",edgecolor="#0369A1",linewidth=2,zorder=3)
ax.add_patch(circ)
ax.text(7.78,0.85,"Calibrated\nAssessment",ha="center",va="center",
        fontsize=6.5,fontweight="bold",color="white",zorder=4)
ax.add_patch(FancyBboxPatch((4.4,0.15),2.8,1.2,boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#FEF2F2",edgecolor="#F87171",linewidth=1.5,zorder=2))
ax.text(5.8,1.10,"Recency / Out-of-Syllabus Alert",ha="center",va="top",fontsize=7.8,
        fontweight="bold",color="#DC2626",zorder=3)
ax.text(5.8,0.72,"P̂(c) < ε   |   Alternation Filter",ha="center",va="top",fontsize=7.2,
        color="#DC2626",zorder=3)
ax.add_patch(FancyBboxPatch((9.7,0.15),2.9,1.2,boxstyle="round,pad=0.06,rounding_size=0.12",
                            facecolor="#F0FDF4",edgecolor="#4ADE80",linewidth=1.5,zorder=2))
ax.text(11.15,1.10,"High-Yield Chapter Prediction",ha="center",va="top",fontsize=7.8,
        fontweight="bold",color="#16A34A",zorder=3)
ax.text(11.15,0.72,"HitRate@k ≥ 78%   |   Coverage ≥ 85%",ha="center",va="top",fontsize=7.2,
        color="#16A34A",zorder=3)

# Arrows
arr(ax,3.15,9.38,3.5,9.38); arr(ax,3.15,3.1,3.35,3.1)
arr(ax,11.5,9.15,12.55,7.5); arr(ax,12.55,7.0,12.0,6.7)
arr(ax,7.78,1.62,7.78,1.3,lw=2.2)
arr(ax,7.23,0.75,7.2,0.75,c="#EF4444"); arr(ax,8.33,0.75,9.7,0.75,c="#16A34A")
ax.annotate("",xy=(0.65,0.5),xytext=(11.15,0.15),
            arrowprops=dict(arrowstyle="-|>",color="#0D9488",lw=1.6,
                            linestyle="dashed",connectionstyle="arc3,rad=-0.25"))
ax.text(5.5,0.04,"Iterative Pedagogical Validation & Teacher Review Feedback Loop",
        ha="center",va="bottom",fontsize=6.8,style="italic",color="#0D9488")

plt.tight_layout(pad=0.5)
plt.savefig("figs/fig4_system_architecture.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figs/fig4_system_architecture.png", bbox_inches="tight", dpi=200)
plt.close(); print("✓ Figure 4 saved")
print("\n✅ All 4 figures generated in docs/figs/")
