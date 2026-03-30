"""UGAF-ITS Output Generator — JSON reports, Markdown summaries, comparative table."""
import json, os
from statistics import mean


def save_json(report, outdir):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, f"{report['system_name'].replace(' ','_').lower()}_report.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    return p


def markdown_summary(r):
    lines = [f"# UGAF-ITS Compliance Report: {r['system_name']}", ""]
    if r.get("description"):
        lines += [f"*{r['description']}*", ""]
    a = r["architecture_summary"]
    lines += ["## Architecture", f"- Components: {a['total_components']}",
              f"- Active Tiers: {', '.join(a['active_tiers'])}",
              f"- Stakeholders: {', '.join(a['owners'])}", ""]
    ca = r["control_activation"]
    lines += [f"## Controls: {ca['total_activated']}/{ca['total_possible']} activated ({ca['activation_ratio']}%)", "",
              "| UC | Name | Tiers | Lifecycle |", "|---|------|-------|-----------|"]
    for uid, uc in sorted(ca["controls"].items()):
        lines.append(f"| {uid} | {uc['name']} | {', '.join(uc['enforced_at_tiers'])} | {', '.join(uc['lifecycle_phases'])} |")
    em = r["evidence_metrics"]
    lines += ["", f"## Evidence: {em['unified_artifacts']} artifacts (vs {em['siloed_baseline']} siloed, "
              f"-{em['reduction_percentage']}%)",
              f"- Reuse factor: {em['avg_reuse_factor']} fw/artifact",
              f"- 3-framework artifacts: {em['three_framework_artifacts']} ({em['three_framework_percentage']}%)", ""]
    tr = r["traceability"]
    lines += [f"## Traceability: {tr['traceability_score']}% - {tr['status']}", ""]
    cov = r["framework_coverage"]
    lines += ["## Coverage", "| Framework | Covered/Total | % |", "|-----------|---------------|---|"]
    for fid in ["ISO42001", "EU_AI_Act", "NIST_RMF"]:
        c = cov[fid]
        lines.append(f"| {c['label']} | {c['covered_obligations']}/{c['total_obligations']} | {c['coverage_percentage']}% |")
    lines.append(f"| **Average** | | **{cov['average']['coverage_percentage']}%** |")
    ga = r["gap_analysis"]
    lines += ["", f"## Gaps: {ga['total_gaps']}"]
    for cat, d in ga["categories"].items():
        if d["count"]:
            lines.append(f"- {cat.replace('_',' ').title()}: {d['count']}")
    lines += ["", f"---", f"*Engine v1.1 - {r['execution_time_ms']}ms*"]
    return "\n".join(lines)


def comparative_table(reports):
    from ugaf.knowledge_base import SOURCE_OBLIGATIONS
    iso_n = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "ISO42001")
    eu_n = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "EU_AI_Act")
    nist_n = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "NIST_RMF")
    total_n = len(SOURCE_OBLIGATIONS)
    lines = ["# UGAF-ITS Multi-Scenario Comparative Validation", "",
             f"**{total_n} source obligations** ({iso_n} ISO/IEC 42001 + "
             f"{eu_n} EU AI Act + {nist_n} NIST AI RMF) --> "
             "**12 unified controls** across **8 governance domains**.", ""]
    names = [r["system_name"] for r in reports]
    lines.append("| Metric | " + " | ".join(names) + " |")
    lines.append("|--------|" + "|".join(["--------"] * len(reports)) + "|")

    def row(label, fn):
        return f"| {label} | " + " | ".join(str(fn(r)) for r in reports) + " |"

    lines.append(row("Active tiers", lambda r: ", ".join(r["architecture_summary"]["active_tiers"])))
    lines.append(row("Components", lambda r: r["architecture_summary"]["total_components"]))
    lines.append(row("Stakeholders", lambda r: len(r["architecture_summary"]["owners"])))
    lines.append(row("Activated UCs", lambda r: f"{r['control_activation']['total_activated']}/12"))
    lines.append(row("Unified artifacts", lambda r: r["evidence_metrics"]["unified_artifacts"]))
    lines.append(row("Siloed baseline", lambda r: r["evidence_metrics"]["siloed_baseline"]))
    lines.append(row("Reduction (%)", lambda r: f"{r['evidence_metrics']['reduction_percentage']}%"))
    lines.append(row("Reuse factor", lambda r: r["evidence_metrics"]["avg_reuse_factor"]))
    lines.append(row("3-fw artifacts", lambda r:
        f"{r['evidence_metrics']['three_framework_artifacts']} ({r['evidence_metrics']['three_framework_percentage']}%)"))
    lines.append(row("ISO 42001", lambda r: f"{r['framework_coverage']['ISO42001']['coverage_percentage']}%"))
    lines.append(row("EU AI Act", lambda r: f"{r['framework_coverage']['EU_AI_Act']['coverage_percentage']}%"))
    lines.append(row("NIST RMF", lambda r: f"{r['framework_coverage']['NIST_RMF']['coverage_percentage']}%"))
    lines.append(row("Avg coverage", lambda r: f"{r['framework_coverage']['average']['coverage_percentage']}%"))
    lines.append(row("Traceability", lambda r: f"{r['traceability']['traceability_score']}%"))
    lines.append(row("Total gaps", lambda r: r["gap_analysis"]["total_gaps"]))
    lines.append(row("Exec (ms)", lambda r: r["execution_time_ms"]))
    lines += ["", "---", "*Generated by UGAF-ITS Governance Engine v1.1.0*"]
    return "\n".join(lines)


def save_md(content, outdir, fname):
    os.makedirs(outdir, exist_ok=True)
    p = os.path.join(outdir, fname)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p
