"""
UGAF-ITS HTML Dashboard Report Generator v1.1
===============================================
Self-contained HTML dashboard with Chart.js visualizations.
Fixed: 154 source obligations (was 155 in v1.0).
"""

import json
from datetime import datetime, timezone


def generate_html_dashboard(reports, output_path="results/dashboard.html"):
    """Generate complete HTML dashboard from a list of scenario reports."""
    from ugaf.knowledge_base import SOURCE_OBLIGATIONS
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    n_scenarios = len(reports)
    total_ms = round(sum(r["execution_time_ms"] for r in reports), 2)
    short_names = [_short_name(r["system_name"]) for r in reports]
    primary = reports[0] if reports else {}

    # Dynamic obligation counts
    ob_total = len(SOURCE_OBLIGATIONS)
    ob_iso = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "ISO42001")
    ob_eu = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "EU_AI_Act")
    ob_nist = sum(1 for o in SOURCE_OBLIGATIONS.values() if o["framework"] == "NIST_RMF")

    html = _render_full_html(reports, short_names, primary, ts, n_scenarios,
                             total_ms, ob_total, ob_iso, ob_eu, ob_nist)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def _render_full_html(reports, short_names, primary, ts, n_scenarios,
                      total_ms, ob_total, ob_iso, ob_eu, ob_nist):
    em = primary.get("evidence_metrics", {})
    ca = primary.get("control_activation", {})
    cov = primary.get("framework_coverage", {})
    tr = primary.get("traceability", {})

    avg_cov = cov.get("average", {}).get("coverage_percentage", 0)
    kpi_ucs = ca.get("total_activated", 12)
    kpi_reduction = em.get("reduction_percentage", 0)
    kpi_trace = tr.get("traceability_score", 0)
    kpi_reuse = em.get("avg_reuse_factor", 0)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>UGAF-ITS Governance Engine - Validation Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
{_get_css()}
</style>
</head>
<body>

<!-- PANEL 0: Header -->
<header class="header">
  <div class="header-brand">
    <div class="logo">&#x2B21;</div>
    <div>
      <h1>UGAF-ITS Governance Engine <span class="version">v1.1</span></h1>
      <p class="subtitle">Multi-Scenario Validation Dashboard</p>
    </div>
  </div>
  <div class="header-meta">
    <span class="meta-pill">{n_scenarios} scenarios</span>
    <span class="meta-pill">{total_ms}ms total</span>
    <span class="meta-pill">{ts}</span>
  </div>
</header>

<!-- PANEL 1: Executive Summary -->
<section class="panel" id="panel-executive">
  <h2 class="panel-title">Executive Summary</h2>
  <p class="panel-desc">Harmonizing ISO/IEC 42001, EU AI Act, and NIST AI RMF across {n_scenarios} ITS deployment archetypes</p>
  <div class="kpi-grid">
    {_kpi(str(ob_total), "Source Obligations", "From 3 frameworks", "neutral")}
    {_kpi(str(kpi_ucs), "Unified Controls", "Consolidated catalog", "brand")}
    {_kpi(str(avg_cov) + "%", "Avg Coverage", "Across all frameworks", "good")}
    {_kpi(str(kpi_reduction) + "%", "Evidence Reduction", "vs siloed approach", "good")}
    {_kpi(str(kpi_trace) + "%", "Traceability", "Bidirectional links", "good")}
  </div>
</section>

<!-- PANEL 2: Framework Coverage -->
<section class="panel" id="panel-coverage">
  <h2 class="panel-title">Framework Coverage Across Deployment Archetypes</h2>
  <p class="panel-desc">Structural coverage of scoped obligations per framework and scenario</p>
  <div class="chart-wrap"><canvas id="chartCoverage"></canvas></div>
  <p class="chart-note">Coverage varies by architecture. Full three-tier deployments achieve &#8805;91% average; partial deployments show proportionally lower coverage due to tier-dependent obligations.</p>
</section>

<!-- PANEL 3: Evidence Backbone -->
<section class="panel" id="panel-evidence">
  <h2 class="panel-title">Evidence Backbone Analysis</h2>
  <div class="split-grid">
    <div class="chart-card">
      <h3>Document Reduction</h3>
      <div class="chart-wrap-sm"><canvas id="chartReduction"></canvas></div>
    </div>
    <div class="chart-card">
      <h3>Artifact Reuse Distribution</h3>
      <div class="chart-wrap-sm"><canvas id="chartReuse"></canvas></div>
    </div>
  </div>
  <p class="chart-note">Each artifact serves {kpi_reuse} frameworks on average, eliminating parallel documentation packages.</p>
