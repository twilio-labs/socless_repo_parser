FUNCTIONS_DIR_PATH = "functions"
PACKAGE_JSON = "package.json"
SERVERLESS_YML = "serverless.yml"
ONBOARDED_REPOS = "onboarded_repos.json"
REQUIREMENTS_TXT = "requirements.txt"
LAMBDA_FUNCTION_FILE = "lambda_function.py"
GLOBAL_REQUIREMENTS_PATH = f"functions/{REQUIREMENTS_TXT}"
SOCLESS_PYTHON_PIP_PATTERN = r"(.+socless_python.git)(@[.\d]+#)(egg=socless)"
HANDLE_STATE_FN_NAME = "handle_state"
INTERACTION_ARG_NAMES = ["receiver"]
INTERNAL_ARG_NAMES = ["context", "receiver", "event_context"]
GHE_DOMAIN = "GHE_DOMAIN"
GHE_TOKEN = "GHE_TOKEN"
