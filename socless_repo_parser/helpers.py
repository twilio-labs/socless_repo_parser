import os
from getpass import getpass
from urllib.parse import urlparse
from typing import List, Optional, Union
from github.MainClass import Github
from socless_repo_parser.constants import GH_TOKEN, GHE_DOMAIN, GHE_TOKEN
from socless_repo_parser.models import RepoMetadata


class RepoParserError(Exception):
    pass


class SoclessGithubWrapper:
    def __init__(self) -> None:
        self.github: Union[Github, None] = None
        self.github_enterprise: Union[Github, None] = None

    def get_or_init_github(self, token: str = "", required: bool = False) -> Github:
        """If required=True, will prompt for user's PAT if none provided."""
        if not self.github or (required and not is_github_authenticated(self.github)):
            env_token = os.getenv("GH_TOKEN")

            if token:
                self.github = Github(login_or_token=token)
            elif env_token:
                self.github = Github(login_or_token=env_token)

            if required and not is_github_authenticated(self.github):
                pat_token = token or get_secret(
                    GH_TOKEN,
                    "Personal Access Token authorized for Github.com",
                )
                self.github = Github(login_or_token=pat_token)

            if not self.github:
                self.github = Github()
        return self.github

    def get_or_init_github_enterprise(
        self, token: str = "", domain: str = ""
    ) -> Github:
        if self.github_enterprise is None:
            ghe_domain = domain or get_secret(
                GHE_DOMAIN, "Github Enterprise Domain (instead of github.com)"
            )
            base_url = f"https://{ghe_domain}/api/v3"
            pat_token = token or get_secret(
                GHE_TOKEN,
                "Personal Access Token authorized for the github enterprise domain",
            )
            self.github_enterprise = Github(base_url=base_url, login_or_token=pat_token)
        return self.github_enterprise


def get_github_domain(gh: Github) -> str:
    """Use private class attributes to get existing base_url domain."""
    base_url = gh._Github__requester._Requester__base_url  # type: ignore
    parsed = urlparse(base_url)
    if not isinstance(parsed.hostname, str):
        raise RepoParserError(
            "Unable to get domain from pygithub enterprise Github class"
        )
    return parsed.hostname


def is_github_authenticated(gh: Optional[Github]) -> bool:
    """Use private class attributes to check if authenticated to github."""
    if not gh:
        return False
    if gh._Github__requester._Requester__authorizationHeader:  # type: ignore
        return True
    return False


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
