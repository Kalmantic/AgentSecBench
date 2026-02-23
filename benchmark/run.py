"""Main benchmark runner — orchestrates tool evaluation."""

import asyncio
import argparse
from pathlib import Path

from benchmark.runners.semgrep_runner import SemgrepRunner
from benchmark.runners.spa_hacking_agent_runner import SPAHackingAgentRunner
from benchmark.scoring.composite import compute_composite, AgentSecScore
from benchmark.reports.generate import generate_leaderboard


RUNNERS = {
    "semgrep": SemgrepRunner,
    "spa-hacking-agent": SPAHackingAgentRunner,
}


async def run_benchmark(
    apps_dir: Path,
    tool_names: list[str] | None = None,
    timeout: int = 300,
) -> list[AgentSecScore]:
    """Run all tools against all apps and produce scores."""

    if tool_names is None:
        tool_names = list(RUNNERS.keys())

    apps = sorted(p for p in apps_dir.iterdir() if p.is_dir())
    if not apps:
        print(f"No apps found in {apps_dir}")
        return []

    scores = []
    for name in tool_names:
        if name not in RUNNERS:
            print(f"Unknown tool: {name}")
            continue

        runner = RUNNERS[name]()
        print(f"\n--- Running {name} ---")

        for app_path in apps:
            print(f"  Scanning {app_path.name}...")
            result = await runner.timed_run(app_path, timeout)
            print(f"  Found {len(result.findings)} findings in {result.wall_clock_seconds:.1f}s")

        # Placeholder scores until full scoring pipeline is wired
        score = compute_composite(
            tool_name=name,
            perspective=runner.perspective.value,
            detection=0,
            quality=0,
            auditability=0,
            surface=0,
        )
        scores.append(score)

    return scores


def main():
    parser = argparse.ArgumentParser(description="AgentSecBench runner")
    parser.add_argument("--apps", default="benchmark/apps", help="Apps directory")
    parser.add_argument("--tools", nargs="*", default=None, help="Tools to run")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout per app")
    parser.add_argument("--output", default="results", help="Output directory")
    args = parser.parse_args()

    scores = asyncio.run(run_benchmark(
        apps_dir=Path(args.apps),
        tool_names=args.tools,
        timeout=args.timeout,
    ))

    if scores:
        leaderboard = generate_leaderboard(scores)
        print(f"\n{leaderboard}")

        output_dir = Path(args.output)
        output_dir.mkdir(exist_ok=True)
        (output_dir / "leaderboard.md").write_text(leaderboard)
        print(f"\nResults written to {output_dir}/")


if __name__ == "__main__":
    main()