</section>

<!-- PANEL 4: Consolidation -->
<section class="panel" id="panel-consolidation">
  <h2 class="panel-title">Crosswalk Consolidation by Governance Domain</h2>
  <p class="panel-desc">How source obligations consolidate into unified controls across 8 governance domains</p>
  <div class="chart-wrap"><canvas id="chartConsolidation"></canvas></div>
</section>

<!-- PANEL 5: Tier Architecture -->
<section class="panel" id="panel-tiers">
  <h2 class="panel-title">Three-Tier Governance Architecture</h2>
  <p class="panel-desc">Control allocation follows deployment topology &mdash; governance attaches where behavior executes</p>
  {_render_tier_diagram(primary)}
</section>

<!-- PANEL 6: Comparative Table -->
<section class="panel" id="panel-table">
  <h2 class="panel-title">Multi-Scenario Comparative Validation</h2>
  {_render_table(reports)}
</section>

<!-- PANEL 7: Gap Classification -->
<section class="panel" id="panel-gaps">
  <h2 class="panel-title">Gap Analysis: What UGAF-ITS Does Not Cover</h2>
  <p class="panel-desc">Obligations outside the framework's technical scope, classified by category</p>
  <div class="chart-wrap-sm"><canvas id="chartGaps"></canvas></div>
</section>

<!-- PANEL 8: Instantiation Depth -->
<section class="panel" id="panel-depth">
  <h2 class="panel-title">Instantiation Depth by Scenario</h2>
  <p class="panel-desc">Beyond structural coverage: how deeply each deployment populates the governance architecture</p>
  <div class="chart-wrap"><canvas id="chartDepth"></canvas></div>
</section>

<!-- PANEL 9: Scenario Builder -->
<section class="panel" id="panel-builder">
  <h2 class="panel-title">Scenario Builder</h2>
  <p class="panel-desc">Configure a custom ITS deployment to generate a YAML scenario file</p>
  {_render_builder()}
</section>

<footer class="footer">
  <p>UGAF-ITS Governance Engine v1.1 &middot; {ob_total} source obligations ({ob_iso} ISO + {ob_eu} EU + {ob_nist} NIST) &middot; Generated {ts}</p>
</footer>

<script>
// ===== DATA =====
{_build_data_block(reports, short_names, primary)}

// ===== CHARTS =====
{_build_chart_block()}

// ===== SCENARIO BUILDER =====
{_build_builder_script()}
</script>
</body>
</html>"""


# =====================================================================
# DATA BLOCK
# =====================================================================

def _build_data_block(reports, short_names, primary):
    em = primary.get("evidence_metrics", {})
    con = primary.get("consolidation", {}).get("per_domain", {})

    cov_data = {
        "labels": short_names,
        "iso": [r["framework_coverage"]["ISO42001"]["coverage_percentage"] for r in reports],
        "eu": [r["framework_coverage"]["EU_AI_Act"]["coverage_percentage"] for r in reports],
        "nist": [r["framework_coverage"]["NIST_RMF"]["coverage_percentage"] for r in reports],
    }

    evidence_data = {
        "labels": short_names,
        "siloed": [r["evidence_metrics"]["siloed_baseline"] for r in reports],
        "unified": [r["evidence_metrics"]["unified_artifacts"] for r in reports],
    }

    three_fw = em.get("three_framework_artifacts", 0)
    two_fw = 0
    one_fw = 0
    if reports:
        eb = reports[0].get("evidence_backbone", {})
        for aid, art in eb.items():
            fc = art.get("framework_count", 0)
            if fc == 2:
                two_fw += 1
            elif fc == 1:
                one_fw += 1
    reuse_data = {"three": three_fw, "two": two_fw, "one": one_fw}

    dom_data = {"labels": [], "iso": [], "eu": [], "nist": [], "ucs": []}
    for did in sorted(con.keys()):
        d = con[did]
        dom_data["labels"].append(d["name"])
        dom_data["iso"].append(d["iso_count"])
        dom_data["eu"].append(d["eu_count"])
        dom_data["nist"].append(d["nist_count"])
        dom_data["ucs"].append(d["unified_controls"])

    gap_data = {"labels": [], "values": []}
    gap_map = {
        "organizational_procedure": "Organizational Procedure",
        "regulatory_workflow": "Regulatory Workflow",
        "context_setting": "Context Setting",
        "tier_not_present": "Tier Not Present",
    }
    gap_totals = {k: 0 for k in gap_map}
    for r in reports:
        cats = r.get("gap_analysis", {}).get("categories", {})
        for key in gap_map:
            gap_totals[key] += cats.get(key, {}).get("count", 0)
    n = len(reports) or 1
    for key, label in gap_map.items():
        avg = round(gap_totals[key] / n, 1)
        if avg > 0:
            gap_data["labels"].append(label)
            gap_data["values"].append(avg)

    depth_data = {"labels": short_names, "datasets": []}
    palette = [
        {"border": "rgb(8,145,178)", "bg": "rgba(8,145,178,0.1)"},
        {"border": "rgb(30,58,110)", "bg": "rgba(30,58,110,0.1)"},
        {"border": "rgb(127,29,29)", "bg": "rgba(127,29,29,0.1)"},
        {"border": "rgb(20,83,45)", "bg": "rgba(20,83,45,0.1)"},
    ]
    for i, r in enumerate(reports):
        cd = r.get("coverage_depth", {})
        c = palette[i % len(palette)]
        depth_data["datasets"].append({
            "label": short_names[i],
            "data": [cd.get("overall_depth", 0),
                     cd.get("component_density", 0),
                     cd.get("risk_factor", 0)],
            "borderColor": c["border"],
            "backgroundColor": c["bg"],
            "pointRadius": 4,
            "borderWidth": 2,
        })

    return f"""
