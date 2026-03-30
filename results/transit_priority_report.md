# UGAF-ITS Compliance Report: Transit Priority Corridor

*Edge-heavy transit signal priority â€” no vehicle AI (T2+T3 only)*

## Architecture
- Components: 5
- Active Tiers: T2, T3
- Stakeholders: integrator, transit_authority

## Controls: 12/12 activated (100.0%)

| UC | Name | Tiers | Lifecycle |
|---|------|-------|-----------|
| UC-01 | AI Risk Assessment | T2, T3 | design, monitor, change |
| UC-02 | Risk Treatment Planning | T2, T3 | design, deploy, change |
| UC-03 | Data Quality Assurance | T2, T3 | design, build, monitor |
| UC-04 | Bias Detection & Mitigation | T2, T3 | build, monitor |
| UC-05 | Human Oversight Design | T2 | design, build |
| UC-06 | Override & Intervention | T2 | design, deploy, monitor |
| UC-07 | System Documentation | T2, T3 | design, build, deploy, change |
| UC-08 | Transparency Communication | T2, T3 | deploy |
| UC-09 | Accuracy Validation | T2, T3 | build, deploy |
| UC-10 | Robustness & Security | T2, T3 | build, deploy, monitor |
| UC-11 | Supplier AI Assessment | T3 | build, change |
| UC-12 | Incident Response | T2, T3 | monitor, change |

## Evidence: 18 artifacts (vs 25 siloed, -28.0%)
- Reuse factor: 2.89 fw/artifact
- 3-framework artifacts: 16 (88.9%)

## Traceability: 100.0% - COMPLETE

## Coverage
| Framework | Covered/Total | % |
|-----------|---------------|---|
| ISO/IEC 42001 | 52/55 | 94.5% |
| EU AI Act | 34/37 | 91.9% |
| NIST AI RMF | 55/62 | 88.7% |
| **Average** | | **91.7%** |

## Gaps: 13
- Organizational Procedure: 3
- Regulatory Workflow: 3
- Context Setting: 7

---
*Engine v1.1 - 0.63ms*