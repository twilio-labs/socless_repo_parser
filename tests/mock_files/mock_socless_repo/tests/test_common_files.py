import pytest

# two ways to import from common_files folder
import template_helpers

# other way to import multiple items from a file (do not do `from x import *`)
from template_helpers import example_function_with_default_args, SoclessTemplateError

# All tests must start with the word `test`
# All test names must be unique
# Test names should be descriptive, don't be afraid to make them long
# If a function has multiple branches (if statements, try/catch) write multiple tests


def test_assert_a_function_intended_to_fail():
    with pytest.raises(SoclessTemplateError):
        template_helpers.example_function_that_fails("My Failure Message")


def test_function_with_default_args_not_populated():
    assert "success! args: 7, optional" == example_function_with_default_args(7)


def test_function_with_default_args_changed():
    result = example_function_with_default_args(2, "new value passed")
    assert "success! args: 2, new value passed" == result


def test_function_fails_with_positional_arg_missing():
    with pytest.raises(TypeError):
        example_function_with_default_args(default_arg=" Im gonna fail :( ")  # type: ignore


def test_function_with_args_passed_as_keyword_args():
    keyword_args = {"positional_arg": 6, "default_arg": "im from kwargs!"}

    # double splat ** operator turns a dict into key=value args
    result = example_function_with_default_args(**keyword_args)
    assert "success! args: 6, im from kwargs!" == result