const DATA = {{
  coverage: {json.dumps(cov_data)},
  evidence: {json.dumps(evidence_data)},
  reuse: {json.dumps(reuse_data)},
  consolidation: {json.dumps(dom_data)},
  gaps: {json.dumps(gap_data)},
  depth: {json.dumps(depth_data)},
}};

const C = {{
  iso: '#1E3A6E', eu: '#7F1D1D', nist: '#14532D',
  brand: '#0891B2', good: '#059669', warn: '#D97706',
  bad: '#DC2626', muted: '#94A3B8', light: '#CBD5E1'
}};
"""


# =====================================================================
# CHART BLOCK
# =====================================================================

def _build_chart_block():
    return """
new Chart(document.getElementById('chartCoverage'), {
  type: 'bar',
  data: {
    labels: DATA.coverage.labels,
    datasets: [
      {label:'ISO/IEC 42001', data:DATA.coverage.iso, backgroundColor:C.iso, borderRadius:4},
      {label:'EU AI Act', data:DATA.coverage.eu, backgroundColor:C.eu, borderRadius:4},
      {label:'NIST AI RMF', data:DATA.coverage.nist, backgroundColor:C.nist, borderRadius:4},
    ]
  },
  options: {
    responsive:true,
    scales: {
      y: {min:0, max:100, ticks:{callback:function(v){return v+'%'}},
        title:{display:true, text:'Coverage (%)', font:{weight:'bold'}}},
      x: {title:{display:true, text:'Deployment Scenario', font:{weight:'bold'}}}
    },
    plugins: {legend:{position:'bottom'}}
  }
});

new Chart(document.getElementById('chartReduction'), {
  type: 'bar',
  data: {
    labels: DATA.evidence.labels,
    datasets: [
      {label:'Siloed baseline', data:DATA.evidence.siloed, backgroundColor:C.muted, borderRadius:4},
      {label:'UGAF-ITS unified', data:DATA.evidence.unified, backgroundColor:C.brand, borderRadius:4},
    ]
  },
  options: {
    responsive:true,
    scales: {
      y:{beginAtZero:true, title:{display:true, text:'Documents'}},
      x:{title:{display:true, text:'Scenario'}}
    },
    plugins: {legend:{position:'bottom'}}
  }
});

new Chart(document.getElementById('chartReuse'), {
  type: 'doughnut',
  data: {
    labels: ['3 frameworks','2 frameworks','1 framework'],
    datasets: [{
      data:[DATA.reuse.three, DATA.reuse.two, DATA.reuse.one],
      backgroundColor:[C.good, C.warn, C.muted],
      borderWidth:0
    }]
  },
  options: {
    responsive:true, cutout:'55%',
    plugins: {legend:{position:'bottom'}}
  }
});

