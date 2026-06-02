"""Benchmark comparison CLI.

Provides the entry point for comparing benchmark results against baselines.
Can be executed as:
    python -m benchmarks.runner.benchmark_compare

Features:
- Compare latest run against baseline
- Configurable warning/fail thresholds
- JSON/Markdown export of comparison
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from benchmarks.report import export_json_file, export_markdown_file
from benchmarks.schema import BenchmarkRun
from benchmarks.thresholds import (
    DEFAULT_FAIL_THRESHOLD,
    DEFAULT_WARNING_THRESHOLD,
    ThresholdConfig,
    compare_runs,
    format_comparison_summary,
    get_summary_status,
)


def find_baseline(directory: Path, profile: str) -> Path | None:
    """Find the most recent baseline file for a profile.

    Args:
        directory: Directory to search
        profile: Profile name

    Returns:
        Path to baseline file or None
    """
    if not directory.exists():
        return None

    patterns = (f"baseline_{profile}_*.json", f"benchmark_{profile}_*.json")
    baseline_files = sorted(
        (path for pattern in patterns for path in directory.glob(pattern)),
        reverse=True,
    )

    if baseline_files:
        return baseline_files[0]
    return None


def find_latest(directory: Path, profile: str) -> Path | None:
    """Find the most recent benchmark run for a profile.

    Args:
        directory: Directory to search
        profile: Profile name

    Returns:
        Path to latest run file or None
    """
    if not directory.exists():
        return None

    pattern = f"benchmark_{profile}_*.json"
    files = sorted(directory.glob(pattern), reverse=True)

    # Skip baseline files (those in baselines directory)
    for f in files:
        if "baselines" not in f.parts:
            return f

    return None


def load_result(path: Path) -> BenchmarkRun:
    """Load a benchmark result from a file.

    Args:
        path: Path to JSON file

    Returns:
        BenchmarkRun object
    """
    with open(path) as f:
        data = json.load(f)
    return BenchmarkRun.from_dict(data)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Arguments to parse (defaults to sys.argv)

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Compare OmniVia Core benchmark results against baselines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--baseline",
        "-b",
        type=Path,
        help="Path to baseline benchmark JSON file",
    )
    parser.add_argument(
        "--latest",
        "-l",
        type=Path,
        help="Path to latest benchmark JSON file",
    )
    parser.add_argument(
        "--baseline-dir",
        type=Path,
        default=Path(__file__).parent.parent / "baselines",
        help="Directory to search for baseline files",
    )
    parser.add_argument(
        "--latest-dir",
        type=Path,
        default=Path(__file__).parent.parent / "reports",
        help="Directory to search for latest benchmark files",
    )
    parser.add_argument(
        "--profile",
        "-p",
        choices=["tiny", "small", "medium", "large", "stress"],
        help="Profile to compare (auto-detected if not specified)",
    )
    parser.add_argument(
        "--warning-threshold",
        type=float,
        default=DEFAULT_WARNING_THRESHOLD,
        help=f"Warning threshold percentage (default: {DEFAULT_WARNING_THRESHOLD})",
    )
    parser.add_argument(
        "--fail-threshold",
        type=float,
        default=DEFAULT_FAIL_THRESHOLD,
        help=f"Fail threshold percentage (default: {DEFAULT_FAIL_THRESHOLD})",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="Output directory for comparison results",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "markdown", "all"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress output except for final status",
    )
    parser.add_argument(
        "--set-baseline",
        action="store_true",
        help="Save latest run as new baseline and exit",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return a non-zero exit code when comparison status is warning",
    )

    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Main entry point for benchmark comparison.

    Args:
        args: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for error, 2 for comparison failure)
    """
    parsed = parse_args(args)

    # Determine file paths
    baseline_path = parsed.baseline
    latest_path = parsed.latest

    # Auto-detect profile
    profile = parsed.profile

    # Handle set-baseline mode
    if parsed.set_baseline:
        if latest_path is None:
            print("Error: --set-baseline requires --latest to be specified")
            return 1

        run = load_result(latest_path)
        profile = run.profile

        baseline_dir = Path(__file__).parent.parent / "baselines"
        baseline_dir.mkdir(parents=True, exist_ok=True)

        import shutil
        from datetime import datetime

        new_baseline_path = baseline_dir / f"baseline_{profile}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        shutil.copy(latest_path, new_baseline_path)

        if not parsed.quiet:
            print(f"Created new baseline: {new_baseline_path}")

        return 0

    # Load baseline
    if baseline_path is None:
        if profile is None:
            print("Error: Either --baseline or --profile must be specified")
            return 1

        baseline_path = find_baseline(parsed.baseline_dir, profile)
        if baseline_path is None:
            print(f"Error: No baseline found for profile '{profile}'")
            print(f"Searched in: {parsed.baseline_dir}")
            return 1
    else:
        run = load_result(baseline_path)
        profile = run.profile

    if not parsed.quiet:
        print(f"Baseline: {baseline_path}")

    try:
        baseline_run = load_result(baseline_path)
    except Exception as e:
        print(f"Error loading baseline: {e}", file=sys.stderr)
        return 1

    # Load latest
    if latest_path is None:
        latest_path = find_latest(parsed.latest_dir, profile)
        if latest_path is None:
            print(f"Error: No latest run found for profile '{profile}'")
            print(f"Searched in: {parsed.latest_dir}")
            return 1

    if not parsed.quiet:
        print(f"Latest:   {latest_path}")

    try:
        latest_run = load_result(latest_path)
    except Exception as e:
        print(f"Error loading latest run: {e}", file=sys.stderr)
        return 1

    # Ensure profiles match
    if baseline_run.profile != latest_run.profile:
        print(
            f"Warning: Profile mismatch ({baseline_run.profile} vs {latest_run.profile})"
        )

    # Compare
    config = ThresholdConfig(
        warning_threshold=parsed.warning_threshold,
        fail_threshold=parsed.fail_threshold,
    )

    comparison = compare_runs(baseline_run, latest_run, config)

    # Output results
    if not parsed.quiet:
        print()
        print(format_comparison_summary(comparison))

    # Export comparison
    if parsed.output_dir:
        parsed.output_dir.mkdir(parents=True, exist_ok=True)
        profile = latest_run.profile
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"comparison_{profile}_{timestamp}"

        if parsed.format in ("json", "all"):
            export_json_file(comparison, parsed.output_dir / f"{base_name}.json")

        if parsed.format in ("markdown", "all"):
            export_markdown_file(comparison, parsed.output_dir / f"{base_name}.md")

    # Determine exit code
    summary_status = get_summary_status(comparison.comparisons)

    if summary_status == "fail":
        return 2
    elif summary_status == "warning":
        return 3 if parsed.fail_on_warning else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
