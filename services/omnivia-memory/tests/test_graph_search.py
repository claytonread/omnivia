"""Focused coverage for graph search and traversal repositories."""

import tempfile
from pathlib import Path

import pytest

# Import memory first to resolve circular import chain
from omnivia_memory.memory.models import Memory  # noqa: F401
from omnivia_memory.memory.service import MemoryService  # noqa: F401

from omnivia_memory.graph.models import (
    ApprovalStatus,
    Entity,
    EntityType,
    Relationship,
    RelationshipType,
)
from omnivia_memory.graph.repository import EntityRepository, RelationshipRepository
from omnivia_memory.graph.search_service import GraphSearchError, GraphSearchService
from omnivia_memory.persistence.database import Database, DatabaseConfig


@pytest.fixture
def temp_db():
    """Create an isolated SQLite database for graph search tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(DatabaseConfig(db_path=db_path))
        db.connect()
        yield db
        db.close()


@pytest.fixture
def entity_repo(temp_db):
    """Create an entity repository."""
    return EntityRepository(temp_db)


@pytest.fixture
def relationship_repo(temp_db):
    """Create a relationship repository."""
    return RelationshipRepository(temp_db)


@pytest.fixture
def search_service(entity_repo, relationship_repo):
    """Create a graph search service."""
    return GraphSearchService(entity_repo, relationship_repo)


@pytest.fixture
def approved_graph(entity_repo, relationship_repo):
    """Create a small approved graph for traversal and search."""
    alice = entity_repo.create(
        Entity(
            id="alice-id",
            name="Alice Smith",
            entity_type=EntityType.PERSON,
            approval_status=ApprovalStatus.APPROVED,
            source_id="source-people",
        )
    )
    auth_service = entity_repo.create(
        Entity(
            id="auth-id",
            name="AuthService",
            entity_type=EntityType.SYSTEM,
            approval_status=ApprovalStatus.APPROVED,
            source_id="source-systems",
        )
    )
    roadmap = entity_repo.create(
        Entity(
            id="roadmap-id",
            name="Roadmap",
            entity_type=EntityType.DOCUMENT,
            approval_status=ApprovalStatus.APPROVED,
            source_id="source-docs",
        )
    )
    proposed = entity_repo.create(
        Entity(
            id="draft-id",
            name="DraftSecret",
            entity_type=EntityType.CONCEPT,
            approval_status=ApprovalStatus.PROPOSED,
        )
    )

    alice_uses_auth = relationship_repo.create(
        Relationship(
            id="rel-alice-auth",
            source_entity_id=alice.id,
            target_entity_id=auth_service.id,
            relationship_type=RelationshipType.USES,
            approval_status=ApprovalStatus.APPROVED,
        )
    )
    roadmap_mentions_auth = relationship_repo.create(
        Relationship(
            id="rel-roadmap-auth",
            source_entity_id=roadmap.id,
            target_entity_id=auth_service.id,
            relationship_type=RelationshipType.RELATES_TO,
            approval_status=ApprovalStatus.APPROVED,
        )
    )

    return {
        "alice": alice,
        "auth_service": auth_service,
        "roadmap": roadmap,
        "proposed": proposed,
        "alice_uses_auth": alice_uses_auth,
        "roadmap_mentions_auth": roadmap_mentions_auth,
    }


def test_search_entities_matches_names_and_filters_to_approved(search_service, approved_graph):
    """Keyword entity search returns approved matches only."""
    results = search_service.search_entities("Secret")
    assert results == []

    results = search_service.search_entities("Alice")
    assert [entity.id for entity in results] == [approved_graph["alice"].id]


def test_search_entities_filters_by_entity_type(search_service, approved_graph):
    """Keyword search can be restricted to entity types."""
    results = search_service.search_entities(
        "Road",
        entity_types=[EntityType.DOCUMENT],
    )

    assert [entity.id for entity in results] == [approved_graph["roadmap"].id]


def test_search_with_context_includes_connected_entities(search_service, approved_graph):
    """Context search carries the graph neighborhood for a matching entity."""
    result_set = search_service.search_with_context("Alice", depth=1)

    alice_result = next(result for result in result_set.results if result.entity.id == "alice-id")
    assert [entity.id for entity in alice_result.context_entities] == [
        approved_graph["auth_service"].id
    ]


def test_search_with_context_requires_entity_repository():
    """Context search fails clearly when repositories are not configured."""
    with pytest.raises(GraphSearchError, match="Entity repository not configured"):
        GraphSearchService().search_with_context("Alice")


def test_get_entity_context_traverses_outgoing_and_incoming_neighbors(
    search_service, approved_graph
):
    """Entity context exposes both incoming and outgoing neighbor entities."""
    context = search_service.get_entity_context(approved_graph["auth_service"].id)

    central_entity, neighbors = context[0]
    assert central_entity.id == approved_graph["auth_service"].id
    assert {entity.id for entity in neighbors} == {
        approved_graph["alice"].id,
        approved_graph["roadmap"].id,
    }


def test_get_entity_context_rejects_unknown_entity(search_service):
    """Unknown entity context requests fail clearly."""
    with pytest.raises(GraphSearchError, match="Entity missing-id not found"):
        search_service.get_entity_context("missing-id")


def test_get_neighbors_returns_neighbor_entities_not_relationship_rows(
    relationship_repo, approved_graph
):
    """Joined neighbor queries must not map relationship IDs into entities."""
    neighbors = relationship_repo.get_neighbors(approved_graph["alice"].id)

    assert [(entity.id, relationship.id) for entity, relationship in neighbors] == [
        (approved_graph["auth_service"].id, approved_graph["alice_uses_auth"].id)
    ]


def test_relationship_traversal_helpers_filter_by_direction_and_type(
    relationship_repo, approved_graph
):
    """Traversal helpers return the expected relationship sets."""
    assert {rel.id for rel in relationship_repo.get_outgoing(approved_graph["alice"].id)} == {
        approved_graph["alice_uses_auth"].id
    }
    assert {
        rel.id for rel in relationship_repo.get_incoming(approved_graph["auth_service"].id)
    } == {
        approved_graph["roadmap_mentions_auth"].id,
        approved_graph["alice_uses_auth"].id,
    }
    assert {
        rel.id
        for rel in relationship_repo.get_by_type(
            approved_graph["auth_service"].id,
            RelationshipType.USES,
        )
    } == {approved_graph["alice_uses_auth"].id}


def test_link_to_memory_is_idempotent(relationship_repo, approved_graph):
    """Entity-memory provenance links are created once per entity and memory."""
    assert relationship_repo.link_to_memory(
        entity_id=approved_graph["alice"].id,
        memory_id="memory-1",
        source_id="source-1",
    )
    assert not relationship_repo.link_to_memory(
        entity_id=approved_graph["alice"].id,
        memory_id="memory-1",
        source_id="source-1",
    )