new Chart(document.getElementById('chartConsolidation'), {
  type: 'bar',
  data: {
    labels: DATA.consolidation.labels,
    datasets: [
      {label:'ISO 42001', data:DATA.consolidation.iso, backgroundColor:C.iso},
      {label:'EU AI Act', data:DATA.consolidation.eu, backgroundColor:C.eu},
      {label:'NIST AI RMF', data:DATA.consolidation.nist, backgroundColor:C.nist},
    ]
  },
  options: {
    indexAxis:'y', responsive:true,
    scales: {
      x:{stacked:true, title:{display:true, text:'Source Obligations'}},
      y:{stacked:true}
    },
    plugins: {legend:{position:'bottom'}}
  }
});

new Chart(document.getElementById('chartGaps'), {
  type: 'bar',
  data: {
    labels: DATA.gaps.labels,
    datasets: [{
      data: DATA.gaps.values,
      backgroundColor: [C.muted, C.muted, C.muted, C.light],
      borderRadius: 4
    }]
  },
  options: {
    indexAxis:'y', responsive:true,
    scales: {x:{beginAtZero:true, title:{display:true, text:'Avg. obligations per scenario'}}},
    plugins: {legend:{display:false}}
  }
});

new Chart(document.getElementById('chartDepth'), {
  type: 'radar',
  data: {
    labels: ['Overall Depth','Component Density','Risk Factor'],
    datasets: DATA.depth.datasets
  },
  options: {
    responsive:true,
    scales: {r:{min:0, max:1, ticks:{stepSize:0.25}}},
    plugins: {legend:{position:'bottom'}}
  }
});
"""


# =====================================================================
# BUILDER SCRIPT
# =====================================================================

def _build_builder_script():
    return """
function addComponent() {
  var row = document.createElement('div');
  row.className = 'comp-row';
  row.innerHTML =
    '<input type="text" placeholder="Component name" class="comp-name" value="New Component"/>' +
    '<select class="comp-tier"><option value="T1">T1 Vehicle</option><option value="T2" selected>T2 Edge/RSU</option><option value="T3">T3 Cloud</option></select>' +
    '<select class="comp-risk"><option value="high">High</option><option value="medium" selected>Medium</option><option value="low">Low</option></select>' +
    '<input type="text" placeholder="Owner" class="comp-owner" value="integrator"/>' +
    '<button class="btn-remove" onclick="this.parentElement.remove()">&#x2715;</button>';
  document.getElementById('sb-components').appendChild(row);
}

function generateYAML() {
  var name = document.getElementById('sb-name').value;
  var desc = document.getElementById('sb-desc').value;
  var rows = document.querySelectorAll('.comp-row');
  var yaml = '# Auto-generated UGAF-ITS scenario\\n';
  yaml += 'name: "' + name + '"\\n';
  yaml += 'description: >\\n  ' + desc + '\\n\\n';
  yaml += 'components:\\n';
  rows.forEach(function(row) {
    var cn = row.querySelector('.comp-name').value;
    var ct = row.querySelector('.comp-tier').value;
    var cr = row.querySelector('.comp-risk').value;
    var co = row.querySelector('.comp-owner').value;
    yaml += '  - name: "' + cn + '"\\n';
    yaml += '    tier: "' + ct + '"\\n';
    yaml += '    risk_level: "' + cr + '"\\n';
    yaml += '    owner: "' + co + '"\\n\\n';
  });
  document.getElementById('sb-yaml').textContent = yaml;
}

function copyYAML() {
  var text = document.getElementById('sb-yaml').textContent;
  navigator.clipboard.writeText(text).then(function() {
    var btn = document.querySelector('.btn-copy');
    if(btn) { btn.textContent = 'Copied!'; setTimeout(function(){btn.textContent='Copy to Clipboard';}, 2000); }
  });
}
"""


# =====================================================================
# HTML COMPONENTS
# =====================================================================

def _kpi(value, label, sub, style="neutral"):
    return f"""<div class="kpi-card kpi-{style}">
  <div class="kpi-value">{value}</div>
  <div class="kpi-label">{label}</div>
  <div class="kpi-sub">{sub}</div>
