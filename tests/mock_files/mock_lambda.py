from socless import socless_bootstrap, socless_template_string
from slack_helpers import slack_client, resolve_slack_target, slack_post_msg_wrapper
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
    """Test file for the python parser"""

    test = "success"

    return {"response": test}


def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
