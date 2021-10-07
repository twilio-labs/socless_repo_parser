from typing import List, Union
from socless_repo_parser.builders import SoclessInfoBuilder
from socless_repo_parser.models import AllIntegrations

# import this to re-export for dependencies & type-checking
from github import Github  # noqa


# deprecated, will be replaced by _from_github_cli
def build_socless_info_from_cli(
    repos: Union[List, str],
    ghe: bool = False,
    output_file_path: str = "socless_info",
) -> AllIntegrations:

    if ghe:
        all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repos)
    else:
        all_integrations = SoclessInfoBuilder().build_from_github(repos)

    if output_file_path and isinstance(output_file_path, str):
        all_integrations.write_info_to_file(output_file_path)

    return all_integrations


# duplicating, this is new function
def build_socless_info_from_github_cli(
    repos: Union[List, str],
    ghe: bool = False,
    output_file_path: str = "socless_info",
) -> AllIntegrations:

    if ghe:
        all_integrations = SoclessInfoBuilder().build_from_github_enterprise(repos)
    else:
        all_integrations = SoclessInfoBuilder().build_from_github(repos)

    if output_file_path and isinstance(output_file_path, str):
        all_integrations.write_info_to_file(output_file_path)

    return all_integrations


def build_socless_info_from_local(dir_paths: List[str]):
    # all_integrations = AllIntegrations()

    ## First, validate all dir_paths
    for socless_dir_path in dir_paths:
        # ensure directory exists
        print(socless_dir_path)
        pass

    ## if validated, build data
    for socless_dir_path in dir_paths:
        print(socless_dir_path)
        pass
        # get serverless.yml from directory

        # get functions

        # build integration info

        # save to all_integrations

    # return all_integrations
    pass
