# socless_repo_parser
Take a list of socless repo names and query the github api for their raw lambda .py files and serverless.yml, parsing key elements into a single json output to build a catalog of all available lambda functions in the ecosystem.

## Usage

By default, output is saved to `./socless_info.json`

### For open source:
```bash
python3 main.py "socless, socless-slack" --org-name="<your_github_organization_or_twilio-labs>"
```

### For Github Enterprise:
First set environment variables for your Github Enterprise Domain and a Personal Access Token
```bash
export GHE_DOMAIN=<Your_GHE_Domain.com>
export GHE_TOKEN=<Personal_Access_Token>
```
Then run this script with flag `--ghe=True`
```bash
python3 main.py "socless, socless-slack" --org-name="<github_organization>" --ghe=True
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
- [ ] correctly fill out repo_url in integration_family.meta
- [X] add supported_in_playbook to each function.meta
- [ ] correctly fill out supported_in_playbook in each function.meta
- [X] add resource_type (probably by trigger_id arg presence)
  - checks if `"receiver"` arg is present in handle_state
- [X] add `data_type` to each function argument
  - converts python type to json type
  - if no type hint, defaults to null because None == Null but if no hint is specified ast will report that as None too. Not great.
- [X] add `placeholder` to each function argument
- [ ] parse placeholder info from function (docstring?)
- [X] add `internal` boolean to each function argument 
