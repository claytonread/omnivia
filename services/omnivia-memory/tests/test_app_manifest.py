"""Tests for the App Manifest contract."""

import pytest

from omnivia_memory.app_manifest import (
    AppManifest,
    AppManifestValidationError,
    AppState,
    DataSource,
    ProvenanceRequirement,
    ValidationResult,
    validate_app_manifest,
)


# ---------------------------------------------------------------------------
# Valid manifest helpers
# ---------------------------------------------------------------------------

def _minimal_dict() -> dict:
    """Return a minimal valid manifest dict."""
    return {
        "manifest_version": "1.0.0",
        "app_id": "com.acme.expense-app",
        "display_name": "Expense App",
        "app_version": "1.0.0",
        "required_module_id": "com.omnivia.apps",
    }


# ---------------------------------------------------------------------------
# Valid manifest tests
# ---------------------------------------------------------------------------

def test_validate_minimal_manifest():
    """A minimal valid manifest returns a populated AppManifest."""
    data = _minimal_dict()
    manifest = validate_app_manifest(data)

    assert isinstance(manifest, AppManifest)
    assert manifest.manifest_version == "1.0.0"
    assert manifest.app_id == "com.acme.expense-app"
    assert manifest.display_name == "Expense App"
    assert manifest.app_version == "1.0.0"
    assert manifest.required_module_id == "com.omnivia.apps"
    assert manifest.compatible_harness_versions == []
    assert manifest.compatible_api_versions == []
    assert manifest.required_components == []
    assert manifest.required_data_sources == []
    assert manifest.requested_permissions == []
    assert manifest.state == AppState.DRAFT
    assert manifest.provenance.require_signed is False
    assert manifest.provenance.require_audit_log is False
    assert manifest.provenance.allowed_source_types == []


def test_validate_with_compatible_versions():
    """A manifest with Harness/API compatibility ranges parses correctly."""
    data = _minimal_dict()
    data["compatible_harness_versions"] = [">=1.0.0", "<2.0.0"]
    data["compatible_api_versions"] = ["2026-06"]

    manifest = validate_app_manifest(data)

    assert manifest.compatible_harness_versions == [">=1.0.0", "<2.0.0"]
    assert manifest.compatible_api_versions == ["2026-06"]


def test_validate_with_required_components():
    """A manifest with required_components parses correctly."""
    data = _minimal_dict()
    data["required_components"] = [
        "omnivia.components.button",
        "omnivia.components.form",
    ]

    manifest = validate_app_manifest(data)

    assert len(manifest.required_components) == 2
    assert manifest.required_components[0] == "omnivia.components.button"
    assert manifest.required_components[1] == "omnivia.components.form"


def test_validate_with_data_sources():
    """A manifest with required_data_sources parses correctly."""
    data = _minimal_dict()
    data["required_data_sources"] = [
        {
            "source_id": "expense-db",
            "display_name": "Expense Database",
            "description": "Primary expense records",
        },
        {
            "source_id": "expense-cache",
            "display_name": "",
            "description": "",
        },
    ]

    manifest = validate_app_manifest(data)

    assert len(manifest.required_data_sources) == 2
    assert manifest.required_data_sources[0].source_id == "expense-db"
    assert manifest.required_data_sources[0].display_name == "Expense Database"
    assert manifest.required_data_sources[0].description == "Primary expense records"
    assert manifest.required_data_sources[1].source_id == "expense-cache"
    assert manifest.required_data_sources[1].display_name == ""
    assert manifest.required_data_sources[1].description == ""


def test_validate_with_data_source_minimal_fields():
    """A data source with only source_id parses correctly."""
    data = _minimal_dict()
    data["required_data_sources"] = [{"source_id": "only-id"}]

    manifest = validate_app_manifest(data)

    assert len(manifest.required_data_sources) == 1
    assert manifest.required_data_sources[0].source_id == "only-id"
    assert manifest.required_data_sources[0].display_name == ""
    assert manifest.required_data_sources[0].description == ""


def test_validate_with_requested_permissions():
    """A manifest with requested_permissions parses correctly."""
    data = _minimal_dict()
    data["requested_permissions"] = [
        "workspace.read",
        "workspace.write",
    ]

    manifest = validate_app_manifest(data)

    assert manifest.requested_permissions == ["workspace.read", "workspace.write"]