</div>"""


def _short_name(name):
    m = {"Urban Smart Intersection": "Urban",
         "Highway Corridor ADS": "Highway",
         "Transit Priority Corridor": "Transit",
         "Rural Intersection": "Rural"}
    return m.get(name, name[:12])


def _render_tier_diagram(report):
    if not report:
        return "<p>No scenario data</p>"
    ca = report.get("control_activation", {}).get("controls", {})
    tier_ucs = {"T3": [], "T2": [], "T1": []}
    for uc_id, uc in ca.items():
        for t in uc.get("enforced_at_tiers", []):
            tier_ucs.setdefault(t, []).append(uc_id)

    def badges(tier):
        return " ".join(
            f'<span class="uc-badge">{uc}</span>'
            for uc in sorted(tier_ucs.get(tier, []))
        )

    tc = report.get("architecture_summary", {}).get("tier_component_counts", {})
    return f"""<div class="tier-stack">
  <div class="tier-box tier-cloud">
    <div class="tier-label">&#9729; Tier 3: Cloud &mdash; Backend Infrastructure</div>
    <div class="tier-ucs">{badges("T3")}</div>
    <div class="tier-meta">{tc.get("T3",0)} components &middot; TMC, ML Training, OTA, Fleet Analytics</div>
  </div>
  <div class="tier-connector">&#9660; V2N Interface</div>
  <div class="tier-box tier-edge">
    <div class="tier-label">&#128225; Tier 2: Edge/RSU &mdash; Roadside Infrastructure</div>
    <div class="tier-ucs">{badges("T2")}</div>
    <div class="tier-meta">{tc.get("T2",0)} components &middot; Smart Signal, VRU Detection, V2I, Decision Engine</div>
  </div>
  <div class="tier-connector">&#9660; V2I Interface</div>
  <div class="tier-box tier-vehicle">
    <div class="tier-label">&#128663; Tier 1: Vehicle &mdash; On-Board Systems</div>
    <div class="tier-ucs">{badges("T1")}</div>
    <div class="tier-meta">{tc.get("T1",0)} components &middot; ADAS, Path Planning, V2X Client, DMS</div>
  </div>
</div>"""


def _render_table(reports):
    if not reports:
        return "<p>No data</p>"

    def cc(v):
        try:
            n = float(str(v).replace("%", ""))
            return "cell-good" if n >= 90 else "cell-warn" if n >= 80 else "cell-bad"
        except Exception:
            return ""

    hdr = "".join(f"<th>{_short_name(r['system_name'])}</th>" for r in reports)

    def row(label, fn, cfn=None):
        cells = "".join(
            f'<td class="{cfn(str(fn(r))) if cfn else ""}">{fn(r)}</td>'
            for r in reports
        )
        return f'<tr><td class="metric-label">{label}</td>{cells}</tr>'

    def grp(name):
        return f'<tr><td class="group-header" colspan="{len(reports)+1}">{name}</td></tr>'

    rows = "".join([
        grp("Architecture"),
        row("Active tiers", lambda r: ", ".join(r["architecture_summary"]["active_tiers"])),
        row("Components", lambda r: r["architecture_summary"]["total_components"]),
        row("Stakeholders", lambda r: len(r["architecture_summary"]["owners"])),
        grp("Governance Controls"),
        row("Activated UCs", lambda r: f'{r["control_activation"]["total_activated"]}/12'),
        row("Evidence chains", lambda r: r["tier_dependencies"]["total_chains"]),
        grp("Evidence Backbone"),
        row("Unified artifacts", lambda r: r["evidence_metrics"]["unified_artifacts"]),
        row("Siloed baseline", lambda r: r["evidence_metrics"]["siloed_baseline"]),
        row("Reduction", lambda r: f'{r["evidence_metrics"]["reduction_percentage"]}%'),
        row("Reuse factor", lambda r: r["evidence_metrics"]["avg_reuse_factor"]),
        grp("Framework Coverage"),
        row("ISO/IEC 42001", lambda r: f'{r["framework_coverage"]["ISO42001"]["coverage_percentage"]}%', cc),
        row("EU AI Act", lambda r: f'{r["framework_coverage"]["EU_AI_Act"]["coverage_percentage"]}%', cc),
        row("NIST AI RMF", lambda r: f'{r["framework_coverage"]["NIST_RMF"]["coverage_percentage"]}%', cc),
        row("Average", lambda r: f'{r["framework_coverage"]["average"]["coverage_percentage"]}%', cc),
        grp("Depth &amp; Quality"),
        row("Inst. depth", lambda r: r["coverage_depth"]["overall_depth"]),
        row("Interpretation", lambda r: r["coverage_depth"]["interpretation"]),
        row("Traceability", lambda r: f'{r["traceability"]["traceability_score"]}%', cc),
        row("Gaps", lambda r: r["gap_analysis"]["total_gaps"]),
    ])

    return f'<table class="comp-table"><thead><tr><th>Metric</th>{hdr}</tr></thead><tbody>{rows}</tbody></table>'


def _render_builder():
    return """<div class="builder-grid">
  <div class="builder-form">
    <label>Scenario Name <input type="text" id="sb-name" value="Custom Deployment" /></label>
    <label>Description <textarea id="sb-desc" rows="2">Custom ITS deployment scenario</textarea></label>
    <h4>Components</h4>
    <div id="sb-components">
      <div class="comp-row">
        <input type="text" placeholder="Component name" class="comp-name" value="ADAS Perception"/>
        <select class="comp-tier"><option value="T1" selected>T1 Vehicle</option><option value="T2">T2 Edge/RSU</option><option value="T3">T3 Cloud</option></select>
        <select class="comp-risk"><option value="high" selected>High</option><option value="medium">Medium</option><option value="low">Low</option></select>
        <input type="text" placeholder="Owner" class="comp-owner" value="oem"/>
        <button class="btn-remove" onclick="this.parentElement.remove()">&#x2715;</button>
      </div>
    </div>
    <button class="btn-add" onclick="addComponent()">+ Add Component</button>
    <button class="btn-primary" onclick="generateYAML()">Generate YAML</button>
  </div>
  <div class="builder-output">
    <h4>Generated YAML</h4>
    <pre id="sb-yaml" class="yaml-output">Click "Generate YAML" to produce scenario file</pre>
    <button class="btn-copy btn-secondary" onclick="copyYAML()">Copy to Clipboard</button>
  </div>
