# socless_repo_parser
Take a list of socless repo names and query the github api for their raw lambda .py files and serverless.yml, parsing key elements into a single json output to build a catalog of all available lambda functions in the ecosystem.

## Usage from CLI

By default, output is saved to `./socless_info.json`

### For open source:
```sh
python3 main.py "twilio-labs/socless, noxasaxon/socless-slack, https://github.com/twilio-labs/socless-sumologic"
```

### For Github Enterprise:
Option 1:
Pass credentials via environment variables for your Github Enterprise Domain and a Personal Access Token
```sh
export GHE_DOMAIN=<Your_GHE_Domain.com>
export GHE_TOKEN=<Personal_Access_Token>
```
Option 2:
If no env vars are found, the script will ask for your domain & password (without exposing to terminal).

Use the flag `--ghe` to signal the script to check for credentials. Github Enterprise repos will require the full url:

```sh
python3 main.py "twilio-labs/socless, <my_enterprise_domain>.com/twilio-labs/socless-slack" --ghe=True
```

## Usage from Python
```sh
pip3 install "https://github.com/twilio-labs/socless_repo_parser#egg=socless_repo_parser"
```
### Getting the Socless Info output as a class
```python
from socless_repo_parser.api import SoclessInfoBuilder
from socless_repo_parser.models import AllIntegrations

repo_list = ["twilio-labs/socless", "noxasaxon/socless-slack", "https://github.com/twilio-labs/socless-sumologic"]

# For regular github.com
all_integrations = SoclessInfoBuilder().build_from_github(repo_list)
# or with authentication
all_integrations = SoclessInfoBuilder().build_from_github(repo_list, token=<my_token_NOT_HARDCODED>)

# for github enterprise in an interactive script, this will ask for your credentials:
all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repo_list)

# Option 1 for github enterprise in a non-interactive environment:
import os
os.environ["GHE_DOMAIN"] = <my_domain>
os.environ["GHE_TOKEN"] = <my_token_NOT_HARDCODED_please>
all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repo_list)

# Option 2 for github enterprise in a non-interactive environment:
all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repo_list, token=<my_token_NOT_HARDCODED>, domain=<my_domain>)

# if you already have a pygithub Github instance from elsewhere in your app/script:
from github import Github
## set up github
gh = Github() # no auth
gh_authed = Github(login_or_token=<my_token>) # github auth
gh_enterprise = Github(base_url=<my_base_url>, login_or_token=<my_token>) # github enterprise / alternate url

## if enterprise
my_builder = SoclessInfoBuilder()
my_builder.github_enterprise = gh_enterprise
all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repo_list)

## if regular github with auth
my_builder.github = gh_authed
all_integrations = SoclessInfoBuilder().build_from_github(repo_list)
```

### Convert to dict, JSON str, or write to `.json` file
```python
from socless_repo_parser.api import SoclessInfoBuilder
repo_list = ["twilio-labs/socless", ""]

all_integrations = SoclessInfoBuilder().build_from_github(repo_list)

# to dict
all_integrations.dict()

# to json string
all_integrations.json()

# to file
all_integrations.write_info_to_file() # `socless_info.json`
all_integrations.write_info_to_file("my_file_path") # `my_file_path.json`
```

## Example of scraper output
```json
{
    "integrations": [
        {
            "meta": {
                "repo_url": "https://www.github.com/twilio-labs/socless-slack",
                "integration_family": "socless-slack"
            },
            "functions": [
                {
                    "meta": {
                        "lambda_folder_name": "check_user_in_channel",
                        "deployed_lambda_name": "socless_slack_check_user_in_channel",
                        "serverless_lambda_name": "CheckIfUserInChannel",
                        "supported_in_playbook": true
                    },
                    "resource_type": "socless_task | socless_interaction",
                    "arguments": [
                        {
                            "name": "user_id",
                            "data_type": "string",
                            "required": true,
                            "description": "",
                            "placeholder": "",
                            "internal": false,
                            "default_value": "<no_default>"
                        },
                        {
                            "name": "target_channel_id",
                            "data_type": "string",
                            "required": true,
                            "description": "",
                            "placeholder": "",
                            "internal": false,
                            "default_value": ""
                        }
                    ],
                    "supports_kwargs": false,
                    "return_statements": [
                        {
                            "ok": true
                        },
                        {
                            "ok": false
                        }
                    ]
                }
            ]
        },
        {
            "meta": {
                "repo_url": "https://www.github.com/twilio-labs/socless",
                "integration_family": "socless"
            }, 
            "functions" : [...]
        }
    ]
}

```

Possible values for argument `data_type`:
```json
- "string"
- "boolean"
- "number"
- "object"
- "null"
- "array<>"
- "union<>"
- "any"
```


# TODO
- [X] convert to lists instead of dicts for output
- [X] add integration_family to integration_family.meta
- [X] add meta to integration family
- [X] add meta to each function
- [X] add repo_url to integration_family.meta
- [X] correctly fill out repo_url in integration_family.meta
- [X] add supported_in_playbook to each function.meta
- [X] correctly fill out supported_in_playbook in each function.meta
- [X] add resource_type (probably by trigger_id arg presence)
  - checks if `"receiver"` arg is present in handle_state
- [X] add `data_type` to each function argument
  - converts python type to json type
  - if no type hint, defaults to null because None == Null but if no hint is specified ast will report that as None too. Not great.
- [X] add `placeholder` to each function argument
- [ ] parse placeholder info from function (docstring?)
- [X] parse docstrings for arg descriptions
- [X] parse docstrings for `handle_state` descriptions
- [X] add `internal` boolean to each function argument 
