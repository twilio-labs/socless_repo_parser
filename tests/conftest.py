import json
import pytest


def pytest_addoption(parser):
    # `tox -- --github`
    parser.addoption(
        "--github",
        action="store_true",
        default=False,
        help="run slow tests that touch github.com",
    )


def pytest_configure(config):
    # `tox -- --github`
    config.addinivalue_line("markers", "github: marks tests that touch github.com")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--github"):
        # `tox -- --github`
        # --github given in cli: do not skip slow tests
        return
    skip_github = pytest.mark.skip(reason="need --github option to run")
    for item in items:
        if "github" in item.keywords:
            item.add_marker(skip_github)


@pytest.fixture(scope="session")
def mock_socless_info_output_as_dict() -> dict:
    # output generated by running `python3 main.py "twiio-labs/socless, twilio-labs/socless-slack" --org-name="twilio-labs"` on 9/10/2021
    with open("tests/mock_files/mock_output.json") as f:
        mock_output = json.loads(f.read())
    return mock_output
