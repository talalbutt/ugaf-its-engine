# UGAF-ITS Knowledge Base Schema — Fill This Accurately

## Instructions for the Strategist

This document defines the EXACT data schema the UGAF-ITS Governance Engine
consumes. The engine code (engine.py, html_report.py, output.py) is correct
and does NOT need changes. Only the data in `knowledge_base.py` needs to be
accurate.

The engine computes ALL metrics from this data:
- Framework coverage percentages
- Evidence reduction
- Traceability score
- Gap counts and categories
- Consolidation ratios
- Per-domain breakdowns

**If the data is wrong, every metric is wrong.**

---

## What the Paper Claims (Target Numbers)

| Metric | Paper Value | Current Engine Value | Match? |
|--------|------------|---------------------|--------|
| Total source obligations | 155 | 154 | NO |
| ISO/IEC 42001 Annex A controls | 38 | 55 (incl. clauses) | DIFFERENT SCOPE |
| EU AI Act high-risk requirements | ~45 | 37 | DIFFERENT SCOPE |
| NIST AI RMF subcategories | 72 | 62 | DIFFERENT SCOPE |
| Unified controls | 12 | 12 | YES |
| Evidence artifacts | 20 | 20 | YES |
| ISO coverage | 95% (36/38) | 94.5% (52/55) | CLOSE BUT DIFFERENT |
| EU AI Act coverage | 92% (41/45) | 91.9% (34/37) | CLOSE BUT DIFFERENT |
| NIST coverage | 88% (63/72) | 88.7% (55/62) | CLOSE BUT DIFFERENT |
| Avg coverage | 91.7% | 91.7% | YES (by luck) |
| Evidence reduction | 46% | 45.9% | CLOSE |

### THE CORE QUESTION:
The paper says "155 source obligations: 38 ISO + 45 EU + 72 NIST"
but also reports coverage as "36/38, 41/45, 63/72".

Decide: Are the TOTALS 38+45+72=155 or something else?
The engine needs the EXACT list of obligations that make up each total.

---

## SCHEMA 1: Source Obligations

Each obligation is one atomic requirement extracted from a framework.
The engine stores them as a Python dict with this structure:

```
{
    "id": "Art.9(2a)",           # Unique identifier within the framework
    "desc": "Short description", # One-line description of the obligation
    "domain": "D1",              # Which governance domain (D1-D8)
    "uc": "UC-01",               # Which unified control it maps to (or None for gaps)
    "tiers": ["T1", "T2", "T3"],  # OPTIONAL: Which tiers this applies to
                                   # Default: ["T1", "T2", "T3"] if omitted
    "gap": null                  # OPTIONAL: Gap category if unmapped. One of:
                                   #   "organizational_procedure"
                                   #   "regulatory_workflow"
                                   #   "context_setting"
                                   #   null (if mapped to a UC)
}
```

### Valid Values

**domain**: D1, D2, D3, D4, D5, D6, D7, D8
**uc**: UC-01 through UC-12, or null/None for gaps
**tiers**: Any combination of "T1", "T2", "T3"
**gap categories**:
- `organizational_procedure` = Internal audit, management review (ISO gaps)
- `regulatory_workflow` = Conformity assessment, registration, CE marking (EU gaps)
- `context_setting` = Organizational profiling, stakeholder engagement (NIST gaps)

### Tier rules from Table 6:
- UC-03, UC-04: T2 and T3 only (not T1)
- UC-05, UC-06: T1 and T2 only (not T3)
- UC-11: T3 only
- All others: T1, T2, T3

---

## SCHEMA 2: Governance Domains (Table 5)

These are FIXED and correct. Do not change.

```
D1: Risk Management        -> UC-01, UC-02
D2: Data Governance         -> UC-03, UC-04
D3: Human Oversight         -> UC-05, UC-06
D4: Transparency            -> UC-08
D5: Accuracy & Robustness   -> UC-09, UC-10
D6: Documentation           -> UC-07
D7: Supply Chain            -> UC-11
D8: Incident Management     -> UC-12
```

---

## SCHEMA 3: Unified Controls (Table 6)

These are FIXED and correct. Do not change.

| UC | Name | Domain | Tiers (Active) |
|----|------|--------|----------------|
| UC-01 | AI Risk Assessment | D1 | T1, T2, T3 |
| UC-02 | Risk Treatment Planning | D1 | T1, T2, T3 |
| UC-03 | Data Quality Assurance | D2 | T2, T3 |
| UC-04 | Bias Detection & Mitigation | D2 | T2, T3 |
| UC-05 | Human Oversight Design | D3 | T1, T2 |
| UC-06 | Override & Intervention | D3 | T1, T2 |
| UC-07 | System Documentation | D6 | T1, T2, T3 |
| UC-08 | Transparency Communication | D4 | T1, T2, T3 |
| UC-09 | Accuracy Validation | D5 | T1, T2, T3 |
| UC-10 | Robustness & Security | D5 | T1, T2, T3 |
| UC-11 | Supplier AI Assessment | D7 | T3 |
| UC-12 | Incident Response | D8 | T1, T2, T3 |

