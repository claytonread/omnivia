"""Scenario registry for benchmark scenarios.

Manages registration and discovery of benchmark scenarios. Scenarios are
registered via decorator for easy discovery and execution.
"""

from __future__ import annotations

import builtins
from dataclasses import dataclass, field
from typing import Any, Callable


# Scenario function signature:
# def scenario_fn(db_path: str, item_count: int, **kwargs) -> dict[str, Any]
ScenarioFunc = Callable[[str, int], dict[str, Any]]


@dataclass
class ScenarioInfo:
    """Information about a registered benchmark scenario."""

    name: str
    description: str
    func: ScenarioFunc
    tags: builtins.list[str] = field(default_factory=list)
    estimated_time_per_item_ms: float = 0.1  # Rough estimate for planning


class ScenarioRegistry:
    """Registry for benchmark scenarios.

    Scenarios are registered using the @scenario decorator and can be
    discovered by name, tag, or iterated over.
    """

    def __init__(self) -> None:
        self._scenarios: dict[str, ScenarioInfo] = {}

    def register(
        self,
        name: str,
        description: str,
        tags: builtins.list[str] | None = None,
        estimated_time_per_item_ms: float = 0.1,
    ) -> Callable[[ScenarioFunc], ScenarioFunc]:
        """Decorator to register a benchmark scenario.

        Args:
            name: Unique scenario name
            description: Human-readable description
            tags: Optional tags for categorization
            estimated_time_per_item_ms: Estimated time per item in milliseconds

        Returns:
            Decorator function
        """

        def decorator(func: ScenarioFunc) -> ScenarioFunc:
            info = ScenarioInfo(
                name=name,
                description=description,
                func=func,
                tags=tags or [],
                estimated_time_per_item_ms=estimated_time_per_item_ms,
            )
            self._scenarios[name] = info
            return func

        return decorator

    def get(self, name: str) -> ScenarioInfo | None:
        """Get a scenario by name.

        Args:
            name: Scenario name

        Returns:
            ScenarioInfo or None if not found
        """
        return self._scenarios.get(name)

    def list(self) -> builtins.list[ScenarioInfo]:
        """List all registered scenarios.

        Returns:
            List of all ScenarioInfo objects
        """
        return list(self._scenarios.values())

    def list_by_tag(self, tag: str) -> builtins.list[ScenarioInfo]:
        """List scenarios filtered by tag.

        Args:
            tag: Tag to filter by

        Returns:
            List of matching ScenarioInfo objects
        """
        return [s for s in self._scenarios.values() if tag in s.tags]

    def names(self) -> builtins.list[str]:
        """Get names of all registered scenarios.

        Returns:
            List of scenario names
        """
        return list(self._scenarios.keys())

    def __contains__(self, name: str) -> bool:
        """Check if a scenario is registered."""
        return name in self._scenarios


# Global registry instance
registry = ScenarioRegistry()


def scenario(
    name: str,
    description: str,
    tags: builtins.list[str] | None = None,
    estimated_time_per_item_ms: float = 0.1,
) -> Callable[[ScenarioFunc], ScenarioFunc]:
    """Decorator to register a benchmark scenario.

    Usage:
        @scenario("my_scenario", "Description of the scenario")
        def my_scenario(db_path: str, item_count: int) -> dict[str, Any]:
            # Benchmark code here
            return {"result": value}
    """
    return registry.register(
        name=name,
        description=description,
        tags=tags,
        estimated_time_per_item_ms=estimated_time_per_item_ms,
    )


def get_registry() -> ScenarioRegistry:
    """Get the global scenario registry.

    Returns:
        The global ScenarioRegistry instance
    """
    return registry
