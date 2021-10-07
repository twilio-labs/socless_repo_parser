import os, json
import pytest
from socless_repo_parser.builders import IntegrationFamilyBuilder, SoclessInfoBuilder
from tests.conftest import get_mock_file


### NOTE: run with cmd `tox -- --github`
@pytest.mark.github
def test_build_from_github_enterprise():
    os.environ["GHE_DOMAIN"] = "test_domain"
    os.environ["GHE_TOKEN"] = "test_token"

    _ = SoclessInfoBuilder().build_from_github_enterprise(
        repo_list="https://github.com/twilio-labs/socless-sumologic"
    )


PATH_TO_LOCAL_MOCK_REPO = "tests/mock_files/mock_socless_repo"


def test_build_from_local():
    expected_output = get_mock_file("expected_local_output.json")
    output = IntegrationFamilyBuilder().build_from_local(
        "tests/mock_files/mock_socless_repo"
    )

    assert json.loads(expected_output)["integrations"][0] == json.loads(output.json())
