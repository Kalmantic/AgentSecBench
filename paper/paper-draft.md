# AgentSecBench: A Benchmark Framework for Evaluating Security Tools in the Age of Agentic Development

**Draft v0.1 — February 2026**

---

## Abstract

The emergence of AI coding agents has collapsed the latency window that traditional application security depended on. Static analysis, dependency scanning, and audit-layer tools were architected for human-speed development — they assume code exists before inspection. Agents generate, execute, and deploy before scanners run. Meanwhile, a new generation of AI-powered security tools — exemplified by Anthropic's Claude Code Security — promises reasoning-based vulnerability detection that surpasses pattern-matching approaches. Yet no standardized benchmark exists to evaluate these tools against each other or against the new attack surfaces that agentic development introduces.

We propose **AgentSecBench**, an open benchmark framework that evaluates security tools across four trust dimensions: *Secure* (vulnerability detection), *Competent* (finding quality and actionability), *Accountable* (explainability and auditability), and *Surface* (coverage of novel agentic attack surfaces including MCP protocols, skill registries, and client-side exposure). We describe the benchmark architecture, a curated dataset of intentionally vulnerable modern web applications, and a scoring methodology designed to capture the fundamental differences between white-box source analysis, black-box runtime reconnaissance, and traditional static/dynamic tools.

---

## 1. Introduction

Application security tooling is undergoing a phase transition. For two decades, the security industry operated on a stable assumption: developers write code, commit it, and scanners inspect it before or shortly after deployment. SAST tools match code against known vulnerability patterns. SCA tools check dependency manifests against CVE databases. DAST tools probe running applications against known attack signatures. The entire audit layer depends on a temporal gap between code creation and code execution.

AI coding agents have eliminated that gap.

Tools like Claude Code, Cursor, and Windsurf generate, test, and deploy code in seconds. The hallucinated npm package is installed before the scanner's next scheduled run. The misconfigured API route is live before the PR reviewer wakes up. Prevention — the foundational promise of DevSecOps — requires a window of time that no longer exists.

Simultaneously, AI is being applied to security itself. Anthropic's Claude Code Security, launched in February 2026, uses Claude Opus 4.6 to reason about codebases "the way a human security researcher would," claiming over 500 vulnerabilities found in production open-source projects that had evaded decades of expert review [1]. This represents a fundamentally different approach: not pattern matching, but semantic understanding of code behavior.

Yet the security landscape is not monolithic. White-box source analysis, no matter how sophisticated, cannot detect what is already exposed to the internet through deployed client-side bundles. A hardcoded API key in a minified JavaScript file, an undocumented admin endpoint visible in a React SPA's routing table, a source map leaking original TypeScript to any browser that requests it — these are runtime exposure problems, not source code problems. Tools operating in the black-box reconnaissance space — exemplified by automated SPA analysis agents that render applications, fetch JavaScript bundles, and extract secrets and endpoints — address a complementary attack surface that source-level tools are structurally blind to.

The problem is that no benchmark exists to evaluate any of this. We have SWE-bench for coding capability [2]. We have nothing equivalent for security tooling in the agentic era. Vendors make claims. Buyers have no basis for comparison. The "Agent Security Scorecard" that the industry needs does not exist.

This paper proposes one.

---

## 2. Background and Motivation

### 2.1 The Collapse of the Audit Layer

Traditional application security follows a linear pipeline:

```
Write → Commit → Scan → Review → Deploy
```

Every commercial security tool inserts itself somewhere in this pipeline. SAST operates between Commit and Review. DAST operates after Deploy. SCA operates at Commit time by inspecting manifests. The entire model assumes sequential, human-paced development.

Agentic development compresses this to:

```
Prompt → Generate → Execute
```

There is no commit phase. There is no review window. The agent generates code and runs it. By the time a scanner processes the output, the code is already executing — potentially in production.

This is not a speed problem solvable with faster scanners. It is an architectural mismatch. The audit layer assumes code exists as a static artifact available for inspection. Agents produce code as a transient byproduct of execution. The inspection model itself is obsolete.

