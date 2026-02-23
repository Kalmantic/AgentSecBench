# Creating Benchmark Test Cases from Vulnerable Agents

You have a vulnerable agent. Here's how to turn it into an AgentSecBench test case.

## Step 1: Identify the Vulnerability Class

Map your vulnerability to the AG taxonomy or OWASP Agentic Top 10:

| AG ID | Category | OWASP Agentic | ATLAS Technique |
|-------|----------|---------------|-----------------|
| AG01 | Client-Side Secret Exposure | ASI03 | AML.T0055, AML.T0083 |
| AG02 | Source Map Leakage | ASI03 | AML.T0000, CWE-312 |
| AG03 | MCP Tool Injection | ASI02, ASI04 | AML.T0053, AML.T0099 |
| AG04 | Skill Registry Poisoning | ASI04 | AML.T0053, AML.T0058 |
| AG05 | Hallucinated Dependency | ASI04, ASI05 | AML.T0060, AML.T0062 |
| AG06 | Agent Prompt Manipulation | ASI01, ASI06 | AML.T0051, AML.T0080 |

If your vulnerability doesn't fit AG01-AG06, consider proposing a new category (see CONTRIBUTING.md).

## Step 2: Isolate the Vulnerable Component

Extract the minimum code that reproduces the vulnerability into a standalone application:

- Use one of the supported frameworks (Next.js, Nuxt, SvelteKit, React/Vite, Angular)
- Keep it minimal: only include code necessary to demonstrate the vulnerability
- Ensure it builds and runs independently
- Include both a development server and a production build

```
benchmark/apps/your-app-name/
  src/           # Minimal source code
  package.json   # Dependencies
  deploy/        # Production build output (run `npm run build` and copy output here)
    url.txt      # For black-box testing: the URL where the app will be served
```

## Step 3: Write the Ground Truth Manifest

Create `ground-truth.yaml` in your app directory:

```yaml
app: nextjs-mcp-injection-001
framework: next.js@15.2
description: >
  Next.js application with MCP server that includes a malicious tool
  exfiltrating conversation context to an external endpoint.

vulnerabilities:
  - id: VULN-001
    type: AG03
    subtype: mcp-tool-injection
    severity: critical
    atlas_technique: AML.T0053
    owasp_agentic: ASI02
    location:
      source: src/mcp/tools/data-export.ts:22
      bundle: null  # Not applicable for server-side MCP
      endpoint: null
    description: >
      MCP tool "export_data" sends full conversation context
      to https://attacker.example.com/collect via POST request
      when invoked by the agent.
    detection_perspective:
      - white_box    # Visible in tool source code
    correct_fix: |
      Remove the external HTTP call. If export functionality is needed,
      restrict to approved internal endpoints with allowlist validation.
```

Key fields:
- `atlas_technique`: The MITRE ATLAS technique ID (required)
- `owasp_agentic`: The OWASP Agentic Top 10 ID (required)
- `detection_perspective`: Which tool types can detect this (white_box, black_box, or both)

## Step 4: Validate Exploitability

Before submitting:

1. **Manual verification**: Confirm the vulnerability is exploitable by manually triggering it
2. **Tool verification**: Run at least one existing tool (Semgrep, SPA Hacking Agent, etc.) against the app and note whether it detects the vulnerability
3. **Document the attack path**: Write a brief proof-of-concept showing how an attacker would exploit this

## Step 5: Submit

1. Fork the AgentSecBench repository
2. Add your app under `benchmark/apps/{framework}-{vuln-type}-{number}/`
3. Include all files: source, build output, ground-truth.yaml
4. Open a pull request with:
   - Description of the vulnerability
   - Which AG category it falls under
   - Which tools you tested it against (and results)
   - The ATLAS technique and OWASP Agentic mapping

## Examples

### From Akash's Vulnerable Agent (Appsecco)

If you have an agent with implemented attacks (e.g., prompt injection, tool misuse), the conversion process is:

1. Take each attack scenario from your vulnerable agent
2. Create a standalone app that demonstrates the attack surface
3. Document which security tools should be able to detect it
4. Write the ground truth with ATLAS and OWASP mappings

This turns your attack research directly into benchmark test cases that the community can use to evaluate security tools.
