import time
from socless_repo_parser.constants import (
    FUNCTIONS_DIR_PATH,
    GHE_DOMAIN,
    GHE_TOKEN,
    LAMBDA_FUNCTION_FILE,
    SERVERLESS_YML,
)
from typing import List, Union
from github import Github
from socless_repo_parser.parse_python import build_parsed_function
from socless_repo_parser.parse_yml import parse_yml
from socless_repo_parser.models import AllIntegrations, IntegrationFamily, RepoMetadata
from socless_repo_parser.helpers import (
    get_github_domain,
    get_secret,
    parse_repo_names,
)


def build_integration_family(
    repo_name_info: RepoMetadata, github_instance: Github
) -> IntegrationFamily:
    integration_family = IntegrationFamily()

    # TODO: make this pull from serverless 'service' name
    integration_family.meta.integration_family = repo_name_info.name

    integration_family.meta.repo_url = repo_name_info.url

    # get repo object
    gh_repo = github_instance.get_repo(f"{repo_name_info.org}/{repo_name_info.name}")

    # get serverless.yml
    file_contents = gh_repo.get_contents(SERVERLESS_YML)
    assert not isinstance(file_contents, list)
    raw_yml: bytes = file_contents.decoded_content

    # get serverless.yml function info, names
    all_serverless_fn_meta = parse_yml(raw_yml)

    time.sleep(1)  # ratelimit prevention

    # ./functions is a folder containing folders and a `requirements.txt`
    functions_dir_contents = gh_repo.get_contents(FUNCTIONS_DIR_PATH)
    assert isinstance(functions_dir_contents, list)
    functions_folders = [x for x in functions_dir_contents if x.type == "dir"]

    for lambda_folder in functions_folders:
        if lambda_folder.name not in all_serverless_fn_meta.functions:
            print(
                f"File exists for function {lambda_folder.name}, but it is not used in serverless.yml. Skipping file."
            )
            continue

        time.sleep(1)  # ratelimit prevention
        raw_lambda = gh_repo.get_contents(
            f"{lambda_folder.path}/{LAMBDA_FUNCTION_FILE}"
        )
        assert not isinstance(raw_lambda, list)

        function_info = build_parsed_function(
            meta_from_yml=all_serverless_fn_meta.functions[lambda_folder.name],
            py_file_string=raw_lambda.decoded_content,
        )

        integration_family.functions.append(function_info)

    return integration_family


class SoclessInfoBuilder:
    def __init__(self) -> None:
        self.github = None
        self.github_enterprise = None

    def get_or_init_github(self, token: str = "") -> Github:
        if not self.github:
            if token:
                self.github = Github(login_or_token=token)
            else:
                self.github = Github()
        return self.github

    def get_or_init_github_enterprise(
        self, token: str = "", domain: str = ""
    ) -> Github:
        if not self.github_enterprise:
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

    def build_from_github(
        self, repo_list: Union[str, List[str]], token: str = ""
    ) -> AllIntegrations:
        """For a list of repos, build socless info."""
        all_integrations = AllIntegrations()

        repos_meta_info = parse_repo_names(cli_repo_input=repo_list)
        for repo_meta in repos_meta_info:
            time.sleep(0.5)
            integration_family = build_integration_family(
                repo_meta, self.get_or_init_github(token)
            )
            all_integrations.integrations.append(integration_family)

        return all_integrations

    def build_from_github_enterprise(
        self,
        repo_list: Union[str, List[str]],
        token: str = "",
        domain: str = "",
    ) -> AllIntegrations:
        """If user already has GHE pygithub instance, use it. otherwise create it from env vars or terminal"""
        self.get_or_init_github_enterprise(token, domain)
        assert self.github_enterprise

        # use private attributes to get the github enterprise domain
        ghe_domain = get_github_domain(self.github_enterprise)

        all_integrations = AllIntegrations()

        repos_meta_info = parse_repo_names(cli_repo_input=repo_list)

        for repo_meta in repos_meta_info:
            if ghe_domain in repo_meta.url:
                integration_family = build_integration_family(
                    repo_meta, self.get_or_init_github_enterprise()
                )
            else:
                integration_family = build_integration_family(
                    repo_meta, self.get_or_init_github()
                )

            all_integrations.integrations.append(integration_family)

        return all_integrations