def test_validate_with_empty_permissions_list():
    """A manifest with empty permissions list parses correctly."""
    data = _minimal_dict()
    data["requested_permissions"] = []

    manifest = validate_app_manifest(data)

    assert manifest.requested_permissions == []


def test_validate_with_empty_components_list():
    """A manifest with empty components list parses correctly."""
    data = _minimal_dict()
    data["required_components"] = []

    manifest = validate_app_manifest(data)

    assert manifest.required_components == []


def test_validate_with_provenance_require_signed():
    """A manifest with provenance.require_signed parses correctly."""
    data = _minimal_dict()
    data["provenance"] = {"require_signed": True}

    manifest = validate_app_manifest(data)

    assert manifest.provenance.require_signed is True
    assert manifest.provenance.require_audit_log is False
    assert manifest.provenance.allowed_source_types == []


def test_validate_with_provenance_require_audit_log():
    """A manifest with provenance.require_audit_log parses correctly."""
    data = _minimal_dict()
    data["provenance"] = {"require_audit_log": True}

    manifest = validate_app_manifest(data)

    assert manifest.provenance.require_signed is False
    assert manifest.provenance.require_audit_log is True


def test_validate_with_provenance_allowed_source_types():
    """A manifest with provenance.allowed_source_types parses correctly."""
    data = _minimal_dict()
    data["provenance"] = {
        "allowed_source_types": ["database", "api", "file"],
    }

    manifest = validate_app_manifest(data)

    assert manifest.provenance.allowed_source_types == ["database", "api", "file"]


def test_validate_with_full_provenance():
    """A manifest with full provenance config parses correctly."""
    data = _minimal_dict()
    data["provenance"] = {
        "require_signed": True,
        "require_audit_log": True,
        "allowed_source_types": ["database", "api"],
    }

    manifest = validate_app_manifest(data)

    assert manifest.provenance.require_signed is True
    assert manifest.provenance.require_audit_log is True
    assert manifest.provenance.allowed_source_types == ["database", "api"]


def test_validate_state_draft():
    """A manifest with state DRAFT parses correctly."""
    data = _minimal_dict()
    data["state"] = "draft"

    manifest = validate_app_manifest(data)

    assert manifest.state == AppState.DRAFT


def test_validate_state_active():
    """A manifest with state ACTIVE parses correctly."""
    data = _minimal_dict()
    data["state"] = "active"

    manifest = validate_app_manifest(data)

    assert manifest.state == AppState.ACTIVE


def test_validate_state_suspended():
    """A manifest with state SUSPENDED parses correctly."""
    data = _minimal_dict()
    data["state"] = "suspended"

    manifest = validate_app_manifest(data)

    assert manifest.state == AppState.SUSPENDED


def test_validate_state_deprecated():
    """A manifest with state DEPRECATED parses correctly."""
    data = _minimal_dict()
    data["state"] = "deprecated"

    manifest = validate_app_manifest(data)

    assert manifest.state == AppState.DEPRECATED


# ---------------------------------------------------------------------------
# Invalid manifest tests — missing required fields
# ---------------------------------------------------------------------------

