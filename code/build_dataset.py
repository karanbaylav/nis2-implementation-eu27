"""
Build the EU27 NIS2 institutional-capacity dataset -- v1 (verified core variables).

Changelog from v0:
- gov_effectiveness + gov_effectiveness_se: replaced aggregator pull with
  official World Bank API data (source=3, indicator GOV_WGI_GE.EST /
  GOV_WGI_GE.SE), single consistent 2024 vintage for all 27 countries.
  This CHANGED Sweden's value materially (was 1.60/2023 via a different
  aggregator, now 1.77/2024 official) -- a concrete example of why the
  verification pass mattered, not a rounding difference.
- gdp_per_capita_ppp: replaced aggregator pull with official World Bank API
  data (NY.GDP.PCAP.PP.CD), single consistent 2025 vintage for all 27.
- population: replaced Worldometer pull with official Eurostat figures
  (via Wikipedia's EU population table, sourced to Eurostat, 1 Jan 2025),
  single consistent vintage for all 27.
- single_dedicated_authority / cyber_gov_maturity: DOWNGRADED, not fixed.
  Checking the Commission's own official per-country NIS2 pages (Latvia,
  Netherlands, Poland, Sweden) showed EVERY member state designates
  MULTIPLE sector-specific competent authorities (energy, transport,
  banking, health, water, digital infra, etc.) plus a single point of
  contact and a CSIRT -- this is how NIS2's legal architecture works for
  ALL 27 states, not a distinguishing feature of a few. The original
  "single vs. multiple authority" coding (from the nisd2.eu secondary
  tracker) was actually picking up something more like "is there one
  flagship arms-length cyber agency (e.g., Italy's ACN, Germany's BSI,
  France's ANSSI) vs. coordination handled by a ministry department
  (e.g., Poland's Ministry of Digital Affairs)" -- a real and
  theoretically interesting distinction, but NOT the one the variable
  name/coding implied, and not yet verified for enough countries to
  trust. Left in as `single_dedicated_authority_PROVISIONAL` with the
  old nisd2.eu-based values, EXCLUDED from cyber_gov_maturity until
  recoded properly. Resolved in v2 (see codebook.md): cyber_gov_maturity is now `strategy_since_2022`
  ALONE (0/1) pending that decision -- i.e., temporarily a weaker,
  single-component index, not the 0-2 index from v0.

Sources: see codebook.md for full citations, exact API calls, and dates
pulled (7 September 2026).
"""
import csv

# --- enforcement_tier (frozen cutoff 7 Sept 2026) -------------------
tier0 = {"Belgium", "Croatia", "Italy", "Lithuania"}
tier1 = {"Greece", "Malta", "Romania", "Slovakia"}
tier3 = {"Ireland", "Spain", "France", "Netherlands"}
# tier2 = everyone else

# --- Government Effectiveness, VERIFIED: World Bank API, source=3, --------
# indicator GOV_WGI_GE.EST, mrv=1 -> all countries return 2024. Pulled 7 Sept 2026.
gov_eff = {
    "Austria": 1.5145106, "Belgium": 1.1947395, "Bulgaria": 0.0428203,
    "Cyprus": 0.8696373, "Czechia": 1.1773279, "Germany": 1.5462994,
    "Denmark": 1.9128986, "Spain": 1.110811, "Estonia": 1.2969908,
    "Finland": 1.8171611, "France": 1.2007009, "Greece": 0.1912731,
    "Croatia": 0.7097625, "Hungary": 0.501908, "Ireland": 1.6115533,
    "Italy": 0.7922891, "Lithuania": 1.2014922, "Luxembourg": 2.0397137,
    "Latvia": 0.7431802, "Malta": 0.622496, "Netherlands": 1.7519974,
    "Poland": 0.6734027, "Portugal": 0.9474847, "Romania": 0.4181246,
    "Slovakia": 0.6575804, "Slovenia": 1.0893351, "Sweden": 1.7746948,
}
gov_eff_se = {  # standard error of the same estimate, same source/vintage
    "Austria": 0.2226321, "Belgium": 0.2226321, "Bulgaria": 0.2124527,
    "Cyprus": 0.2226321, "Czechia": 0.2124527, "Germany": 0.2226321,
    "Denmark": 0.2237758, "Spain": 0.2226321, "Estonia": 0.2124527,
    "Finland": 0.2237758, "France": 0.2226321, "Greece": 0.2226321,
    "Croatia": 0.2124527, "Hungary": 0.2124527, "Ireland": 0.2226321,
    "Italy": 0.2226321, "Lithuania": 0.2134459, "Luxembourg": 0.2237758,
    "Latvia": 0.2124527, "Malta": 0.2359767, "Netherlands": 0.2237758,
    "Poland": 0.2124527, "Portugal": 0.2226321, "Romania": 0.2124527,
    "Slovakia": 0.2124527, "Slovenia": 0.2124527, "Sweden": 0.2226321,
}

