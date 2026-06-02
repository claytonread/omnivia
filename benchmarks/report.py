"""Report generation and export utilities.

Provides functionality to export benchmark results in various formats
(JSON, Markdown, CSV) and generate human-readable reports.
"""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from typing import Any

from benchmarks.schema import BenchmarkRun, ComparisonResult


def export_json(result: BenchmarkRun | ComparisonResult) -> str:
    """Export result to JSON format.

    Args:
        result: BenchmarkRun or ComparisonResult to export

    Returns:
        JSON string
    """
    return json.dumps(result.to_dict(), indent=2)


def export_json_file(result: BenchmarkRun | ComparisonResult, path: str | Path) -> None:
    """Export result to JSON file.

    Args:
        result: BenchmarkRun or ComparisonResult to export
        path: Output file path
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(export_json(result))


def export_markdown(result: BenchmarkRun | ComparisonResult) -> str:
    """Export result to Markdown format.

    Args:
        result: BenchmarkRun or ComparisonResult to export

    Returns:
        Markdown string
    """
    if isinstance(result, ComparisonResult):
        return _export_comparison_markdown(result)
    else:
        return _export_run_markdown(result)


def _export_run_markdown(run: BenchmarkRun) -> str:
    """Export a benchmark run to Markdown format."""
    lines = [
        f"# Benchmark Run: {run.profile}",
        "",
        f"**Run ID:** `{run.run_id}`",
        f"**Timestamp:** {run.timestamp}",
        "",
        "## Environment",
        "",
        f"- OS: {run.environment.os}",
        f"- Python: {run.environment.python_version}",
        f"- Node: {run.environment.node_version or 'N/A'}",
        f"- CPU: {run.environment.cpu}",
        "",
        "## Results",
        "",
        "| Scenario | Operations | Mean (ms) | P95 (ms) | P99 (ms) | Ops/sec | Status |",
        "|:---------|-----------:|----------:|---------:|---------:|--------:|:-------|",
    ]

    for scenario in run.scenarios:
        lines.append(
            f"| {scenario.name} | {scenario.operation_count:,} | "
            f"{scenario.mean_latency_ms:.3f} | {scenario.p95_latency_ms:.3f} | "
            f"{scenario.p99_latency_ms:.3f} | "
            f"{scenario.throughput_ops_per_second:,.1f} | {scenario.status} |"
        )

    total_ms = float(run.comparison.get("total_duration_ms", 0))
    lines.extend(["", f"**Total Duration:** {total_ms / 1000:.2f}s", ""])

    return "\n".join(lines)


def _export_comparison_markdown(comparison: ComparisonResult) -> str:
    """Export a comparison result to Markdown format."""
    lines = [
        f"# Benchmark Comparison: {comparison.profile}",
        "",
        f"**Timestamp:** {comparison.timestamp}",
        "",
        "## Runs",
        "",
        f"- **Baseline:** `{comparison.baseline_run.run_id}` "
        f"({comparison.baseline_run.timestamp[:10]})",
        f"- **Latest:** `{comparison.latest_run.run_id}` "
        f"({comparison.latest_run.timestamp[:10]})",
        "",
        "## Results",
        "",
        "| Scenario | Metric | Baseline | Latest | Change | Status |",
        "|:---------|:-------|---------:|-------:|-------:|:-------|",
    ]

    for comp in comparison.comparisons:
        sign = "+" if comp.percentage_change >= 0 else ""
        status_icon = {"pass": "✓", "warning": "⚠", "fail": "✗"}.get(
            comp.status, "?"
        )
        lines.append(
            f"| {comp.scenario_name} | {comp.metric} | {comp.baseline_value:,.3f} | "
            f"{comp.latest_value:,.3f} | "
            f"{sign}{comp.percentage_change:.1f}% | {status_icon} {comp.status} |"
        )

    lines.append("")

    return "\n".join(lines)


def export_markdown_file(
    result: BenchmarkRun | ComparisonResult, path: str | Path
) -> None:
    """Export result to Markdown file.

    Args:
        result: BenchmarkRun or ComparisonResult to export
        path: Output file path
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(export_markdown(result))


def export_csv(result: BenchmarkRun) -> str:
    """Export benchmark run results to CSV format.

    Args:
        result: BenchmarkRun to export

    Returns:
        CSV string
    """
    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(
        [
            "scenario_name",
            "profile",
            "status",
            "operation_count",
            "total_duration_ms",
            "mean_latency_ms",
            "median_latency_ms",
            "p95_latency_ms",
            "p99_latency_ms",
            "throughput_ops_per_second",
            "memory_peak_mb",
            "database_size_mb",
            "error_count",
            "warnings",
        ]
    )

    # Data rows
    for scenario in result.scenarios:
        writer.writerow(
            [
                scenario.name,
                scenario.profile,
                scenario.status,
                scenario.operation_count,
                scenario.total_duration_ms,
                scenario.mean_latency_ms,
                scenario.median_latency_ms,
                scenario.p95_latency_ms,
                scenario.p99_latency_ms,
                scenario.throughput_ops_per_second,
                scenario.memory_peak_mb or "",
                scenario.database_size_mb or "",
                scenario.error_count,
                "; ".join(scenario.warnings),
            ]
        )

    return output.getvalue()


def export_csv_file(result: BenchmarkRun, path: str | Path) -> None:
    """Export benchmark run results to CSV file.

    Args:
        result: BenchmarkRun to export
        path: Output file path
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(export_csv(result))


def generate_summary(result: BenchmarkRun | ComparisonResult) -> dict[str, Any]:
    """Generate a summary dictionary from a result.

    Args:
        result: BenchmarkRun or ComparisonResult

    Returns:
        Summary dictionary with key metrics
    """
    if isinstance(result, ComparisonResult):
        return {
            "type": "comparison",
            "profile": result.profile,
            "baseline_run_id": result.baseline_run.run_id,
            "latest_run_id": result.latest_run.run_id,
            "scenario_count": len(result.comparisons),
            "timestamp": result.timestamp,
        }
    else:
        return {
            "type": "run",
            "profile": result.profile,
            "run_id": result.run_id,
            "scenario_count": len(result.scenarios),
            "total_duration_ms": result.comparison.get("total_duration_ms", 0),
            "timestamp": result.timestamp,
        }
