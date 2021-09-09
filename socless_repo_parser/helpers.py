import os
from getpass import getpass
from urllib.parse import urlparse
from typing import List, Union
from socless_repo_parser.constants import GHE_DOMAIN
from socless_repo_parser.models import RepoMetadata


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


def is_repo_ghe(repo_url: str, domain: Union[str, None] = ""):
    """Check if repo is from Github Enterprise."""
    domain = domain or os.getenv(GHE_DOMAIN)
    if domain:
        return domain in repo_url
    return False


def parse_repo_names(
    cli_repo_input: Union[List, str], default_org="", ghe=False
) -> List[RepoMetadata]:
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
            repo_name_info = RepoMetadata(name=name, org=default_org, url=url)
        else:
            repo_name_info = RepoMetadata(name=repo_path[1], org=repo_path[0], url=repo)
        all_repos.append(repo_name_info)

    return all_repos


def parse_repo_names_v2(
    cli_repo_input: Union[List, str], default_org="", ghe_domain: str = ""
) -> List[RepoMetadata]:
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
            domain = ghe_domain if ghe_domain else "github.com"
            if ghe_domain:
                domain = os.getenv(GHE_DOMAIN, "<no_enterprise_domain>")
            else:
                domain = "github.com"
            name = repo_path[0]
            url = f"https://{domain}/{default_org}/{name}"
            repo_name_info = RepoMetadata(name=name, org=default_org, url=url)
        else:
            repo_name_info = RepoMetadata(name=repo_path[1], org=repo_path[0], url=repo)
        all_repos.append(repo_name_info)

    return all_repos
