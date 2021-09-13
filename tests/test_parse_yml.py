from socless_repo_parser.parse_yml import parse_yml


def test_parse_yml():
    """Ensure that we can parse a serverless.yml without errors."""
    with open("tests/mock_files/mock_serverless.yml") as f:
        mock_serverless_yml_as_string = f.read()

    result = parse_yml(mock_serverless_yml_as_string)

    assert result.functions

    for name, function_meta in result.functions.items():
        assert name == function_meta.lambda_folder_name
