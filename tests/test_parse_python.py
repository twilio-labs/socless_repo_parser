from socless_repo_parser.models import (
    JsonDataType,
    SoclessFunctionArgument,
)
from socless_repo_parser.parse_python import (
    socless_lambda_file_parser,
)
from conftest import get_mock_file


MOCK_LAMBDA_FILE = get_mock_file("mock_lambda.py")
MOCK_LAMBDA_WITH_NESTED_HANDLE_STATE = get_mock_file(
    "mock_lambda_with_nested_handle_state.py"
)


def test_socless_lambda_file_parser():
    parsed = socless_lambda_file_parser(MOCK_LAMBDA_FILE)

    assert parsed.supports_kwargs

    for arg in parsed.arguments:
        if arg.name == "str_test":
            assert arg.data_type == JsonDataType.STRING

        if arg.name == "test_if_hint_overrides_default_none_type":
            assert arg.data_type != JsonDataType.NULL  # same as JsonDataType.NULL
            assert "array" in arg.data_type

    assert len(parsed.arguments) == 11


def test_socless_lambda_file_parser_nested_handle_state_fn():
    parsed = socless_lambda_file_parser(MOCK_LAMBDA_WITH_NESTED_HANDLE_STATE)

    assert not parsed.supports_kwargs
    assert len(parsed.arguments) == 7
    assert len([x for x in parsed.arguments if not x.internal]) == 6


def test_socless_docstring_parser():
    parsed = socless_lambda_file_parser(MOCK_LAMBDA_WITH_NESTED_HANDLE_STATE)

    assert parsed.description
    for arg in parsed.arguments:
        if not arg.internal:
            assert arg.description


EXPECTED_PARSED_ARGS_FOR_MOCK_LAMBDA = [
    SoclessFunctionArgument(
        name="no_type_info_test",
        data_type="null",
        required=True,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="str_test",
        data_type="string",
        required=True,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="list_test",
        data_type="array<>",
        required=True,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="dict_test",
        data_type="object",
        required=True,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="int_test",
        data_type="number",
        required=True,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="none_test",
        data_type="null",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
    SoclessFunctionArgument(
        name="empty_dict_test",
        data_type="object",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value={},
    ),
    SoclessFunctionArgument(
        name="union_test",
        data_type="union<string,array<>>",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value=[],
    ),
    SoclessFunctionArgument(
        name="optional_test",
        data_type="string",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value="",
    ),
    SoclessFunctionArgument(
        name="list_typing_test",
        data_type="array<string>",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value=[],
    ),
    SoclessFunctionArgument(
        name="test_if_hint_overrides_default_none_type",
        data_type="array<string>",
        required=False,
        description="",
        placeholder="",
        internal=False,
        default_value=None,
    ),
]


def test_parsed_handle_state_args_and_data_types():
    parsed_file = socless_lambda_file_parser(MOCK_LAMBDA_FILE)
    expected_args = EXPECTED_PARSED_ARGS_FOR_MOCK_LAMBDA

    for arg in parsed_file.arguments:
        found = False
        for expected_arg in expected_args:
            if arg.name == expected_arg.name:
                found = True

        if not found:
            print("MISSING ARG: ")
            print(arg)
        assert found

    assert len(parsed_file.arguments) == len(expected_args)
