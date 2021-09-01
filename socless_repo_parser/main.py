import json, os
from socless_repo_parser.constants import GHE_DOMAIN
from typing import List, Union
from socless_repo_parser.parse_python import build_parsed_function
from socless_repo_parser.parse_yml import parse_yml
from socless_repo_parser.github import (
    get_lambda_folders_data,
    fetch_raw_function,
    fetch_raw_serverless_yml,
)
from socless_repo_parser.models import AllIntegrations, IntegrationFamily, RepoNameInfo
from urllib.parse import urlparse


def parse_repo_names(
    cli_repo_input: Union[List, str], default_org="", ghe=False
) -> List[RepoNameInfo]:
    """Parse CLI string into a list of repo names and orgs. If no org is supplied, use the default org.

    Example repo names:
        "socless" (will use the default_org)
        "noxasaxon/socless"
        "https://github.com/noxasaxon/socless"
    """
    if isinstance(cli_repo_input, str):
        cli_repo_input = cli_repo_input.split(",")
    repos = [name.strip() for name in cli_repo_input]

    all_repos = []
    for repo in repos:
        parsed = urlparse(repo)
        repo_path = parsed.path

        # if supplied with a full url, path will have a leading /
        repo_path = repo_path[1:] if repo_path.startswith("/") else repo_path
        repo_path = repo_path.split("/")

        if len(repo_path) < 2:
            # no full url supplied. build url from context
            if ghe:
                domain = os.getenv(GHE_DOMAIN, "<no_enterprise_domain>")
            else:
                domain = "github.com"
            name = repo_path[0]
            url = f"https://{domain}/{default_org}/{name}"
            repo_name_info = RepoNameInfo(name=name, org=default_org, url=url)
        else:
            repo_name_info = RepoNameInfo(name=repo_path[1], org=repo_path[0], url=repo)
        all_repos.append(repo_name_info)

    return all_repos


def check_if_ghe(repo_url: str):
    domain = os.getenv("GHE_DOMAIN")
    if domain:
        return domain in repo_url
    return False


def build_socless_info(
    repos: Union[List, str],
    default_org: str = "twilo-labs",
    ghe: bool = False,
    output_file_path: str = "socless_info",
) -> AllIntegrations:
    repos = parse_repo_names(repos, default_org=default_org)
    print(f"fetching socless info for: {repos}")

    all_integrations = AllIntegrations()
    for repo_name_obj in repos:
        integration_family = IntegrationFamily()
        sub_ghe = ghe or check_if_ghe(repo_name_obj.url)

        # TODO: make this pull from serverless 'service' name
        integration_family.meta.integration_family = repo_name_obj.name

        integration_family.meta.repo_url = repo_name_obj.url

        # get serverless.yml function info, names
        raw_yml = fetch_raw_serverless_yml(
            repo_name_obj.name, repo_name_obj.org, ghe=sub_ghe
        )
        all_serverless_fn_meta = parse_yml(raw_yml)

        for folder_data in get_lambda_folders_data(
            repo_name_obj.name, repo_name_obj.org, ghe=sub_ghe
        ):
            dir_name = folder_data["name"]
            if dir_name not in all_serverless_fn_meta.functions:
                print(
                    f"File exists for function {dir_name}, but it is not used in serverless.yml. Skip saving info for {dir_name}."
                )
                continue

            raw_function = fetch_raw_function(
                folder_data, repo_name_obj.name, repo_name_obj.org, ghe=sub_ghe
            )

            function_info = build_parsed_function(
                meta_from_yml=all_serverless_fn_meta.functions[dir_name],
                py_file_string=raw_function,
            )

            integration_family.functions.append(function_info)
        all_integrations.integrations.append(integration_family)

    if output_file_path and isinstance(output_file_path, str):
        root, ext = os.path.splitext(output_file_path)
        ext = ext if ext else ".json"
        with open(f"{root}{ext}", "w") as f:
            f.write(json.dumps(all_integrations.dict(), indent=4))
    else:
        print(json.dumps(all_integrations.dict()))

    return all_integrations
