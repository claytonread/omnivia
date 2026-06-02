"""Tests for the package-level public API."""

import omnivia_memory
from omnivia_memory import (
    CreatedBy,
    LifecycleState,
    Memory,
    MemoryCreate,
    MemoryService,
    Source,
    SourceType,
    Workspace,
)


def test_top_level_exports_core_primitives() -> None:
    """Common core primitives are importable from the package root."""
    source = Source(type=SourceType.HUMAN, reference="direct")
    memory = MemoryCreate(
        content="Package root import smoke test",
        source=source,
        created_by=CreatedBy.HUMAN,
    ).to_memory()

    assert isinstance(memory, Memory)
    assert memory.lifecycle_state == LifecycleState.APPROVED
    assert MemoryService is omnivia_memory.MemoryService

    workspace = Workspace(
        name="Example",
        root_path="/tmp/example",
        storage_path="/tmp/example/.omnivia",
    )
    assert workspace.name == "Example"


def test_all_declares_public_root_api() -> None:
    """__all__ records the intentional package root API."""
    expected = {
        "CreatedBy",
        "Database",
        "Entity",
        "FileScanner",
        "GraphService",
        "GraphSearchService",
        "IngestionPipeline",
        "LifecycleState",
        "Memory",
        "MemoryCreate",
        "MemoryRepository",
        "MemoryService",
        "SearchService",
        "Source",
        "SourceType",
        "Workspace",
        "WorkspaceRepository",
        "WorkspaceService",
        "get_database",
    }

    assert expected.issubset(set(omnivia_memory.__all__))
