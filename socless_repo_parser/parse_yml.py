import os
from ruamel.yaml import YAML
from pydantic import BaseModel
from typing import Dict
from socless_repo_parser.constants import LAMBDA_FUNCTION_FILE
from socless_repo_parser.models import SoclessFunctionMeta

yaml = YAML(typ="safe")


class SoclessParsedYml(BaseModel):
    functions: Dict[str, SoclessFunctionMeta] = {}
    # map of deployed_name to function_package_directory
    fn_paths: Dict[str, str] = {}
    service: str = ""

    def get_fn_by_deployed_name(self, deployed_name):
        for fn in self.functions.values():
            if fn.deployed_lambda_name == deployed_name:
                return fn
        raise Exception(f"{deployed_name} not found in SoclessParsedYml.")

    def get_fn_path_github(self, deployed_lambda_name) -> str:
        return f"{self.fn_paths[deployed_lambda_name]}/{LAMBDA_FUNCTION_FILE}"

    def get_fn_path_local(self, deployed_lambda_name) -> str:
        return os.path.join(self.fn_paths[deployed_lambda_name], LAMBDA_FUNCTION_FILE)


def parse_yml(raw_yml) -> SoclessParsedYml:
    """Retrieve relevant SOCless function API info from `serverless.yml`."""
    yml_dict = yaml.load(raw_yml)

    output = SoclessParsedYml()
    output.service = yml_dict["service"]

    yml_functions = yml_dict["functions"]
    for serverless_lambda_name, func_obj in yml_functions.items():
        function_info = SoclessFunctionMeta(
            serverless_lambda_name=serverless_lambda_name,
            lambda_folder_name=func_obj["package"]["include"][0].split("/")[1],
            deployed_lambda_name=func_obj["name"],
        )

        output.fn_paths[function_info.deployed_lambda_name] = func_obj["package"][
            "include"
        ][0]

        output.functions[function_info.lambda_folder_name] = function_info

    # nothing else needed from serverless.yml right now
    return output
