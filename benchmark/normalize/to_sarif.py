"""Convert normalized findings to SARIF 2.1.0 format."""

import json
from benchmark.runners.base import Finding, RunResult


SEVERITY_TO_SARIF = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "note",
}


def to_sarif(result: RunResult) -> dict:
    """Convert a RunResult to SARIF 2.1.0 JSON."""
    results = []
    rules = {}

    for i, finding in enumerate(result.findings):
        rule_id = finding.vuln_type
        if rule_id not in rules:
            rules[rule_id] = {
                "id": rule_id,
                "shortDescription": {"text": rule_id},
            }

        sarif_result = {
            "ruleId": rule_id,
            "level": SEVERITY_TO_SARIF.get(finding.severity, "warning"),
            "message": {"text": finding.description},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.location},
                }
            }],
        }
        if finding.confidence:
            sarif_result["properties"] = {"confidence": finding.confidence}

        results.append(sarif_result)

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": result.tool_name,
                    "rules": list(rules.values()),
                }
            },
            "results": results,
        }],
    }


def write_sarif(result: RunResult, path: str) -> None:
    sarif = to_sarif(result)
    with open(path, "w") as f:
        json.dump(sarif, f, indent=2)
