"""
Re-draws Figures 4 and 5 (forest plots) from the saved regression tables.
Run from the repository root:  python code/make_forest_plots.py
Reads tables/table3_baseline_ordered_logit.csv and tables/table6_cox_ph_results.csv.
"""
import pandas as pd
import matplotlib.pyplot as plt

BLUE = "#3b5b92"
labels = {"gov_effectiveness": "gov_effectiveness",
          "cyber_gov_maturity": "cyber_gov_maturity",
          "log_gdp": "log(gdp_per_capita)",
          "log(gdp_per_capita)": "log(gdp_per_capita)"}


def forest(df, est, lo, hi, title, xlabel, outfile, log=False, ref=0.0):
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ys = list(range(len(df)))[::-1]
    for y, (_, r) in zip(ys, df.iterrows()):
        ax.plot([r[lo], r[hi]], [y, y], color=BLUE, lw=2)
        ax.plot(r[est], y, "o", color=BLUE, ms=7)
    ax.axvline(ref, color="k", ls="--", lw=0.8)
    ax.set_yticks(ys)
    ax.set_yticklabels([labels.get(v, v) for v in df["Variable"]])
    if log:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(outfile, dpi=200)
    plt.close(fig)


t3 = pd.read_csv("tables/table3_baseline_ordered_logit.csv")
forest(t3, "Coefficient", "CI Low", "CI High",
       "Figure 4. Baseline ordered-logit coefficients with 95% CI\n"
       "(enforcement_tier ~ gov_eff + cyber_gov_maturity + log_gdp)",
       "Coefficient (95% CI), ordered logit", "figures/fig4_ordered_logit_forest.png")

t6 = pd.read_csv("tables/table6_cox_ph_results.csv")
forest(t6, "HR", "CI Low", "CI High",
       "Figure 5. Cox PH hazard ratios with 95% CI\n"
       "(time_since_directive_days ~ gov_eff + cyber_gov_maturity + log_gdp)",
       "Hazard ratio (95% CI, log scale); >1 = faster transposition",
       "figures/fig5_cox_ph_forest.png", log=True, ref=1.0)
