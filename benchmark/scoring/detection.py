"""Dimension 1: Detection scoring (SecureBench)."""

from dataclasses import dataclass

from benchmark.runners.base import Finding, RunResult


@dataclass
class DetectionScore:
    """Detection dimension score breakdown."""
    tpr: float              # True Positive Rate (0-1)
    fpr: float              # False Positive Rate (0-1), inverted for scoring
    severity_accuracy: float  # Correct severity / total found
    time_score: float       # Normalized speed score (0-1)
    patch_quality: float    # Correct fixes / total fixes (0-1)
    composite: float        # Weighted 0-100

    WEIGHTS = {
        "tpr": 0.30,
        "fpr": 0.20,
        "severity_accuracy": 0.15,
        "time_score": 0.15,
        "patch_quality": 0.20,
    }


def score_detection(
    result: RunResult,
    ground_truth: dict,
    max_time_seconds: float = 600,
) -> DetectionScore:
    """Score a tool run on the Detection dimension.

    Args:
        result: The tool's run result with findings.
        ground_truth: Parsed ground-truth.yaml with known vulnerabilities.
        max_time_seconds: Time budget for normalization.
    """
    gt_vulns = ground_truth.get("vulnerabilities", [])
    total_vulns = len(gt_vulns)

    if total_vulns == 0:
        return DetectionScore(0, 0, 0, 0, 0, 0)

    # Match findings to ground truth
    matched = set()
    false_positives = 0
    severity_correct = 0
    fixes_correct = 0
    fixes_total = 0

    for finding in result.findings:
        match = _match_finding_to_gt(finding, gt_vulns)
        if match:
            matched.add(match["id"])
            if finding.severity == match.get("severity", ""):
                severity_correct += 1
            if finding.suggested_fix:
                fixes_total += 1
                # In full implementation: compile + test the fix
                # For now: check if fix text is non-empty and relevant
                if _fix_is_plausible(finding.suggested_fix, match):
                    fixes_correct += 1
        else:
            false_positives += 1

    total_findings = len(result.findings)
    found = len(matched)

    tpr = found / total_vulns if total_vulns > 0 else 0
    fpr_raw = false_positives / total_findings if total_findings > 0 else 0
    fpr_score = 1 - fpr_raw  # Higher is better
    sev_acc = severity_correct / found if found > 0 else 0
    time_score = max(0, 1 - (result.wall_clock_seconds / max_time_seconds))
    patch_q = fixes_correct / fixes_total if fixes_total > 0 else 0

    composite = 100 * (
        DetectionScore.WEIGHTS["tpr"] * tpr
        + DetectionScore.WEIGHTS["fpr"] * fpr_score
        + DetectionScore.WEIGHTS["severity_accuracy"] * sev_acc
        + DetectionScore.WEIGHTS["time_score"] * time_score
        + DetectionScore.WEIGHTS["patch_quality"] * patch_q
    )

    return DetectionScore(
        tpr=tpr,
        fpr=fpr_score,
        severity_accuracy=sev_acc,
        time_score=time_score,
        patch_quality=patch_q,
        composite=round(composite, 1),
    )


def _match_finding_to_gt(finding: Finding, gt_vulns: list[dict]) -> dict | None:
    """Match a finding to a ground truth vulnerability."""
    for vuln in gt_vulns:
        # Match by type
        if finding.vuln_type == vuln.get("type") or finding.vuln_type == vuln.get("subtype"):
            # Match by location (fuzzy)
            loc = vuln.get("location", {})
            for loc_val in [loc.get("source", ""), loc.get("bundle", ""), loc.get("endpoint", "")]:
                if loc_val and loc_val in finding.location:
                    return vuln
            # Type match without location is weak but still counts
            return vuln
    return None


def _fix_is_plausible(fix: str, vuln: dict) -> bool:
    """Basic heuristic: does the fix mention relevant concepts?"""
    correct_fix = vuln.get("correct_fix", "").lower()
    if not correct_fix:
        return len(fix) > 20  # Non-trivial fix text
    # Check keyword overlap
    fix_words = set(fix.lower().split())
    gt_words = set(correct_fix.split())
    overlap = fix_words & gt_words
    return len(overlap) >= 2
