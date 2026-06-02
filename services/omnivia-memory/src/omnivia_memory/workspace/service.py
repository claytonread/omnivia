"""Workspace service and workspace-aware import orchestration."""

from __future__ import annotations

from pathlib import Path

from omnivia_memory.ingestion.pipeline import IngestionPipeline
from omnivia_memory.ingestion.repositories import ChunkRepository, SourceRepository
from omnivia_memory.lifecycle.rules import CreatedBy
from omnivia_memory.memory.models import MemoryCreate
from omnivia_memory.memory.service import MemoryService
from omnivia_memory.provenance.models import Source as ProvenanceSource
from omnivia_memory.provenance.models import SourceType
from omnivia_memory.workspace.models import (
    ImportSummary,
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
)
from omnivia_memory.workspace.repository import WorkspaceRepository


class WorkspaceServiceError(Exception):
    """Base workspace service error."""


class WorkspaceNotFoundError(WorkspaceServiceError):
    """Raised when a requested workspace does not exist."""


class WorkspaceService:
    """High-level workspace operations."""

    def __init__(
        self,
        repository: WorkspaceRepository,
        source_repository: SourceRepository,
        chunk_repository: ChunkRepository,
        memory_service: MemoryService,
        ingestion_pipeline: IngestionPipeline | None = None,
    ) -> None:
        self.repository = repository
        self.source_repository = source_repository
        self.chunk_repository = chunk_repository
        self.memory_service = memory_service
        self.ingestion_pipeline = ingestion_pipeline or IngestionPipeline(
            source_repository=source_repository,
            chunk_repository=chunk_repository,
        )

    def create(self, input_data: WorkspaceCreate) -> Workspace:
        """Create a workspace."""
        workspace = input_data.to_workspace()
        return self.repository.create(workspace)

    def get(self, workspace_id: str) -> Workspace:
        """Retrieve a workspace by ID."""
        workspace = self.repository.get_by_id(workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError(f"Workspace {workspace_id} not found")
        return workspace

    def list(self, limit: int = 100, offset: int = 0) -> list[Workspace]:
        """List workspaces."""
        return self.repository.list_all(limit=limit, offset=offset)

    def update(self, workspace_id: str, input_data: WorkspaceUpdate) -> Workspace:
        """Update workspace metadata."""
        workspace = self.get(workspace_id)
        input_data.apply_to(workspace)
        return self.repository.update(workspace)

    def delete(self, workspace_id: str) -> bool:
        """Delete workspace metadata."""
        self.get(workspace_id)
        return self.repository.delete(workspace_id)

    def import_path(self, workspace_id: str, path: Path | None = None) -> ImportSummary:
        """Import a file or directory into a workspace."""
        workspace = self.get(workspace_id)
        import_path = (path or Path(workspace.root_path)).expanduser().resolve()
        if not import_path.exists():
            workspace.mark_error()
            self.repository.update(workspace)
            return ImportSummary(
                workspace_id=workspace_id,
                files_seen=0,
                sources_created=0,
                memories_created=0,
                errors=[f"Path does not exist: {import_path}"],
            )

        if import_path.is_file():
            results = [self.ingestion_pipeline.ingest_file(import_path, workspace_id=workspace_id)]
        else:
            results = self.ingestion_pipeline.ingest_directory(
                import_path,
                workspace_id=workspace_id,
            )

        sources_created = 0
        memories_created = 0
        errors: list[str] = []
        files_seen = len(results)

        for result in results:
            if result.error:
                errors.append(result.error)
                continue
            if result.source is None:
                continue
            if result.chunks:
                sources_created += 1
            for chunk in result.chunks:
                self.memory_service.create(
                    MemoryCreate(
                        content=chunk.content,
                        source=ProvenanceSource(
                            type=SourceType.FILE,
                            reference=result.source.path,
                            description=f"Workspace source {result.source.id}",
                        ),
                        memory_type="context",
                        created_by=CreatedBy.AGENT,
                        workspace_id=workspace_id,
                    )
                )
                memories_created += 1

        if errors:
            workspace.mark_error()
        else:
            workspace.mark_indexed()
        self.repository.update(workspace)

        return ImportSummary(
            workspace_id=workspace_id,
            files_seen=files_seen,
            sources_created=sources_created,
            memories_created=memories_created,
            errors=errors,
        )
