# Codebook — `eu27_nis2_dataset_v2.csv`

*Version 2 — 7 September 2026. Supersedes v1. The `dedicated_cyber_agency` variable has now been coded for all 27 states against the Commission's official per-country NIS2 pages, replacing the flawed `single_dedicated_authority_PROVISIONAL` from v0/v1.*

## 1. Variable-by-variable

| Variable | Meaning | Source | Vintage | Scale | Status |
|---|---|---|---|---|---|
| `country` | EU27 member state | — | — | — | — |
| `enforcement_tier` | Position on Commission NIS2 enforcement ladder (0=fastest … 3=CJEU-referred) | Commission press releases | Snapshot 7 Sept 2026 | Ordinal 0–3 | Unchanged, high confidence. |
| `gov_effectiveness` / `gov_effectiveness_se` | WGI Government Effectiveness estimate + standard error | World Bank API, `source=3`, `GOV_WGI_GE.EST`/`GOV_WGI_GE.SE` | 2024, all 27 | Continuous | Verified (v1). |
| `gdp_per_capita_ppp` | GDP per capita, PPP | World Bank API, `NY.GDP.PCAP.PP.CD` | 2025, all 27 | Continuous | Verified (v1). |
| `population` | Total population | Eurostat (via Wikipedia's sourced EU table) | 1 Jan 2025, all 27 | Continuous | Verified (v1). |
| `strategy_year` / `strategy_since_2022` | Cybersecurity strategy recency | ENISA NCSS map | ~Sept 2026 | Year / binary | Unchanged (v0). |
| `single_dedicated_authority_PROVISIONAL` | Old, retired v0 coding | nisd2.eu | — | Binary | **Retired — kept only as a record of what was wrong. Do not use.** |
| `dedicated_cyber_agency` | 1 = the NIS2 Single Point of Contact (and/or lead CSIRT) is a specialized, cyber-dedicated body; 0 = it sits inside a general ministry or a broader security/regulatory body | **Commission's official per-country NIS2 pages** (digital-strategy.ec.europa.eu/en/policies/nis-directive-\<country\>), all 27 checked individually | Pulled 7 Sept 2026 | Binary | **New in v2, primary source, all 27 verified.** Split: 13 coded 1, 14 coded 0 — reasonably balanced. See §2 for the exact coding rule and six flagged borderline cases. |
| `cyber_gov_maturity` | Domain-specific cyber-governance maturity index | `strategy_since_2022` + `dedicated_cyber_agency` | — | Ordinal 0–2 | **Restored to the intended 0–2 design**, now built on a properly verified second component. |
| `delay_days` (in `delay_days_partial.csv`) | Days between the 17 Oct 2024 Art. 41 deadline and each state's transposing law entering into force. Negative = transposed early. | National gazettes / legal-tracker sources, per-country notes in `code/build_delay_days.py` | Pulled 7 Sept 2026 | Continuous (can be negative) | **Complete, 27/27** (22 observed + 5 censored; 19 exact dates, 3 month-only). Malta and Latvia — the two cases open in earlier passes — were closed in a third verification pass. Descriptive use only — do not feed into a survival model directly. |
| `time_since_directive_days` (in `delay_days_partial.csv`) | Days between NIS2's entry into force (16 Jan 2023) and each state's transposing law entering into force. Non-negative by construction. | Same as `delay_days`, re-based | Pulled 7 Sept 2026 | Continuous (≥0) | Same coverage as `delay_days` — **complete, 27/27**. This is the outcome variable used in the Cox PH survival model (`code/survival_analysis.py`), not `delay_days`, because Cox models need a non-negative time variable (see the docstring in that script). |
| `censored` (in `delay_days_partial.csv`) | 1 = state had not transposed as of the 7 Sept 2026 cutoff (right-censored); 0 = transposition date observed | Derived | — | Binary | 5 censored: Austria, France, Ireland, Netherlands, Spain. |

## 2. Coding rule for `dedicated_cyber_agency` and where it's genuinely a judgment call

**Rule:** code 1 if the country's official NIS2 Single Point of Contact (and/or its lead CSIRT) is a body whose name and primary mandate is specifically cybersecurity or information-systems security — an "agency," "centre," or "authority" built around that mission, regardless of its precise legal status. Code 0 if the SPOC is a department/directorate inside a general-purpose ministry (interior, digital governance, home affairs), or a broader body whose mandate spans more than cybersecurity (national security councils, civil-contingencies/emergency-management agencies, general telecom/utilities regulators, classified-information-protection authorities).

This is a real interpretive judgment, not a mechanical fact, and six cases could plausibly be coded the other way depending on how strictly "cyber-specific" is read:

- **Estonia** (coded 1): RIA, the "Information System Authority" — its remit is broader than cybersecurity alone (it covers state IT infrastructure generally), but it's consistently treated as Estonia's cyber agency in comparative literature.
- **Finland** (coded 1): the NCSC-FI is a named, cyber-specific unit, but it sits inside Traficom, which is fundamentally a transport/communications regulator, not a cyber body.
- **Romania** (coded 1): CERT-RO is a standalone incident-response body, not embedded in a ministry, but it's narrower than the "agency" model (ACN, BSI, ANSSI) the rule was built around.
- **Croatia** (coded 0): the SPOC is the Office of the National Security Council — a general security coordination body, not cyber-specific, though "National Security Council" bodies in some countries do lean heavily cyber in practice.
- **Slovakia** (coded 0): the National Security Authority (NBÚ) also handles classified-information protection — broader than cyber alone, but it's a specialized security body, not a general ministry.
- **Sweden** (coded 0): MSB, the Swedish Civil Contingencies Agency, has a broad civil-protection/emergency-management mandate with cyber as one part — but it is still a dedicated agency, not a ministry department, which is a different kind of "not quite fitting the rule" than Austria or Malta.

**Recommendation:** before this variable goes into the final regression, get a second, independent read on these six specifically — even just re-reading each one's official Commission page yourself and seeing if you'd code it the same way. A few flips here could move the variable's correlation with the DV, and it's cheap insurance given how central this variable is to H3.

## 3. What changed empirically between v1 and v2

- `dedicated_cyber_agency` alone correlates **-0.18** with `enforcement_tier` (i.e., having a dedicated agency associates with a *better*, lower-numbered tier) — the expected direction for H3, though still a raw bivariate correlation, not a regression result.
- The combined `cyber_gov_maturity` (strategy recency + dedicated agency) correlates only **-0.015** with `enforcement_tier` — essentially flat. This is worth sitting with rather than averaging away: the two components are pulling in different directions once combined, and it's possible one component (strategy recency) is adding noise rather than signal to H3. Consider reporting both the combined index and `dedicated_cyber_agency` alone as separate specifications in the robustness battery, rather than committing only to the combined index.
- `dedicated_cyber_agency` correlates **0.10** with `gov_effectiveness` — small, not the near-zero seen in the v0 pass, but still low enough that both variables are defensible in the same model without serious collinearity concern.
