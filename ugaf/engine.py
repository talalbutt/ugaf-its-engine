"""
UGAF-ITS Governance Engine v1.1
================================
Eight computations validating UGAF-ITS across arbitrary ITS architectures.
C1-C5: Core validation. C6-C8: Dashboard analytics.
"""
import time
from statistics import mean
from ugaf.knowledge_base import (
    UNIFIED_CONTROLS, EVIDENCE_ARTIFACTS, SOURCE_OBLIGATIONS,
    GOVERNANCE_DOMAINS, SILOED_BASELINE, SILOED_TOTAL_DOCUMENTS,
)


def _get_scope_aware_baseline(active_tiers):
    """Scope-aware siloed document baseline scaled to active tiers.

    The 37-document three-tier total breaks down as:
      13 documents relevant to edge/RSU operations
      12 documents relevant to vehicle operations
      12 documents relevant to cloud operations

    A deployment missing a tier would not produce that tier's
    siloed documents under independent compliance either.
    """
    tier_set = set(active_tiers)
    has_t1 = "T1" in tier_set
    has_t2 = "T2" in tier_set
    has_t3 = "T3" in tier_set

    if has_t1 and has_t2 and has_t3:
        return 37   # full three-tier
    elif has_t2 and has_t3:
        return 25   # edge + cloud (Transit)
    elif has_t1 and has_t3:
        return 30   # vehicle + cloud
    elif has_t1 and has_t2:
        return 28   # vehicle + edge
    elif has_t3:
        return 24   # cloud only
    elif has_t2:
        return 13   # edge only (Rural)
    elif has_t1:
        return 12   # vehicle only
    else:
        return 37   # fallback


