import json, os
from typing import List, Union
from github import Github
from socless_repo_parser.parse_python import build_parsed_function
from socless_repo_parser.parse_yml import parse_yml
from socless_repo_parser.github import (
    get_lambda_folders_data,
    fetch_raw_function,
    fetch_raw_serverless_yml,
)
from socless_repo_parser.models import AllIntegrations, IntegrationFamily, RepoMetadata
from socless_repo_parser.helpers import parse_repo_names, is_repo_ghe


class SoclessInfoBuilder:
    def __init__(self) -> None:
        self.github = None
        self.github_enterprise = None

    def build_no_credentials(self, repo_list):
        pass

    def build_github_enterprise(self, repo_list):
        pass


def build_integration_family(
    repo_name_info: RepoMetadata, ghe=False
) -> IntegrationFamily:
    integration_family = IntegrationFamily()
    sub_ghe = ghe or is_repo_ghe(repo_name_info.url)

    # TODO: make this pull from serverless 'service' name
    integration_family.meta.integration_family = repo_name_info.name

    integration_family.meta.repo_url = repo_name_info.url

    # get serverless.yml function info, names
    raw_yml = fetch_raw_serverless_yml(
        repo_name_info.name, repo_name_info.org, ghe=sub_ghe
    )
    all_serverless_fn_meta = parse_yml(raw_yml)

    for folder_data in get_lambda_folders_data(
        repo_name_info.name, repo_name_info.org, ghe=sub_ghe
    ):
        dir_name = folder_data["name"]
        if dir_name not in all_serverless_fn_meta.functions:
            print(
                f"File exists for function {dir_name}, but it is not used in serverless.yml. Skip saving info for {dir_name}."
            )
            continue

        raw_function = fetch_raw_function(
            folder_data, repo_name_info.name, repo_name_info.org, ghe=sub_ghe
        )

        function_info = build_parsed_function(
            meta_from_yml=all_serverless_fn_meta.functions[dir_name],
            py_file_string=raw_function,
        )

        integration_family.functions.append(function_info)

    return integration_family


def write_info_to_file(
    all_integrations: AllIntegrations,
    file_path: str = "socless_info",
):
    root, ext = os.path.splitext(file_path)
    ext = ext if ext else ".json"
    with open(f"{root}{ext}", "w") as f:
        f.write(json.dumps(all_integrations.dict(), indent=4))


def build_socless_info_from_cli(
    repos: Union[List, str],
    default_org: str = "twilo-labs",
    ghe: bool = False,
    output_file_path: str = "socless_info",
) -> AllIntegrations:
    repo_names = parse_repo_names(repos, default_org=default_org)
    print(f"fetching socless info for: {[x.name for x in repo_names]}")

    all_integrations = AllIntegrations()
    all_integrations.integrations = [
        build_integration_family(r_name, ghe) for r_name in repo_names
    ]

    if output_file_path and isinstance(output_file_path, str):
        write_info_to_file(all_integrations, output_file_path)

    return all_integrations


def build_integrations_from_pygithub(
    repos: Union[List, str], ghe_github: Github = None, ghe_domain: str = None
) -> AllIntegrations:
    """Use an already created pygithub instance"""
    pass
