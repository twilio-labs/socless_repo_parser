"""Everything in this file is public API & will be re-exported directly under `socless_repo_parser`."""
from typing import List, Union
from socless_repo_parser.builders import SoclessInfoBuilder, validate_dir_path

# import these to re-export for dependencies & type-checking
from socless_repo_parser.models import AllIntegrations, RepoMetadata  # noqa
from socless_repo_parser.constants import GH_TOKEN, GHE_DOMAIN, GHE_TOKEN  # noqa
from github import Github  # noqa
from socless_repo_parser.helpers import (  # noqa
    SoclessGithubWrapper,  # noqa
    parse_repo_names,  # noqa
    get_github_domain,  # noqa
    is_github_authenticated,  # noqa
)


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
def build_from_github(
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


def build_from_local(dir_paths: List[str]):
    # all_integrations = AllIntegrations()

    ## First, validate all dir_paths
    for socless_dir_path in dir_paths:
        # ensure directory exists
        validate_dir_path(socless_dir_path)

    ## if validated, build data
    all_integrations = SoclessInfoBuilder().build_from_local(dir_paths)
    return all_integrations
