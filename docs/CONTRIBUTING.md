# Contributing to AgentSecBench

## Adding Test Applications

1. Create a directory under `benchmark/apps/{framework}-{vuln-type}-{number}/`
2. Include `src/` with the vulnerable application source
3. Include `ground-truth.yaml` following the schema in existing examples
4. Each vulnerability must be documented with type, severity, location (source + bundle + endpoint), detection perspective, and correct fix

## Adding Tool Runners

1. Create `benchmark/runners/{tool}_runner.py`
2. Extend `BaseRunner` from `benchmark/runners/base.py`
3. Implement `run()` and `normalize()` methods
4. Add to the `RUNNERS` dict in `benchmark/run.py`

## Proposing New Vulnerability Categories

To propose AG07+:
1. Open an issue with the category name, description, and detection perspective
2. Include at least one concrete example of the vulnerability in a modern framework
3. Explain why existing categories (OWASP + AG01-AG06) don't cover it

## Submitting Benchmark Results

1. Run the benchmark with default configuration
2. Include the full SARIF output and scorecard
3. Open a PR adding results to `results/{tool-name}/`
