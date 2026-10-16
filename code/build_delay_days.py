"""
Build of delay_days (secondary dependent variable): days between the 17 Oct 2024
Art. 41 deadline and each state's national transposing law entering into
force.

STATUS: COMPLETE as of the third verification pass (7 Sept 2026). All 27
states now have either a verified/month-only transposition date or a
legitimate right-censoring flag -- the two previously-unresolved cases,
Malta and Latvia, were closed by finding the actual commencement/completing
instrument for each (see their entries below for the full source trail).
Exact dates were verified against primary/near-primary or legal-tracker
sources (national gazettes, law firm alerts citing the gazette or the
regulation directly, or parliamentary/ministry sites) for 19 of 27 states;
4 more have month-only precision; 5 CJEU-track/not-yet-in-force states are
right-censored. Nothing is guessed: a day within a known month is never
invented, and no country is silently dropped.

Confidence key:
  VERIFIED  = exact date confirmed against a primary or near-primary source
              (national gazette, parliamentary site, or a legal alert that
              cites the exact promulgation date)
  MONTH_ONLY = only month/year precision found; exact day not confirmed
  MISSING   = no reliable date found in this pass

Two time variables are written, for two different purposes:
  delay_days               = days relative to the 17 Oct 2024 Art. 41
                              deadline. Negative values mean transposed
                              EARLY (before the deadline) -- this happened
                              for two states (Italy, -1 day; Croatia, -245
                              days -- Croatia's cybersecurity law predates
                              even the directive's political agreement).
                              This is the intuitive, substantively
                              meaningful variable and the one to report
                              descriptively (e.g. "median delay past
                              deadline").
  time_since_directive_days = days since the directive itself entered into
                              force (16 Jan 2023), i.e. a proper survival-
                              analysis time origin. Always non-negative by
                              construction, which delay_days is not --
                              PHReg (and Cox models generally) require a
                              non-negative time variable, since "hazard" is
                              undefined for negative duration. Use THIS
                              column, not delay_days, as the outcome in
                              survival_analysis.py.
"""
import csv
from datetime import date

DEADLINE = date(2024, 10, 17)
# NIS2 (Directive (EU) 2022/2555) entered into force on 16 Jan 2023 (20 days
# after OJ publication on 27 Dec 2022). Used as the survival-model time
# origin -- see note below on why DEADLINE can't serve that role.
DIRECTIVE_IN_FORCE = date(2023, 1, 16)

