"""
Robustness check: Cox proportional-hazards model of transposition delay,
per the thesis pre-analysis plan (section 6.2). Treats states that
had not transposed as of the 7 Sept 2026 cutoff as right-censored, rather
than dropping them or imputing a delay value.

Uses the full 27-state dataset (as of the 7 Sept 2026 third verification
pass, which closed the previously-open Malta and Latvia cases -- see
build_delay_days.py for the source trail on both): 22 with an observed
transposition date (event=1; 19 exact + 3 month-only precision), 5
right-censored (event=0: Austria + the four CJEU-referred states).

Uses time_since_directive_days (time since NIS2 entered into force, 16 Jan
2023) rather than delay_days (time since the 17 Oct 2024 deadline) as the
survival time, because two states -- Italy and especially Croatia --
transposed BEFORE the deadline, giving delay_days negative values for them.
Cox models require a non-negative time variable (statsmodels raises
"endog must be non-negative" otherwise); time_since_directive_days is
non-negative by construction since no state transposed before the directive
existed. See build_delay_days.py for the full rationale.
"""
import pandas as pd
import numpy as np
from statsmodels.duration.hazard_regression import PHReg

main = pd.read_csv("data/processed/eu27_nis2_dataset_v2.csv")
delay = pd.read_csv("data/processed/delay_days_partial.csv")

df = main.merge(delay, on="country", how="inner")
df["log_gdp"] = np.log(df["gdp_per_capita_ppp"])
# PHReg wants event=1 for the event happening (transposition observed),
# status=0 for censored (not yet transposed as of cutoff)
df["event_observed"] = 1 - df["censored"]

print(f"N used: {len(df)} (full EU27 -- no exclusions needed as of the third verification pass)")
print(f"Events observed (transposed): {df['event_observed'].sum()}, "
      f"censored (not yet transposed at cutoff): {(1-df['event_observed']).sum()}")

X = df[["gov_effectiveness", "cyber_gov_maturity", "log_gdp"]]
mod = PHReg(df["time_since_directive_days"], X, status=df["event_observed"])
res = mod.fit()
print("\n" + "="*70)
print("COX PROPORTIONAL HAZARDS MODEL: time_since_directive_days ~ gov_eff + cyber_gov_maturity + log_gdp")
print("(higher hazard ratio = FASTER transposition, i.e. shorter delay)")
print("="*70)
print(res.summary())

# hazard ratios for interpretability
hr = np.exp(res.params)
print("\nHazard ratios (exp(coef)):")
for name, val in zip(X.columns, hr):
    print(f"  {name}: {val:.3f}")
