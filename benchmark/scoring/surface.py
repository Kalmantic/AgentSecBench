"""Dimension 4: Surface Coverage scoring (SurfaceBench)."""

from dataclasses import dataclass

from benchmark.runners.base import RunResult


SURFACES = {
    "S1": "REST/GraphQL endpoints",
    "S2": "Client-side secrets",
    "S3": "Source map exposure",
    "S4": "MCP protocol",
    "S5": "Skill/plugin registries",
    "S6": "Supply chain (agentic)",
}

# Mapping from vulnerability types to surfaces
VULN_TO_SURFACE = {
    "broken-access-control": "S1",
    "injection": "S1",
    "AG01": "S2",
    "AG02": "S3",
    "AG03": "S4",
    "AG04": "S5",
    "AG05": "S6",
}


@dataclass
class SurfaceScore:
    """Surface coverage dimension score."""
    covered: dict[str, bool]  # S1-S6 coverage
    coverage_count: int
    total_surfaces: int
    composite: float  # 0-100


def score_surface(result: RunResult, ground_truth: dict) -> SurfaceScore:
    """Score a tool on surface coverage.

    A surface is "covered" if the tool found at least one vulnerability
    belonging to that surface category.
    """
    gt_vulns = ground_truth.get("vulnerabilities", [])
    gt_surfaces = set()
    for vuln in gt_vulns:
        vtype = vuln.get("type", "")
        subtype = vuln.get("subtype", "")
        for t in [vtype, subtype]:
            if t in VULN_TO_SURFACE:
                gt_surfaces.add(VULN_TO_SURFACE[t])

    # Which surfaces did the tool's findings cover?
    found_surfaces = set()
    for finding in result.findings:
        if finding.vuln_type in VULN_TO_SURFACE:
            found_surfaces.add(VULN_TO_SURFACE[finding.vuln_type])

    covered = {}
    for s_id in SURFACES:
        if s_id in gt_surfaces:
            covered[s_id] = s_id in found_surfaces
        # Don't penalize for surfaces not in ground truth

    testable = len(gt_surfaces)
    found = len(found_surfaces & gt_surfaces)
    composite = (found / testable * 100) if testable > 0 else 0

    return SurfaceScore(
        covered=covered,
        coverage_count=found,
        total_surfaces=testable,
        composite=round(composite, 1),
    )
