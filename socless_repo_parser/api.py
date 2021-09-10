from typing import List, Union
from socless_repo_parser.builders import SoclessInfoBuilder
from socless_repo_parser.models import AllIntegrations

# import this to re-export for dependencies & type-checking
from github import Github  # noqa


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
