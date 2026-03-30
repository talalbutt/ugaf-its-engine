#!/usr/bin/env python3
"""
UGAF-ITS Dashboard Panel Exporter
===================================
Renders dashboard.html in a headless Chromium browser at high DPI
and exports each panel as a separate high-quality PDF and PNG.

Produces paper-ready figures matching the three composite layouts:
  fig_tool_dashboard.pdf    = Executive Summary + Three-Tier Architecture
  fig_coverage_reduction.pdf = Framework Coverage + Evidence Backbone
  fig_consolidation_domain.pdf = Crosswalk Consolidation by Domain

Usage:
    python export_panels.py [--html dashboard.html] [--output figures/]
"""

import argparse
import os
import sys
import time

from playwright.sync_api import sync_playwright


# Panel definitions: ID, descriptive filename, and which paper figure they belong to
PANELS = [
    {"id": "panel-executive",     "name": "executive_summary"},
    {"id": "panel-coverage",      "name": "framework_coverage"},
    {"id": "panel-evidence",      "name": "evidence_backbone"},
    {"id": "panel-consolidation", "name": "consolidation_domain"},
    {"id": "panel-tiers",         "name": "tier_architecture"},
    {"id": "panel-table",         "name": "comparative_table"},
    {"id": "panel-gaps",          "name": "gap_analysis"},
    {"id": "panel-depth",         "name": "instantiation_depth"},
]

# Composite figures for the paper (panel IDs to combine vertically)
COMPOSITES = [
    {
        "name": "fig_tool_dashboard",
        "panels": ["panel-executive", "panel-tiers"],
        "description": "Executive Summary + Three-Tier Architecture",
    },
    {
        "name": "fig_coverage_reduction",
        "panels": ["panel-coverage", "panel-evidence"],
        "description": "Framework Coverage + Evidence Backbone Analysis",
    },
    {
        "name": "fig_consolidation_domain",
        "panels": ["panel-consolidation"],
        "description": "Crosswalk Consolidation by Governance Domain",
    },
]

# High DPI scale factor (3x = effectively 288 DPI at screen resolution)
SCALE_FACTOR = 3
# Viewport width matching a nice wide render
VIEWPORT_WIDTH = 1400
VIEWPORT_HEIGHT = 900


def export_panels(html_path, output_dir):
    """Export all panels and composites from the dashboard HTML."""
    os.makedirs(output_dir, exist_ok=True)
    abs_html = os.path.abspath(html_path)
    file_url = f"file://{abs_html}"

    print(f"  Source:  {abs_html}")
    print(f"  Output:  {os.path.abspath(output_dir)}")
    print(f"  Scale:   {SCALE_FACTOR}x ({SCALE_FACTOR * 96} effective DPI)")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            device_scale_factor=SCALE_FACTOR,
        )
        page = context.new_page()

        print("  Loading dashboard...", end=" ", flush=True)
        page.goto(file_url, wait_until="networkidle")
        page.wait_for_timeout(2000)
        print("OK")

        # --- Export individual panels ---
        print("\n  Individual panels:")
        for panel in PANELS:
            el = page.query_selector(f"#{panel['id']}")
            if not el:
                print(f"    SKIP: #{panel['id']} not found")
                continue

            png_path = os.path.join(output_dir, f"{panel['name']}.png")
            el.screenshot(path=png_path, type="png")
            print(f"    {panel['name']}.png  ({_file_size(png_path)})")

        # --- Export composite figures for the paper ---
        print("\n  Composite paper figures:")
        for comp in COMPOSITES:
            _export_composite(browser, page, comp, output_dir)

        # --- Export full-page PDF ---
        pdf_path = os.path.join(output_dir, "dashboard_full.pdf")
        page.pdf(
            path=pdf_path,
            format="A3",
            print_background=True,
            scale=0.65,
        )
        print(f"\n  Full dashboard PDF: dashboard_full.pdf ({_file_size(pdf_path)})")

        context.close()
        browser.close()

    print(f"\n  All exports complete -> {os.path.abspath(output_dir)}/")


def _export_composite(browser, page, comp, output_dir):
    """
    Export a composite figure by hiding all other panels, removing gaps,
    and capturing only the target panels tightly clipped together.
    """
    keep_ids = list(comp["panels"])

    # Hide everything except target panels, remove margins/gaps for tight clip
    page.evaluate("""(keepIds) => {
        document.querySelector('.header').style.display = 'none';
        document.querySelector('.footer').style.display = 'none';
        document.body.style.background = 'white';
        document.querySelectorAll('.panel').forEach(el => {
            if (keepIds.includes(el.id)) {
                el.style.display = 'block';
                el.style.margin = '0';
                el.style.borderRadius = '0';
                el.style.boxShadow = 'none';
            } else {
                el.style.display = 'none';
            }
        });
    }""", keep_ids)
    page.wait_for_timeout(300)

    # Get bounding box of the combined visible panels
    bbox = page.evaluate("""(keepIds) => {
        let top = Infinity, bottom = 0, left = Infinity, right = 0;
        keepIds.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                const r = el.getBoundingClientRect();
                if (r.top < top) top = r.top;
                if (r.bottom > bottom) bottom = r.bottom;
                if (r.left < left) left = r.left;
                if (r.right > right) right = r.right;
            }
        });
        return {x: left, y: top, width: right - left, height: bottom - top};
    }""", keep_ids)

    # PNG: clipped screenshot of just the panels
    png_path = os.path.join(output_dir, f"{comp['name']}.png")
    page.screenshot(path=png_path, type="png", clip=bbox)

    # PDF: print with tight page size
    pdf_path = os.path.join(output_dir, f"{comp['name']}.pdf")
    page.pdf(
        path=pdf_path,
        print_background=True,
        width=f"{int(bbox['width'])}px",
        height=f"{int(bbox['height'] + 20)}px",
    )

    # Restore all panels
    page.evaluate("""() => {
        document.querySelector('.header').style.display = '';
        document.querySelector('.footer').style.display = '';
        document.body.style.background = '';
        document.querySelectorAll('.panel').forEach(el => {
            el.style.display = '';
            el.style.margin = '';
            el.style.borderRadius = '';
            el.style.boxShadow = '';
        });
    }""")
    page.wait_for_timeout(200)

    print(f"    {comp['name']}.pdf  ({_file_size(pdf_path)}) - {comp['description']}")
    print(f"    {comp['name']}.png  ({_file_size(png_path)})")


def _file_size(path):
    """Return human-readable file size."""
    size = os.path.getsize(path)
    if size > 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    return f"{size / 1024:.0f} KB"


def main():
    parser = argparse.ArgumentParser(description="Export UGAF-ITS dashboard panels")
    parser.add_argument("--html", default="dashboard.html",
                        help="Path to dashboard.html")
    parser.add_argument("--output", default="figures",
                        help="Output directory for figures")
    args = parser.parse_args()

    if not os.path.exists(args.html):
        # Try results/ subdirectory
        alt = os.path.join("results", args.html)
        if os.path.exists(alt):
            args.html = alt
        else:
            print(f"ERROR: {args.html} not found")
            return 1

    print("=" * 60)
    print("UGAF-ITS Dashboard Panel Exporter")
    print("=" * 60)
    export_panels(args.html, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