# --- GDP per capita PPP, VERIFIED: World Bank API, indicator ---------------
# NY.GDP.PCAP.PP.CD, mrv=1 -> all countries return 2025. Pulled 7 Sept 2026.
gdp_pc = {
    "Austria": 76777.54, "Belgium": 74675.61, "Bulgaria": 44451.10,
    "Cyprus": 64574.62, "Czechia": 60487.29, "Germany": 75406.69,
    "Denmark": 83218.07, "Spain": 59867.69, "Estonia": 52105.51,
    "Finland": 65884.49, "France": 63975.35, "Greece": 45263.65,
    "Croatia": 50946.17, "Hungary": 49837.60, "Ireland": 155089.41,
    "Italy": 62802.51, "Lithuania": 56837.81, "Luxembourg": 156542.08,
    "Latvia": 46136.69, "Malta": 72210.34, "Netherlands": 87320.15,
    "Poland": 54262.40, "Portugal": 53145.73, "Romania": 50895.08,
    "Slovakia": 49308.70, "Slovenia": 59244.71, "Sweden": 72528.89,
}

# --- Population, VERIFIED: Eurostat via Wikipedia's EU population table, --
# reference date 1 January 2025, released July 2025. Pulled 7 Sept 2026.
population = {
    "Germany": 83577100, "France": 68635900, "Italy": 58934200, "Spain": 49078000,
    "Poland": 36497500, "Romania": 19036400, "Netherlands": 18044000,
    "Belgium": 11900100, "Czechia": 10909500, "Portugal": 10749600,
    "Sweden": 10587700, "Greece": 10409500, "Hungary": 9539500, "Austria": 9197200,
    "Bulgaria": 6437400, "Denmark": 5992700, "Finland": 5636000, "Ireland": 5439900,
    "Slovakia": 5419500, "Croatia": 3874400, "Lithuania": 2890700, "Slovenia": 2130900,
    "Latvia": 1856900, "Estonia": 1370000, "Cyprus": 979900, "Luxembourg": 682000,
    "Malta": 574300,
}

# --- Cybersecurity strategy year (ENISA NCSS map, strategies list) ---------
strategy_year = {
    "Austria": 2021, "Belgium": 2021, "Bulgaria": 2021, "Croatia": 2015,
    "Cyprus": 2020, "Czechia": 2025, "Denmark": 2022, "Estonia": 2024,
    "Finland": 2024, "France": 2025, "Germany": 2021, "Greece": 2020,
    "Hungary": 2025, "Ireland": 2019, "Italy": 2022, "Latvia": 2023,
    "Lithuania": 2018, "Luxembourg": 2021, "Malta": 2023, "Netherlands": 2022,
    "Poland": 2019, "Portugal": 2019, "Romania": 2022, "Slovakia": 2021,
    "Slovenia": 2023, "Spain": 2019, "Sweden": 2025,
}

# --- single_dedicated_authority_PROVISIONAL: retained only as a record of ---
# what v0 got wrong (see codebook.md v1 changelog); no longer used anywhere.
single_authority_PROVISIONAL = {
    "Austria": 1, "Belgium": 1, "Bulgaria": 1, "Croatia": 1, "Cyprus": 1,
    "Czechia": 1, "Denmark": 1, "Estonia": 1, "Finland": 1, "France": 1,
    "Germany": 1, "Greece": 1, "Hungary": 1, "Ireland": 1, "Italy": 1,
    "Latvia": 0, "Lithuania": 1, "Luxembourg": 1, "Malta": 1,
    "Netherlands": 0, "Poland": 1, "Portugal": 1, "Romania": 1,
    "Slovakia": 1, "Slovenia": 1, "Spain": 0, "Sweden": 0,
}