def test_rejects_missing_manifest_version():
    """Missing manifest_version raises a clear error."""
    data = _minimal_dict()
    del data["manifest_version"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "manifest_version" in str(exc_info.value).lower()


def test_rejects_empty_manifest_version():
    """Empty manifest_version raises a clear error."""
    data = _minimal_dict()
    data["manifest_version"] = ""

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "manifest_version" in str(exc_info.value).lower()


def test_rejects_whitespace_manifest_version():
    """Whitespace-only manifest_version raises a clear error."""
    data = _minimal_dict()
    data["manifest_version"] = "   "

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "manifest_version" in str(exc_info.value).lower()


def test_rejects_missing_app_id():
    """Missing app_id raises a clear error."""
    data = _minimal_dict()
    del data["app_id"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "app_id" in str(exc_info.value).lower()


def test_rejects_empty_app_id():
    """Empty app_id raises a clear error."""
    data = _minimal_dict()
    data["app_id"] = ""

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "app_id" in str(exc_info.value).lower()


def test_rejects_missing_display_name():
    """Missing display_name raises a clear error."""
    data = _minimal_dict()
    del data["display_name"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "display_name" in str(exc_info.value).lower()


def test_rejects_empty_display_name():
    """Empty display_name raises a clear error."""
    data = _minimal_dict()
    data["display_name"] = ""

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "display_name" in str(exc_info.value).lower()


def test_rejects_missing_app_version():
    """Missing app_version raises a clear error."""
    data = _minimal_dict()
    del data["app_version"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "app_version" in str(exc_info.value).lower()


def test_rejects_empty_app_version():
    """Empty app_version raises a clear error."""
    data = _minimal_dict()
    data["app_version"] = ""

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "app_version" in str(exc_info.value).lower()


def test_rejects_missing_required_module_id():
    """Missing required_module_id raises a clear error."""
    data = _minimal_dict()
    del data["required_module_id"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_module_id" in str(exc_info.value).lower()


def test_rejects_empty_required_module_id():
    """Empty required_module_id raises a clear error."""
    data = _minimal_dict()
    data["required_module_id"] = ""

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_module_id" in str(exc_info.value).lower()


@pytest.mark.parametrize(
    "field_name",
    ["compatible_harness_versions", "compatible_api_versions"],
)
def test_rejects_non_list_compatible_versions(field_name):
    """Compatible version fields must be lists when present."""
    data = _minimal_dict()
    data[field_name] = ">=1.0.0"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert field_name in str(exc_info.value).lower()


@pytest.mark.parametrize(
    "field_name",
    ["compatible_harness_versions", "compatible_api_versions"],
)
def test_rejects_invalid_compatible_version_item(field_name):
    """Compatible version field items must be non-empty strings."""
    data = _minimal_dict()
    data[field_name] = [">=1.0.0", ""]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert f"{field_name}[1]" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — wrong types
# ---------------------------------------------------------------------------

def test_rejects_non_string_manifest_version():
    """Non-string manifest_version raises a clear error."""
    data = _minimal_dict()
    data["manifest_version"] = 42

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "manifest_version" in str(exc_info.value).lower()


def test_rejects_non_string_app_id():
    """Non-string app_id raises a clear error."""
    data = _minimal_dict()
    data["app_id"] = 42

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "app_id" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — invalid state
# ---------------------------------------------------------------------------

def test_rejects_missing_state():
    """Missing state defaults to DRAFT and does not raise."""
    data = _minimal_dict()
    assert "state" not in data

    manifest = validate_app_manifest(data)

    assert manifest.state == AppState.DRAFT


def test_rejects_invalid_state_string():
    """Unknown state value raises a clear error."""
    data = _minimal_dict()
    data["state"] = "premium"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "state" in str(exc_info.value).lower()
    assert "premium" in str(exc_info.value)


def test_rejects_non_string_state():
    """Non-string state raises a clear error."""
    data = _minimal_dict()
    data["state"] = 42

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "state" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — required_components
# ---------------------------------------------------------------------------

def test_rejects_non_list_required_components():
    """Non-list required_components raises a clear error."""
    data = _minimal_dict()
    data["required_components"] = "not-a-list"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_components" in str(exc_info.value).lower()


def test_rejects_non_string_in_required_components():
    """Non-string item in required_components raises a clear error."""
    data = _minimal_dict()
    data["required_components"] = ["valid-id", 42]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_components[1]" in str(exc_info.value).lower()


def test_rejects_empty_string_in_required_components():
    """Empty string in required_components raises a clear error."""
    data = _minimal_dict()
    data["required_components"] = ["valid-id", ""]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_components[1]" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — requested_permissions
# ---------------------------------------------------------------------------

def test_rejects_non_list_requested_permissions():
    """Non-list requested_permissions raises a clear error."""
    data = _minimal_dict()
    data["requested_permissions"] = "not-a-list"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "requested_permissions" in str(exc_info.value).lower()


def test_rejects_non_string_in_requested_permissions():
    """Non-string item in requested_permissions raises a clear error."""
    data = _minimal_dict()
    data["requested_permissions"] = ["read", 42]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "requested_permissions[1]" in str(exc_info.value).lower()


def test_rejects_empty_string_in_requested_permissions():
    """Empty string in requested_permissions raises a clear error."""
    data = _minimal_dict()
    data["requested_permissions"] = ["read", ""]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "requested_permissions[1]" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — required_data_sources
# ---------------------------------------------------------------------------

def test_rejects_non_list_required_data_sources():
    """Non-list required_data_sources raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = "not-a-list"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources" in str(exc_info.value).lower()


def test_rejects_non_dict_in_required_data_sources():
    """Non-dict item in required_data_sources raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = ["not-a-dict"]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources[0]" in str(exc_info.value).lower()


def test_rejects_missing_source_id_in_data_source():
    """Data source missing source_id raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = [{"display_name": "No ID source"}]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources[0].source_id" in str(exc_info.value).lower()


def test_rejects_empty_source_id_in_data_source():
    """Data source with empty source_id raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = [{"source_id": ""}]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources[0].source_id" in str(exc_info.value).lower()


def test_rejects_non_string_display_name_in_data_source():
    """Data source with non-string display_name raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = [{"source_id": "ds1", "display_name": 42}]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources[0].display_name" in str(exc_info.value).lower()


def test_rejects_non_string_description_in_data_source():
    """Data source with non-string description raises a clear error."""
    data = _minimal_dict()
    data["required_data_sources"] = [{"source_id": "ds1", "description": 42}]

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "required_data_sources[0].description" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Invalid manifest tests — provenance
# ---------------------------------------------------------------------------

def test_rejects_non_dict_provenance():
    """Non-dict provenance raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = "not-a-dict"

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance" in str(exc_info.value).lower()


def test_rejects_non_bool_require_signed():
    """Non-bool provenance.require_signed raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = {"require_signed": "yes"}

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance.require_signed" in str(exc_info.value).lower()


def test_rejects_non_bool_require_audit_log():
    """Non-bool provenance.require_audit_log raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = {"require_audit_log": "yes"}

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance.require_audit_log" in str(exc_info.value).lower()


def test_rejects_non_list_allowed_source_types():
    """Non-list provenance.allowed_source_types raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = {"allowed_source_types": "not-a-list"}

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance.allowed_source_types" in str(exc_info.value).lower()


def test_rejects_non_string_in_allowed_source_types():
    """Non-string item in provenance.allowed_source_types raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = {"allowed_source_types": ["database", 42]}

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance.allowed_source_types[1]" in str(exc_info.value).lower()


def test_rejects_empty_string_in_allowed_source_types():
    """Empty string in provenance.allowed_source_types raises a clear error."""
    data = _minimal_dict()
    data["provenance"] = {"allowed_source_types": ["database", ""]}

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    assert "provenance.allowed_source_types[1]" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Multiple error collection test
# ---------------------------------------------------------------------------

def test_collects_multiple_errors():
    """Multiple errors are collected and reported together."""
    data = {
        "manifest_version": "",
        "app_id": "",
        "display_name": "",
        "app_version": "",
        "required_module_id": "",
        "required_components": ["valid", ""],
        "requested_permissions": ["read", ""],
    }

    with pytest.raises(AppManifestValidationError) as exc_info:
        validate_app_manifest(data)
    error_msg = str(exc_info.value)
    # Should contain multiple errors joined by semicolons
    assert "manifest_version" in error_msg
    assert "app_id" in error_msg
    assert "required_components[1]" in error_msg
    assert "requested_permissions[1]" in error_msg


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

def test_app_state_enum_values():
    """AppState enum has correct string values."""
    assert AppState.DRAFT.value == "draft"
    assert AppState.ACTIVE.value == "active"
    assert AppState.SUSPENDED.value == "suspended"
    assert AppState.DEPRECATED.value == "deprecated"


def test_data_source_defaults():
    """DataSource defaults display_name and description to empty strings."""
    ds = DataSource(source_id="test-source")
    assert ds.source_id == "test-source"
    assert ds.display_name == ""
    assert ds.description == ""


def test_data_source_with_all_fields():
    """DataSource with all fields sets them correctly."""
    ds = DataSource(
        source_id="my-source",
        display_name="My Source",
        description="A data source",
    )
    assert ds.source_id == "my-source"
    assert ds.display_name == "My Source"
    assert ds.description == "A data source"


def test_provenance_requirement_defaults():
    """ProvenanceRequirement defaults all fields."""
    pr = ProvenanceRequirement()
    assert pr.require_signed is False
    assert pr.require_audit_log is False
    assert pr.allowed_source_types == []


def test_provenance_requirement_with_all_fields():
    """ProvenanceRequirement with all fields sets them correctly."""
    pr = ProvenanceRequirement(
        require_signed=True,
        require_audit_log=True,
        allowed_source_types=["database", "api"],
    )
    assert pr.require_signed is True
    assert pr.require_audit_log is True
    assert pr.allowed_source_types == ["database", "api"]


def test_validation_result_defaults():
    """ValidationResult defaults errors and warnings to empty lists."""
    vr = ValidationResult(is_valid=True)
    assert vr.is_valid is True
    assert vr.errors == []
    assert vr.warnings == []


def test_validation_result_with_errors_and_warnings():
    """ValidationResult with errors and warnings sets them correctly."""
    vr = ValidationResult(
        is_valid=False,
        errors=["error1", "error2"],
        warnings=["warning1"],
    )
    assert vr.is_valid is False
    assert vr.errors == ["error1", "error2"]
    assert vr.warnings == ["warning1"]


def test_app_manifest_dataclass_mutable():
    """AppManifest is a mutable dataclass."""
    manifest = AppManifest(
        manifest_version="1.0.0",
        app_id="com.acme.test",
        display_name="Test App",
        app_version="1.0.0",
        required_module_id="com.omnivia.apps",
    )
    # Verify it is mutable by assigning to a field
    manifest.display_name = "Updated Name"
    assert manifest.display_name == "Updated Name"
    # Verify mutable fields can be set
    manifest.required_components = ["comp1"]
    assert manifest.required_components == ["comp1"]


def test_app_manifest_default_provenance():
    """AppManifest defaults provenance to empty ProvenanceRequirement."""
    manifest = AppManifest(
        manifest_version="1.0.0",
        app_id="com.acme.test",
        display_name="Test App",
        app_version="1.0.0",
        required_module_id="com.omnivia.apps",
    )
    assert isinstance(manifest.provenance, ProvenanceRequirement)
    assert manifest.provenance.require_signed is False


def test_app_manifest_default_state():
    """AppManifest defaults state to AppState.DRAFT."""
    manifest = AppManifest(
        manifest_version="1.0.0",
        app_id="com.acme.test",
        display_name="Test App",
        app_version="1.0.0",
        required_module_id="com.omnivia.apps",
    )
    assert manifest.state == AppState.DRAFT


def test_app_manifest_default_validation():
    """AppManifest defaults validation to valid ValidationResult."""
    manifest = AppManifest(
        manifest_version="1.0.0",
        app_id="com.acme.test",
        display_name="Test App",
        app_version="1.0.0",
        required_module_id="com.omnivia.apps",
    )
    assert isinstance(manifest.validation, ValidationResult)
    assert manifest.validation.is_valid is True
    assert manifest.validation.errors == []


def test_app_manifest_with_all_fields():
    """AppManifest with all fields sets them correctly."""
    manifest = AppManifest(
        manifest_version="1.0.0",
        app_id="com.acme.test",
        display_name="Full App",
        app_version="2.0.0",
        required_module_id="com.omnivia.dev",
        required_components=["comp1", "comp2"],
        required_data_sources=[
            DataSource(source_id="ds1", display_name="DS1"),
        ],
        requested_permissions=["perm1", "perm2"],
        provenance=ProvenanceRequirement(
            require_signed=True,
            allowed_source_types=["api"],
        ),
        state=AppState.ACTIVE,
        validation=ValidationResult(is_valid=True, warnings=["watch this"]),
    )
    assert manifest.manifest_version == "1.0.0"
    assert manifest.app_id == "com.acme.test"
    assert manifest.display_name == "Full App"
    assert manifest.app_version == "2.0.0"
    assert manifest.required_module_id == "com.omnivia.dev"
    assert manifest.required_components == ["comp1", "comp2"]
    assert len(manifest.required_data_sources) == 1
    assert manifest.required_data_sources[0].source_id == "ds1"
    assert manifest.requested_permissions == ["perm1", "perm2"]
    assert manifest.provenance.require_signed is True
    assert manifest.provenance.allowed_source_types == ["api"]
    assert manifest.state == AppState.ACTIVE
    assert manifest.validation.is_valid is True
    assert manifest.validation.warnings == ["watch this"]
