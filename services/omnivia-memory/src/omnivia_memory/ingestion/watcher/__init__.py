"""File watcher / indexer module.

Provides components for watching file system changes and triggering
re-indexing of modified content.

Core provides interfaces and pure models. Platform-specific file system
watching (using watchdog, watchfiles, FSEvents, etc.) is deferred to
consuming applications.
"""

from omnivia_memory.ingestion.watcher.debouncer import Debouncer
from omnivia_memory.ingestion.watcher.models import (
    DebounceConfig,
    FileChange,
    FileChangeBatch,
    FileChangeType,
    IndexerScheduler,
    IndexerState,
    IndexerStatus,
    ScheduledJob,
    SourceReference,
    WatchedPath,
)
from omnivia_memory.ingestion.watcher.tracker import SourceTracker

__all__ = [
    "Debouncer",
    "DebounceConfig",
    "FileChange",
    "FileChangeBatch",
    "FileChangeType",
    "IndexerScheduler",
    "IndexerState",
    "IndexerStatus",
    "ScheduledJob",
    "SourceReference",
    "SourceTracker",
    "WatchedPath",
]