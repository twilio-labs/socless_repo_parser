from ruamel.yaml import YAML
from pydantic import BaseModel
from typing import Dict
from socless_repo_parser.models import SoclessFunctionMeta

yaml = YAML(typ="safe")


class SoclessParsedYml(BaseModel):
    functions: Dict[str, SoclessFunctionMeta] = {}


def parse_yml(raw_yml) -> SoclessParsedYml:
    """Retrieve relevant SOCless function API info from `serverless.yml`."""
    output = SoclessParsedYml()
    yml_dict = yaml.load(raw_yml)

    yml_functions = yml_dict["functions"]

    for sls_lambda_name, func_obj in yml_functions.items():
        function_info = SoclessFunctionMeta(
            serverless_lambda_name=sls_lambda_name,
            lambda_folder_name=func_obj["package"]["include"][0].split("/")[1],
            deployed_lambda_name=func_obj["name"],
        )

        output.functions[function_info.lambda_folder_name] = function_info

    # nothing else needed from serverless.yml right now
    return output
