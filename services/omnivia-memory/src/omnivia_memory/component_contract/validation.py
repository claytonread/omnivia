"""Component Contract validation."""

from typing import Any, Dict

class ComponentContractValidationError(Exception):
    """Raised when a Component Contract fails validation."""
    pass


def validate_component_contract(data: Dict[str, Any]) -> "ComponentContract":
    """Validate a plain dict and return a ComponentContract.

    Args:
        data: A dictionary containing contract data.

    Returns:
        A validated ComponentContract instance.

    Raises:
        ComponentContractValidationError: If validation fails.
    """
    errors = []

    # Required string fields
    for field_name in ("contract_version", "component_id", "display_name", "version"):
        value = data.get(field_name)
        if value is None:
            errors.append(f"'{field_name}' is required")
        elif not isinstance(value, str):
            errors.append(f"'{field_name}' must be a string, got {type(value).__name__}")
        elif not value.strip():
            errors.append(f"'{field_name}' must not be empty")

    # family: required enum
    family_raw = data.get("family")
    if family_raw is None:
        errors.append("'family' is required")
    else:
        from .models import ComponentFamily
        try:
            ComponentFamily(family_raw)
        except ValueError:
            valid = ", ".join(f.value for f in ComponentFamily)
            errors.append(f"'family' must be one of: {valid}, got {family_raw!r}")

    # provenance_behavior: optional enum, default passthrough
    provenance_raw = data.get("provenance_behavior")
    if provenance_raw is not None:
        from .models import ProvenanceBehavior
        try:
            ProvenanceBehavior(provenance_raw)
        except ValueError:
            valid = ", ".join(f.value for f in ProvenanceBehavior)
            errors.append(f"'provenance_behavior' must be one of: {valid}, got {provenance_raw!r}")

    # inputs: optional list of dicts
    inputs_raw = data.get("inputs")
    if inputs_raw is not None:
        if not isinstance(inputs_raw, list):
            errors.append("'inputs' must be a list")
        else:
            for i, item in enumerate(inputs_raw):
                if not isinstance(item, dict):
                    errors.append(f"'inputs[{i}]' must be a dict, got {type(item).__name__}")
                elif not item.get("name"):
                    errors.append(f"'inputs[{i}]' is missing 'name'")

    # outputs: optional list of dicts
    outputs_raw = data.get("outputs")
    if outputs_raw is not None:
        if not isinstance(outputs_raw, list):
            errors.append("'outputs' must be a list")
        else:
            for i, item in enumerate(outputs_raw):
                if not isinstance(item, dict):
                    errors.append(f"'outputs[{i}]' must be a dict, got {type(item).__name__}")
                elif not item.get("name"):
                    errors.append(f"'outputs[{i}]' is missing 'name'")

    # permission_requirements: optional list of dicts
    permissions_raw = data.get("permission_requirements")
    if permissions_raw is not None:
        if not isinstance(permissions_raw, list):
            errors.append("'permission_requirements' must be a list")
        else:
            for i, item in enumerate(permissions_raw):
                if not isinstance(item, dict):
                    errors.append(
                        f"'permission_requirements[{i}]' must be a dict, got {type(item).__name__}"
                    )
                elif not item.get("name"):
                    errors.append(f"'permission_requirements[{i}]' is missing 'name'")

    if errors:
        raise ComponentContractValidationError("; ".join(errors))

    # Build enums
    from .models import ComponentFamily, ProvenanceBehavior, ComponentContract
    from .models import ComponentInput, ComponentOutput, ComponentPermission, ValidationResult

    family = ComponentFamily(data["family"])
    provenance_behavior = ProvenanceBehavior(data.get("provenance_behavior", "passthrough"))

    inputs = [
        ComponentInput(name=item["name"], description=item.get("description", ""))
        for item in (inputs_raw or [])
    ]
    outputs = [
        ComponentOutput(name=item["name"], description=item.get("description", ""))
        for item in (outputs_raw or [])
    ]
    permission_requirements = [
        ComponentPermission(name=item["name"], description=item.get("description", ""))
        for item in (permissions_raw or [])
    ]

    return ComponentContract(
        contract_version=data["contract_version"],
        component_id=data["component_id"],
        display_name=data["display_name"],
        family=family,
        version=data["version"],
        inputs=inputs,
        outputs=outputs,
        permission_requirements=permission_requirements,
        provenance_behavior=provenance_behavior,
        validation=ValidationResult(is_valid=True),
    )