</div>"""


# =====================================================================
# CSS
# =====================================================================

def _get_css():
    return """
:root {
  --iso:#1E3A6E;--eu:#7F1D1D;--nist:#14532D;
  --brand:#0891B2;--good:#059669;--warn:#D97706;--bad:#DC2626;
  --bg:#F1F5F9;--card:#FFFFFF;--text:#1E293B;--text2:#64748B;
  --border:#E2E8F0;--radius:12px;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  background:var(--bg);color:var(--text);line-height:1.6;}
.header{background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);
  color:white;padding:24px 40px;display:flex;justify-content:space-between;
  align-items:center;flex-wrap:wrap;gap:16px;}
.header-brand{display:flex;align-items:center;gap:16px;}
.logo{font-size:36px;opacity:0.9;}
.header h1{font-size:22px;font-weight:700;letter-spacing:-0.5px;}
.header .subtitle{font-size:14px;opacity:0.7;font-weight:400;}
.version{font-weight:400;opacity:0.6;font-size:16px;}
.header-meta{display:flex;gap:8px;flex-wrap:wrap;}
.meta-pill{background:rgba(255,255,255,0.12);padding:4px 14px;
  border-radius:20px;font-size:13px;font-weight:500;}
.panel{background:var(--card);margin:20px 24px;padding:32px;
  border-radius:var(--radius);box-shadow:0 1px 3px rgba(0,0,0,0.06);}
.panel-title{font-size:20px;font-weight:700;margin-bottom:4px;color:var(--text);}
.panel-desc{font-size:14px;color:var(--text2);margin-bottom:24px;}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;}
.kpi-card{padding:20px;border-radius:10px;border:1px solid var(--border);
  text-align:center;transition:transform .15s;}
