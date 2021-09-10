import pytest
from socless_repo_parser.helpers import parse_repo_names
from socless_repo_parser.models import build_integration_classes_from_json
from socless_repo_parser.api import build_socless_info_from_cli


#### NOTE: run with cmd `tox -- --github`
@pytest.mark.github
def test_output_structure(mock_socless_info_output_as_json):
    mock_output = build_integration_classes_from_json(mock_socless_info_output_as_json)
    output = build_socless_info_from_cli(
        "twilio-labs/socless, twilio-labs/socless-slack",
        output_file_path="socless_info.json",
    )

    assert output == mock_output
    assert output.json()


def test_parse_repo_names():
    names = ["socless-slack", "socless-sumologic"]
    result = parse_repo_names(
        "twilio-labs/socless-slack, https://github.com/twilio-labs/socless-sumologic"
    )

    for index, name in enumerate(names):
        assert result[index].name == name
        assert result[index].org == "twilio-labs"
        assert result[index].url == f"https://github.com/twilio-labs/{name}"


def test_parse_repo_names_missing_org():
    with pytest.raises(ValueError):
        _ = parse_repo_names("twilio-labs/socless-slack, socless")
