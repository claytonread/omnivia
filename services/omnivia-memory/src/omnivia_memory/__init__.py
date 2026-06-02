"""Public OmniVia Core memory primitives.

The package root exports the stable, public-safe primitives that consumers
usually need for memory, provenance, persistence, workspaces, ingestion, graph
links, and basic search. Subpackages remain available for more focused imports.
"""

from omnivia_memory.graph import (
    ApprovalStatus,
    Entity,
    EntityType,
    GraphSearchError,
    GraphSearchQuery,
    GraphSearchResult,
    GraphSearchResultSet,
    GraphSearchService,
    Relationship,
    RelationshipType,
)
from omnivia_memory.graph.repository import EntityRepository, RelationshipRepository
from omnivia_memory.graph.service import (
    EntityNotFoundError,
    EntityValidationError,
    GraphService,
    GraphServiceError,
    RelationshipNotFoundError,
)
from omnivia_memory.ingestion import (
    BaseChunker,
    BaseExtractor,
    CharacterChunker,
    Chunk,
    ChunkConfig,
    ChunkRepository,
    DOCXExtractor,
    ExtractionResult,
    FileInfo,
    FileScanner,
    FileType,
    IngestResult,
    IngestionPipeline,
    MarkdownExtractor,
    PDFExtractor,
    ParagraphChunker,
    ParseStatus,
    ScanOptions,
)
from omnivia_memory.ingestion.extractors import TextExtractor
from omnivia_memory.lifecycle import CreatedBy, LifecycleRules, LifecycleState
from omnivia_memory.memory import (
    InvalidTransitionError,
    Memory,
    MemoryCreate,
    MemoryNotFoundError,
    MemoryService,
    MemoryServiceError,
    MemoryUpdate,
)
from omnivia_memory.persistence import Database, get_database
from omnivia_memory.persistence.database import DatabaseConfig
from omnivia_memory.persistence.repositories import MemoryRepository
from omnivia_memory.provenance import Source, SourceType
from omnivia_memory.search import SearchService
from omnivia_memory.workspace import (
    ImportSummary,
    Workspace,
    WorkspaceCreate,
    WorkspaceIndexStatus,
    WorkspaceRepository,
    WorkspaceService,
    WorkspaceUpdate,
)

__version__ = "0.1.0"

__all__ = [
    "ApprovalStatus",
    "BaseChunker",
    "BaseExtractor",
    "CharacterChunker",
    "Chunk",
    "ChunkConfig",
    "ChunkRepository",
    "CreatedBy",
    "DOCXExtractor",
    "Database",
    "DatabaseConfig",
    "Entity",
    "EntityNotFoundError",
    "EntityRepository",
    "EntityType",
    "EntityValidationError",
    "ExtractionResult",
    "FileInfo",
    "FileScanner",
    "FileType",
    "GraphService",
    "GraphServiceError",
    "GraphSearchError",
    "GraphSearchQuery",
    "GraphSearchResult",
    "GraphSearchResultSet",
    "GraphSearchService",
    "ImportSummary",
    "IngestResult",
    "IngestionPipeline",
    "InvalidTransitionError",
    "LifecycleRules",
    "LifecycleState",
    "MarkdownExtractor",
    "Memory",
    "MemoryCreate",
    "MemoryNotFoundError",
    "MemoryRepository",
    "MemoryService",
    "MemoryServiceError",
    "MemoryUpdate",
    "PDFExtractor",
    "ParagraphChunker",
    "ParseStatus",
    "Relationship",
    "RelationshipNotFoundError",
    "RelationshipRepository",
    "RelationshipType",
    "ScanOptions",
    "SearchService",
    "Source",
    "SourceType",
    "TextExtractor",
    "Workspace",
    "WorkspaceCreate",
    "WorkspaceIndexStatus",
    "WorkspaceRepository",
    "WorkspaceService",
    "WorkspaceUpdate",
    "__version__",
    "get_database",
]
