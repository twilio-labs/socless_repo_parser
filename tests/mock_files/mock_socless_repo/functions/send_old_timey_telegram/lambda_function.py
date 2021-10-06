# This is an example of how you can write a lambda function for the SOCless Framework.
#
# At the bare minimum, a SOCless lambda must include the following:
#
# ```
# from socless import socless_bootstrap
# def handle_state(<arguments_go_here>) -> dict:
#     return {}
#
# def lambda_handler(event, context):
#    return socless_bootstrap(event, context, handle_state, include_event=True)
# ```

import os
from socless import socless_bootstrap
from template_helpers import SoclessTemplateError


### a mock api call function
def send_telegram(message) -> bool:
    """An example of a function that will fail if run outside of AWS."""
    try:
        example_that_will_fail_on_local_machine = os.environ["_HANDLER"]
        print(example_that_will_fail_on_local_machine)
        return True
    except Exception:
        raise SoclessTemplateError(
            f"no connection to telephone lines, unable to send: {message}"
        )


### a function that handle_state will use to build messages before they are sent
### to an external API call
def build_telegram(name: str, message: str, title="Dr") -> str:
    """Generate a properly formatted telegram message body.

    Args:
        name:    The recipient of this telegram
        message: The message to send this user
        title:   The recipient's title
    Returns:
        A properly formatted string for a telegram message
    """
    STOP = " -STOP- "
    punctuation = [".", ",", "!"]

    for symbol in punctuation:
        message = message.replace(symbol, STOP)

    greeting = f"ATTN {title} {name}{STOP} "

    telegram = f"{greeting}{message}".upper()
    return telegram


### handle_state is the start of your customized integration.
### handle_state MUST return a Python Dictionary type.
def handle_state(name: str, message: str, title="Dr") -> dict:
    """Compose and send an old timey telegram message.
    Args:
        name:    The recipient of this telegram
        message: The message to send this user
        title:   The recipient's title
    Returns:
        {
            "telegram" : (str) <a copy of the sent message>
        }
    """
    ## An example of a function that does business logic NOT involving external APIs.
    ##   Dividing your `handle_state` fn into multiple functions that separate
    ##   the business logic from api calls allows you to easily write unit tests with limited "mocking".
    ##   API calls will be tested as part of the Integration Test Playbook.
    telegram = build_telegram(name, message, title)

    # an example of an external API call function your lambda uses,
    #  that will fail outside of an AWS deployment (needs to be mocked in testing)
    send_telegram(telegram)

    output_to_playbook = {"telegram": telegram}
    return output_to_playbook


## lambda_handler is the entrypoint for this file, but SHOULD NOT contain any integration logic.
## lambda_handler calls socless_bootstrap which will take the `event` from your playbook and
##  match it up to the global playbook state from dynamo_db.
##  socless_bootstrap resolves parameters from the playbook and formats them into KeywordArgs for
##  the handle_state function.
def lambda_handler(event, context):
    return socless_bootstrap(event, context, handle_state, include_event=True)