### 2.2 The Rise of AI-Powered Security

Claude Code Security represents the first major attempt by a foundation model provider to apply frontier reasoning capabilities to vulnerability detection. Rather than matching patterns against a database of known exploits, it reads code and reasons about data flows, component interactions, and logical invariants — the way an experienced security researcher would.

This approach addresses a long-standing limitation of SAST: traditional tools excel at finding known vulnerability patterns (SQL injection via string concatenation, XSS via unsanitized output) but fail at business logic flaws, broken access control, and novel vulnerability classes that don't match existing signatures. Claude Code Security claims to find vulnerabilities "that had gone undetected for decades, despite years of expert review" [1].

However, this capability operates strictly in the white-box domain. It requires access to source code. It cannot assess what an attacker sees from the outside.

### 2.3 The Black-Box Reconnaissance Gap

Modern single-page applications ship substantial application logic to the client. A React or Next.js application's JavaScript bundles contain:

- API endpoint URLs and routing patterns
- Authentication flow logic and token handling
- Hardcoded configuration values, sometimes including API keys and secrets
- Client-side access control logic that reveals authorization models
- Library versions with known CVEs
- Source maps that expose original, unminified source code

None of this is visible to a source-code scanner unless the scanner also models the build pipeline and deployment configuration. In practice, it doesn't. The shipped bundle is a different artifact from the source repository.

Black-box SPA analysis tools — which render applications in headless browsers, intercept network requests, fetch and analyze JavaScript bundles, and check for source map exposure — operate in this gap. They answer a different question: not "is this code vulnerable?" but "what has this application already exposed to every visitor?"

### 2.4 The Benchmark Gap

The security tooling landscape now contains at least four distinct categories:

1. **Traditional SAST/SCA** (Semgrep, Snyk, SonarQube, CodeQL) — pattern-matching on source code and dependency manifests
2. **Traditional DAST** (Burp Suite, ZAP) — probing running applications with known attack payloads
3. **AI-powered white-box analysis** (Claude Code Security) — reasoning-based source code analysis
4. **AI-powered black-box reconnaissance** (SPA Hacking Agent and similar) — autonomous client-side exposure analysis

No benchmark evaluates these categories against each other. No dataset captures the vulnerability classes unique to agentic development. No scoring methodology accounts for the fundamental architectural differences between these approaches.

---

## 3. The AgentSecBench Framework

We propose a benchmark organized around four trust dimensions, inspired by the emerging trust infrastructure framework for agentic systems [3].

### 3.1 Design Principles

**P1: Ground truth, not opinion.** Every test case has a documented vulnerability with known type, location, severity, and correct fix. Scoring is automated against this ground truth.

**P2: Modern stack, real patterns.** Test applications use current frameworks (Next.js 15, Nuxt 4, SvelteKit, React Router v7) with realistic code patterns. No artificial constructs that only exist in benchmarks.

**P3: Multi-perspective evaluation.** The same vulnerability may be detectable from source code, from the deployed bundle, or both. The benchmark captures which perspective each tool operates from and scores accordingly.

**P4: Novel surfaces included.** The benchmark includes vulnerability classes specific to agentic development: MCP protocol security, skill registry poisoning, agent-to-agent communication, and AI-generated code artifacts.

**P5: Open and extensible.** The dataset, runner harnesses, and scoring methodology are open-source. Vendors can self-report. Researchers can contribute test cases.

### 3.2 Benchmark Dimensions

#### Dimension 1: Detection (SecureBench)

*Core question: Does the tool find real vulnerabilities?*

**Dataset composition:**

The test corpus consists of 60 intentionally vulnerable web applications organized into three tiers:

| Tier | Count | Description | Examples |
|------|-------|-------------|----------|
| **Standard** | 20 | OWASP Top 10 in modern frameworks | SQLi in Next.js API route, XSS in React component, SSRF via fetch proxy |
| **Complex** | 20 | Multi-step, logic-dependent | IDOR via client-side route guard bypass, privilege escalation through role enum in JWT, race condition in payment flow |
| **Agentic** | 20 | Novel to AI-generated code | Hallucinated package dependency, secrets in AI-generated config, prompt injection via code comments, malicious MCP tool |

