import os
import pytest
from socless_repo_parser.builders import SoclessInfoBuilder


### NOTE: run with cmd `tox -- --github`
@pytest.mark.github
def test_build_from_github_enterprise():
    os.environ["GHE_DOMAIN"] = "test_domain"
    os.environ["GHE_TOKEN"] = "test_token"

    _ = SoclessInfoBuilder().build_from_github_enterprise(
        repo_list="https://github.com/twilio-labs/socless-sumologic"
    )
