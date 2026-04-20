"""
E²-Bench: Analyze pilot evaluation results and generate figures for the paper.
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'figure.dpi': 150,
})

OUTPUT_DIR = "/home/ubuntu/e2_bench/paper/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Data from pilot evaluation
# ============================================================
results = {
    "GPT-4.1-mini": {
        "Code Generation": {"SVA": 0.467, "FPR": 0.889, "FNR": 0.0, "TCA": 0.40, "TP": 12, "TN": 2, "FP": 16, "FN": 0},
        "Logical Reasoning": {"SVA": 0.900, "FPR": 1.0, "FNR": 0.0, "TCA": 0.90, "TP": 27, "TN": 0, "FP": 3, "FN": 0},
    },
    "Gemini 2.5 Flash": {
        "Code Generation": {"SVA": 0.467, "FPR": 0.889, "FNR": 0.0, "TCA": 0.40, "TP": 12, "TN": 2, "FP": 16, "FN": 0},
        "Logical Reasoning": {"SVA": 0.733, "FPR": 0.60, "FNR": 0.20, "TCA": 0.833, "TP": 20, "TN": 2, "FP": 3, "FN": 5},
        "Data Analysis": {"SVA": 0.250, "FPR": 1.0, "FNR": 0.0, "TCA": 0.25, "TP": 5, "TN": 0, "FP": 15, "FN": 0},
    }
}

# ============================================================
# Figure 1: SVA vs TCA comparison (the key insight)
# ============================================================
def plot_sva_vs_tca():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    models = ["GPT-4.1-mini", "Gemini 2.5 Flash"]
    domains = ["Code Generation", "Logical Reasoning"]
    
    x = np.arange(len(domains))
    width = 0.15
    
    colors_sva = ['#2196F3', '#4CAF50']
    colors_tca = ['#90CAF9', '#A5D6A7']
    
    for i, model in enumerate(models):
        sva_vals = [results[model][d]["SVA"] for d in domains]
        tca_vals = [results[model][d]["TCA"] for d in domains]
        
        offset = (i - 0.5) * width * 2.5
        bars1 = ax.bar(x + offset - width/2, tca_vals, width, label=f'{model} (TCA)', 
                       color=colors_tca[i], edgecolor='gray', linewidth=0.5)
        bars2 = ax.bar(x + offset + width/2, sva_vals, width, label=f'{model} (SVA)',
                       color=colors_sva[i], edgecolor='gray', linewidth=0.5)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.0%}',
                    ha='center', va='bottom', fontsize=9)
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01, f'{height:.0%}',
                    ha='center', va='bottom', fontsize=9)
    
    ax.set_ylabel('Accuracy')
    ax.set_title('Task Completion Accuracy (TCA) vs Self-Validation Accuracy (SVA)')
    ax.set_xticks(x)
    ax.set_xticklabels(domains)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.axhline(y=0.5, color='red', linestyle='--', alpha=0.3, label='Random baseline')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig1_sva_vs_tca.png'), bbox_inches='tight')
    plt.close()
    print("Saved fig1_sva_vs_tca.png")

# ============================================================
# Figure 2: False Positive Rate (Yes Man Bias) heatmap
# ============================================================
def plot_fpr_heatmap():
    fig, ax = plt.subplots(figsize=(8, 4))
    
    models = ["GPT-4.1-mini", "Gemini 2.5 Flash"]
    domains = ["Code Generation", "Logical Reasoning", "Data Analysis"]
    
    data = np.zeros((len(models), len(domains)))
    for i, model in enumerate(models):
        for j, domain in enumerate(domains):
            if domain in results[model]:
                data[i][j] = results[model][domain]["FPR"]
            else:
                data[i][j] = np.nan
    
    # Create heatmap
    cmap = plt.cm.Reds
    cmap.set_bad(color='lightgray')
    
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=1, aspect='auto')
    
    ax.set_xticks(np.arange(len(domains)))
    ax.set_yticks(np.arange(len(models)))
    ax.set_xticklabels(domains, fontsize=11)
    ax.set_yticklabels(models, fontsize=11)
    
    # Add text annotations
    for i in range(len(models)):
        for j in range(len(domains)):
            if not np.isnan(data[i][j]):
                text = ax.text(j, i, f'{data[i][j]:.0%}',
                              ha="center", va="center", color="white" if data[i][j] > 0.5 else "black",
                              fontsize=14, fontweight='bold')
            else:
                text = ax.text(j, i, 'N/A', ha="center", va="center", color="gray", fontsize=12)
    
    ax.set_title('False Positive Rate ("Yes Man" Bias) by Model and Domain', fontsize=14)
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('False Positive Rate', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig2_fpr_heatmap.png'), bbox_inches='tight')
    plt.close()
    print("Saved fig2_fpr_heatmap.png")

# ============================================================
# Figure 3: Confusion matrix visualization for each model-domain
# ============================================================
def plot_confusion_matrices():
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    configs = [
        ("GPT-4.1-mini", "Code Generation"),
        ("GPT-4.1-mini", "Logical Reasoning"),
        ("Gemini 2.5 Flash", "Code Generation"),
        ("Gemini 2.5 Flash", "Logical Reasoning"),
    ]
    
    for idx, (model, domain) in enumerate(configs):
        ax = axes[idx // 2][idx % 2]
        d = results[model][domain]
        
        cm = np.array([[d["TP"], d["FN"]], [d["FP"], d["TN"]]])
        total = cm.sum()
        
        im = ax.imshow(cm, cmap='Blues', vmin=0, vmax=total)
        
        labels = [["TP\n(Reliable)", "FN\n(Over-thinker)"], 
                  ["FP\n(Yes Man)", "TN\n(Reliable)"]]
        colors_text = [["white" if cm[0][0] > total*0.3 else "black", 
                        "white" if cm[0][1] > total*0.3 else "black"],
                       ["white" if cm[1][0] > total*0.3 else "black",
                        "white" if cm[1][1] > total*0.3 else "black"]]
        
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f'{labels[i][j]}\n{cm[i][j]}',
                       ha="center", va="center", fontsize=11, fontweight='bold',
                       color=colors_text[i][j])
        
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Actual: Correct", "Actual: Incorrect"])
        ax.set_yticklabels(["Agent: PASS", "Agent: FAIL"])
        ax.set_title(f'{model}\n{domain}', fontsize=12)
    
    plt.suptitle('Self-Validation Confusion Matrices', fontsize=16, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig3_confusion_matrices.png'), bbox_inches='tight')
    plt.close()
    print("Saved fig3_confusion_matrices.png")

# ============================================================
# Figure 4: The "Validation Gap" - SVA vs TCA scatter
# ============================================================
def plot_validation_gap():
    fig, ax = plt.subplots(figsize=(8, 8))
    
    markers = {'GPT-4.1-mini': 'o', 'Gemini 2.5 Flash': 's'}
    colors = {'Code Generation': '#E53935', 'Logical Reasoning': '#1E88E5', 'Data Analysis': '#43A047'}
    
    for model in results:
        for domain in results[model]:
            d = results[model][domain]
            ax.scatter(d["TCA"], d["SVA"], 
                      marker=markers[model], color=colors[domain],
                      s=200, edgecolors='black', linewidth=1, zorder=5)
            ax.annotate(f'{model[:8]}...\n{domain[:8]}...', 
                       (d["TCA"], d["SVA"]),
                       textcoords="offset points", xytext=(10, -10),
                       fontsize=8, alpha=0.7)
    
    # Diagonal line (SVA = TCA would mean perfect self-validation)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='SVA = TCA (ideal)')
    
    # Region labels
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.05, color='red')
    ax.text(0.7, 0.3, '"Yes Man"\nRegion', fontsize=12, alpha=0.4, ha='center',
            style='italic', color='red')
    
    ax.set_xlabel('Task Completion Accuracy (TCA)')
    ax.set_ylabel('Self-Validation Accuracy (SVA)')
    ax.set_title('The Validation Gap: TCA vs SVA')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    
    # Legend
    model_handles = [plt.Line2D([0], [0], marker=m, color='gray', linestyle='None', markersize=10, label=model)
                     for model, m in markers.items()]
    domain_handles = [plt.Line2D([0], [0], marker='o', color=c, linestyle='None', markersize=10, label=domain)
                      for domain, c in colors.items()]
    ax.legend(handles=model_handles + domain_handles, loc='upper left', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig4_validation_gap.png'), bbox_inches='tight')
    plt.close()
    print("Saved fig4_validation_gap.png")

# ============================================================
# Figure 5: Outcome distribution stacked bar chart
# ============================================================
def plot_outcome_distribution():
    fig, ax = plt.subplots(figsize=(12, 6))
    
    configs = []
    for model in results:
        for domain in results[model]:
            d = results[model][domain]
            total = d["TP"] + d["TN"] + d["FP"] + d["FN"]
            configs.append({
                "label": f'{model}\n{domain}',
                "TP": d["TP"]/total, "TN": d["TN"]/total,
                "FP": d["FP"]/total, "FN": d["FN"]/total,
            })
    
    labels = [c["label"] for c in configs]
    x = np.arange(len(labels))
    width = 0.6
    
    tp_vals = [c["TP"] for c in configs]
    tn_vals = [c["TN"] for c in configs]
    fp_vals = [c["FP"] for c in configs]
    fn_vals = [c["FN"] for c in configs]
    
    p1 = ax.bar(x, tp_vals, width, label='True Positive (Reliable)', color='#4CAF50')
    p2 = ax.bar(x, tn_vals, width, bottom=tp_vals, label='True Negative (Reliable)', color='#81C784')
    
    bottom2 = [tp + tn for tp, tn in zip(tp_vals, tn_vals)]
    p3 = ax.bar(x, fp_vals, width, bottom=bottom2, label='False Positive ("Yes Man")', color='#F44336')
    
    bottom3 = [b + fp for b, fp in zip(bottom2, fp_vals)]
    p4 = ax.bar(x, fn_vals, width, bottom=bottom3, label='False Negative ("Over-thinker")', color='#FFC107')
    
    ax.set_ylabel('Proportion of Tasks')
    ax.set_title('Outcome Distribution Across Models and Domains')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(0, 1.05)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'fig5_outcome_distribution.png'), bbox_inches='tight')
    plt.close()
    print("Saved fig5_outcome_distribution.png")

# ============================================================
# Run all
# ============================================================
if __name__ == "__main__":
    print("Generating figures for E²-Bench paper...\n")
    plot_sva_vs_tca()
    plot_fpr_heatmap()
    plot_confusion_matrices()
    plot_validation_gap()
    plot_outcome_distribution()
    print(f"\nAll figures saved to {OUTPUT_DIR}")
