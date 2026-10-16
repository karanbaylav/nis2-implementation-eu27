"""
Primary analysis: ordered logit of enforcement_tier on institutional-capacity
predictors, per the thesis pre-analysis plan.

Baseline: enforcement_tier ~ gov_effectiveness + cyber_gov_maturity + log(gdp_per_capita_ppp)
Robustness: ordered probit; dedicated_cyber_agency alone instead of combined index;
            log(population) added; leave-one-out; correlation matrix.

NOTE: the delay_days survival-model robustness check from the pre-analysis
plan is NOT run here -- that variable has not been built yet (needs manual
EUR-Lex/national-gazette date verification). This
script covers everything that's possible with the current dataset.
"""
import pandas as pd
import numpy as np
from statsmodels.miscmodels.ordinal_model import OrderedModel

df = pd.read_csv("data/processed/eu27_nis2_dataset_v2.csv")
df["log_gdp"] = np.log(df["gdp_per_capita_ppp"])
df["log_pop"] = np.log(df["population"])

print("="*70)
print("N =", len(df))
print("\nCorrelation matrix (continuous predictors):")
corr_vars = ["gov_effectiveness", "cyber_gov_maturity", "dedicated_cyber_agency",
             "log_gdp", "log_pop", "enforcement_tier"]
print(df[corr_vars].corr().round(3))

def run_ordered(y, X_df, distr="logit", label=""):
    mod = OrderedModel(y, X_df, distr=distr)
    res = mod.fit(method="bfgs", disp=False, maxiter=500)
    print(f"\n{'='*70}\n{label}\n{'='*70}")
    print(res.summary())
    return res

y = df["enforcement_tier"]

# --- Baseline specification -------------------------------------------------
X1 = df[["gov_effectiveness", "cyber_gov_maturity", "log_gdp"]]
res1 = run_ordered(y, X1, "logit", "BASELINE: ordered logit, gov_eff + cyber_gov_maturity + log(gdp_pc)")

# --- Robustness 1: ordered probit -------------------------------------------
res2 = run_ordered(y, X1, "probit", "ROBUSTNESS 1: ordered probit, same specification")

# --- Robustness 2: dedicated_cyber_agency alone instead of combined index --
X3 = df[["gov_effectiveness", "dedicated_cyber_agency", "log_gdp"]]
res3 = run_ordered(y, X3, "logit", "ROBUSTNESS 2: ordered logit, dedicated_cyber_agency alone (not combined index)")

# --- Robustness 3: add log(population) --------------------------------------
X4 = df[["gov_effectiveness", "cyber_gov_maturity", "log_gdp", "log_pop"]]
res4 = run_ordered(y, X4, "logit", "ROBUSTNESS 3: baseline + log(population)")

# --- Robustness 4: leave-one-out on the baseline gov_effectiveness coef ----
print(f"\n{'='*70}\nROBUSTNESS 4: Leave-one-out (baseline spec, gov_effectiveness coefficient)\n{'='*70}")
loo_results = []
for i, country in enumerate(df["country"]):
    df_loo = df.drop(index=i).reset_index(drop=True)
    X_loo = df_loo[["gov_effectiveness", "cyber_gov_maturity", "log_gdp"]]
    y_loo = df_loo["enforcement_tier"]
    try:
        mod = OrderedModel(y_loo, X_loo, distr="logit")
        r = mod.fit(method="bfgs", disp=False, maxiter=500)
        coef = r.params["gov_effectiveness"]
        pval = r.pvalues["gov_effectiveness"]
        loo_results.append((country, coef, pval))
    except Exception as e:
        loo_results.append((country, None, None))

print(f"{'Dropped country':16}{'gov_eff coef':>14}{'p-value':>10}")
for country, coef, pval in loo_results:
    if coef is not None:
        print(f"{country:16}{coef:14.3f}{pval:10.3f}")
    else:
        print(f"{country:16}{'FAILED':>14}")

coefs = [c for _, c, _ in loo_results if c is not None]
print(f"\ngov_effectiveness coefficient range across leave-one-out: "
      f"[{min(coefs):.3f}, {max(coefs):.3f}], full-sample = {res1.params['gov_effectiveness']:.3f}")
sign_flips = [c for c, _, _ in loo_results if _ is not None]
n_same_sign = sum(1 for _, coef, _ in loo_results if coef is not None and (coef > 0) == (res1.params["gov_effectiveness"] > 0))
print(f"Sign stable in {n_same_sign}/{len(coefs)} leave-one-out re-estimations")
