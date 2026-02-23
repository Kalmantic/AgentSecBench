"""Generate leaderboard and comparison reports."""

from benchmark.scoring.composite import AgentSecScore


def generate_leaderboard(scores: list[AgentSecScore]) -> str:
    """Generate a markdown leaderboard table from scores."""
    sorted_scores = sorted(scores, key=lambda s: s.composite, reverse=True)

    lines = [
        "# AgentSecBench Leaderboard",
        "",
        "| Rank | Tool | Type | Detection | Quality | Audit | Surface | **Score** |",
        "|------|------|------|-----------|---------|-------|---------|-----------|",
    ]

    for i, s in enumerate(sorted_scores, 1):
        lines.append(
            f"| {i} | {s.tool_name} | {s.perspective} | "
            f"{s.detection:.1f} | {s.quality:.1f} | {s.auditability:.1f} | "
            f"{s.surface:.1f} | **{s.composite:.1f}** |"
        )

    return "\n".join(lines)
