"""AgentSec composite score calculation."""

from dataclasses import dataclass


WEIGHTS = {
    "detection": 0.35,
    "quality": 0.25,
    "auditability": 0.15,
    "surface": 0.25,
}


@dataclass
class AgentSecScore:
    """The final AgentSec Score for a tool."""
    tool_name: str
    perspective: str  # WB, BB, HY
    detection: float
    quality: float
    auditability: float
    surface: float
    composite: float

    def scorecard(self) -> str:
        """Render the scorecard as text."""
        return (
            f"{'=' * 60}\n"
            f"  AgentSec Scorecard v1.0\n"
            f"{'=' * 60}\n"
            f"  Tool: {self.tool_name:<30} Perspective: {self.perspective}\n"
            f"{'-' * 60}\n"
            f"  Detection        {self.detection:6.1f}/100\n"
            f"  Quality          {self.quality:6.1f}/100\n"
            f"  Auditability     {self.auditability:6.1f}/100\n"
            f"  Surface Coverage {self.surface:6.1f}/100\n"
            f"{'-' * 60}\n"
            f"  AGENTSEC SCORE   {self.composite:6.1f}/100\n"
            f"{'=' * 60}\n"
        )


def compute_composite(
    tool_name: str,
    perspective: str,
    detection: float,
    quality: float,
    auditability: float,
    surface: float,
) -> AgentSecScore:
    composite = (
        WEIGHTS["detection"] * detection
        + WEIGHTS["quality"] * quality
        + WEIGHTS["auditability"] * auditability
        + WEIGHTS["surface"] * surface
    )
    return AgentSecScore(
        tool_name=tool_name,
        perspective=perspective,
        detection=round(detection, 1),
        quality=round(quality, 1),
        auditability=round(auditability, 1),
        surface=round(surface, 1),
        composite=round(composite, 1),
    )
