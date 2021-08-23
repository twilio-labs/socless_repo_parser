from ruamel.yaml import YAML
from pydantic import BaseModel
from typing import Dict
from src.models import SoclessFunctionMeta

yaml = YAML(typ="safe")


class ParseYmlOutput(BaseModel):
    # functions: List[SoclessFunctionMeta] = []
    functions: Dict[str, SoclessFunctionMeta] = {}


def parse_yml(raw_yml) -> ParseYmlOutput:
    output = ParseYmlOutput()
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
