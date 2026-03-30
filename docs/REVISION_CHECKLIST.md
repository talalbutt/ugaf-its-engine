# UGAF-ITS Revision Checklist

## Pre-Flight (30 min)
- [ ] Tool runs cleanly: `python run_validation.py` completes without error
- [ ] Output shows **154** source obligations (not 155)
- [ ] Average coverage shows **91.7%** for three-tier deployments
- [ ] All 4 scenario reports generated in `results/`

## Day 1: GitHub Setup
- [ ] Create public repo: `ugaf-its-engine`
- [ ] Push all code, scenarios, results, README, LICENSE
- [ ] Tag release v1.1.0
- [ ] Verify README renders correctly on GitHub
- [ ] Copy the repo URL for the paper footnote

## Day 2-3: Paper Surgery (use `docs/paper_latex_insertions.tex`)

### CUT (~3 pages)
- [ ] Section II Background: cut ~30% — remove general framework descriptions,
      keep only clauses/articles that justify crosswalk design decisions
- [ ] Section IV-D Three-Tier Model: cut ~40% — let Figure 3 do the work
- [ ] Section VI ITS Component Mapping: cut ~40% — tool demonstrates this now
- [ ] Section VIII-F Societal Implications: remove entirely (if targeting CSI)

### ADD (~2 pages)
- [ ] Insert new Section VII-B "Computational Validation via Prototype Tool"
      (copy from `paper_latex_insertions.tex`, Section 1)
- [ ] Insert Listing 1: YAML snippet (transit priority scenario)
- [ ] Insert Listing 2: JSON output fragment
- [ ] Add GitHub footnote URL

### REPLACE
- [ ] Replace Table 9 with multi-scenario comparative table
      (copy from `paper_latex_insertions.tex`, Section 2)
- [ ] Update abstract validation sentence
      (copy from `paper_latex_insertions.tex`, Section 3)
- [ ] Update VII-D External Validity paragraph
      (copy from `paper_latex_insertions.tex`, Section 4)
- [ ] Add multi-scenario findings paragraph to VII-C
      (copy from `paper_latex_insertions.tex`, Section 5)
- [ ] Add sentence to Conclusion
      (copy from `paper_latex_insertions.tex`, Section 6)

### RENUMBER
- [ ] Current VII-B (UGAF-ITS Application) becomes VII-C
- [ ] Current VII-C (Validation Results) becomes VII-D
- [ ] Current VII-D (Threats to Validity) becomes VII-E
- [ ] Fix all internal \ref{} cross-references

## Day 4: Format & Polish
- [ ] Download target journal LaTeX template (elsarticle for CSI or Array)
- [ ] Reformat paper into new template
- [ ] Add 5 venue-specific citations (recent papers from the target journal)
- [ ] Verify page count within limits
- [ ] Run one final check: do paper numbers match tool output?
      - 154 obligations (not 155)
      - 91.7% average coverage
      - 45.9% evidence reduction (three-tier)
      - 100% traceability
- [ ] Proofread for AI-drafting patterns: vary sentence openers,
      break parallel structures, add domain jargon

## Day 5: Submit
- [ ] Write cover letter emphasizing:
      - EU AI Act August 2026 deadline urgency
      - Open-source tool for reproducibility
      - Multi-scenario computational validation
      - Paper fills gap between enterprise governance and ITS practice
- [ ] Submit via Elsevier Editorial Manager
- [ ] Suggest 3-5 reviewers from AI governance / standards compliance
- [ ] Notify co-authors with submission confirmation

## Venue Priority
1. **Computer Standards & Interfaces** (Q1, Elsevier, free) — primary target
2. **Array** (Q1, Elsevier, $2,250 APC) — backup if CSI desk-rejects
3. **CLSR** (Q1, Elsevier, free) — fallback with legal reframing
