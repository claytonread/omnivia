"""Workspace repository for SQLite persistence."""

from __future__ import annotations

import json
from typing import Any

from omnivia_memory.persistence.database import Database
from omnivia_memory.workspace.models import Workspace, WorkspaceIndexStatus


class WorkspaceRepository:
    """Repository for local workspace metadata."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def create(self, workspace: Workspace) -> Workspace:
        """Persist a new workspace."""
        if self.get_by_id(workspace.id) is not None:
            raise ValueError(f"Workspace with ID {workspace.id} already exists")

        self.db.execute(
            """
            INSERT INTO workspaces (
                id, name, root_path, storage_path, description, index_status,
                settings_json, created_at, updated_at, last_indexed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workspace.id,
                workspace.name,
                workspace.root_path,
                workspace.storage_path,
                workspace.description,
                workspace.index_status.value,
                json.dumps(workspace.settings),
                workspace.created_at,
                workspace.updated_at,
                workspace.last_indexed_at,
            ),
        )
        return workspace

    def get_by_id(self, workspace_id: str) -> Workspace | None:
        """Retrieve a workspace by ID."""
        cursor = self.db.execute("SELECT * FROM workspaces WHERE id = ?", (workspace_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_workspace(row)

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Workspace]:
        """List workspaces ordered by creation time."""
        cursor = self.db.execute(
            """
            SELECT * FROM workspaces
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        return [self._row_to_workspace(row) for row in cursor.fetchall()]

    def update(self, workspace: Workspace) -> Workspace:
        """Update an existing workspace."""
        if self.get_by_id(workspace.id) is None:
            raise ValueError(f"Workspace with ID {workspace.id} not found")

        self.db.execute(
            """
            UPDATE workspaces SET
                name = ?,
                root_path = ?,
                storage_path = ?,
                description = ?,
                index_status = ?,
                settings_json = ?,
                updated_at = ?,
                last_indexed_at = ?
            WHERE id = ?
            """,
            (
                workspace.name,
                workspace.root_path,
                workspace.storage_path,
                workspace.description,
                workspace.index_status.value,
                json.dumps(workspace.settings),
                workspace.updated_at,
                workspace.last_indexed_at,
                workspace.id,
            ),
        )
        return workspace

    def delete(self, workspace_id: str) -> bool:
        """Delete workspace metadata."""
        cursor = self.db.execute("DELETE FROM workspaces WHERE id = ?", (workspace_id,))
        return bool(cursor.rowcount)

    def _row_to_workspace(self, row: Any) -> Workspace:
        """Convert a SQLite row to a workspace."""
        return Workspace(
            id=row["id"],
            name=row["name"],
            root_path=row["root_path"],
            storage_path=row["storage_path"],
            description=row["description"],
            index_status=WorkspaceIndexStatus(row["index_status"]),
            settings=json.loads(row["settings_json"] or "{}"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_indexed_at=row["last_indexed_at"],
        )