# --- dedicated_cyber_agency: RECODED, v2, 27/27 checked against the -------
# Commission's official per-country NIS2 pages (digital-strategy.ec.europa.eu
# /en/policies/nis-directive-<country>), 7 Sept 2026. Coding rule: 1 if the
# SPOC (and/or lead CSIRT) is a specialized body whose sole or primary
# mandate is cybersecurity/information-systems security (an "agency",
# "centre" or "authority" with a cyber-specific name/mandate, whatever its
# formal legal status) -- 0 if the SPOC is a department/directorate inside
# a general-purpose ministry, or a broader security/emergency-management/
# regulatory body that has cyber as one mandate among several (national
# security councils, civil-contingencies agencies, telecom regulators,
# classified-information-protection authorities).
#
# THIS IS A JUDGMENT CALL, not a mechanical fact -- flagged explicitly for
# the following borderline cases, each decided by whether the identified
# body's own name/mandate reads as cyber-specific:
#   Estonia (RIA, "Information System Authority" -- broader IT-systems remit
#     but closely cyber-adjacent, commonly treated as a cyber agency) -> 1
#   Finland (NCSC-FI, housed inside Traficom, a transport/communications
#     regulator -- but NCSC itself is a named, cyber-specific unit) -> 1
#   Romania (CERT-RO -- a standalone incident-response body, not embedded
#     in a ministry, though not a broad "agency" in the ACN/BSI sense) -> 1
#   Croatia (Office of the National Security Council -- general security
#     body, not cyber-specific) -> 0
#   Slovakia (National Security Authority, NBU -- also handles classified-
#     information protection, broader than cyber alone) -> 0
#   Sweden (MSB, Swedish Civil Contingencies Agency -- broader civil-
#     protection/emergency-management mandate, cyber is one part) -> 0
# A second coder re-checking these six specifically, independent of this
# pass, would be a reasonable robustness step given N=27 and how much a
# handful of flips could move the variable's correlation with the DV.
dedicated_cyber_agency = {
    "Austria": 0,      # SPOC = Federal Ministry of the Interior
    "Belgium": 1,       # Centre for Cybersecurity Belgium (CCB)
    "Bulgaria": 0,      # State e-Government Agency
    "Croatia": 0,       # Office of the National Security Council -- borderline, see note
    "Cyprus": 1,        # Digital Security Authority (DSA)
    "Czechia": 1,       # NUKIB (National Cyber and Information Security Agency)
    "Denmark": 1,       # Danish Centre for Cybersecurity
    "Estonia": 1,       # RIA, Estonian Information System Authority -- borderline, see note
    "Finland": 1,       # NCSC-FI (within Traficom) -- borderline, see note
    "France": 1,        # ANSSI
    "Germany": 1,       # BSI
    "Greece": 0,        # National Cyber Security Authority, dept within Ministry of Digital Governance
    "Hungary": 1,       # National Cyber Security Centre
    "Ireland": 0,       # CSIRT-IE, housed within Dept of Communications
    "Italy": 1,         # ACN (Agenzia per la Cybersicurezza Nazionale)
    "Latvia": 0,        # SPOC = Ministry of Defence
    "Lithuania": 1,     # NCSC / CERT-LT
    "Luxembourg": 0,    # ILR, a general telecom/utilities regulator
    "Malta": 0,         # Critical Information Infrastructure Protection Unit, within Ministry for Home Affairs
    "Netherlands": 0,   # Fragmented across sectoral regulators, no single cyber agency as SPOC
    "Poland": 0,        # Ministry of Digital Affairs, Department of Cybersecurity
    "Portugal": 1,      # CNCS (Portuguese National Cybersecurity Centre)
    "Romania": 1,       # CERT-RO -- borderline, see note
    "Slovakia": 0,      # National Security Authority (NBU) -- borderline, see note
    "Slovenia": 0,      # Information Security Administration, dept within general ministry
    "Spain": 0,         # National Security Council / National Security Department
    "Sweden": 0,        # MSB, Swedish Civil Contingencies Agency -- borderline, see note
}

EU27 = sorted(population.keys())

def tier(country):
    if country in tier0: return 0
    if country in tier1: return 1
    if country in tier3: return 3
    return 2

def strategy_since_2022(country):
    y = strategy_year.get(country)
    return int(y is not None and y >= 2022)

rows = []
for c in EU27:
    rows.append({
        "country": c,
        "enforcement_tier": tier(c),
        "gov_effectiveness": gov_eff.get(c),
        "gov_effectiveness_se": gov_eff_se.get(c),
        "gdp_per_capita_ppp": gdp_pc.get(c),
        "population": population.get(c),
        "strategy_year": strategy_year.get(c),
        "strategy_since_2022": strategy_since_2022(c),
        "single_dedicated_authority_PROVISIONAL": single_authority_PROVISIONAL.get(c),
        "dedicated_cyber_agency": dedicated_cyber_agency.get(c),
        "cyber_gov_maturity": strategy_since_2022(c) + dedicated_cyber_agency.get(c, 0),
    })

out_path = "data/processed/eu27_nis2_dataset_v2.csv"
with open(out_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to {out_path}")
missing = [c for c in EU27 if gov_eff.get(c) is None or gdp_pc.get(c) is None or population.get(c) is None]
print("Rows with missing values:", missing)

def corr(a, b):
    n = len(a); ma = sum(a) / n; mb = sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((x - ma) ** 2 for x in a); vb = sum((x - mb) ** 2 for x in b)
    return cov / ((va * vb) ** 0.5)

ge = [gov_eff[c] for c in EU27]
tiers_l = [tier(c) for c in EU27]
cgm = [strategy_since_2022(c) + dedicated_cyber_agency.get(c, 0) for c in EU27]
dca = [dedicated_cyber_agency.get(c, 0) for c in EU27]
print("corr(gov_eff, cyber_gov_maturity) =", round(corr(ge, cgm), 3))
print("corr(cyber_gov_maturity, enforcement_tier) =", round(corr(cgm, tiers_l), 3))
print("corr(dedicated_cyber_agency, enforcement_tier) =", round(corr(dca, tiers_l), 3))
print("dedicated_cyber_agency count: 1s =", sum(dca), "0s =", len(dca) - sum(dca))
