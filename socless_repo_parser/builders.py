import json, os
from socless_repo_parser.constants import GHE_DOMAIN, GHE_TOKEN
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
from socless_repo_parser.helpers import (
    get_secret,
    parse_repo_names,
    is_repo_ghe,
    parse_repo_names_v2,
)


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


def build_integration_family_v2(
    repo_name_info: RepoMetadata, github_instance: Github
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


class SoclessInfoBuilder:
    def __init__(self) -> None:
        self.github = None
        self.github_enterprise = None

    def build_no_credentials(self, repo_list):
        pass

    def build_github_enterprise(
        self,
        repo_list: Union[str, List[str]],
        github_enterprise: Github = None,
        domain: str = None,
    ):
        """If user already has GHE pygithub instance, use it. otherwise create it from env vars or terminal"""

        if github_enterprise:
            ghe_domain = github_enterprise.__requester.__base_url
            raise NotImplementedError(
                "This needs to be parsed for just the domain, not full url"
            )
        else:
            ghe_domain = get_secret(
                GHE_DOMAIN, "Github Enterprise Domain (instead of github.com)"
            )
            base_url = f"https://{ghe_domain}/api/v3"
            pat_token = get_secret(
                GHE_TOKEN,
                "Personal Access Token authorized for the github enterprise domain",
            )
            self.github_enterprise = Github(base_url=base_url, login_or_token=pat_token)

        repo_names = parse_repo_names_v2(repo_list, ghe_domain)
        all_integrations = AllIntegrations()
        pass
