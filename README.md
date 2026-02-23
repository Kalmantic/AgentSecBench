# AgentSecBench

**A Benchmark Framework for Evaluating Security Tools in the Age of Agentic Development**

*By Akash Mahajan (Appsecco), Kashi KS (Kalmantic Labs), Thiyagarajan M (Kalmantic Labs), Subho Halder (MatterSec)*

No standardized benchmark exists to compare AI-powered security tools against traditional scanners, or against the new attack surfaces that agentic development introduces. AgentSecBench fills that gap, specifically for **coding agents and web application agents**.

## The Problem

Traditional security tools (SAST, DAST, SCA) were built for human-speed development. AI coding agents collapsed the latency window these tools depended on. Meanwhile, new AI security tools like [Claude Code Security](https://www.anthropic.com/news/claude-code-security) claim reasoning-based vulnerability detection, but no benchmark exists to verify these claims or compare approaches.

## Scope

AgentSecBench is deliberately scoped to **coding and web application agents**. A universal "all agents" benchmark abstracts away the specific guardrails, surfaces, and compliance requirements that differ across agent types. Healthcare agents, autonomous vehicle agents, and financial trading agents each need domain-specific benchmarks. This specificity follows the OWASP ASVS model: scoped, testable, and actionable.

## Standards Mapping

AgentSecBench maps to existing enterprise standards:
- **[MITRE ATLAS](https://atlas.mitre.org/)**: AG01-AG06 mapped to ATLAS technique IDs (AML.T0051-T0099)
- **[OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)**: AG categories mapped to ASI01-ASI10
- **[OWASP AISVS](https://owasp.org/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/)**: Aligned with 13 verification categories
- **[NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)**: Dimensions mapped to Govern/Map/Measure/Manage functions
- **PCI DSS v4.0**: AG taxonomy supplementary to OWASP Top 10 per Req 6.4.1
- **HIPAA**: Auditability dimension supports 164.312(b) audit controls

## What AgentSecBench Measures

Four dimensions, inspired by the [trust infrastructure framework](paper/paper-draft.md) for agentic systems:

| Dimension | Question | What It Scores |
|-----------|----------|----------------|
| **Detection** (SecureBench) | Does the tool find real vulnerabilities? | TPR, FPR, severity accuracy, time, patch quality |
| **Quality** (CompetenceBench) | Are findings actionable? | Precision, adversarial robustness, explanation quality |
| **Auditability** (AccountabilityBench) | Can we trace what happened? | Reasoning chain, reproducibility, output standards |
| **Surface** (SurfaceBench) | Does it cover 2026 attack surfaces? | 6 surfaces including MCP, skills, client-side exposure |

## Vulnerability Taxonomy (AG01-AG06)

Extends OWASP Top 10 with agentic-specific categories, mapped to MITRE ATLAS and OWASP Agentic Top 10:

| ID | Name | ATLAS Technique | OWASP Agentic | Perspective |
|----|------|-----------------|---------------|-------------|
| AG01 | Client-Side Secret Exposure | AML.T0055, AML.T0083 | ASI03 | Black-box |
| AG02 | Source Map Leakage | AML.T0000, CWE-312 | ASI03 | Black-box |
| AG03 | MCP Tool Injection | AML.T0053, AML.T0099 | ASI02, ASI04 | White-box |
| AG04 | Skill Registry Poisoning | AML.T0053, AML.T0058 | ASI04 | White-box |
| AG05 | Hallucinated Dependency | AML.T0060, AML.T0062 | ASI04, ASI05 | White-box / SCA |
| AG06 | Agent Prompt Manipulation | AML.T0051, AML.T0080 | ASI01, ASI06 | Both |

### Evangelism vs. Verification

The AG taxonomy is the *evangelism layer* (like OWASP Top 10). Per-category [verification requirements](docs/verification-requirements.md) provide the *operational layer* (like OWASP ASVS), with L1 (automated) and L2 (review) requirements for each category.

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

## Documentation

- [Verification Requirements](docs/verification-requirements.md) - L1/L2 requirements per AG category with compliance cross-reference
- [Creating Test Cases from Vulnerable Agents](docs/creating-test-cases-from-vulnerable-agents.md) - How to convert your vulnerable agent into a benchmark test case
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - How to contribute apps, runners, and categories

## Paper

The research paper is available in [`paper/`](paper/):
- [paper.pdf](paper/paper.pdf) - Compiled PDF (v0.2, 7 pages)
- [paper.tex](paper/paper.tex) - LaTeX source
- [paper-draft.md](paper/paper-draft.md) - Markdown draft (v0.1)

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
