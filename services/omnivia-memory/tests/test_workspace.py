"""Tests for workspace domain and workspace-aware import."""

from pathlib import Path

import pytest

from omnivia_memory.ingestion.repositories import ChunkRepository, SourceRepository
from omnivia_memory.memory.service import MemoryService
from omnivia_memory.persistence.database import Database, DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.workspace.models import (
    WorkspaceCreate,
    WorkspaceIndexStatus,
    WorkspaceUpdate,
)
from omnivia_memory.workspace.repository import WorkspaceRepository
from omnivia_memory.workspace.service import WorkspaceNotFoundError, WorkspaceService


@pytest.fixture
def workspace_stack(tmp_path):
    """Create workspace services backed by an isolated database."""
    db = Database(DatabaseConfig(db_path=tmp_path / "workspace.db"))
    db.connect()
    memory_repository = MemoryRepository(db)
    source_repository = SourceRepository(db)
    chunk_repository = ChunkRepository(db)
    service = WorkspaceService(
        repository=WorkspaceRepository(db),
        source_repository=source_repository,
        chunk_repository=chunk_repository,
        memory_service=MemoryService(memory_repository),
    )
    yield service, source_repository, memory_repository
    db.close()


def test_workspace_crud_round_trip(workspace_stack, tmp_path):
    """Workspaces can be created, read, listed, updated, and deleted."""
    service, _, _ = workspace_stack
    root = tmp_path / "vault"
    root.mkdir()

    workspace = service.create(
        WorkspaceCreate(
            name="Research Vault",
            root_path=root,
            description="Local markdown vault",
            settings={"include_patterns": ["**/*.md"]},
        )
    )

    assert service.get(workspace.id) == workspace
    assert service.list() == [workspace]
    assert workspace.root_path == str(root.resolve())
    assert Path(workspace.storage_path).name == workspace.id

    updated = service.update(
        workspace.id,
        WorkspaceUpdate(
            name="Updated Vault",
            description="Updated description",
            settings={"include_patterns": ["**/*.md", "**/*.txt"]},
        ),
    )

    assert updated.name == "Updated Vault"
    assert updated.description == "Updated description"
    assert updated.settings == {"include_patterns": ["**/*.md", "**/*.txt"]}
    assert service.delete(workspace.id) is True

    with pytest.raises(WorkspaceNotFoundError):
        service.get(workspace.id)


def test_workspace_persistence_survives_repository_recreation(tmp_path):
    """Workspace records round-trip through SQLite."""
    db_path = tmp_path / "workspace.db"
    root = tmp_path / "vault"
    root.mkdir()

    db = Database(DatabaseConfig(db_path=db_path))
    db.connect()
    repository = WorkspaceRepository(db)
    created = repository.create(WorkspaceCreate(name="Vault", root_path=root).to_workspace())
    db.close()

    reopened = Database(DatabaseConfig(db_path=db_path))
    reopened.connect()
    try:
        retrieved = WorkspaceRepository(reopened).get_by_id(created.id)
    finally:
        reopened.close()

    assert retrieved == created


def test_workspace_import_creates_sources_memories_and_preserves_files(
    workspace_stack,
    tmp_path,
):
    """Workspace import scans markdown/text files without mutating sources."""
    service, source_repository, memory_repository = workspace_stack
    root = tmp_path / "vault"
    root.mkdir()
    markdown = root / "decision.md"
    text = root / "note.txt"
    ignored = root / "script.py"
    markdown.write_text("# Decision\n\nUse Python for the brain.\n")
    text.write_text("Plain text project note.\n")
    ignored.write_text("print('not imported')\n")
    original_markdown = markdown.read_text()
    original_text = text.read_text()

    workspace = service.create(WorkspaceCreate(name="Vault", root_path=root))
    summary = service.import_path(workspace.id)

    sources = source_repository.list_by_workspace(workspace.id)
    memories = memory_repository.get_by_workspace(workspace.id)
    refreshed = service.get(workspace.id)

    assert summary.files_seen == 2
    assert summary.sources_created == 2
    assert summary.memories_created >= 2
    assert summary.errors == []
    assert {Path(source.path).name for source in sources} == {"decision.md", "note.txt"}
    memory_contents = {memory.content.strip() for memory in memories}
    assert "Use Python for the brain." in memory_contents
    assert "Plain text project note." in memory_contents
    assert {memory.workspace_id for memory in memories} == {workspace.id}
    assert markdown.read_text() == original_markdown
    assert text.read_text() == original_text
    assert ignored.read_text() == "print('not imported')\n"
    assert refreshed.index_status == WorkspaceIndexStatus.INDEXED


def test_workspace_import_missing_path_reports_error(workspace_stack, tmp_path):
    """Missing import paths return an error summary and mark workspace error."""
    service, _, _ = workspace_stack
    root = tmp_path / "vault"
    root.mkdir()
    workspace = service.create(WorkspaceCreate(name="Vault", root_path=root))

    summary = service.import_path(workspace.id, tmp_path / "missing")

    assert summary.files_seen == 0
    assert summary.sources_created == 0
    assert summary.memories_created == 0
    assert "Path does not exist" in summary.errors[0]
    assert service.get(workspace.id).index_status == WorkspaceIndexStatus.ERROR


def test_same_source_path_can_belong_to_different_workspaces(workspace_stack, tmp_path):
    """Workspace scoping allows the same local source path in separate workspaces."""
    service, source_repository, _ = workspace_stack
    root = tmp_path / "vault"
    root.mkdir()
    (root / "note.md").write_text("Shared folder content.\n")
    workspace_a = service.create(WorkspaceCreate(name="Vault A", root_path=root))
    workspace_b = service.create(WorkspaceCreate(name="Vault B", root_path=root))

    service.import_path(workspace_a.id)
    service.import_path(workspace_b.id)

    assert len(source_repository.list_by_workspace(workspace_a.id)) == 1
    assert len(source_repository.list_by_workspace(workspace_b.id)) == 1
