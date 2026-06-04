from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ComponentFamily(Enum):
    """Component family/classification."""
    UI = "ui"
    DATA = "data"
    LOGIC = "logic"
    INTEGRATION = "integration"
    UTILITY = "utility"


class ProvenanceBehavior(Enum):
    """How the Component handles source/provenance data."""
    PASSTHROUGH = "passthrough"
    TRACK = "track"
    SIGN = "sign"
    VERIFY = "verify"


@dataclass
class ComponentInput:
    """An input port for a Component."""
    name: str
    description: str = ""


@dataclass
class ComponentOutput:
    """An output port for a Component."""
    name: str
    description: str = ""


@dataclass
class ComponentPermission:
    """A permission required by a Component."""
    name: str
    description: str = ""


@dataclass
class ValidationResult:
    """Result of validating a Component contract."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ComponentContract:
    """Contract definition for a reusable Component.

    Attributes:
        contract_version: Semantic version of the contract schema.
        component_id: Unique identifier for the Component.
        display_name: Human-readable name.
        family: Component family/classification.
        version: Semantic version of the Component.
        inputs: List of input ports.
        outputs: List of output ports.
        permission_requirements: List of permissions required.
        provenance_behavior: How the Component handles provenance.
        validation: Validation result metadata.
    """
    contract_version: str
    component_id: str
    display_name: str
    family: ComponentFamily
    version: str
    inputs: List[ComponentInput] = field(default_factory=list)
    outputs: List[ComponentOutput] = field(default_factory=list)
    permission_requirements: List[ComponentPermission] = field(default_factory=list)
    provenance_behavior: ProvenanceBehavior = ProvenanceBehavior.PASSTHROUGH
    validation: ValidationResult = field(default_factory=lambda: ValidationResult(is_valid=True))