class UGAFEngine:
    def __init__(self):
        self.controls = UNIFIED_CONTROLS
        self.artifacts = EVIDENCE_ARTIFACTS
        self.obligations = SOURCE_OBLIGATIONS
        self.domains = GOVERNANCE_DOMAINS

    def evaluate(self, deployment):
        start = time.perf_counter()
        active_tiers = set(c["tier"] for c in deployment["components"])
        activated = self._activate_controls(active_tiers, deployment)
        backbone, ev_metrics = self._evidence_backbone(activated, active_tiers)
        trace = self._verify_traceability(activated)
        coverage = self._compute_coverage(activated)
        gaps = self._detect_gaps(active_tiers, activated)
        coverage_depth = self._compute_coverage_depth(deployment, activated)
        consolidation = self._compute_consolidation(activated)
        tier_deps = self._compute_tier_dependencies(deployment, activated, backbone)
        return {
            "system_name": deployment["name"],
            "description": deployment.get("description", ""),
            "architecture_summary": {
                "total_components": len(deployment["components"]),
                "active_tiers": sorted(list(active_tiers)),
                "tier_component_counts": self._tier_counts(deployment),
                "owners": sorted(list(set(c.get("owner", "unspecified")
                                         for c in deployment["components"]))),
            },
            "control_activation": activated,
            "evidence_backbone": backbone,
            "evidence_metrics": ev_metrics,
            "traceability": trace,
            "framework_coverage": coverage,
            "gap_analysis": gaps,
            "coverage_depth": coverage_depth,
            "consolidation": consolidation,
            "tier_dependencies": tier_deps,
            "execution_time_ms": round((time.perf_counter() - start) * 1000, 2),
        }

    def _activate_controls(self, active_tiers, deployment):
        activated = {}
        for uid, uc in self.controls.items():
            tiers = [t for t, on in uc["tier_activation"].items() if on and t in active_tiers]
            if tiers:
                owners = {}
                for t in tiers:
                    owners[t] = sorted(set(c.get("owner", "?")
                                           for c in deployment["components"] if c["tier"] == t))
                activated[uid] = {
                    "name": uc["name"], "domain": uc["domain"],
                    "enforced_at_tiers": tiers, "tier_owners": owners,
                    "primary_artifact": uc["primary_artifact"],
                    "lifecycle_phases": uc["lifecycle_phases"],
                    "source_count": sum(1 for o in self.obligations.values()
                                        if o["mapped_uc"] == uid),
                }
        return {
            "total_activated": len(activated),
            "total_possible": len(self.controls),
            "activation_ratio": round(len(activated) / len(self.controls) * 100, 1),
            "controls": activated,
        }

    def _evidence_backbone(self, activated, active_tiers):
        uc_ids = set(activated["controls"].keys())
        required = {}
        for aid, art in self.artifacts.items():
            served = [u for u in art["serves_ucs"] if u in uc_ids]
            producible = any(t in active_tiers for t in art["producing_tiers"])
            if served and producible:
                required[aid] = {
                    "name": art["name"], "primary_tier": art["primary_tier"],
                    "producing_tiers": [t for t in art["producing_tiers"] if t in active_tiers],
                    "frameworks_served": art["serves_frameworks"],
                    "framework_count": len(art["serves_frameworks"]),
                    "ucs_served": served, "owner_role": art["owner_role"],
                }
        n = len(required)
        siloed = _get_scope_aware_baseline(active_tiers)
        fwc = [a["framework_count"] for a in required.values()]
        three = sum(1 for a in required.values() if a["framework_count"] == 3)
        return required, {
            "unified_artifacts": n, "siloed_baseline": siloed,
            "reduction_count": siloed - n,
            "reduction_percentage": round((1 - n / siloed) * 100, 1) if siloed else 0,
            "avg_reuse_factor": round(mean(fwc), 2) if fwc else 0,
            "three_framework_artifacts": three,
            "three_framework_percentage": round(three / n * 100, 1) if n else 0,
        }

    def _verify_traceability(self, activated):
        uc_ids = set(activated["controls"].keys())
        ok, broken = [], []
        for uid in uc_ids:
            uc = self.controls[uid]
            aid = uc["primary_artifact"]
            obs = [oid for oid, o in self.obligations.items() if o["mapped_uc"] == uid]
            for ob in obs:
                (ok if aid in self.artifacts else broken).append(
                    {"obligation": ob, "uc": uid, "artifact": aid})
        total = len(ok) + len(broken)
        score = round(len(ok) / total * 100, 1) if total else 100.0
        return {
            "traceability_score": score, "status": "COMPLETE" if score == 100.0 else "INCOMPLETE",
            "forward_links_verified": len(ok), "forward_links_broken": len(broken),
            "broken_link_details": broken,
        }

    def _compute_coverage(self, activated):
        uc_ids = set(activated["controls"].keys())
        fw_data = {
            "ISO42001": {"label": "ISO/IEC 42001", "total": 0, "covered": 0, "gaps": []},
            "EU_AI_Act": {"label": "EU AI Act", "total": 0, "covered": 0, "gaps": []},
            "NIST_RMF": {"label": "NIST AI RMF", "total": 0, "covered": 0, "gaps": []},
        }
        for oid, ob in self.obligations.items():
            fw = ob["framework"]
            if fw not in fw_data:
                continue
            fw_data[fw]["total"] += 1
            if ob["mapped_uc"] and ob["mapped_uc"] in uc_ids:
                fw_data[fw]["covered"] += 1
            else:
                fw_data[fw]["gaps"].append({
                    "id": ob["id"], "description": ob["description"],
                    "gap_category": ob.get("gap_category", "tier_not_present"),
                })
        result = {}
        for fid, fd in fw_data.items():
            t, c = fd["total"], fd["covered"]
            result[fid] = {
                "label": fd["label"], "total_obligations": t,
                "covered_obligations": c,
                "coverage_percentage": round(c / t * 100, 1) if t else 0,
                "gap_count": len(fd["gaps"]), "gaps": fd["gaps"],
            }
        pcts = [v["coverage_percentage"] for v in result.values()]
        result["average"] = {"coverage_percentage": round(mean(pcts), 1) if pcts else 0}
        return result

    def _detect_gaps(self, active_tiers, activated):
        uc_ids = set(activated["controls"].keys())
        cats = {"tier_not_present": [], "organizational_procedure": [],
                "regulatory_workflow": [], "context_setting": []}
        for oid, ob in self.obligations.items():
            if ob["mapped_uc"] and ob["mapped_uc"] in uc_ids:
                continue
            gc = ob.get("gap_category")
            if gc and gc in cats:
                cats[gc].append({"id": ob["id"], "framework": ob["framework"],
                                 "description": ob["description"]})
            elif ob["mapped_uc"]:
                cats["tier_not_present"].append({
                    "id": ob["id"], "framework": ob["framework"],
                    "description": ob["description"], "required_uc": ob["mapped_uc"],
                })
        return {
            "total_gaps": sum(len(v) for v in cats.values()),
            "categories": {c: {"count": len(i), "obligations": i} for c, i in cats.items()},
        }

    # === C6: Coverage Depth (radar chart) ===
    def _compute_coverage_depth(self, deployment, activated):
        active_tiers = set(c["tier"] for c in deployment["components"])
        tc = self._tier_counts(deployment)
        density = {t: min(1.0, tc.get(t, 0) / 4.0) for t in active_tiers}
        avg_density = mean(density.values()) if density else 0.0
        comps = deployment["components"]
        high_risk = sum(1 for c in comps if c.get("risk_level") == "high")
        risk_factor = high_risk / len(comps) if comps else 0.0
        owners = set(c.get("owner", "unspecified") for c in comps)
        breadth = min(1.0, len(owners) / 3.0)
        depth = round(0.40 * avg_density + 0.35 * risk_factor + 0.25 * breadth, 3)
        interp = ("Production-grade" if depth >= 0.85 else
                  "Substantial" if depth >= 0.65 else
                  "Partial" if depth >= 0.45 else "Minimal")
        return {
            "overall_depth": depth, "component_density": round(avg_density, 3),
            "risk_factor": round(risk_factor, 3),
            "stakeholder_breadth": round(breadth, 3),
            "interpretation": interp,
        }

    # === C7: Consolidation Analysis (domain stacked bar) ===
    def _compute_consolidation(self, activated):
        uc_ids = set(activated["controls"].keys())
        stats = {}
        for did, dom in self.domains.items():
            stats[did] = {
                "name": dom["name"], "iso_count": 0, "eu_count": 0, "nist_count": 0,
                "total_source": 0,
                "unified_controls": len(dom["unified_controls"]),
                "active_controls": sum(1 for uc in dom["unified_controls"] if uc in uc_ids),
            }
        for oid, ob in self.obligations.items():
            did = ob["domain"]
            if did not in stats:
                continue
            stats[did]["total_source"] += 1
            key = {"ISO42001": "iso_count", "EU_AI_Act": "eu_count",
                   "NIST_RMF": "nist_count"}.get(ob["framework"])
            if key:
                stats[did][key] += 1
        for did, s in stats.items():
            t, u = s["total_source"], s["unified_controls"]
            s["consolidation_ratio"] = round((1 - u / t) * 100, 1) if t > 0 else 0.0
        total_src = sum(s["total_source"] for s in stats.values())
        return {
            "total_source_obligations": total_src,
            "total_unified_controls": len(uc_ids),
            "overall_consolidation_ratio": round(
                (1 - len(uc_ids) / total_src) * 100, 1) if total_src > 0 else 0,
            "per_domain": stats,
        }

    # === C8: Cross-Tier Dependencies (evidence chains) ===
    def _compute_tier_dependencies(self, deployment, activated, backbone):
        uc_ids = set(activated["controls"].keys())
        active_tiers = set(c["tier"] for c in deployment["components"])
        templates = [
            {"chain_id": "incident_response_escalation",
             "description": "Edge anomaly -> cloud triage -> controlled change -> redeploy",
             "required_tiers": ["T2", "T3"],
             "ucs": ["UC-12", "UC-07", "UC-01", "UC-02"],
             "artifacts": ["monitoring_alerting_plan", "incident_ticket_log",
                           "risk_register", "model_change_notice"]},
            {"chain_id": "model_update_governance",
             "description": "Cloud training -> validation -> OTA -> edge deploy",
             "required_tiers": ["T3", "T2"],
             "ucs": ["UC-09", "UC-07", "UC-10", "UC-11"],
             "artifacts": ["vv_test_report", "technical_file",
                           "deployment_record", "release_manifest"]},
            {"chain_id": "data_quality_pipeline",
             "description": "Edge sensors -> cloud aggregation -> quality report",
             "required_tiers": ["T2", "T3"],
             "ucs": ["UC-03", "UC-04"],
             "artifacts": ["data_quality_report", "bias_performance_report"]},
            {"chain_id": "oversight_chain",
             "description": "Vehicle operator -> edge status -> oversight monitoring",
             "required_tiers": ["T1", "T2"],
             "ucs": ["UC-05", "UC-06", "UC-08"],
             "artifacts": ["oversight_protocol", "intervention_fallback_plan"]},
            {"chain_id": "supplier_to_deployment",
             "description": "Cloud supplier assessment -> integration -> validation",
             "required_tiers": ["T3"],
             "ucs": ["UC-11", "UC-07", "UC-09"],
             "artifacts": ["supplier_audit_report", "technical_file"]},
        ]
        chains = []
        for t in templates:
            if all(tier in active_tiers for tier in t["required_tiers"]):
                active_ucs = [uc for uc in t["ucs"] if uc in uc_ids]
                if active_ucs:
                    chains.append({
                        "chain_id": t["chain_id"], "description": t["description"],
                        "tiers_involved": t["required_tiers"],
                        "ucs_involved": active_ucs,
                        "artifacts_in_chain": t["artifacts"],
                        "chain_length": len(active_ucs),
                        "completeness": round(len(active_ucs) / len(t["ucs"]) * 100, 1),
                    })
        lengths = [c["chain_length"] for c in chains]
        return {
            "total_chains": len(chains), "chains": chains,
            "max_chain_length": max(lengths) if lengths else 0,
            "avg_chain_length": round(mean(lengths), 1) if lengths else 0,
        }

    def _tier_counts(self, dep):
        c = {}
        for comp in dep["components"]:
            c[comp["tier"]] = c.get(comp["tier"], 0) + 1
        return c
