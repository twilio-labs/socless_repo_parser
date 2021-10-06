# SOCless Template 
Template Repository 

# Requirements
- Node.js
- Python 3.7
- AWS account and IAM profile configured with Programmatic access
- Socless Core Stack deployed in AWS

# Usage

## Setup
```bash
$ git clone https://github.com/twilio-labs/socless-template.git
$ cd socless-template
$ npm install
```

## Rename Template With New Integration Name
```bash
npm run rename
```

## Deployment to AWS 
```bash
$ npm run [dev|stage|prod|sandbox]
```

# Testing

## Unit Tests
```bash
$ npm run test
```
**Note:** Requires Python 3.7 to accurately reflect the environment used by these lambda functions


# Stack Outputs

| Output                         | Type                | Description                                            |
|--------------------------------|---------------------|--------------------------------------------------------|
| SendOldTimeyTelegram           | Lambda Function ARN | ARN of mock socless integration for example use        |
| ServerlessDeploymentBucketName | S3 Bucket name      | S3 bucket used by Serverless to deploy the integration |

## Tips for Writing SOCless Integrations


- **Use the `./common_files` folder to share code between all your lambda functions**
  - Any files in this folder will be packaged with each lambda function, allowing you to write generic helper functions and constants that only need to be written once and imported by the lambdas that need them.

- `handle_state` must always return a Dict, but feel free to add multiple fields that could be useful in current & future playbooks
  - When writing a playbook function, try to think of all the useful data that this function generates from its input that might be helpful to reference later, and add it under a descriptive key in the return dict. 

- Use [Type Hints](https://www.pythonsheets.com/notes/python-typing.html#basic-types) for your function definitions, it will only make things easier to debug and reference later


### (OPTIONAL) - Setting up VSCode for optimal python development
#### Setup your python installation
1. Ensure you have Python 3.7 installed
2. `pip install black`
   1. This is an opinionated Python linter that will ensure your code is formatted correctly
3. `pip install flake8`
4. `pip install flake8-bugbear`
   1. better error messaging that pairs well with `pylance` language server and `black`
5. `git+https://github.com/twilio-labs/socless_python.git#egg=socless`
   1. _Optional_ but this will allow VSCode to provide syntax hints and descriptions for `socless_python` functions used in your lambda functions


#### Install the following recommended extensions 
_(Search with extension ID in the VSCode extensions tab)_

Extension ID                       | Description
---------------------------------- | -------------
`ms-python.python`                   | Basic Python support for VSCode
`ms-python.vscode-pylance`           | a fast, enhanced language server that type checks and lints automatically
`noxasaxon.socless-visualizer`       | An alpha tool for socless-specific visualization of `playbook.json` files
`paulshestakov.aws-step-functions-constructor` | A polished tool for visualizing Step Functions json definitions (but does not include any socless specific code)
`bungcip.better-toml`                | (_optional_) `.toml` language syntax highlighting
`redhat.vscode-yaml`                 | (_optional_) `.yaml` language syntax highlighting
`coenraads.bracket-pair-colorizer-2` | (_optional_) `{([])}` will no longer be the same color, pairs will be matching colors for easier debugging missing parentheses, brackets etc and also for better reading in general
`oderwat.indent-rainbow`             | (_optional_) Each indent will be a different highlighted color, to easily tell how nested python code is. also will highlight red if code is not indented with the current file's default (helps find bad indents which would raise an error)

#### Setup your VSCode `settings.json` file 
This will turn on advanced python language server capabilities, allow VSCode to view [./common_files](./common_files) python files as valid modules for importing in lambda functions, run `black` linter on every `.py` file save, and keep things fast by exempting temporary build folders from analysis.

- Press `CMD + ,` to open your settings UI.
- Click the document icon in the top right to open `settings.json`
- Copy over the following code and save the file:
```json
    "python.formatting.provider": "black",
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--select=B,C,E,F,W,T4,B9",
        "--ignore=E203,E266,E265,E501,E401,W503,B950"
    ],
    "python.languageServer": "Pylance",
    "python.analysis.extraPaths": [
        "./common_files"
    ],
    "python.analysis.diagnosticMode": "workspace",
    "python.analysis.typeCheckingMode": "basic",
    "files.watcherExclude": {
        "**/build/**": true
    },
    "search.exclude": {
        "**/build/**": true
    },
```
