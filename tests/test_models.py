import json
from socless_repo_parser.models import build_integration_classes_from_json


# def test_generate_jsonschema():
#     test = IntegrationFamily().__pydantic_model__.schema_json()
#     print(test)
#     assert test
#     raise AssertionError()

# using pytest fixture from .conftest


def test_generate_dataclasses_from_json(mock_socless_info_output_as_dict):  # noqa: F811
    assert mock_socless_info_output_as_dict == build_integration_classes_from_json(
        mock_socless_info_output_as_dict
    )


def test_output_methods(mock_socless_info_output_as_dict):
    all_integrations = build_integration_classes_from_json(
        mock_socless_info_output_as_dict
    )

    assert mock_socless_info_output_as_dict == all_integrations.dict()
    assert json.dumps(mock_socless_info_output_as_dict) == all_integrations.json()
