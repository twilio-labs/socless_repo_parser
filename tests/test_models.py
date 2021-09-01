from socless_repo_parser.models import build_integration_classes_from_json


# def test_generate_jsonschema():
#     test = IntegrationFamily().__pydantic_model__.schema_json()
#     print(test)
#     assert test
#     raise AssertionError()

# using pytest fixture from .conftest


def test_generate_dataclasses_from_json(mock_socless_info_output_as_json):  # noqa: F811
    assert mock_socless_info_output_as_json == build_integration_classes_from_json(
        mock_socless_info_output_as_json
    )
