from socless_repo_parser.parse_yml import parse_yml


def test_parse_yml():
    with open("tests/mock_files/mock_serverless.yml") as f:
        mock_serverless_yml_as_string = f.read()

    result = parse_yml(mock_serverless_yml_as_string)
