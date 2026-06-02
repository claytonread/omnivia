"""Benchmarks package initialization."""

from benchmarks.dataset import PROFILE_SIZES, get_item_count, iter_profiles
from benchmarks.registry import get_registry, registry, scenario
from benchmarks.report import (
    export_csv,
    export_csv_file,
    export_json,
    export_json_file,
    export_markdown,
    export_markdown_file,
    generate_summary,
)
from benchmarks.schema import (
    BenchmarkRun,
    ComparisonResult,
    EnvironmentInfo,
    ScenarioComparison,
    ScenarioResult,
)
from benchmarks.thresholds import (
    DEFAULT_FAIL_THRESHOLD,
    DEFAULT_WARNING_THRESHOLD,
    ThresholdConfig,
    calculate_percentage_change,
    compare_runs,
    compare_scenario_results,
    determine_status,
    format_comparison_summary,
    get_summary_status,
)

__version__ = "0.1.0"

__all__ = [
    # Dataset
    "PROFILE_SIZES",
    "get_item_count",
    "iter_profiles",
    # Registry
    "registry",
    "scenario",
    "get_registry",
    # Schema
    "BenchmarkRun",
    "ComparisonResult",
    "EnvironmentInfo",
    "ScenarioComparison",
    "ScenarioResult",
    # Thresholds
    "DEFAULT_FAIL_THRESHOLD",
    "DEFAULT_WARNING_THRESHOLD",
    "ThresholdConfig",
    "calculate_percentage_change",
    "compare_runs",
    "compare_scenario_results",
    "determine_status",
    "format_comparison_summary",
    "get_summary_status",
    # Report
    "export_csv",
    "export_csv_file",
    "export_json",
    "export_json_file",
    "export_markdown",
    "export_markdown_file",
    "generate_summary",
    # Version
    "__version__",
]