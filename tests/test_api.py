import pytest, json
from socless_repo_parser.helpers import parse_repo_names
from socless_repo_parser.models import (
    build_integration_classes_from_json,
)
from socless_repo_parser.api import build_from_github


#### NOTE: run with cmd `tox -- --github`
@pytest.mark.github
def test_output_structure(mock_socless_info_output_as_dict):
    mock_output = build_integration_classes_from_json(mock_socless_info_output_as_dict)
    output = build_from_github(
        "twilio-labs/socless",
        output_file_path="socless_info.json",
    )

    # assert that it converts to json without error
    output_as_json = output.json()
    mock_output_as_json = mock_output.json()

    # assert equality using dicts
    assert json.loads(output_as_json) == json.loads(mock_output_as_json)


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


def test_public_api_exports():
    from socless_repo_parser.api import SoclessInfoBuilder
    from socless_repo_parser.api import Github
    from socless_repo_parser.api import SoclessGithubWrapper
    from socless_repo_parser.api import parse_repo_names  # noqa
    from socless_repo_parser.api import get_github_domain  # noqatox

    _ = SoclessInfoBuilder()
    _ = Github()
    _ = SoclessGithubWrapper()
