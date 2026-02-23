"""SPA Hacking Agent runner — AI-powered black-box reconnaissance."""

import asyncio
import json
import re
from pathlib import Path

from .base import BaseRunner, Finding, Perspective, RunResult


SEVERITY_MAP = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
    "info": "info",
}


class SPAHackingAgentRunner(BaseRunner):
    name = "spa-hacking-agent"
    perspective = Perspective.BLACK_BOX

    def __init__(self, agent_path: str = "python main.py"):
        self.agent_path = agent_path

    async def run(self, app_path: Path, timeout_seconds: int = 300) -> RunResult:
        # Read the target URL from the app's deploy config
        url_file = app_path / "deploy" / "url.txt"
        if not url_file.exists():
            return RunResult(
                tool_name=self.name,
                app_name=app_path.name,
                perspective=self.perspective,
                findings=[],
                wall_clock_seconds=0,
                error="No deploy/url.txt found",
            )

        target_url = url_file.read_text().strip()
        output_dir = app_path / "results" / self.name

        proc = await asyncio.create_subprocess_exec(
            *self.agent_path.split(),
            target_url,
            "-o", str(output_dir),
            "-q",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            proc.kill()
            return RunResult(
                tool_name=self.name,
                app_name=app_path.name,
                perspective=self.perspective,
                findings=[],
                wall_clock_seconds=timeout_seconds,
                timed_out=True,
            )

        # Parse the markdown report
        report_files = list(output_dir.glob("security-report-*.md"))
        raw = report_files[0].read_text() if report_files else ""
        findings = self.normalize(raw)

        return RunResult(
            tool_name=self.name,
            app_name=app_path.name,
            perspective=self.perspective,
            findings=findings,
            wall_clock_seconds=0,
            raw_output=raw,
        )

    def normalize(self, raw_output: str) -> list[Finding]:
        """Parse SPA Hacking Agent markdown report into findings."""
        findings = []

        # Extract endpoint findings
        for match in re.finditer(
            r"##\s+(?:API\s+)?Endpoint[s]?.*?\n(.*?)(?=\n##|\Z)",
            raw_output, re.DOTALL
        ):
            for line in match.group(1).strip().split("\n"):
                line = line.strip("- ")
                if line and not line.startswith("#"):
                    findings.append(Finding(
                        vuln_type="AG01",
                        severity="medium",
                        confidence=0.8,
                        description=f"Exposed endpoint: {line}",
                        location=line,
                    ))

        # Extract secret findings
        for match in re.finditer(
            r"##\s+(?:Hardcoded\s+)?Secret[s]?.*?\n(.*?)(?=\n##|\Z)",
            raw_output, re.DOTALL
        ):
            for line in match.group(1).strip().split("\n"):
                line = line.strip("- ")
                if line and not line.startswith("#"):
                    severity = "critical" if any(
                        k in line.lower() for k in ["aws", "private", "secret_key"]
                    ) else "high"
                    findings.append(Finding(
                        vuln_type="AG01",
                        severity=severity,
                        confidence=0.9,
                        description=f"Exposed secret: {line}",
                        location="client-bundle",
                    ))

        return findings
