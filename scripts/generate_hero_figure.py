#!/usr/bin/env python3
"""
E²-Bench Hero Figure — One comprehensive figure showing all 3 levels, all 3 models.
Layout: 2x2 grid with a shared title.
  Top-left:     Level 1 FPR heatmap
  Top-right:    Level 2 Perceptual (Recall vs Precision + False Alarms)
  Bottom-left:  Level 3 Consistency (grouped bars)
  Bottom-right: Cross-Level Reliability Radar Chart
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import os

OUTPUT_DIR = "/home/ubuntu/e2_bench/paper/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'figure.dpi': 250,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})

MODELS = ["GPT-4.1-mini", "Gemini 2.5\nFlash", "GPT-4.1-nano"]
MODELS_SHORT = ["GPT-4.1-mini", "Gemini 2.5 Flash", "GPT-4.1-nano"]
MODEL_COLORS = ["#4285F4", "#EA4335", "#34A853"]

# === DATA ===
# Level 1
l1_fpr = {
    "GPT-4.1-mini":    {"Code": 100.0, "Reasoning": 100.0, "Data Analysis": 100.0},
    "Gemini 2.5 Flash": {"Code": 66.7,  "Reasoning": 100.0, "Data Analysis": 100.0},
    "GPT-4.1-nano":    {"Code": 100.0, "Reasoning": 80.0,  "Data Analysis": 100.0},
}

# Level 2
l2_data = {
    "GPT-4.1-mini":    {"Recall": 100.0, "Precision": 25.9, "False Alarms": 43},
    "Gemini 2.5 Flash": {"Recall": 100.0, "Precision": 35.7, "False Alarms": 27},
    "GPT-4.1-nano":    {"Recall": 100.0, "Precision": 26.8, "False Alarms": 41},
}

# Level 3
l3_data = {
    "GPT-4.1-mini":    {"Recall": 82.2, "Precision": 78.7, "Avg Det Rate": 73.0},
    "Gemini 2.5 Flash": {"Recall": 93.3, "Precision": 72.4, "Avg Det Rate": 85.0},
    "GPT-4.1-nano":    {"Recall": 62.2, "Precision": 82.3, "Avg Det Rate": 60.2},
}

# =============================================
# CREATE THE HERO FIGURE
# =============================================
fig = plt.figure(figsize=(16, 14))

# Main title
fig.suptitle(
    'E²-Bench: Comprehensive Self-Validation Reliability Assessment\n'
    'Three Levels × Three Models',
    fontsize=16, fontweight='bold', y=0.98
)

gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3, top=0.92, bottom=0.05)

# =============================================
# Panel A: Level 1 — FPR Heatmap
# =============================================
ax1 = fig.add_subplot(gs[0, 0])

domains = ["Code", "Reasoning", "Data\nAnalysis"]
data = np.array([
    [l1_fpr[m][d] for d in ["Code", "Reasoning", "Data Analysis"]] 
    for m in MODELS_SHORT
])

im = ax1.imshow(data, cmap='Reds', aspect='auto', vmin=0, vmax=100)

ax1.set_xticks(range(len(domains)))
ax1.set_xticklabels(domains, fontsize=9)
ax1.set_yticks(range(len(MODELS)))
ax1.set_yticklabels(MODELS, fontsize=9)

for i in range(len(MODELS)):
    for j in range(len(domains)):
        val = data[i, j]
        color = "white" if val > 60 else "black"
        ax1.text(j, i, f"{val:.0f}%", ha="center", va="center",
                fontsize=13, fontweight="bold", color=color)

ax1.set_title('(A) Level 1: Logical Validation\nFalse Positive Rate ("Yes Man" Bias)',
              fontsize=11, fontweight='bold', pad=10)

cbar = plt.colorbar(im, ax=ax1, shrink=0.7, pad=0.02)
cbar.set_label('FPR (%)', fontsize=9)

# Add danger annotation
ax1.annotate('DANGER\nZONE', xy=(2.6, 1), fontsize=8, fontweight='bold',
            color='darkred', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFE0E0', edgecolor='darkred', alpha=0.8))

# =============================================
# Panel B: Level 2 — Perceptual Validation
# =============================================
ax2 = fig.add_subplot(gs[0, 1])

x = np.arange(len(MODELS))
width = 0.25

recalls = [l2_data[m]["Recall"] for m in MODELS_SHORT]
precisions = [l2_data[m]["Precision"] for m in MODELS_SHORT]
# Compute F1
f1s = [2*r*p/(r+p) if (r+p) > 0 else 0 for r, p in zip(recalls, precisions)]

bars1 = ax2.bar(x - width, recalls, width, label='Recall', color='#34A853', alpha=0.85)
bars2 = ax2.bar(x, precisions, width, label='Precision', color='#EA4335', alpha=0.85)
bars3 = ax2.bar(x + width, f1s, width, label='F1', color='#FBBC04', alpha=0.85)

for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., h + 1,
                f'{h:.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')

ax2.set_title('(B) Level 2: Perceptual Validation\nUI Bug Detection (Planted Bug Paradigm)',
              fontsize=11, fontweight='bold', pad=10)
ax2.set_xticks(x)
ax2.set_xticklabels(MODELS, fontsize=9)
ax2.set_ylim(0, 120)
ax2.set_ylabel('Rate (%)')
ax2.legend(loc='upper right', fontsize=9)

# Add annotation about the gap
ax2.annotate('100% Recall but\n~30% Precision\n= Over-Reporting',
            xy=(1, 70), fontsize=8, fontstyle='italic',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF3E0', edgecolor='#FF9800', alpha=0.8))

# =============================================
# Panel C: Level 3 — Consistency Validation
# =============================================
ax3 = fig.add_subplot(gs[1, 0])

x = np.arange(len(MODELS))
width = 0.25

l3_recalls = [l3_data[m]["Recall"] for m in MODELS_SHORT]
l3_precisions = [l3_data[m]["Precision"] for m in MODELS_SHORT]
l3_det = [l3_data[m]["Avg Det Rate"] for m in MODELS_SHORT]

bars1 = ax3.bar(x - width, l3_recalls, width, label='Recall', color='#34A853', alpha=0.85)
bars2 = ax3.bar(x, l3_precisions, width, label='Precision', color='#FBBC04', alpha=0.85)
bars3 = ax3.bar(x + width, l3_det, width, label='Avg Det Rate', color='#4285F4', alpha=0.85)

for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., h + 1,
                f'{h:.0f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')

ax3.set_title('(C) Level 3: Consistency Validation\nCross-Context Contradiction Detection',
              fontsize=11, fontweight='bold', pad=10)
ax3.set_xticks(x)
ax3.set_xticklabels(MODELS, fontsize=9)
ax3.set_ylim(0, 110)
ax3.set_ylabel('Rate (%)')
ax3.legend(loc='upper right', fontsize=9)

# Add annotation
ax3.annotate('Best level:\nScales with\nmodel capability',
            xy=(1, 50), fontsize=8, fontstyle='italic',
            ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F5E9', edgecolor='#4CAF50', alpha=0.8))

# =============================================
# Panel D: Cross-Level Radar / Summary
# =============================================
ax4 = fig.add_subplot(gs[1, 1], polar=True)

# Compute summary scores per level per model
# L1: 100 - avg FPR (lower FPR = better, so higher score = better)
# L2: Precision
# L3: F1 = 2*P*R/(P+R)
categories = ['L1: Logical\n(100-FPR)', 'L2: Perceptual\n(Precision)', 'L3: Consistency\n(F1 Score)']
N = len(categories)

model_scores = {}
for m in MODELS_SHORT:
    fpr_avg = np.mean([l1_fpr[m][d] for d in ["Code", "Reasoning", "Data Analysis"]])
    l1_score = 100 - fpr_avg
    l2_score = l2_data[m]["Precision"]
    l3_r = l3_data[m]["Recall"]
    l3_p = l3_data[m]["Precision"]
    l3_f1 = 2 * l3_r * l3_p / (l3_r + l3_p) if (l3_r + l3_p) > 0 else 0
    model_scores[m] = [l1_score, l2_score, l3_f1]

angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

for i, m in enumerate(MODELS_SHORT):
    values = model_scores[m] + model_scores[m][:1]
    ax4.plot(angles, values, 'o-', linewidth=2, label=MODELS[i].replace('\n', ' '),
            color=MODEL_COLORS[i], markersize=6)
    ax4.fill(angles, values, alpha=0.1, color=MODEL_COLORS[i])

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(categories, fontsize=9)
ax4.set_ylim(0, 100)
ax4.set_yticks([20, 40, 60, 80])
ax4.set_yticklabels(['20', '40', '60', '80'], fontsize=8)
ax4.set_title('(D) Cross-Level Reliability Summary\n(Higher = More Reliable)',
              fontsize=11, fontweight='bold', pad=20)
ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)

# Add a "50% random baseline" circle
theta = np.linspace(0, 2*np.pi, 100)
ax4.plot(theta, [50]*100, '--', color='gray', alpha=0.4, linewidth=1)
ax4.text(np.pi/4, 54, 'random\nbaseline', fontsize=7, color='gray', alpha=0.6, ha='center')

plt.savefig(os.path.join(OUTPUT_DIR, "fig_hero_comprehensive.png"))
plt.close()
print(f"Hero figure saved to {OUTPUT_DIR}/fig_hero_comprehensive.png")
