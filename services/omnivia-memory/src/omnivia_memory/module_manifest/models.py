"""Module Manifest data models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ModuleKind(Enum):
    """Module kinds supported by OmniVia."""

    APPS = "apps"
    DEV = "dev"
    PRO = "pro"


@dataclass(frozen=True)
class Entrypoint:
    """Entrypoint metadata for a Module."""

    module: str
    class_name: str = "Module"
    config_key: str = ""


@dataclass(frozen=True)
class Permission:
    """Permission requested by a Module."""

    name: str
    description: str = ""


@dataclass(frozen=True)
class Integrity:
    """Integrity metadata for signature/hash verification."""

    algorithm: str
    digest: str
    signature: str = ""


@dataclass
class ModuleManifest:
    """Manifest definition for an installable Module.

    Attributes:
        manifest_version: Semantic version of the manifest schema (e.g., "1.0.0").
        module_id: Unique identifier for the Module (e.g., "com.omnivia.apps").
        display_name: Human-readable name shown in the UI.
        kind: Module kind (apps, dev, or pro).
        version: Semantic version of the Module (e.g., "1.0.0").
        compatible_core_versions: Version range strings for compatible Core releases.
        compatible_platform_versions: Version range strings for compatible Platform releases.
        entrypoint: Entrypoint metadata for the Harness.
        permissions: List of permissions requested by the Module.
        integrity: Integrity metadata for verification.
    """

    manifest_version: str
    module_id: str
    display_name: str
    kind: ModuleKind
    version: str
    compatible_core_versions: List[str] = field(default_factory=list)
    compatible_platform_versions: List[str] = field(default_factory=list)
    entrypoint: Entrypoint = field(default_factory=lambda: Entrypoint(module=""))
    permissions: List[Permission] = field(default_factory=list)
    integrity: Integrity = field(default_factory=lambda: Integrity(algorithm="sha256", digest=""))