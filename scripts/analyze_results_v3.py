#!/usr/bin/env python3
"""
E²-Bench Results Analysis v3 — All 3 Models, All 3 Levels
Generates publication-quality figures for the paper.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT_DIR = "/home/ubuntu/e2_bench/paper/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Use a clean style then customize
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'figure.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

MODELS = ["GPT-4.1-mini", "Gemini 2.5 Flash", "GPT-4.1-nano"]
MODEL_COLORS = ["#4285F4", "#EA4335", "#34A853"]

# ============================================================
# DATA (from pilot evaluations)
# ============================================================

# Level 1: FPR data
l1_fpr = {
    "GPT-4.1-mini":    {"Code": 100.0, "Reasoning": 100.0, "Data Analysis": 100.0},
    "Gemini 2.5 Flash": {"Code": 66.7,  "Reasoning": 100.0, "Data Analysis": 100.0},
    "GPT-4.1-nano":    {"Code": 100.0, "Reasoning": 80.0,  "Data Analysis": 100.0},
}

l1_sva = {
    "GPT-4.1-mini":    {"Code": 30.0, "Reasoning": 60.0, "Data Analysis": 20.0},
    "Gemini 2.5 Flash": {"Code": 40.0, "Reasoning": 60.0, "Data Analysis": 20.0},
    "GPT-4.1-nano":    {"Code": 30.0, "Reasoning": 60.0, "Data Analysis": 20.0},
}

l1_tca = {
    "GPT-4.1-mini":    {"Code": 30.0, "Reasoning": 60.0, "Data Analysis": 20.0},
    "Gemini 2.5 Flash": {"Code": 10.0, "Reasoning": 80.0, "Data Analysis": 20.0},
    "GPT-4.1-nano":    {"Code": 30.0, "Reasoning": 50.0, "Data Analysis": 20.0},
}

# Level 2: Perceptual
l2_data = {
    "GPT-4.1-mini":    {"Recall": 100.0, "Precision": 25.9, "False Alarms": 43},
    "Gemini 2.5 Flash": {"Recall": 100.0, "Precision": 35.7, "False Alarms": 27},
    "GPT-4.1-nano":    {"Recall": 100.0, "Precision": 26.8, "False Alarms": 41},
}

# Level 3: Consistency
l3_data = {
    "GPT-4.1-mini":    {"Recall": 82.2, "Precision": 78.7, "Avg Det Rate": 73.0},
    "Gemini 2.5 Flash": {"Recall": 93.3, "Precision": 72.4, "Avg Det Rate": 85.0},
    "GPT-4.1-nano":    {"Recall": 62.2, "Precision": 82.3, "Avg Det Rate": 60.2},
}

# ============================================================
# FIGURE 1: FPR Heatmap (Level 1)
# ============================================================
def fig1_fpr_heatmap():
    domains = ["Code", "Reasoning", "Data Analysis"]
    data = np.array([[l1_fpr[m][d] for d in domains] for m in MODELS])
    
    fig, ax = plt.subplots(figsize=(7, 3.5))
    im = ax.imshow(data, cmap='Reds', aspect='auto', vmin=0, vmax=100)
    
    ax.set_xticks(range(len(domains)))
    ax.set_xticklabels(domains)
    ax.set_yticks(range(len(MODELS)))
    ax.set_yticklabels(MODELS)
    
    for i in range(len(MODELS)):
        for j in range(len(domains)):
            val = data[i, j]
            color = "white" if val > 70 else "black"
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center", 
                    fontsize=14, fontweight="bold", color=color)
    
    ax.set_title('Level 1: False Positive Rate ("Yes Man" Bias)\nHigher = More Dangerous', 
                 fontsize=13, fontweight='bold', pad=10)
    
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('False Positive Rate (%)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_fpr_heatmap.png"))
    plt.close()
    print("  fig1_fpr_heatmap.png saved")

# ============================================================
# FIGURE 2: SVA vs TCA Comparison (Level 1)
# ============================================================
def fig2_sva_vs_tca():
    domains = ["Code", "Reasoning", "Data Analysis"]
    
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    
    x = np.arange(len(MODELS))
    width = 0.35
    
    for idx, domain in enumerate(domains):
        sva_vals = [l1_sva[m][domain] for m in MODELS]
        tca_vals = [l1_tca[m][domain] for m in MODELS]
        
        bars1 = axes[idx].bar(x - width/2, sva_vals, width, label='SVA', color='#4285F4', alpha=0.85)
        bars2 = axes[idx].bar(x + width/2, tca_vals, width, label='TCA', color='#FBBC04', alpha=0.85)
        
        axes[idx].set_title(domain, fontweight='bold')
        axes[idx].set_xticks(x)
        axes[idx].set_xticklabels([m.replace(" ", "\n") for m in MODELS], fontsize=9)
        axes[idx].set_ylim(0, 105)
        axes[idx].set_ylabel('Accuracy (%)' if idx == 0 else '')
        
        for bar in bars1:
            axes[idx].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                          f'{bar.get_height():.0f}%', ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            axes[idx].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                          f'{bar.get_height():.0f}%', ha='center', va='bottom', fontsize=9)
    
    axes[0].legend(loc='upper right')
    fig.suptitle('Level 1: Self-Validation Accuracy (SVA) vs Task Completion Accuracy (TCA)', 
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_sva_vs_tca.png"))
    plt.close()
    print("  fig2_sva_vs_tca.png saved")

# ============================================================
# FIGURE 3: Level 2 Perceptual - Recall vs Precision
# ============================================================
def fig3_perceptual():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    
    x = np.arange(len(MODELS))
    width = 0.35
    
    recalls = [l2_data[m]["Recall"] for m in MODELS]
    precisions = [l2_data[m]["Precision"] for m in MODELS]
    
    bars1 = ax1.bar(x - width/2, recalls, width, label='Recall', color='#34A853', alpha=0.85)
    bars2 = ax1.bar(x + width/2, precisions, width, label='Precision', color='#EA4335', alpha=0.85)
    
    ax1.set_title('Recall vs Precision', fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([m.replace(" ", "\n") for m in MODELS], fontsize=9)
    ax1.set_ylim(0, 115)
    ax1.set_ylabel('Rate (%)')
    ax1.legend()
    
    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{bar.get_height():.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar in bars2:
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # False alarms
    false_alarms = [l2_data[m]["False Alarms"] for m in MODELS]
    planted = [15, 15, 15]  # 15 planted bugs per model
    
    bars3 = ax2.bar(x - width/2, planted, width, label='Planted Bugs', color='#4285F4', alpha=0.85)
    bars4 = ax2.bar(x + width/2, false_alarms, width, label='False Alarms', color='#EA4335', alpha=0.85)
    
    ax2.set_title('Planted Bugs vs False Alarms', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([m.replace(" ", "\n") for m in MODELS], fontsize=9)
    ax2.set_ylabel('Count')
    ax2.legend()
    
    for bar in bars3:
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    for bar in bars4:
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{int(bar.get_height())}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    fig.suptitle('Level 2 (Perceptual): UI Bug Detection Performance', 
                 fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_perceptual.png"))
    plt.close()
    print("  fig3_perceptual.png saved")

# ============================================================
# FIGURE 4: Level 3 Consistency
# ============================================================
def fig4_consistency():
    fig, ax = plt.subplots(figsize=(8, 5))
    
    x = np.arange(len(MODELS))
    width = 0.25
    
    recalls = [l3_data[m]["Recall"] for m in MODELS]
    precisions = [l3_data[m]["Precision"] for m in MODELS]
    det_rates = [l3_data[m]["Avg Det Rate"] for m in MODELS]
    
    bars1 = ax.bar(x - width, recalls, width, label='Recall', color='#34A853', alpha=0.85)
    bars2 = ax.bar(x, precisions, width, label='Precision', color='#FBBC04', alpha=0.85)
    bars3 = ax.bar(x + width, det_rates, width, label='Avg Detection Rate', color='#4285F4', alpha=0.85)
    
    ax.set_title('Level 3 (Consistency): Contradiction Detection Performance', 
                 fontweight='bold', fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(MODELS, fontsize=10)
    ax.set_ylim(0, 110)
    ax.set_ylabel('Rate (%)')
    ax.legend(loc='upper right')
    
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                   f'{bar.get_height():.0f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_consistency.png"))
    plt.close()
    print("  fig4_consistency.png saved")

# ============================================================
# FIGURE 5: Cross-Level Reliability Summary (Radar/Spider)
# ============================================================
def fig5_cross_level():
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Create a summary metric per level per model
    # L1: 100 - avg FPR (lower FPR = better)
    # L2: Precision (higher = better)
    # L3: F1 = 2*P*R/(P+R)
    
    categories = [
        'L1: Logical\n(100-FPR)',
        'L2: Perceptual\n(Precision)',
        'L3: Consistency\n(F1 Score)'
    ]
    
    model_scores = {}
    for m in MODELS:
        fpr_avg = np.mean([l1_fpr[m][d] for d in ["Code", "Reasoning", "Data Analysis"]])
        l1_score = 100 - fpr_avg
        l2_score = l2_data[m]["Precision"]
        l3_r = l3_data[m]["Recall"]
        l3_p = l3_data[m]["Precision"]
        l3_f1 = 2 * l3_r * l3_p / (l3_r + l3_p) if (l3_r + l3_p) > 0 else 0
        model_scores[m] = [l1_score, l2_score, l3_f1]
    
    x = np.arange(len(categories))
    width = 0.25
    
    for i, m in enumerate(MODELS):
        bars = ax.bar(x + i * width, model_scores[m], width, 
                     label=m, color=MODEL_COLORS[i], alpha=0.85)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                   f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_title('Cross-Level Reliability Summary\n(Higher = More Reliable Self-Validation)', 
                 fontweight='bold', fontsize=13)
    ax.set_xticks(x + width)
    ax.set_xticklabels(categories, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_ylabel('Score (%)')
    ax.legend(loc='upper right')
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='_nolegend_')
    ax.text(-0.3, 51, 'Random baseline', fontsize=9, color='gray', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_cross_level.png"))
    plt.close()
    print("  fig5_cross_level.png saved")

# ============================================================
# RUN ALL
# ============================================================
if __name__ == "__main__":
    print("Generating E²-Bench figures (3 models, 3 levels)...")
    fig1_fpr_heatmap()
    fig2_sva_vs_tca()
    fig3_perceptual()
    fig4_consistency()
    fig5_cross_level()
    print(f"\nAll figures saved to {OUTPUT_DIR}")