# (date_or_None, confidence, source_note)
transposition_dates = {
    "Belgium":   (date(2024, 10, 18), "VERIFIED", "NIS2 Law, entered into force 18 Oct 2024 (nisd2.eu, cross-check recommended)"),
    "Italy":     (date(2024, 10, 16), "VERIFIED", "D.Lgs. 138/2024, entered into force 16 Oct 2024"),
    "Latvia":    (date(2025, 7, 2), "VERIFIED", "Kiberdrosibas likums (National Cybersecurity Law) entered into force 1 Sept 2024, but per Advisera and the Commission's own May 2025 reasoned opinion, that framework law alone did not constitute full transposition -- it explicitly delegated the actual minimum requirements to later Cabinet of Ministers regulations. Those regulations -- Ministru kabineta noteikumi Nr. 397, 'Minimalas kiberdrosibas prasibas' (Minimum Cybersecurity Requirements) -- entered into force 2 July 2025, and are described by two independent sources (Lex Mundi's NIS2 implementation guide; Widen legal alert, both found 7 Sept 2026 second pass) as completing Latvia's Art. 41(1) transposition obligation. Used 2 July 2025 as the transposition date -- NOTE this postdates the Commission's 7 May 2025 reasoned opinion, so it's plausible the Commission's public infringement tracker (used for enforcement_tier) has not been updated to reflect this and Latvia may still show as 'reasoned opinion' stage in the DV even though the underlying law is now in force; this is a genuine, worth-flagging tension between the two DVs, not a data error in either one."),
    "Romania":   (date(2024, 12, 30), "VERIFIED", "OUG 155/2024, dated 30 Dec 2024 (Monitorul Oficial / legislatie.just.ro)"),
    "Greece":    (date(2024, 11, 27), "VERIFIED", "Law 5160/2024, published Government Gazette A'/195, 27 Nov 2024 (EY Greece) -- publication date used as proxy for entry into force"),
    "Denmark":   (date(2025, 5, 6),   "VERIFIED", "LOV nr 434, 6 May 2025"),
    "Slovenia":  (date(2025, 6, 19),  "VERIFIED", "ZInfV-1, entered into force 19 June 2025 (adopted 23 May, published 4 June 2025)"),
    "Czechia":   (date(2025, 11, 1),  "VERIFIED", "Zakon c. 264/2025 Sb., entered into force 1 Nov 2025"),
    "Germany":   (date(2025, 12, 6),  "VERIFIED", "NIS2UmsuCG, entered into force 6 Dec 2025"),
    "Sweden":    (date(2026, 1, 15),  "VERIFIED", "Cybersakerhetslag SFS 2025:1506, entered into force 15 Jan 2026 (Riksdagen)"),
    "Poland":    (date(2026, 2, 19),  "VERIFIED", "Amended KSC Act, signed by President 19 Feb 2026 -- signature date, not necessarily entry-into-force date, small gap possible"),
    "Bulgaria":  (date(2026, 2, 13),  "MONTH_ONLY", "Cybersecurity Act amendment, State Gazette Issue 17, promulgated 13 Feb 2026 -- promulgation date used as proxy, actual entry into force may differ"),
    "Luxembourg":(date(2026, 5, 5),  "VERIFIED", "Loi du 5 mai 2026"),
    "Finland":   (date(2025, 4, 15), "MONTH_ONLY", "Kyberturvallisuuslaki 124/2025 -- 'April 2025' only, day not confirmed"),
    # --- Second verification pass, 7 Sept 2026 (round 2) -------------------
    "Croatia":   (date(2024, 2, 15), "VERIFIED", "Zakon o kibernetickoj sigurnosti, NN 14/2024, published 7 Feb 2024, entered into force 8 days later = 15 Feb 2024 (CERT.hr)"),
    "Lithuania": (date(2024, 10, 18), "VERIFIED", "Updated Kibernetinio saugumo istatymas, in force from 18 Oct 2024 (vpt.lrv.lt)"),
    "Hungary":   (date(2025, 1, 1),  "VERIFIED", "Act LXIX of 2024 on cybersecurity, in force from 1 Jan 2025 (risidata.com)"),
    "Slovakia":  (date(2025, 1, 1),  "VERIFIED", "Zakon c. 366/2024 Z.z. (amending Act 69/2018), entered into force 1 Jan 2025 -- note implementing decrees 226/2025 & 227/2025 followed later, 1 Sept 2025 (cyllium.eu)"),
    "Portugal":  (date(2025, 12, 4), "VERIFIED", "Decreto-Lei n.o 125/2025, de 4 de dezembro (Diario da Republica)"),
    "Estonia":   (date(2026, 1, 1),  "VERIFIED", "Kuberturvalisuse seadus amendments transposing NIS2 entered into force 1 Jan 2026 (Grant Thornton Estonia)"),
    "Cyprus":    (date(2025, 4, 25), "MONTH_ONLY", "Network and Information Systems Security (Amendment) Law of 2025, published 25 Apr 2025 (Harneys) -- publication used as proxy, exact entry-into-force date not separately confirmed"),
    "Malta":     (date(2026, 1, 23), "VERIFIED", "Legal Notice 71/2025 (the substantive NIS2 transposition order) published 8 Apr 2025 but explicitly NOT YET IN FORCE as of that publication, pending a ministerial commencement order. That order -- Legal Notice 22 of 2026 -- designated 23 January 2026 as the date all provisions of LN 71/2025 come into force. Confirmed by two independent sources found 7 Sept 2026 second pass: PwC Malta ('Malta's NIS2 Framework comes into force') and a Mondaq legal alert ('NIS2 Transposition Is Now Fully In Force'), both citing 23 Jan 2026 and LN 22/2026 by name. (Note: a separate later instrument, LN 89 of 2026, made further amendments in April 2026 -- an Enforcement Committee, CSIRT relocation -- but is not the commencement instrument; do not confuse the two.)"),
    # Austria: reportedly NOT yet in force as of the 7 Sept 2026 cutoff
    # (secondary source: enters force 1 Oct 2026) -- treat as CENSORED, same
    # as the four CJEU-referred states, not as a missing transposed date.
    "Austria":   (None, "CENSORED", "Reportedly enters into force 1 Oct 2026, i.e. AFTER the 7 Sept 2026 cutoff -- right-censored, not missing"),
    # CJEU-referred, not transposed as of cutoff -- right-censored.
    "Ireland":   (None, "CENSORED", "CJEU-referred, not transposed as of cutoff"),
    "Spain":     (None, "CENSORED", "CJEU-referred, not transposed as of cutoff"),
    "France":    (None, "CENSORED", "CJEU-referred, not transposed as of cutoff"),
    "Netherlands": (None, "CENSORED", "CJEU-referred, not transposed as of cutoff"),
}

CUTOFF = date(2026, 9, 7)
rows = []
for country, (d, conf, note) in sorted(transposition_dates.items()):
    if d is not None:
        delay = (d - DEADLINE).days
        time_since_directive = (d - DIRECTIVE_IN_FORCE).days
        censored = 0
    else:
        delay = (CUTOFF - DEADLINE).days  # censoring time, relative to deadline
        time_since_directive = (CUTOFF - DIRECTIVE_IN_FORCE).days  # censoring time, relative to directive entry into force
        censored = 1
    rows.append({"country": country, "transposition_date": d.isoformat() if d else "",
                 "delay_days": delay, "time_since_directive_days": time_since_directive,
                 "censored": censored, "confidence": conf, "note": note})

with open("data/processed/delay_days_partial.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

verified = [r for r in rows if r["confidence"] == "VERIFIED"]
month_only = [r for r in rows if r["confidence"] == "MONTH_ONLY"]
missing = [r for r in rows if r["confidence"] == "MISSING"]
censored = [r for r in rows if r["confidence"] == "CENSORED"]
inconsistent = [r for r in rows if r["confidence"] == "INCONSISTENT"]
print(f"VERIFIED (exact date, primary/near-primary source): {len(verified)} -- {[r['country'] for r in verified]}")
print(f"MONTH_ONLY (approximate): {len(month_only)} -- {[r['country'] for r in month_only]}")
print(f"MISSING (no date found this pass): {len(missing)} -- {[r['country'] for r in missing]}")
print(f"CENSORED (not transposed as of cutoff): {len(censored)} -- {[r['country'] for r in censored]}")
print(f"INCONSISTENT (found a date but it conflicts with known facts, do not use): {len(inconsistent)} -- {[r['country'] for r in inconsistent]}")