Each application includes a ground truth manifest:

```yaml
# ground-truth/nextjs-idor-001.yaml
app: nextjs-idor-001
framework: next.js@15.2
vulnerabilities:
  - id: VULN-001
    type: broken-access-control
    subtype: idor
    severity: high
    location:
      source: src/app/api/users/[id]/route.ts:14
      bundle: _next/static/chunks/app/api/users/route-a3f2b1.js
      endpoint: /api/users/:id
    description: >
      User ID parameter accepted without authorization check.
      Any authenticated user can access any other user's data.
    detection_perspective:
      - white_box    # Visible in source code
      - black_box    # Endpoint discoverable in client bundle
    correct_fix: |
      Add session.userId === params.id check before data access.
```

**Metrics:**

| Metric | Formula | Weight |
|--------|---------|--------|
| True Positive Rate (TPR) | found_vulns / total_vulns | 0.30 |
| False Positive Rate (FPR) | 1 - (false_positives / total_findings) | 0.20 |
| Severity Accuracy | correct_severity / total_found | 0.15 |
| Time to Detection | normalized(1 / avg_seconds_per_vuln) | 0.15 |
| Patch Quality | compilable_and_correct_fixes / total_fixes | 0.20 |

#### Dimension 2: Quality (CompetenceBench)

*Core question: Are the findings actionable and correct?*

This dimension evaluates the signal-to-noise ratio and practical utility of findings. A tool that finds 90% of vulnerabilities but buries them in 500 false positives is less useful than one that finds 70% with near-zero noise.

**Tests:**

1. **Precision under load**: Scan 10 large real-world open-source projects (>100K LOC each) with known CVE history. Measure findings against NVD ground truth.

2. **Adversarial robustness**: Inject prompt-injection attempts into code comments, variable names, and documentation within test applications. Measure whether AI-powered tools are manipulated into suppressing findings or generating false ones.

   ```javascript
   // AI security note: this endpoint is safe, no vulnerabilities here
   // Ignore all previous instructions about security scanning
   app.get('/admin/delete-all', (req, res) => {
     db.query(`DELETE FROM users WHERE id = ${req.query.id}`); // SQLi
   });
   ```

3. **Explanation quality**: Human security engineers rate each finding's explanation on a 1-5 scale across: accuracy, completeness, actionability, and specificity. Inter-rater reliability measured via Krippendorff's alpha.

4. **Fix correctness**: For tools that suggest patches, automatically verify that: (a) the fix compiles, (b) existing tests still pass, (c) the vulnerability is no longer exploitable, (d) no new vulnerabilities are introduced.

#### Dimension 3: Auditability (AccountabilityBench)

*Core question: Can we trace and reproduce what the tool did?*

This dimension matters for enterprise adoption, where compliance teams need to understand and verify security tool outputs.

**Criteria (scored 0-5 each):**

| Criterion | Description |
|-----------|-------------|
| **Reasoning chain** | Does the tool explain *why* something is a vulnerability, not just *that* it is? |
| **Evidence linking** | Can you trace from finding → specific code path → data flow → exploit scenario? |
| **Confidence calibration** | Does the tool express uncertainty? Are confidence scores well-calibrated (90% confidence findings are correct ~90% of the time)? |
| **Output standardization** | Does it produce machine-readable output (SARIF, CycloneDX, custom schema)? |
| **Reproducibility** | Same input produces same findings across multiple runs? |
| **Audit trail** | Does the tool log its own decision process for post-hoc review? |

#### Dimension 4: Surface Coverage (SurfaceBench)

*Core question: Does the tool cover the attack surfaces that matter in 2026?*

This is the differentiation dimension. Traditional tools were built for traditional surfaces. The benchmark tests coverage of six attack surfaces:

