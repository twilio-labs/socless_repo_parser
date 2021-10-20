import pytest
from template_helpers import SoclessTemplateError
from functions.send_old_timey_telegram import lambda_function
from functions.send_old_timey_telegram.lambda_function import (
    build_telegram,
    handle_state,
)


# This is an example of a way you can test a lambda function's logic without mocking an external API call.
#  By separating handle_state in to multiple functions, you can create easy unit tests and leave the API
#  tests to your deployed Integration Test Playbook.
def test_build_telegram_default_title():
    telegram_message = build_telegram(
        "Elias Kronish", "we are looking forward to the annual christmas party."
    )

    expected_telegram = "ATTN DR ELIAS KRONISH -STOP-  WE ARE LOOKING FORWARD TO THE ANNUAL CHRISTMAS PARTY -STOP- "
    assert telegram_message == expected_telegram


def test_example_handle_state_without_mock_api_call_will_fail():
    # This fails because we are trying to use a function that doesnt work on local machines.
    # For example, when a fn requires interacting with services such as Jira or Slack, its not
    # recommended to create testing artifacts on external services every time a unit test is run.
    # The Integration Test Playbook can use credentials deployed to SSM and runs the deployed
    # lambda in your dev environment, allowing test coverage of live api calls before deployment to production.
    with pytest.raises(SoclessTemplateError):
        _ = handle_state(
            "Elias Kronish", "we are looking forward to the annual christmas party."
        )


# https://docs.pytest.org/en/stable/monkeypatch.html
def test_handle_state_with_monkeypatch_to_prevent_failure_of_external_api_call(
    monkeypatch,
):
    expected_telegram_message = "ATTN DR ELIAS KRONISH -STOP-  WE ARE LOOKING FORWARD TO THE ANNUAL CHRISTMAS PARTY -STOP- "

    # The REAL lambda_function.send_telegram function returns a bool True
    #  when it succeeds, so we replicate that here too.
    def mock_send_telegram(telegram):
        assert telegram == expected_telegram_message
        return True

    # assign our mock send telegram function to overwrite the real send_telegram in this test
    monkeypatch.setattr(lambda_function, "send_telegram", mock_send_telegram)

    # run the now modified handle_state
    send_telegram_lambda_output = handle_state(
        "Elias Kronish", "we are looking forward to the annual christmas party."
    )
    assert send_telegram_lambda_output["telegram"] == expected_telegram_message
