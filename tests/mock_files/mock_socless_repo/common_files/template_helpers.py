# This file is an example of how you can share code between all your lambdas in the ./functions folder.
# Any files in the ./common_files folder will be individually packaged with each of your python functions,
#   which allows you to reduce repeated code and share library functions or classes for the entire Integration.


# An example of an Error Class shared for the entire Repo, allows you to surface descriptive customized errors
# for your playbooks. A custom error class can help you write useful Catch statements in your playbook to react
# if something has broken but is recoverable or expected.
class SoclessTemplateError(Exception):
    """An error class for the socless-template integration."""

    pass


def example_function_that_fails(failure_message: str):
    """An function that will always fail.
    Args:
        failure_message: customize the raised error message

    Raises:
        SoclessTemplateError
    """
    raise SoclessTemplateError(f"Test failure message: {failure_message}")


def example_function_with_default_args(
    positional_arg: int, default_arg: str = "optional"
) -> str:
    """Return a string that tells what args you passed in.
    Args:
        positional_arg: any number to print
        default_arg:    any string to print

    Returns:
        A success message that includes the given arguments.
    """
    return f"success! args: {positional_arg}, {default_arg}"


## PYTHON TIPS ##
# Docstrings """ """ are used to explain what a function does.
#  Example docstring layout is shown in the Google Python Style Guide:
#  https://google.github.io/styleguide/pyguide.html#doc-function-raises

# Type Hints (:str, :list, :dict, -> str, -> bool) are not required by Python
#  but help ensure your code has consistent usage and can drastically reduce bugs.
#  IDEs can also use type hints to surface errors and inconsistencies to developers
#  before any code is run
