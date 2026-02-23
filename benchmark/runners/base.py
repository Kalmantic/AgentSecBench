"""Abstract base runner for security tool evaluation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
import time
import yaml


class Perspective(Enum):
    WHITE_BOX = "WB"
    BLACK_BOX = "BB"
    HYBRID = "HY"


@dataclass
class Finding:
    """A normalized security finding."""
    vuln_type: str          # e.g. "broken-access-control", "AG01"
    severity: str           # critical, high, medium, low, info
    confidence: float       # 0.0 - 1.0
    description: str
    location: str           # file:line or URL path
    evidence: str = ""
    suggested_fix: str = ""
    raw: dict = field(default_factory=dict)


@dataclass
class RunResult:
    """Result from a single tool run against a single app."""
    tool_name: str
    app_name: str
    perspective: Perspective
    findings: list[Finding]
    wall_clock_seconds: float
    timed_out: bool = False
    error: str | None = None
    raw_output: str = ""


class BaseRunner(ABC):
    """Abstract interface for security tool runners."""

    name: str
    perspective: Perspective

    @abstractmethod
    async def run(self, app_path: Path, timeout_seconds: int = 300) -> RunResult:
        """Run the tool against a test application.

        Args:
            app_path: Path to the test application directory.
                      For WB tools: contains src/ directory.
                      For BB tools: contains deploy/ or a URL file.
            timeout_seconds: Maximum time budget.

        Returns:
            RunResult with normalized findings.
        """
        ...

    @abstractmethod
    def normalize(self, raw_output: Any) -> list[Finding]:
        """Normalize tool-specific output to Finding objects."""
        ...

    def load_ground_truth(self, app_path: Path) -> dict:
        """Load ground-truth.yaml for a test application."""
        gt_path = app_path / "ground-truth.yaml"
        if not gt_path.exists():
            raise FileNotFoundError(f"No ground truth at {gt_path}")
        with open(gt_path) as f:
            return yaml.safe_load(f)

    async def timed_run(self, app_path: Path, timeout_seconds: int = 300) -> RunResult:
        """Wrapper that enforces time budget."""
        start = time.monotonic()
        result = await self.run(app_path, timeout_seconds)
        result.wall_clock_seconds = time.monotonic() - start
        if result.wall_clock_seconds > timeout_seconds:
            result.timed_out = True
        return result
