import os
from getpass import getpass
from urllib.parse import urlparse
from typing import List, Union
from github.MainClass import Github
from socless_repo_parser.models import RepoMetadata


def get_github_domain(gh: Github) -> str:
    """Use private class attributes to get existing base_url domain."""
    base_url = gh._Github__requester._Requester__base_url  # type: ignore
    parsed = urlparse(base_url)
    assert isinstance(parsed.hostname, str)
    return parsed.hostname


def get_secret(env_name: str = "", prompt: str = ""):
    secret = os.getenv(env_name) if env_name else ""
    if not secret:
        # get secret from user via cli (do not expose to terminal)
        prompt = (
            prompt
            or f"Please enter the value for {env_name} (this will not expose to terminal)"
        )
        secret = getpass(f"No env variable found for {env_name}. {prompt}: ")
    return secret


def parse_repo_names(cli_repo_input: Union[List, str]) -> List[RepoMetadata]:
    """Parse CLI string into a list of repo names and orgs. If no org is supplied, use the default org.

    Example repo names:
        "noxasaxon/socless"
        "https://github.com/noxasaxon/socless"
    """
    if isinstance(cli_repo_input, str):
        cli_repo_input = cli_repo_input.split(",")
    repo_identifiers = [name.strip() for name in cli_repo_input]

    all_repos = []
    for repo_id_string in repo_identifiers:
        parsed = urlparse(repo_id_string)
        repo_path = parsed.path

        # if supplied with a full url, path will have a leading /
        repo_path = repo_path[1:] if repo_path.startswith("/") else repo_path
        repo_path = repo_path.split("/")

        if len(repo_path) < 2:
            raise ValueError("Must supply either the full url OR <org>/<name>")

        org = repo_path[0]
        name = repo_path[1]
        if parsed.hostname:
            # full url was given
            url = repo_id_string
        else:
            url = f"https://github.com/{org}/{name}"

        repo_name_info = RepoMetadata(name=repo_path[1], org=repo_path[0], url=url)
        all_repos.append(repo_name_info)

    return all_repos
