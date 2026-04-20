#!/usr/bin/env python3
"""
E²-Bench Results Analysis v2 — All 3 Levels
Generates publication-quality figures for the paper.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# Apply style first, then set fonts
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'figure.dpi': 300,
    'savefig.dpi': 300,

})

FIG_DIR = "/home/ubuntu/e2_bench/paper/figures"
os.makedirs(FIG_DIR, exist_ok=True)

# ============================================================
# Data from Pilot v2 Results
# ============================================================

# Level 1: Logical Validation
L1_DATA = {
    "gpt-4.1-mini": {
        "code":          {"SVA": 0.30, "FPR": 1.00, "FNR": 0.00, "TCA": 0.30},
        "reasoning":     {"SVA": 0.60, "FPR": 1.00, "FNR": 0.00, "TCA": 0.60},
        "data_analysis": {"SVA": 0.20, "FPR": 1.00, "FNR": 0.00, "TCA": 0.20},
    },
    "gemini-2.5-flash": {
        "code":          {"SVA": 0.40, "FPR": 0.667, "FNR": 0.00, "TCA": 0.10},
        "reasoning":     {"SVA": 0.60, "FPR": 1.00, "FNR": 0.25, "TCA": 0.80},
        "data_analysis": {"SVA": 0.20, "FPR": 1.00, "FNR": 0.00, "TCA": 0.20},
    }
}

# Level 2: Perceptual Validation
L2_DATA = {
    "gpt-4.1-mini":     {"recall": 1.00, "precision": 0.259, "avg_det": 1.00, "false_alarms": 43, "planted": 15, "matched": 15},
    "gemini-2.5-flash":  {"recall": 1.00, "precision": 0.357, "avg_det": 1.00, "false_alarms": 27, "planted": 15, "matched": 15},
}

# Level 3: Consistency Validation
L3_DATA = {
    "gpt-4.1-mini":     {"recall": 0.822, "precision": 0.974, "avg_det": 0.80, "false_alarms": 1, "planted": 45, "matched": 37},
    "gemini-2.5-flash":  {"recall": 0.933, "precision": 0.955, "avg_det": 0.908, "false_alarms": 2, "planted": 45, "matched": 42},
}

L3_BY_CAT = {
    "gpt-4.1-mini": {
        "report_vs_data": {"matched": 6, "planted": 7},
        "readme_vs_code": {"matched": 19, "planted": 21},
        "chart_vs_data":  {"matched": 10, "planted": 13},
        "slide_deck":     {"matched": 2, "planted": 4},
    },
    "gemini-2.5-flash": {
        "report_vs_data": {"matched": 6, "planted": 7},
        "readme_vs_code": {"matched": 21, "planted": 21},
        "chart_vs_data":  {"matched": 12, "planted": 13},
        "slide_deck":     {"matched": 3, "planted": 4},
    }
}

COLORS = {
    "gpt-4.1-mini": "#4A90D9",
    "gemini-2.5-flash": "#E8744F",
}

# ============================================================
# Figure 1: Three-Level Overview (Radar/Spider Chart)
# ============================================================
def fig1_three_level_overview():
    fig, ax = plt.subplots(figsize=(8, 6))
    
    models = ["gpt-4.1-mini", "gemini-2.5-flash"]
    
    # Aggregate metrics per level
    # L1: average SVA across domains
    # L2: recall
    # L3: recall
    metrics_labels = [
        "L1: Logical\nSVA",
        "L1: Logical\nFPR (inverted)",
        "L2: Perceptual\nRecall",
        "L2: Perceptual\nPrecision",
        "L3: Consistency\nRecall",
        "L3: Consistency\nPrecision",
    ]
    
    x = np.arange(len(metrics_labels))
    width = 0.35
    
    for i, model in enumerate(models):
        l1 = L1_DATA[model]
        avg_sva = np.mean([l1[d]["SVA"] for d in l1])
        avg_fpr_inv = 1 - np.mean([l1[d]["FPR"] for d in l1])
        l2 = L2_DATA[model]
        l3 = L3_DATA[model]
        
        values = [
            avg_sva,
            avg_fpr_inv,
            l2["recall"],
            l2["precision"],
            l3["recall"],
            l3["precision"],
        ]
        
        bars = ax.bar(x + i * width - width/2, values, width, 
                      label=model, color=COLORS[model], alpha=0.85, edgecolor='white')
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.0%}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Score')
    ax.set_title('E²-Bench: Three-Level Self-Validation Performance Overview', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_labels, fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right')
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig1_three_level_overview.png"))
    plt.close()
    print("Saved fig1_three_level_overview.png")

# ============================================================
# Figure 2: Level 1 — SVA vs TCA Gap (The "Yes Man" Chart)
# ============================================================
def fig2_sva_vs_tca():
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    
    domains = ["code", "reasoning", "data_analysis"]
    domain_labels = ["Code", "Reasoning", "Data Analysis"]
    x = np.arange(len(domains))
    width = 0.35
    
    for idx, model in enumerate(["gpt-4.1-mini", "gemini-2.5-flash"]):
        ax = axes[idx]
        sva_vals = [L1_DATA[model][d]["SVA"] for d in domains]
        fpr_vals = [L1_DATA[model][d]["FPR"] for d in domains]
        tca_vals = [L1_DATA[model][d]["TCA"] for d in domains]
        
        bars1 = ax.bar(x - width/2, sva_vals, width, label='SVA', color='#2ecc71', alpha=0.85)
        bars2 = ax.bar(x + width/2, fpr_vals, width, label='FPR', color='#e74c3c', alpha=0.85)
        
        # Add TCA as text annotations
        for i, (s, f, t) in enumerate(zip(sva_vals, fpr_vals, tca_vals)):
            ax.text(i, max(s, f) + 0.05, f'TCA={t:.0%}', ha='center', fontsize=9, style='italic')
        
        ax.set_title(model, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(domain_labels)
        ax.set_ylim(0, 1.2)
        ax.legend(loc='upper left', fontsize=9)
    
    axes[0].set_ylabel('Rate')
    fig.suptitle('Level 1 (Logical): Self-Validation Accuracy vs False Positive Rate', 
                 fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig2_l1_sva_vs_fpr.png"))
    plt.close()
    print("Saved fig2_l1_sva_vs_fpr.png")

# ============================================================
# Figure 3: Level 2 — Perceptual Detection (Recall vs Precision)
# ============================================================
def fig3_perceptual():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    models = list(L2_DATA.keys())
    recalls = [L2_DATA[m]["recall"] for m in models]
    precisions = [L2_DATA[m]["precision"] for m in models]
    false_alarms = [L2_DATA[m]["false_alarms"] for m in models]
    
    # Left: Recall vs Precision
    x = np.arange(len(models))
    width = 0.3
    
    bars1 = ax1.bar(x - width/2, recalls, width, label='Recall', color='#2ecc71', alpha=0.85)
    bars2 = ax1.bar(x + width/2, precisions, width, label='Precision', color='#3498db', alpha=0.85)
    
    for bar, val in zip(bars1, recalls):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.0%}', ha='center', fontsize=10, fontweight='bold')
    for bar, val in zip(bars2, precisions):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.0%}', ha='center', fontsize=10, fontweight='bold')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=9)
    ax1.set_ylim(0, 1.2)
    ax1.set_ylabel('Rate')
    ax1.set_title('L2 Perceptual: Recall vs Precision', fontweight='bold')
    ax1.legend()
    
    # Right: Bug counts (planted vs found vs matched)
    planted = [L2_DATA[m]["planted"] for m in models]
    matched = [L2_DATA[m]["matched"] for m in models]
    fa = [L2_DATA[m]["false_alarms"] for m in models]
    
    bar_width = 0.25
    bars_p = ax2.bar(x - bar_width, planted, bar_width, label='Planted Bugs', color='#95a5a6')
    bars_m = ax2.bar(x, matched, bar_width, label='Correctly Detected', color='#2ecc71')
    bars_f = ax2.bar(x + bar_width, fa, bar_width, label='False Alarms', color='#e74c3c')
    
    for bars in [bars_p, bars_m, bars_f]:
        for bar in bars:
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{int(bar.get_height())}', ha='center', fontsize=10, fontweight='bold')
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(models, fontsize=9)
    ax2.set_ylabel('Count')
    ax2.set_title('L2 Perceptual: Bug Detection Counts', fontweight='bold')
    ax2.legend(fontsize=9)
    
    fig.suptitle('Level 2 (Perceptual): UI Bug Detection Performance', fontweight='bold', fontsize=13)
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig3_l2_perceptual.png"))
    plt.close()
    print("Saved fig3_l2_perceptual.png")

# ============================================================
# Figure 4: Level 3 — Consistency Detection by Category
# ============================================================
def fig4_consistency():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    categories = ["report_vs_data", "readme_vs_code", "chart_vs_data", "slide_deck"]
    cat_labels = ["Report vs\nData", "README vs\nCode", "Chart vs\nData", "Slide\nDeck"]
    
    x = np.arange(len(categories))
    width = 0.35
    
    for i, model in enumerate(["gpt-4.1-mini", "gemini-2.5-flash"]):
        rates = []
        for cat in categories:
            d = L3_BY_CAT[model][cat]
            rates.append(d["matched"] / d["planted"] if d["planted"] > 0 else 0)
        
        bars = ax.bar(x + i * width - width/2, rates, width,
                      label=model, color=COLORS[model], alpha=0.85, edgecolor='white')
        
        for j, (bar, rate) in enumerate(zip(bars, rates)):
            d = L3_BY_CAT[model][categories[j]]
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{d["matched"]}/{d["planted"]}', ha='center', fontsize=9, fontweight='bold')
    
    ax.set_ylabel('Detection Rate')
    ax.set_title('Level 3 (Consistency): Contradiction Detection by Category', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(cat_labels)
    ax.set_ylim(0, 1.15)
    ax.legend()
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, linewidth=0.8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig4_l3_consistency_by_cat.png"))
    plt.close()
    print("Saved fig4_l3_consistency_by_cat.png")

# ============================================================
# Figure 5: Cross-Level Comparison (The Money Chart)
# ============================================================
def fig5_cross_level():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    models = ["gpt-4.1-mini", "gemini-2.5-flash"]
    levels = ["L1: Logical\n(SVA)", "L1: Logical\n(1-FPR)", "L2: Perceptual\n(Precision)", "L3: Consistency\n(Recall)"]
    
    x = np.arange(len(levels))
    width = 0.35
    
    for i, model in enumerate(models):
        l1 = L1_DATA[model]
        avg_sva = np.mean([l1[d]["SVA"] for d in l1])
        avg_fpr_inv = 1 - np.mean([l1[d]["FPR"] for d in l1])
        
        values = [
            avg_sva,
            avg_fpr_inv,
            L2_DATA[model]["precision"],
            L3_DATA[model]["recall"],
        ]
        
        bars = ax.bar(x + i * width - width/2, values, width,
                      label=model, color=COLORS[model], alpha=0.85, edgecolor='white')
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.0%}', ha='center', fontsize=10, fontweight='bold')
    
    # Add a "danger zone" below 50%
    ax.axhspan(0, 0.5, alpha=0.08, color='red')
    ax.text(0.02, 0.25, 'Unreliable Zone', transform=ax.transAxes,
            fontsize=10, color='red', alpha=0.5, style='italic')
    
    ax.set_ylabel('Score (higher = more reliable)')
    ax.set_title('E²-Bench Cross-Level Reliability Comparison\n"Where do LLMs fail at self-validation?"',
                 fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.set_ylim(0, 1.15)
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig5_cross_level_comparison.png"))
    plt.close()
    print("Saved fig5_cross_level_comparison.png")

# ============================================================
# Figure 6: The "Validation Paradox" — L1 FPR Heatmap
# ============================================================
def fig6_fpr_heatmap():
    fig, ax = plt.subplots(figsize=(8, 4))
    
    models = ["gpt-4.1-mini", "gemini-2.5-flash"]
    domains = ["code", "reasoning", "data_analysis"]
    domain_labels = ["Code", "Reasoning", "Data Analysis"]
    
    data = np.array([
        [L1_DATA[m][d]["FPR"] for d in domains]
        for m in models
    ])
    
    im = ax.imshow(data, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=1)
    
    ax.set_xticks(np.arange(len(domains)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(domain_labels)
    ax.set_yticklabels(models)
    
    for i in range(len(models)):
        for j in range(len(domains)):
            text = ax.text(j, i, f'{data[i, j]:.0%}',
                          ha="center", va="center", color="white",
                          fontsize=14, fontweight="bold")
    
    ax.set_title('Level 1: False Positive Rate ("Yes Man" Bias)\nHigher = More Dangerous',
                 fontweight='bold')
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('False Positive Rate')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "fig6_l1_fpr_heatmap.png"))
    plt.close()
    print("Saved fig6_l1_fpr_heatmap.png")

# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("Generating E²-Bench paper figures...")
    fig1_three_level_overview()
    fig2_sva_vs_tca()
    fig3_perceptual()
    fig4_consistency()
    fig5_cross_level()
    fig6_fpr_heatmap()
    print(f"\nAll figures saved to {FIG_DIR}")
