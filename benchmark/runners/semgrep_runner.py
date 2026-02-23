"""Semgrep runner — traditional SAST baseline."""

import asyncio
import json
from pathlib import Path

from .base import BaseRunner, Finding, Perspective, RunResult


SEVERITY_MAP = {
    "ERROR": "high",
    "WARNING": "medium",
    "INFO": "low",
}


class SemgrepRunner(BaseRunner):
    name = "semgrep"
    perspective = Perspective.WHITE_BOX

    async def run(self, app_path: Path, timeout_seconds: int = 300) -> RunResult:
        src_path = app_path / "src"
        if not src_path.exists():
            src_path = app_path

        proc = await asyncio.create_subprocess_exec(
            "semgrep", "scan", "--json", "--config", "auto", str(src_path),
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

        raw = stdout.decode()
        findings = self.normalize(raw)

        return RunResult(
            tool_name=self.name,
            app_name=app_path.name,
            perspective=self.perspective,
            findings=findings,
            wall_clock_seconds=0,  # filled by timed_run
            raw_output=raw,
        )

    def normalize(self, raw_output: str) -> list[Finding]:
        try:
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            return []

        findings = []
        for result in data.get("results", []):
            findings.append(Finding(
                vuln_type=result.get("check_id", "unknown"),
                severity=SEVERITY_MAP.get(result.get("extra", {}).get("severity", ""), "medium"),
                confidence=0.7,  # Semgrep doesn't provide confidence
                description=result.get("extra", {}).get("message", ""),
                location=f"{result.get('path', '')}:{result.get('start', {}).get('line', 0)}",
                evidence=result.get("extra", {}).get("lines", ""),
                raw=result,
            ))
        return findings
