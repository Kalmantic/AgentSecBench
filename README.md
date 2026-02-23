# AgentSecBench

**A Benchmark Framework for Evaluating Security Tools in the Age of Agentic Development**

No standardized benchmark exists to compare AI-powered security tools against traditional scanners — or against the new attack surfaces that agentic development introduces. AgentSecBench fills that gap.

## The Problem

Traditional security tools (SAST, DAST, SCA) were built for human-speed development. AI coding agents collapsed the latency window these tools depended on. Meanwhile, new AI security tools like [Claude Code Security](https://www.anthropic.com/news/claude-code-security) claim reasoning-based vulnerability detection — but no benchmark exists to verify these claims or compare approaches.

## What AgentSecBench Measures

Four dimensions, inspired by the [trust infrastructure framework](paper/paper-draft.md) for agentic systems:

| Dimension | Question | What It Scores |
|-----------|----------|----------------|
| **Detection** (SecureBench) | Does the tool find real vulnerabilities? | TPR, FPR, severity accuracy, time, patch quality |
| **Quality** (CompetenceBench) | Are findings actionable? | Precision, adversarial robustness, explanation quality |
| **Auditability** (AccountabilityBench) | Can we trace what happened? | Reasoning chain, reproducibility, output standards |
| **Surface** (SurfaceBench) | Does it cover 2026 attack surfaces? | 6 surfaces including MCP, skills, client-side exposure |

## Novel Vulnerability Taxonomy (AG01-AG06)

Extends OWASP Top 10 with agentic-specific categories:

| ID | Name | Perspective |
|----|------|-------------|
| AG01 | Client-Side Secret Exposure | Black-box |
| AG02 | Source Map Leakage | Black-box |
| AG03 | MCP Tool Injection | White-box |
| AG04 | Skill Registry Poisoning | White-box |
| AG05 | Hallucinated Dependency | White-box / SCA |
| AG06 | Agent Prompt Manipulation | Both |

## Tools Under Evaluation

| Category | Tools | Perspective |
|----------|-------|-------------|
| AI White-Box | Claude Code Security | WB |
| AI Black-Box | [SPA Hacking Agent](https://github.com/mtr7x/spa-hacking-agent) | BB |
| Traditional SAST | Semgrep, Snyk Code, CodeQL | WB |
| Traditional DAST | Burp Suite, ZAP | BB |

## Composite Score

```
AgentSec Score = (0.35 × Detection) + (0.25 × Quality) + (0.15 × Auditability) + (0.25 × Surface)
```

## Project Structure

```
AgentSecBench/
├── paper/                    # Research paper (LaTeX + PDF)
├── benchmark/
│   ├── apps/                 # 60 intentionally vulnerable test apps
│   │   └── {app-name}/
│   │       ├── src/          # Application source
│   │       ├── deploy/       # Build output
│   │       └── ground-truth.yaml
│   ├── runners/              # Tool integration harnesses
│   │   ├── base.py           # Abstract runner interface
│   │   ├── claude_code_security.py
│   │   ├── spa_hacking_agent.py
│   │   ├── semgrep_runner.py
│   │   ├── snyk_runner.py
│   │   └── zap_runner.py
│   ├── normalize/            # Output normalization (SARIF)
│   ├── scoring/              # Dimension scoring engines
│   └── reports/              # Leaderboard generation
├── docs/                     # Additional documentation
└── tests/                    # Benchmark self-tests
```

## Quick Start

```bash
# Clone
git clone https://github.com/mtr7x/AgentSecBench.git
cd AgentSecBench

# Install
pip install -r requirements.txt

# Run a single tool against a single app
python -m benchmark.runners.semgrep_runner benchmark/apps/nextjs-idor-001/

# Run full benchmark suite
python -m benchmark.run --tools all --apps all

# Generate scorecard
python -m benchmark.reports.generate --output results/
```

## Contributing

We welcome contributions:

- **New test apps**: Add vulnerable applications with ground-truth manifests
- **New runners**: Integrate additional security tools
- **New surfaces**: Propose AG07+ vulnerability categories
- **Benchmark results**: Submit scored runs for the leaderboard

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## Paper

The research paper is available in [`paper/`](paper/):
- [paper.pdf](paper/paper.pdf) — Compiled PDF
- [paper.tex](paper/paper.tex) — LaTeX source
- [paper-draft.md](paper/paper-draft.md) — Markdown draft

## License

MIT

## Citation

```bibtex
@article{agentsecbench2026,
  title={AgentSecBench: A Benchmark Framework for Evaluating Security Tools in the Age of Agentic Development},
  year={2026},
  note={Draft v0.1}
}
```
