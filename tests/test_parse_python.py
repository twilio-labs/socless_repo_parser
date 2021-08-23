import ast
from src.models import JsonDataType, SoclessFunction, SoclessFunctionArgument
from src.parse_python import (
    get_function_args_info,
    socless_lambda_file_parser,
)


def mock_handle_state_function() -> ast.FunctionDef:
    mock_handle_state_fn_def = """
def tester(no_type_info_test, str_test: str, list_test: list, dict_test: dict, int_test: int, none_test = None, empty_dict_test = {}, union_test: Union[str, list] = [], optional_test: Optional[str] = "", list_typing_test: List[str] = [], **kwargs):
    pass
    """
    mock_ast_module = ast.parse(mock_handle_state_fn_def)
    for node in mock_ast_module.body:
        if isinstance(node, ast.FunctionDef):
            return node
    raise NotImplementedError("No function definition in mock ast data")


def mock_lambda_file() -> str:
    with open("tests/mock_files/mock_lambda.py") as f:
        python_file_as_string = f.read()
    return python_file_as_string


def mock_lambda_file_with_nested_handle_state() -> str:
    with open("tests/mock_files/mock_lambda_with_nested_handle_state.py") as f:
        python_file_as_string = f.read()
    return python_file_as_string


def expected_parsed_fn_for_mock_handle_state() -> SoclessFunction:
    mock_function = SoclessFunction()
    mock_function.arguments = [
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
    ]
    return mock_function


def test_fn_args_parse():
    function_info = SoclessFunction()
    function_info.arguments = get_function_args_info(mock_handle_state_function())
    expected_fn = expected_parsed_fn_for_mock_handle_state()
    assert function_info.arguments == expected_fn.arguments


def test_socless_lambda_file_parser():
    parsed = socless_lambda_file_parser(mock_lambda_file())

    assert parsed.supports_kwargs

    for arg in parsed.arguments:
        if arg.name == "str_test":
            assert arg.data_type == JsonDataType.STRING

        if arg.name == "test_if_hint_overrides_default_none_type":
            assert arg.data_type != JsonDataType.NULL  # same as JsonDataType.NULL
            assert "array" in arg.data_type

    assert len(parsed.arguments) == 11


def test_socless_lambda_file_parser_nested_handle_state_fn():
    parsed = socless_lambda_file_parser(mock_lambda_file_with_nested_handle_state())

    assert not parsed.supports_kwargs
    assert len(parsed.arguments) == 7
    assert len([x for x in parsed.arguments if not x.internal]) == 6


def test_socless_docstring_parser():
    py_file_string = mock_lambda_file_with_nested_handle_state()
    # handle_state_node = get_handle_state(py_file_string)
    parsed = socless_lambda_file_parser(py_file_string)

    assert parsed.description
    for arg in parsed.arguments:
        if not arg.internal:
            assert arg.description
    # parsed = socless_lambda_file_parser(mock_lambda_file_with_nested_handle_state())

    # assert not parsed.supports_kwargs
    # assert len(parsed.arguments) == 7
    # assert len([x for x in parsed.arguments if not x.internal]) == 6