---

## SCHEMA 4: Evidence Artifacts

These are FIXED and correct (20 artifacts). Do not change.

---

## WHAT YOU NEED TO FILL

Fill the three CSV files below. Each row = one obligation.
The engine will compute everything else.

### File: `iso42001_obligations.csv`

Paper says 38 Annex A controls. Coverage = 36/38 (95%).
So: 36 mapped + 2 gaps = 38 total.

```csv
id,desc,domain,uc,tiers,gap
A.4.1,"AI risk identification",D1,UC-01,"T1;T2;T3",
A.4.2,"AI risk analysis",D1,UC-01,"T1;T2;T3",
...fill all 38...
A.GAP.1,"Internal audit workflow",D8,,"T1;T2;T3",organizational_procedure
A.GAP.2,"Management review",D8,,"T1;T2;T3",organizational_procedure
```

Questions to answer:
- Are there exactly 38 items or more (clause-level items too)?
- Which 2 are gaps? (paper says ISO gaps = "internal audit and management review")
- Do all 36 mapped items map cleanly to one of UC-01 through UC-12?

### File: `eu_ai_act_obligations.csv`

Paper says ~45 requirements. Coverage = 41/45 (92%).
So: 41 mapped + 4 gaps = 45 total.

```csv
id,desc,domain,uc,tiers,gap
Art.9(1),"Establish risk management system",D1,UC-01,"T1;T2;T3",
Art.9(2a),"Identify foreseeable risks",D1,UC-01,"T1;T2;T3",
...fill all 45...
Art.GAP.CA,"Conformity assessment procedure",D6,,"T1;T2;T3",regulatory_workflow
Art.GAP.REG,"EU database registration",D6,,"T1;T2;T3",regulatory_workflow
Art.GAP.CE,"CE marking",D6,,"T1;T2;T3",regulatory_workflow
Art.GAP.DOC,"Declaration of conformity",D6,,"T1;T2;T3",regulatory_workflow
```

Questions to answer:
- Are there exactly 45 items? The paper says "~45" — what's the exact number?
- Which 4 are gaps? (paper says EU gaps = "conformity assessment, registration, marking")
- How are Articles 8-15 decomposed into 45 sub-obligations?

### File: `nist_rmf_obligations.csv`

Paper says 72 subcategories. Coverage = 63/72 (88%).
So: 63 mapped + 9 gaps = 72 total.

```csv
id,desc,domain,uc,tiers,gap
GV.1.1,"Legal requirements identified",D1,UC-01,"T1;T2;T3",
GV.1.2,"Trustworthy AI prioritised",D1,UC-01,"T1;T2;T3",
...fill all 72...
NIST.GAP.1,"Organizational profiling",D1,,"T1;T2;T3",context_setting
...fill all 9 gaps...
```

Questions to answer:
- Are there exactly 72 subcategories or a subset?
- Which 9 are gaps? (paper says NIST gaps = "context-setting governance practices")
- The NIST RMF has exactly 72 subcategories in 19 categories across 4 functions.
  Are ALL 72 included, or only those scoped to high-risk ITS?

---

## HOW TO CONVERT BACK TO PYTHON

Once the CSVs are filled, the conversion to knowledge_base.py is mechanical:

```python
# Each CSV row becomes:
{"id": row["id"], "desc": row["desc"], "domain": row["domain"],
 "uc": row["uc"] or None,
 "tiers": row["tiers"].split(";") if row["tiers"] else ["T1","T2","T3"],
 "gap": row["gap"] or None}
```

The engine code does NOT need any changes. Only the obligation lists
in `knowledge_base.py` need to be replaced.

---

## VERIFICATION AFTER FILLING

After updating knowledge_base.py, run:
```
python run_validation.py
```

Check that the output matches these paper targets:
- ISO coverage: 95% (36/38)  — or whatever the corrected numbers are
- EU coverage: 92% (41/45)
- NIST coverage: 88% (63/72)
- Avg coverage: 91.7%
- Evidence reduction: ~46%
- Traceability: 100%
- Total gaps: count should match paper

If numbers don't match, the obligation list has errors.
The engine math is correct — only the input data can be wrong.
