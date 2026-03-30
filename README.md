# UGAF-ITS Governance Engine

[![DOI](https://zenodo.org/badge/DOI/PLACEHOLDER.svg)](https://doi.org/PLACEHOLDER)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> Computational validation tool for the Unified Governance and Assurance Framework for Distributed Intelligent Transportation Systems (UGAF-ITS).

## Overview

UGAF-ITS harmonizes **154 governance obligations** from three regulatory instruments into **12 unified controls** across **8 governance domains**, with tier-aware allocation across vehicle, edge/RSU, and cloud boundaries.

| Framework             | Obligations | Type                      | Applicability     |
| --------------------- | ----------- | ------------------------- | ----------------- |
| ISO/IEC 42001:2023    | 55          | Voluntary / Certifiable   | Management system |
| EU AI Act (2024/1689) | 37          | Mandatory                 | August 2026       |
| NIST AI RMF 1.0       | 62          | Voluntary / Best Practice | Risk management   |

This tool validates the framework by evaluating ITS deployment architectures against the unified control catalog through eight computations:

1. **Tier-Aware Control Activation** &mdash; which controls apply based on active tiers
2. **Evidence Backbone with Reuse Analysis** &mdash; minimal artifact set with cross-framework deduplication
3. **Bidirectional Traceability Verification** &mdash; forward and reverse trace-link completeness
4. **Per-Framework Coverage Analysis** &mdash; ISO, EU AI Act, and NIST coverage percentages
5. **Gap Detection and Classification** &mdash; categorized gaps with architectural rationale
6. **Coverage Depth Analysis** &mdash; component density, risk profile, and stakeholder breadth
7. **Consolidation Analysis** &mdash; per-domain obligation-to-control consolidation ratios
8. **Cross-Tier Dependency Chains** &mdash; evidence flow across architectural boundaries

## Quick Start

```bash
git clone https://github.com/talalbutt/ugaf-its-engine.git
cd ugaf-its-engine
pip install -r requirements.txt
python run_validation.py
```

## Deployment Scenarios

Four architecturally distinct ITS deployments validate that governance requirements are architecturally contingent:

| Scenario                  | Tiers      | Components | Archetype                                           |
| ------------------------- | ---------- | ---------- | --------------------------------------------------- |
| Urban Smart Intersection  | T1, T2, T3 | 12         | Full three-tier, multi-stakeholder (Dubai-inspired) |
| Highway Corridor ADS      | T1, T2, T3 | 7          | Vehicle-heavy, minimal edge                         |
| Transit Priority Corridor | T2, T3     | 5          | Edge-heavy, no vehicle AI                           |
| Rural Intersection        | T2         | 2          | Single-tier, single-owner minimum                   |

### Key Validation Results

| Metric             | Urban | Highway | Transit | Rural |
| ------------------ | ----- | ------- | ------- | ----- |
| Activated UCs      | 12/12 | 12/12   | 12/12   | 11/12 |
| Evidence reduction | 45.9% | 45.9%   | 28.0%   | 7.7%  |
| Avg. coverage      | 91.7% | 91.7%   | 91.7%   | 88.1% |
| Traceability       | 100%  | 100%    | 100%    | 100%  |

Evidence reduction uses a scope-aware siloed baseline scaled to the tiers present in each deployment (37 documents for three-tier, 25 for edge+cloud, 13 for edge-only).

## Project Structure

```
ugaf-its-engine/
├── ugaf/
│   ├── knowledge_base.py    # 154 obligations, 12 UCs, 20 artifacts
│   ├── engine.py            # Eight governance computations
│   ├── output.py            # JSON + Markdown report generators
│   └── html_report.py       # Interactive HTML dashboard with Chart.js
├── data/
│   ├── iso42001_obligations.csv
│   ├── eu_ai_act_obligations.csv
│   └── nist_rmf_obligations.csv
├── scenarios/               # YAML deployment descriptors
├── results/                 # Generated reports and dashboard
├── run_validation.py        # Multi-scenario validation runner
├── rebuild_kb.py            # Regenerate knowledge base from CSVs
└── export_panels.py         # High-quality figure export (Playwright)
```

## Custom Scenarios

Create a YAML file in `scenarios/`:

```yaml
name: "My ITS Deployment"
description: "Description of the deployment"
components:
  - name: "Component Name"
    tier: "T1"           # T1=Vehicle, T2=Edge/RSU, T3=Cloud
    risk_level: "high"   # high, medium, low
    owner: "oem"         # oem, integrator, authority, etc.
```

Run: `python run_validation.py`

## Exporting Paper Figures

Generate publication-quality figures at 288 effective DPI:

```bash
pip install playwright && playwright install chromium
python run_validation.py
python export_panels.py --html results/dashboard.html --output figures/
```

Produces three composite PDF/PNG figures:

- `fig_tool_dashboard` &mdash; Executive Summary + Three-Tier Architecture
- `fig_coverage_reduction` &mdash; Framework Coverage + Evidence Backbone
- `fig_consolidation_domain` &mdash; Crosswalk Consolidation by Domain

## Updating the Knowledge Base

Edit the CSV files in `data/`, then rebuild:

```bash
python rebuild_kb.py
python run_validation.py
```

## Associated Publication

> Butt, T.A., Iqbal, M., & Iqbal, R. (2026). *UGAF-ITS: A Unified Governance and Assurance Framework for Intelligent Transport Systems.* Computer Standards & Interfaces. [Submitted]

## License

MIT &mdash; see [LICENSE](LICENSE).
