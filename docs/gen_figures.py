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
# FIGURE 4: Methodology Architecture (Clean & Non-overlapping)
# ─────────────────────────────────────────────────────────────────────────────
import textwrap

fig, ax = plt.subplots(figsize=(16, 6.8), dpi=300)
ax.set_xlim(0, 16)
ax.set_ylim(0, 6.8)
ax.axis("off")
fig.patch.set_facecolor("#FFFFFF")

stages = [
    {
        "tag": "STAGE 1",
        "title": "Problem Formulation & Inputs",
        "primary": "#1D4ED8",
        "bg": "#F8FAFC",
        "border": "#94A3B8",
        "items": [
            ("Historical Question Stream",
             "Sequence of past board exam questions from 2010 to t-1 across 9 education divisions."),
            ("Curricular Knowledge Base",
             "Official NCTB textbooks, chapter taxonomies, and statutory learning outcomes."),
            ("Policy Disruption Covariates",
             "Pandemic short syllabi, cancelled exam years (auto-pass), and mark choice ratios.")
        ]
    },
    {
        "tag": "STAGE 2",
        "title": "Semantic & Temporal Encoding",
        "primary": "#0D9488",
        "bg": "#F8FAFC",
        "border": "#94A3B8",
        "items": [
            ("Dense Bilingual Encoder",
             "BanglaBERT encodes question stems, Bengali text, and English technical terms."),
            ("Continuous Time Encoding",
             "Sinusoidal harmonic time vectors capture multi-year topic rotation and decay."),
            ("Dynamic Knowledge Graph",
             "Heterogeneous temporal graph linking boards, exam years, chapters, and topics.")
        ]
    },
    {
        "tag": "STAGE 3",
        "title": "Hierarchical Predictive Engine",
        "primary": "#0284C7",
        "bg": "#F8FAFC",
        "border": "#94A3B8",
        "items": [
            ("Macro: Chapter Prior (TGAT)",
             "Temporal Graph Attention Network predicts high-probability chapters for year t."),
            ("Meso: Marks Allocation (Dirichlet)",
             "Constrained Dirichlet model conserves total statutory exam marks (70/100)."),
            ("Micro: Question Synthesizer (RAG)",
             "Generates novel 4-tier Creative Questions (a, b, c, d) grounded in curriculum.")
        ]
    },
    {
        "tag": "STAGE 4",
        "title": "Inference & Pedagogical Audit",
        "primary": "#7C3AED",
        "bg": "#F8FAFC",
        "border": "#94A3B8",
        "items": [
            ("Predictive Exam Blueprint",
             "Ranked chapter priority forecasts with calibrated prediction intervals."),
            ("Recency & Alternation Filter",
             "Penalizes consecutive-year repeats to enforce statutory curriculum breadth."),
            ("Educational Parity Benchmark",
             "Validates fairness and topic diversity across rural and metropolitan boards.")
        ]
    }
]

box_w = 3.35
box_h = 5.20
box_y = 1.05
xs = [0.45, 4.35, 8.25, 12.15]

for x, s in zip(xs, stages):
    box = FancyBboxPatch((x, box_y), box_w, box_h,
                         boxstyle="round,pad=0.04,rounding_size=0.14",
                         facecolor=s["bg"], edgecolor=s["border"], linewidth=1.5, zorder=1)
    ax.add_patch(box)

    head_h = 0.85
    head_y = box_y + box_h - head_h
    head_patch = FancyBboxPatch((x, head_y), box_w, head_h,
                                boxstyle="round,pad=0.04,rounding_size=0.14",
                                facecolor=s["primary"], edgecolor="none", zorder=2)
    ax.add_patch(head_patch)
    ax.fill_between([x, x + box_w], [head_y, head_y], [head_y + 0.15, head_y + 0.15],
                    color=s["primary"], zorder=2)

    ax.text(x + box_w / 2, head_y + head_h - 0.24, s["tag"],
            ha="center", va="center", fontsize=8.0, fontweight="bold",
            color="#E0E7FF", zorder=3)
    ax.text(x + box_w / 2, head_y + 0.26, s["title"],
            ha="center", va="center", fontsize=8.8, fontweight="bold",
            color="#FFFFFF", zorder=3)

    item_y_starts = [head_y - 0.35, head_y - 1.70, head_y - 3.05]
    for (item_title, item_desc), iy in zip(s["items"], item_y_starts):
        ax.text(x + 0.20, iy, f"▶  {item_title}", ha="left", va="top",
                fontsize=8.3, fontweight="bold", color=s["primary"], zorder=3)
        wrapped = textwrap.fill(item_desc, width=36)
        ax.text(x + 0.20, iy - 0.26, wrapped, ha="left", va="top",
                fontsize=7.3, color="#334155", linespacing=1.35, zorder=3)

for i in range(3):
    x_from = xs[i] + box_w + 0.05
    x_to = xs[i+1] - 0.05
    y_mid = box_y + box_h / 2
    ax.annotate("", xy=(x_to, y_mid), xytext=(x_from, y_mid),
                arrowprops=dict(arrowstyle="-|>", lw=2.4, color="#475569",
                                mutation_scale=18), zorder=4)

fb_x_start = xs[3] + box_w / 2
fb_x_end = xs[2] + box_w / 2
ax.annotate("", xy=(fb_x_end, box_y), xytext=(fb_x_start, box_y),
            arrowprops=dict(arrowstyle="-|>", lw=2.0, color="#0D9488",
                            linestyle="dashed", connectionstyle="arc3,rad=-0.25",
                            mutation_scale=15), zorder=4)

ax.text((fb_x_start + fb_x_end) / 2, 0.18,
        "Teacher-in-the-Loop Feedback & Pedagogical Alignment Loop",
        ha="center", va="center", fontsize=8.4, fontweight="bold",
        style="italic", color="#0F766E")

plt.tight_layout()
plt.savefig("figs/fig4_system_architecture.pdf", bbox_inches="tight", dpi=300)
plt.savefig("figs/fig4_system_architecture.png", bbox_inches="tight", dpi=200)
plt.close()
print("✓ Figure 4 saved (Methodology Architecture)")
print("\n✅ All 4 figures generated in docs/figs/")