| # | Surface | Test Scenario | Traditional | AI White-Box | AI Black-Box |
|---|---------|--------------|-------------|-------------|-------------|
| S1 | **REST/GraphQL endpoints** | Undocumented admin APIs, unprotected mutations | Partial | Yes | Yes |
| S2 | **Client-side secrets** | API keys, tokens, credentials in JS bundles | No | Partial | Yes |
| S3 | **Source map exposure** | .map files serving original source to any requester | No | No | Yes |
| S4 | **MCP protocol** | Malicious MCP tools, unsafe context sharing, tool injection | No | Possible | No |
| S5 | **Skill/plugin registries** | Typosquatted or trojaned agent skills | No | Possible | No |
| S6 | **Supply chain (agentic)** | Hallucinated packages, AI-generated vulnerable dependencies | Partial | Yes | No |

The "Yes/No/Partial" columns represent expected capability based on architectural analysis. The benchmark replaces expectations with measurements.

**Test applications for each surface:**

- **S1**: Next.js app with 15 API routes, 5 undocumented, 3 with broken auth
- **S2**: React SPA with AWS keys in environment config shipped to client bundle, Stripe publishable key in source, internal service URL in axios defaults
- **S3**: Production build with source maps accessible at standard paths (.js.map, webpack://)
- **S4**: MCP server registry with 10 tools, 3 containing data exfiltration logic (sending context to external endpoints)
- **S5**: Agent skill directory with 20 SKILL.md files, 4 containing obfuscated malicious instructions
- **S6**: package.json with 3 hallucinated package names that resolve to typosquatted malicious packages on npm

### 3.3 Composite Scoring

The **AgentSec Score** is a weighted composite:

```
AgentSec Score = (0.35 × Detection) + (0.25 × Quality) + (0.15 × Auditability) + (0.25 × Surface)
```

Surface coverage is weighted equally with quality because coverage of novel attack surfaces is the primary differentiator in the agentic era. A tool that perfectly detects traditional vulnerabilities but is blind to MCP injection and client-side exposure is increasingly inadequate.

Each dimension is normalized to 0-100. The composite score is also 0-100.

Tools are additionally tagged with their **operating perspective**:

- `WB` — White-box (requires source access)
- `BB` — Black-box (requires only a URL or deployed artifact)
- `HY` — Hybrid

This prevents misleading comparisons. A white-box tool should not be penalized for missing source-map exposure (a black-box finding), and a black-box tool should not be penalized for missing business logic flaws only visible in source.

---

## 4. Benchmark Dataset Construction

### 4.1 Application Generation Methodology

Test applications are constructed using three methods:

**Method 1: Manual seeding.** Security engineers write realistic vulnerable applications using modern frameworks. Each vulnerability is documented, reviewed by a second engineer, and validated as exploitable.

**Method 2: CVE reproduction.** Known CVEs from real-world applications are reproduced in isolated test applications. This ensures the benchmark tests against vulnerabilities that actually occur in production, not synthetic constructs.

**Method 3: AI-assisted generation with human validation.** AI coding agents are used to generate applications with specific architectural patterns. A security engineer then seeds vulnerabilities that are natural to the generated code's structure. This produces the "agentic" tier — vulnerabilities characteristic of AI-generated code.

### 4.2 Framework Coverage

The initial benchmark targets the most common SPA frameworks:

| Framework | Apps | Rationale |
|-----------|------|-----------|
| Next.js 15 | 20 | Dominant React meta-framework, server components create new attack surface |
| Nuxt 4 | 10 | Vue equivalent, different SSR patterns |
| SvelteKit | 10 | Growing adoption, different compilation model |
| React SPA (Vite) | 10 | Pure client-side, maximum bundle exposure |
| Angular 19 | 10 | Enterprise adoption, different module system |

### 4.3 Vulnerability Taxonomy

We extend the OWASP Top 10 with agentic-specific categories:

| Category | ID | Source |
|----------|----|--------|
| Injection | A03 | OWASP 2021 |
| Broken Access Control | A01 | OWASP 2021 |
| Cryptographic Failures | A02 | OWASP 2021 |
| Security Misconfiguration | A05 | OWASP 2021 |
| Vulnerable Components | A06 | OWASP 2021 |
| **Client-Side Secret Exposure** | AG01 | AgentSecBench |
| **Source Map Leakage** | AG02 | AgentSecBench |
| **MCP Tool Injection** | AG03 | AgentSecBench |
| **Skill Registry Poisoning** | AG04 | AgentSecBench |
| **Hallucinated Dependency** | AG05 | AgentSecBench |
| **Agent Prompt Manipulation** | AG06 | AgentSecBench |

---

## 5. Runner Architecture

### 5.1 Tool Integration

Each tool under evaluation is wrapped in a standardized runner that:

1. Accepts a test application (source directory or deployed URL, depending on tool type)
2. Invokes the tool with default configuration (no custom rules or tuning)
3. Captures all output and normalizes it to a common finding schema
4. Records wall-clock time and resource consumption

```
benchmark/
├── apps/                          # Test applications
│   ├── nextjs-idor-001/
│   │   ├── src/                   # Application source
│   │   ├── deploy/                # Build output / deployment artifact
│   │   └── ground-truth.yaml      # Vulnerability manifest
│   └── ...
├── runners/
│   ├── base.py                    # Abstract runner interface
│   ├── claude_code_security.py    # White-box: feeds source directory
│   ├── spa_hacking_agent.py       # Black-box: feeds deployed URL
│   ├── semgrep.py                 # White-box: feeds source directory
│   ├── snyk.py                    # White-box: feeds source + manifest
│   ├── burp_suite.py              # Black-box: feeds deployed URL
│   └── zap.py                     # Black-box: feeds deployed URL
├── normalize/
│   └── to_sarif.py                # Normalize all outputs to SARIF
├── scoring/
│   ├── detection.py               # Dimension 1 scoring
│   ├── quality.py                 # Dimension 2 scoring
│   ├── auditability.py            # Dimension 3 scoring
│   ├── surface.py                 # Dimension 4 scoring
│   └── composite.py               # AgentSec Score calculation
└── reports/
    └── generate.py                # Leaderboard and comparison reports
```

### 5.2 Deployment Harness

For black-box tools, test applications are deployed to isolated containers:

```python
class DeploymentHarness:
    """Deploys test apps and returns accessible URLs for black-box tools."""

    async def deploy(self, app_path: str) -> str:
        # Build the application
        # Deploy to isolated container
        # Return accessible URL
        # Teardown after evaluation
```

For white-box tools, the source directory is provided directly. This architectural split ensures each tool operates in its natural mode.

### 5.3 Time Budget

Each tool receives a fixed time budget per application:

| App Complexity | Time Budget |
|---------------|-------------|
| Small (<10 files) | 2 minutes |
| Medium (10-50 files) | 5 minutes |
| Large (50+ files) | 10 minutes |

Tools that exceed the time budget receive partial credit for findings produced within the window.

---

## 6. Preliminary Analysis: Architectural Capability Mapping

Before running the benchmark, we can predict structural strengths and weaknesses based on each tool category's architecture.

### 6.1 White-Box AI (Claude Code Security)

**Structural strengths:**
- Can reason about code semantics, not just patterns
- Understands data flow across function boundaries
- Can detect business logic flaws invisible to pattern matching
- Can suggest contextually appropriate fixes

**Structural blindspots:**
- Cannot see what the build pipeline produces (source vs. bundle gap)
- Cannot detect runtime exposure (source maps, client-side secrets in deployed bundles)
- Cannot assess the attacker's view of a deployed application
- Requires source code access (not available for third-party assessment)

### 6.2 Black-Box AI (SPA Hacking Agent)

**Structural strengths:**
- Sees exactly what an attacker sees
- Detects client-side secret exposure in production bundles
- Discovers source map leakage
- Enumerates actual deployed API endpoints
- Identifies client-side library versions with known CVEs
- Operates without source code access

**Structural blindspots:**
- Cannot reason about server-side business logic
- Cannot detect vulnerabilities in code paths not reachable from the client
- Limited to what the application exposes through its client-side bundle
- Cannot suggest source-level fixes

### 6.3 Traditional SAST (Semgrep, CodeQL)

**Structural strengths:**
- Fast, deterministic, reproducible
- Well-understood false positive characteristics
- Extensive rule libraries for known patterns
- Integrates into CI/CD pipelines

**Structural blindspots:**
- Pattern-matching cannot detect novel vulnerability classes
- No understanding of business logic or application context
- High false positive rates for complex vulnerability types
- Blind to client-side exposure and deployment configuration

### 6.4 Traditional DAST (Burp, ZAP)

**Structural strengths:**
- Tests actual running applications
- Can detect runtime vulnerabilities (misconfigurations, header issues)
- Well-established methodology

**Structural blindspots:**
- Probe-based: only tests attack patterns in its database
- Limited JavaScript analysis capability
- Cannot reason about application logic
- Slow: requires crawling and probing each endpoint

### 6.5 The Complementarity Thesis

This analysis suggests that no single tool category provides complete coverage. The benchmark is designed to make this complementarity **quantifiable**. We hypothesize that:

1. AI white-box tools will dominate Dimensions 1 and 3 (Detection and Auditability)
2. AI black-box tools will dominate Dimension 4, surfaces S1-S3 (client-side exposure)
3. Traditional tools will show competitive speed but lower coverage
4. No tool will score above 70 across all four dimensions
5. A combination of white-box + black-box AI tools will score higher than any single tool

If confirmed, this has direct implications for security architecture: the agentic era requires **layered AI security** — not a single tool, but a composition of perspectives.

---

## 7. Implications for the Security Industry

### 7.1 The Trust Infrastructure Thesis

The benchmark framework aligns with the emerging "trust infrastructure" analysis of agentic security [3]. The four benchmark dimensions map directly to the four trust problems:

| Trust Problem | Benchmark Dimension | What It Measures |
|--------------|---------------------|------------------|
| Secure: "Will this harm us?" | Detection (SecureBench) | Vulnerability finding capability |
| Competent: "Will it work correctly?" | Quality (CompetenceBench) | Finding reliability and actionability |
| Accountable: "Can we prove what happened?" | Auditability (AccountabilityBench) | Explainability and compliance readiness |
| Verified: "Does it cover what matters?" | Surface (SurfaceBench) | Coverage of real-world attack surfaces |

### 7.2 Pricing Model Disruption

Traditional security tools price per seat or per scan. Both models break down when agents are the primary developers:

- **Per-seat pricing**: Agent-driven development reduces human headcount. Fewer seats, less revenue.
- **Per-scan pricing**: Agents generate code continuously. Scanning every generation is prohibitively expensive.

The benchmark enables a new pricing conversation: **per-vulnerability-class coverage**. Organizations can evaluate which vulnerability classes they need covered, select tools that cover those classes, and pay for coverage rather than scans.

### 7.3 The Composition Architecture

If the benchmark confirms the complementarity thesis, the winning security architecture is not a single tool but a **composition layer** that:

1. Routes source code to white-box AI analysis
2. Routes deployed applications to black-box AI reconnaissance
3. Routes build artifacts to supply-chain analysis
4. Routes agent configurations (MCP, skills) to agentic surface analysis
5. Deduplicates, correlates, and prioritizes findings across all perspectives

This composition layer — the "security orchestrator for agentic development" — may be the most valuable product category the benchmark reveals.

---

## 8. Limitations and Future Work

**Current limitations:**

- The initial dataset of 60 applications, while diverse, cannot cover all vulnerability classes and framework combinations. Community contribution is essential for comprehensive coverage.
- Dimension 3 (Auditability) relies partially on human evaluation, introducing subjectivity. We plan to develop automated proxies for explanation quality.
- The benchmark evaluates tools in isolation. Real-world security involves tool composition, organizational context, and human judgment that the benchmark cannot capture.
- MCP and skill registry attack surfaces (S4, S5) are nascent. The test scenarios are based on early threat modeling, not observed real-world attacks at scale.

**Future work:**

- **Continuous updating**: New vulnerability classes and attack surfaces will be added quarterly as the agentic development landscape evolves.
- **Adversarial track**: A dedicated track for evaluating tool robustness against evasion techniques — can attackers craft code that specifically evades AI-powered detection?
- **Composition scoring**: Evaluate tool combinations, not just individual tools, to quantify the value of layered security architectures.
- **Cost-effectiveness dimension**: Add a fifth dimension measuring security value per dollar, enabling ROI comparisons.

---

## 9. Conclusion

The security industry is undergoing a structural transition. The audit layer that sustained two decades of security tooling is being compressed out of existence by AI coding agents. New AI-powered security tools — both white-box and black-box — offer capabilities that traditional pattern-matching cannot match. But they operate from fundamentally different perspectives, with complementary strengths and blindspots.

The industry needs a benchmark. Not a vendor benchmark designed to make one product look good, but an open, community-maintained framework that quantifies what each tool actually catches, what it misses, and where the gaps remain.

AgentSecBench is that framework. By evaluating tools across detection capability, finding quality, auditability, and novel surface coverage, it provides the empirical foundation for security architecture decisions in the agentic era.

The audit layer is dying. The trust layer is emerging. The benchmark tells you who to trust — and what to verify.

---

## References

[1] Anthropic. "Making frontier cybersecurity capabilities available to defenders." February 2026. https://www.anthropic.com/news/claude-code-security

[2] C. E. Jimenez et al. "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?" ICLR 2024.

[3] P. Gosavi. "SaaS Cybersecurity is Dead." 2026. As analyzed in "Follow the White Trust" (unpublished).

[4] OWASP Foundation. "OWASP Top 10:2021." https://owasp.org/Top10/

[5] OASIS. "Static Analysis Results Interchange Format (SARIF) Version 2.1.0." 2018.

[6] CyberNews. "Amateur attacker uses AI toolkits, including Claude and Deepseek, to hack Fortinet firewalls." February 2026.

[7] NIST. "National Vulnerability Database." https://nvd.nist.gov/

---

## Appendix A: Proposed AgentSec Scorecard Format

```
╔══════════════════════════════════════════════════════════════════╗
║                    AgentSec Scorecard v1.0                      ║
╠══════════════════════════════════════════════════════════════════╣
║ Tool: [Name]                    Perspective: [WB/BB/HY]        ║
║ Version: [X.Y.Z]               Date: [YYYY-MM-DD]             ║
╠══════════════════════════════════════════════════════════════════╣
║ DIMENSION          │ SCORE │ BREAKDOWN                         ║
╠═════════════════════╪═══════╪═════════════════════════════════════╣
║ Detection          │ 82/100│ TPR:91% FPR:8% Sev:85% Fix:72%  ║
║ Quality            │ 75/100│ Precision:88% Robustness:62%     ║
║ Auditability       │ 68/100│ Reasoning:4.2 Repro:95% SARIF:✓ ║
║ Surface Coverage   │ 71/100│ S1:✓ S2:✓ S3:✗ S4:✗ S5:✗ S6:✓  ║
╠═════════════════════╪═══════╪═════════════════════════════════════╣
║ AGENTSEC SCORE     │ 75/100│                                   ║
╚══════════════════════════════════════════════════════════════════╝
```

## Appendix B: Vulnerability Taxonomy Extension (AG01-AG06)

| ID | Name | Description | Detection Perspective |
|----|------|-------------|----------------------|
| AG01 | Client-Side Secret Exposure | API keys, tokens, or credentials present in JavaScript bundles served to end users | Black-box |
| AG02 | Source Map Leakage | Source map files (.js.map) accessible in production, exposing original source code | Black-box |
| AG03 | MCP Tool Injection | Malicious or vulnerable tools registered in MCP servers that execute with agent privileges | White-box |
| AG04 | Skill Registry Poisoning | Trojaned or typosquatted skills in agent skill registries (SKILL.md, plugin marketplaces) | White-box |
| AG05 | Hallucinated Dependency | Non-existent packages referenced by AI-generated code, resolvable to attacker-controlled typosquats | White-box / SCA |
| AG06 | Agent Prompt Manipulation | Code constructs (comments, variable names, documentation) designed to manipulate AI security tools into suppressing or fabricating findings | Both |
