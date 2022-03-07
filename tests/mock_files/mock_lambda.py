from socless import socless_bootstrap
from typing import List, Optional, Union


def handle_state(
    no_type_info_test,
    str_test: str,
    list_test: list,
    dict_test: dict,
    int_test: int,
    none_test=None,
    empty_dict_test={},
    union_test: Union[str, list] = [],
    optional_test: Optional[str] = "",
    list_typing_test: List[str] = [],
    test_if_hint_overrides_default_none_type: List[str] = None,
    **kwargs,
):
    """Test file for the python parser

    Args:
        no_type_info_test : an argument description

        str_test :
        list_test : an argument description

        dict_test : an argument description
        int_test : an argument description
        none_test: an argument description
        empty_dict_test: an argument description
        union_test : an argument description
        optional_test : an argument description
        list_typing_test : an argument description
        test_if_hint_overrides_default_none_type : an argument description
    """

    test = "success"

    return {"response": test}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