.kpi-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.08);}
.kpi-value{font-size:32px;font-weight:800;line-height:1.1;margin-bottom:4px;}
.kpi-label{font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;}
.kpi-sub{font-size:12px;color:var(--text2);margin-top:4px;}
.kpi-good .kpi-value{color:var(--good);}
.kpi-brand .kpi-value{color:var(--brand);}
.kpi-neutral .kpi-value{color:var(--text);}
.chart-wrap{position:relative;height:340px;max-width:850px;margin:0 auto;}
.chart-wrap-sm{position:relative;height:280px;}
.chart-note{font-size:13px;color:var(--text2);margin-top:16px;padding:12px 16px;
  background:#F8FAFC;border-left:3px solid var(--brand);border-radius:4px;}
.split-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;}
.chart-card{padding:20px;border:1px solid var(--border);border-radius:10px;}
.chart-card h3{font-size:15px;margin-bottom:16px;color:var(--text);}
.tier-stack{display:flex;flex-direction:column;gap:8px;max-width:800px;margin:0 auto;}
.tier-box{border-radius:10px;padding:20px 24px;}
.tier-cloud{background:linear-gradient(135deg,#EFF6FF,#DBEAFE);border:1.5px solid #93C5FD;}
.tier-edge{background:linear-gradient(135deg,#FFF7ED,#FFEDD5);border:1.5px solid #FDBA74;}
.tier-vehicle{background:linear-gradient(135deg,#F0FDF4,#DCFCE7);border:1.5px solid #86EFAC;}
.tier-label{font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;}
.tier-cloud .tier-label{color:#1E40AF;}
.tier-edge .tier-label{color:#C2410C;}
.tier-vehicle .tier-label{color:#166534;}
.tier-ucs{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0;}
.uc-badge{padding:3px 10px;border-radius:6px;font-size:12px;font-weight:600;
  background:rgba(0,0,0,.06);color:var(--text);}
.tier-meta{font-size:12px;color:var(--text2);}
.tier-connector{text-align:center;font-size:13px;color:var(--text2);padding:2px 0;}
.comp-table{width:100%;border-collapse:collapse;font-size:14px;}
.comp-table th{background:#F1F5F9;padding:10px 14px;text-align:left;
  font-weight:600;border-bottom:2px solid var(--border);font-size:13px;}
.comp-table td{padding:8px 14px;border-bottom:1px solid var(--border);}
.comp-table tr:hover{background:#F8FAFC;}
.comp-table .metric-label{font-weight:600;color:var(--text);white-space:nowrap;}
.comp-table .group-header{background:#F8FAFC;font-weight:700;font-size:12px;
  text-transform:uppercase;letter-spacing:.5px;color:var(--text2);}
.cell-good{color:var(--good);font-weight:600;}
.cell-warn{color:var(--warn);font-weight:600;}
.cell-bad{color:var(--bad);font-weight:600;}
.builder-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;}
.builder-form label{display:block;margin-bottom:12px;font-size:14px;font-weight:600;}
.builder-form input,.builder-form textarea,.builder-form select{
  width:100%;padding:8px 12px;border:1px solid var(--border);border-radius:6px;
  font-size:14px;margin-top:4px;}
.comp-row{display:flex;gap:8px;margin-bottom:8px;align-items:center;}
.comp-row input,.comp-row select{margin-top:0;}
.comp-row .comp-name{flex:2;} .comp-row select{flex:1;}
.comp-row .comp-owner{flex:1;}
.btn-remove{background:none;border:none;color:var(--bad);cursor:pointer;
  font-size:18px;padding:4px 8px;}
.btn-add{background:none;border:1px dashed var(--border);padding:8px 16px;
  border-radius:6px;cursor:pointer;font-size:14px;color:var(--text2);
  margin:8px 0;display:block;width:100%;}
.btn-add:hover{border-color:var(--brand);color:var(--brand);}
.btn-primary{background:var(--brand);color:white;border:none;padding:10px 24px;
  border-radius:6px;cursor:pointer;font-weight:600;font-size:14px;margin-top:12px;}
.btn-primary:hover{opacity:.9;}
.btn-secondary{background:#F1F5F9;color:var(--text);border:1px solid var(--border);
  padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px;margin-top:8px;}
.yaml-output{background:#1E293B;color:#E2E8F0;padding:16px;border-radius:8px;
  font-size:13px;line-height:1.5;overflow-x:auto;min-height:200px;
  font-family:'JetBrains Mono','Fira Code',monospace;white-space:pre;}
.builder-output h4{margin-bottom:8px;font-size:14px;}
.footer{text-align:center;padding:24px;font-size:13px;color:var(--text2);}
@media print{
  body{background:white;}
  .panel{box-shadow:none;border:1px solid #ddd;break-inside:avoid;margin:12px 0;}
  .header{background:#1E293B!important;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  #panel-builder{display:none;}
}
@media(max-width:768px){
  .split-grid,.builder-grid{grid-template-columns:1fr;}
  .kpi-grid{grid-template-columns:repeat(2,1fr);}
  .header{padding:16px 20px;}
  .panel{margin:12px;padding:20px;}
}
"""
