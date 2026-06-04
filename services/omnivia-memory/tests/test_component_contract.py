import pytest

from omnivia_memory.component_contract import (
    ComponentFamily,
    ProvenanceBehavior,
    ComponentInput,
    ComponentOutput,
    ComponentPermission,
    ValidationResult,
    ComponentContract,
    ComponentContractValidationError,
    validate_component_contract,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def minimal_data(**overrides):
    """Return a minimal valid contract dict."""
    return {
        "contract_version": "1.0.0",
        "component_id": "test-component",
        "display_name": "Test Component",
        "family": "ui",
        "version": "1.0.0",
        **overrides,
    }


# ---------------------------------------------------------------------------
# Valid contract tests
# ---------------------------------------------------------------------------

class TestValidateComponentContractValid:
    def test_minimal_valid(self):
        data = minimal_data()
        contract = validate_component_contract(data)
        assert contract.contract_version == "1.0.0"
        assert contract.component_id == "test-component"
        assert contract.display_name == "Test Component"
        assert contract.family == ComponentFamily.UI
        assert contract.version == "1.0.0"
        assert contract.inputs == []
        assert contract.outputs == []
        assert contract.permission_requirements == []
        assert contract.provenance_behavior == ProvenanceBehavior.PASSTHROUGH
        assert contract.validation.is_valid is True

    def test_with_inputs(self):
        data = minimal_data(
            inputs=[
                {"name": "text", "description": "Raw text input"},
                {"name": "image"},
            ]
        )
        contract = validate_component_contract(data)
        assert len(contract.inputs) == 2
        assert contract.inputs[0].name == "text"
        assert contract.inputs[0].description == "Raw text input"
        assert contract.inputs[1].name == "image"
        assert contract.inputs[1].description == ""

    def test_with_outputs(self):
        data = minimal_data(
            outputs=[
                {"name": "result", "description": "Processed result"},
                {"name": "metadata"},
            ]
        )
        contract = validate_component_contract(data)
        assert len(contract.outputs) == 2
        assert contract.outputs[0].name == "result"
        assert contract.outputs[0].description == "Processed result"
        assert contract.outputs[1].name == "metadata"
        assert contract.outputs[1].description == ""

    def test_with_permission_requirements(self):
        data = minimal_data(
            permission_requirements=[
                {"name": "filesystem:read", "description": "Read files from disk"},
                {"name": "network:outbound"},
            ]
        )
        contract = validate_component_contract(data)
        assert len(contract.permission_requirements) == 2
        assert contract.permission_requirements[0].name == "filesystem:read"
        assert (
            contract.permission_requirements[0].description == "Read files from disk"
        )
        assert contract.permission_requirements[1].name == "network:outbound"
        assert contract.permission_requirements[1].description == ""

    def test_provenance_behavior_variants(self):
        for value in ("passthrough", "track", "sign", "verify"):
            data = minimal_data(provenance_behavior=value)
            contract = validate_component_contract(data)
            assert contract.provenance_behavior == ProvenanceBehavior(value)

    def test_provenance_behavior_default(self):
        # Explicitly omit provenance_behavior
        data = minimal_data()
        data.pop("provenance_behavior", None)
        contract = validate_component_contract(data)
        assert contract.provenance_behavior == ProvenanceBehavior.PASSTHROUGH

    def test_all_fields_present(self):
        data = minimal_data(
            inputs=[{"name": "in1", "description": "desc"}],
            outputs=[{"name": "out1", "description": "desc"}],
            permission_requirements=[{"name": "perm1", "description": "desc"}],
            provenance_behavior="track",
        )
        contract = validate_component_contract(data)
        assert len(contract.inputs) == 1
        assert len(contract.outputs) == 1
        assert len(contract.permission_requirements) == 1
        assert contract.provenance_behavior == ProvenanceBehavior.TRACK


# ---------------------------------------------------------------------------
# Invalid contract tests
# ---------------------------------------------------------------------------

class TestValidateComponentContractInvalid:
    @pytest.mark.parametrize(
        "field",
        ["contract_version", "component_id", "display_name", "version"],
    )
    def test_missing_required_field(self, field):
        data = minimal_data()
        data.pop(field)
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        assert f"'{field}' is required" in exc_info.value.args[0]

    @pytest.mark.parametrize(
        "field",
        ["contract_version", "component_id", "display_name", "version"],
    )
    def test_empty_required_field(self, field):
        data = minimal_data(**{field: "   "})
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        assert f"'{field}' must not be empty" in exc_info.value.args[0]

    @pytest.mark.parametrize(
        "field",
        ["contract_version", "component_id", "display_name", "version"],
    )
    def test_wrong_type_required_field(self, field):
        data = minimal_data(**{field: 123})
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        assert f"'{field}' must be a string" in exc_info.value.args[0]

    def test_missing_family(self):
        data = minimal_data()
        data.pop("family")
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        assert "'family' is required" in exc_info.value.args[0]

    @pytest.mark.parametrize("invalid_family", ["widget", "uii", "", 42])
    def test_invalid_family(self, invalid_family):
        data = minimal_data(family=invalid_family)
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "family" in error_msg
        assert "must be one of" in error_msg

    @pytest.mark.parametrize("invalid_provenance", ["passthru", "log", "", 42])
    def test_invalid_provenance_behavior(self, invalid_provenance):
        data = minimal_data(provenance_behavior=invalid_provenance)
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "provenance_behavior" in error_msg
        assert "must be one of" in error_msg

    def test_inputs_not_list(self):
        data = minimal_data(inputs="not-a-list")
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "'inputs' must be a list" in error_msg

    @pytest.mark.parametrize(
        "invalid_input",
        ["not-a-dict", 42, None, {"description": "has no name"}],
        ids=["string", "int", "None", "missing-name"],
    )
    def test_invalid_inputs_item(self, invalid_input):
        data = minimal_data(inputs=[invalid_input])
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "inputs[0]" in error_msg

    def test_outputs_not_list(self):
        data = minimal_data(outputs={"name": "x"})
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "'outputs' must be a list" in error_msg

    @pytest.mark.parametrize(
        "invalid_output",
        [None, {"description": "no name"}],
        ids=["None", "missing-name"],
    )
    def test_invalid_outputs_item(self, invalid_output):
        data = minimal_data(outputs=[invalid_output])
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "outputs[0]" in error_msg

    def test_permission_requirements_not_list(self):
        data = minimal_data(permission_requirements=True)
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "'permission_requirements' must be a list" in error_msg

    @pytest.mark.parametrize(
        "invalid_perm",
        [{"description": "no name"}, 3.14],
        ids=["missing-name", "wrong-type"],
    )
    def test_invalid_permission_requirements_item(self, invalid_perm):
        data = minimal_data(permission_requirements=[invalid_perm])
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert "permission_requirements[0]" in error_msg

    def test_multiple_errors_collected(self):
        data = {
            "contract_version": "",
            "display_name": "",
            "family": "invalid",
            "inputs": "bad",
            "outputs": 42,
        }
        with pytest.raises(ComponentContractValidationError) as exc_info:
            validate_component_contract(data)
        error_msg = str(exc_info.value)
        assert len(error_msg.split(";")) >= 4


# ---------------------------------------------------------------------------
# Model instantiation tests
# ---------------------------------------------------------------------------

class TestComponentContractModel:
    def test_default_validation_result(self):
        contract = ComponentContract(
            contract_version="1.0.0",
            component_id="id",
            display_name="Name",
            family=ComponentFamily.DATA,
            version="1.0.0",
        )
        assert contract.validation.is_valid is True
        assert contract.validation.errors == []
        assert contract.validation.warnings == []

    def test_mutable_inputs(self):
        contract = ComponentContract(
            contract_version="1.0.0",
            component_id="id",
            display_name="Name",
            family=ComponentFamily.LOGIC,
            version="1.0.0",
        )
        contract.inputs.append(ComponentInput(name="x", description="y"))
        assert len(contract.inputs) == 1

    def test_provenance_behavior_default(self):
        contract = ComponentContract(
            contract_version="1.0.0",
            component_id="id",
            display_name="Name",
            family=ComponentFamily.UI,
            version="1.0.0",
        )
        assert contract.provenance_behavior == ProvenanceBehavior.PASSTHROUGH

    def test_validation_result_mutable(self):
        result = ValidationResult(is_valid=False, errors=["err1"])
        result.errors.append("err2")
        assert result.errors == ["err1", "err2"]


class TestComponentFamily:
    def test_all_values_present(self):
        assert len(ComponentFamily) == 5
        values = {f.value for f in ComponentFamily}
        assert values == {"ui", "data", "logic", "integration", "utility"}


class TestProvenanceBehavior:
    def test_all_values_present(self):
        assert len(ProvenanceBehavior) == 4
        values = {f.value for f in ProvenanceBehavior}
        assert values == {"passthrough", "track", "sign", "verify"}
