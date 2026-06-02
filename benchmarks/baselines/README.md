# Benchmark Baselines

This directory stores baseline benchmark results for performance regression tracking.

Baseline capture, variance, promotion, and CI gate rules are defined in
[`GOVERNANCE.md`](GOVERNANCE.md).

## Purpose

Baseline files enable the benchmark comparison tool (`benchmark_compare`) to detect performance regressions by comparing new runs against established performance characteristics.

## Storage Format

Baseline files are named following the pattern:
```
baseline_{profile}_{timestamp}.json
```

Example: `baseline_tiny_20240101_120000.json`

## Creating a Baseline

### Option 1: Run benchmarks and promote to baseline

```bash
# Run benchmarks
scripts/run-core-benchmarks.sh --profile tiny

# Use the generated file as a baseline
python -m benchmarks.runner.benchmark_compare \
    --latest benchmarks/reports/benchmark_tiny_20240101.json \
    --set-baseline
```

### Option 2: Copy an existing report

```bash
cp benchmarks/reports/benchmark_tiny_20240101.json benchmarks/baselines/
```

## Baseline Management

### View Baseline Info

```bash
# List all baselines
ls -la benchmarks/baselines/

# View baseline contents
cat benchmarks/baselines/baseline_tiny_*.json | jq .
```

### Update a Baseline

When performance legitimately improves, update the baseline:

```bash
# Run new benchmarks
scripts/run-core-benchmarks.sh --profile tiny

# Set new baseline
python -m benchmarks.runner.benchmark_compare \
    --latest benchmarks/reports/benchmark_tiny_latest.json \
    --set-baseline
```

### Delete a Baseline

```bash
rm benchmarks/baselines/baseline_tiny_old.json
```

## Baseline Profiles

Store separate baselines for different profiles:

| Profile | Typical Use |
|---------|-------------|
| tiny | Quick validation |
| small | Development checks |
| medium | CI/CD validation |

Keep at least one baseline per profile you regularly test.

## CI/CD Integration

In continuous integration, compare against stored baselines:

```bash
# Run benchmarks with the local Core source pinned on PYTHONPATH
scripts/run-core-benchmarks.sh --profile tiny

# Compare against baseline
python -m benchmarks.runner.benchmark_compare --profile tiny

# Exit code 2 indicates failure
if [ $? -eq 2 ]; then
    echo "Performance regression detected!"
    exit 1
fi
```

For local preflight checks, prefer the repository helper:

```bash
scripts/check-core-performance.sh
```

The helper runs the tiny profile, compares against the latest tiny baseline,
and keeps generated reports in `benchmarks/reports`. Use it before promoting a
new baseline so regressions are visible before baseline churn.

## Best Practices

1. **Establish baselines on reference hardware** for meaningful comparisons
2. **Update baselines when intentionally optimizing** to avoid false failures
3. **Keep baseline environment info** in version control for reproducibility
4. **Use versioned baselines** when significant API changes occur
5. **Do not replace baselines after a single failing local run**; follow the
   governance checklist first.
