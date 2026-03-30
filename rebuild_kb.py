#!/usr/bin/env python3
"""
UGAF-ITS Knowledge Base Rebuilder
====================================
Reads the three CSV files in data/ and regenerates the SOURCE_OBLIGATIONS
section of knowledge_base.py.

Usage:
    1. Edit the CSVs in data/ to fix obligation lists
    2. Run: python rebuild_kb.py
    3. Run: python run_validation.py   (to verify numbers)

The script replaces ONLY the SOURCE_OBLIGATIONS block in knowledge_base.py.
Everything else (UNIFIED_CONTROLS, EVIDENCE_ARTIFACTS, GOVERNANCE_DOMAINS,
SILOED_BASELINE) is preserved untouched.
"""

import csv
import os
import sys


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
KB_PATH = os.path.join(os.path.dirname(__file__), "ugaf", "knowledge_base.py")

CSV_FILES = {
    "ISO42001": "iso42001_obligations.csv",
    "EU_AI_Act": "eu_ai_act_obligations.csv",
    "NIST_RMF": "nist_rmf_obligations.csv",
}

# Marker comments in knowledge_base.py that bracket the obligations block
START_MARKER = "# ===== SOURCE_OBLIGATIONS START (auto-generated) ====="
END_MARKER = "# ===== SOURCE_OBLIGATIONS END (auto-generated) ====="


def load_csv(filepath):
    """Load obligations from a CSV file."""
    obligations = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ob = {
                "id": row["id"].strip(),
                "desc": row["desc"].strip(),
                "domain": row["domain"].strip(),
                "uc": row["uc"].strip() if row["uc"].strip() else None,
                "tiers": row["tiers"].strip().split(";") if row["tiers"].strip() else ["T1", "T2", "T3"],
                "gap": row["gap"].strip() if row["gap"].strip() else None,
            }
            obligations.append(ob)
    return obligations


def generate_python_block(all_obligations):
    """Generate the Python source code for SOURCE_OBLIGATIONS."""
    lines = []
    lines.append(START_MARKER)
    lines.append("")
    lines.append("SOURCE_OBLIGATIONS = {}")
    lines.append("")
    lines.append("def _add(framework, items):")
    lines.append("    for it in items:")
    lines.append('        oid = f"{framework}:{it[\'id\']}"')
    lines.append("        SOURCE_OBLIGATIONS[oid] = {")
    lines.append('            "framework": framework, "id": it["id"],')
    lines.append('            "description": it["desc"], "domain": it["domain"],')
    lines.append('            "mapped_uc": it.get("uc"),')
    lines.append('            "tier_applicability": it.get("tiers", ["T1", "T2", "T3"]),')
    lines.append('            "gap_category": it.get("gap"),')
    lines.append("        }")
    lines.append("")

    for fw_key, csv_name in CSV_FILES.items():
        obs = all_obligations[fw_key]
        mapped = [o for o in obs if o["uc"] is not None]
        gaps = [o for o in obs if o["gap"] is not None]

        lines.append(f"# ----- {fw_key}: {len(obs)} obligations "
                     f"({len(mapped)} mapped + {len(gaps)} gaps) -----")
        lines.append(f'_add("{fw_key}", [')

        for ob in obs:
            parts = [f'"id": "{ob["id"]}"', f'"desc": "{ob["desc"]}"',
                     f'"domain": "{ob["domain"]}"']

            if ob["uc"]:
                parts.append(f'"uc": "{ob["uc"]}"')
            else:
                parts.append('"uc": None')

            # Only include tiers if not the default T1;T2;T3
            if ob["tiers"] != ["T1", "T2", "T3"]:
                tier_str = str(ob["tiers"]).replace("'", '"')
                parts.append(f'"tiers": {tier_str}')

            if ob["gap"]:
                parts.append(f'"gap": "{ob["gap"]}"')

            lines.append("    {" + ", ".join(parts) + "},")

        lines.append("])")
        lines.append("")

    lines.append(END_MARKER)
    return "\n".join(lines)


def rebuild():
    """Read CSVs, generate Python, replace block in knowledge_base.py."""

    # Load all CSVs
    all_obs = {}
    total = 0
    print("Loading CSVs:")
    for fw_key, csv_name in CSV_FILES.items():
        path = os.path.join(DATA_DIR, csv_name)
        if not os.path.exists(path):
            print(f"  ERROR: {path} not found")
            return 1
        obs = load_csv(path)
        all_obs[fw_key] = obs
        mapped = sum(1 for o in obs if o["uc"] is not None)
        gaps = sum(1 for o in obs if o["gap"] is not None)
        total += len(obs)
        print(f"  {fw_key}: {len(obs)} total ({mapped} mapped + {gaps} gaps)")
    print(f"  TOTAL: {total}")

    # Generate the Python block
    new_block = generate_python_block(all_obs)

    # Read current knowledge_base.py
    with open(KB_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Find and replace the obligations block
    if START_MARKER in content and END_MARKER in content:
        # Replace between markers
        before = content[:content.index(START_MARKER)]
        after = content[content.index(END_MARKER) + len(END_MARKER):]
        new_content = before + new_block + after
    else:
        # First time: find the old block and replace it
        # Look for the old-style marker
        old_start = "# =====================================================================\n# SOURCE OBLIGATIONS"
        if old_start in content:
            # Find where the obligations section starts
            idx = content.index(old_start)
            # Find where evidence artifacts section starts (next major block)
            ev_marker = "# =====================================================================\n# EVIDENCE ARTIFACTS"
            if ev_marker in content:
                ev_idx = content.index(ev_marker)
                before = content[:idx]
                after = content[ev_idx:]
                new_content = before + new_block + "\n\n" + after
            else:
                print("ERROR: Cannot find EVIDENCE ARTIFACTS marker in knowledge_base.py")
                return 1
        else:
            print("ERROR: Cannot find SOURCE OBLIGATIONS section in knowledge_base.py")
            print("       Add these markers to knowledge_base.py:")
            print(f"       {START_MARKER}")
            print(f"       ...obligations...")
            print(f"       {END_MARKER}")
            return 1

    # Write back
    with open(KB_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"\nRegenerated {KB_PATH}")
    print(f"Run 'python run_validation.py' to verify numbers.")
    return 0


if __name__ == "__main__":
    sys.exit(rebuild())
