import os
import time, json
from github.Repository import Repository
from socless_repo_parser.constants import (
    LAMBDA_FUNCTION_FILE,
    PACKAGE_JSON,
    SERVERLESS_YML,
)
from typing import ByteString, Dict, List, Union

from socless_repo_parser.parse_python import build_parsed_function
from socless_repo_parser.parse_yml import SoclessParsedYml, parse_yml
from socless_repo_parser.models import (
    AllIntegrations,
    IntegrationFamily,
    IntegrationMeta,
)
from socless_repo_parser.helpers import (
    RepoParserError,
    SoclessGithubWrapper,
    get_github_domain,
    parse_repo_names,
)


def validate_dir_path(dir_path: str):
    if not os.path.exists(dir_path):
        raise Exception(f"{dir_path} does not exist.")
    if not os.path.isdir(dir_path):
        raise Exception(f"{dir_path} is not a directory.")


class BuilderError(Exception):
    pass


class IntegrationFamilyBuilder:
    def build_from_github(self, gh_repo: Repository) -> IntegrationFamily:
        parsed_yml = self._fetch_and_parse_serverless_yml_from_github(gh_repo)
        raw_lambda_files = self._fetch_raw_lambda_files_from_github(gh_repo, parsed_yml)
        meta = IntegrationMeta(
            repo_url=gh_repo.html_url, integration_family=parsed_yml.service
        )
        return self._parse_lambdas_and_build_family(parsed_yml, raw_lambda_files, meta)

    def build_from_local(self, local_dir_path: str) -> IntegrationFamily:
        parsed_yml = self._fetch_and_parse_serverless_from_local(local_dir_path)
        raw_lambda_files = self._fetch_raw_lambda_files_from_local(
            local_dir_path, parsed_yml
        )

        # use package.json "homepage" to get repo url. raise error if not set (no url means no links to code)
        pkg_json = self._fetch_pkg_json_from_local(local_dir_path)
        try:
            repo_url = pkg_json["homepage"]
        except KeyError:
            raise BuilderError(
                f"To build from local, you must set `homepage` as the repo url in package.json. Missing homepage for {parsed_yml.service} at path {local_dir_path}"
            )

        meta = IntegrationMeta(repo_url=repo_url, integration_family=parsed_yml.service)
        return self._parse_lambdas_and_build_family(parsed_yml, raw_lambda_files, meta)

    def _parse_lambdas_and_build_family(
        self,
        parsed_yml: SoclessParsedYml,
        raw_lambda_files: Dict[str, ByteString],
        meta: IntegrationMeta,
    ) -> IntegrationFamily:
        integration_family = IntegrationFamily(meta=meta)
        for deployed_name, raw_lambda in raw_lambda_files.items():

            function_info = build_parsed_function(
                meta_from_yml=parsed_yml.get_fn_by_deployed_name(deployed_name),
                py_file_string=raw_lambda,
            )

            integration_family.functions.append(function_info)

        integration_family.fill_missing_arg_descriptions()
        return integration_family

    def _fetch_and_parse_serverless_yml_from_github(
        self, gh_repo: Repository
    ) -> SoclessParsedYml:
        file_contents = gh_repo.get_contents(SERVERLESS_YML)
        if isinstance(file_contents, list):
            raise RepoParserError(
                f"Github Path {SERVERLESS_YML} may have pointed to a directory, multiple files returned for serverless.yml contents query."
            )
        raw_yml: bytes = file_contents.decoded_content
        return parse_yml(raw_yml)

    def _fetch_raw_lambda_files_from_github(
        self, gh_repo: Repository, parsed_yml: SoclessParsedYml
    ) -> Dict[str, ByteString]:
        raw_lambda_files: Dict[str, ByteString] = {}

        for fn_meta in parsed_yml.functions.values():
            lambda_path = f"{parsed_yml.fn_paths[fn_meta.deployed_lambda_name]}/{LAMBDA_FUNCTION_FILE}"
            time.sleep(1)  # ratelimit prevention
            raw_lambda = gh_repo.get_contents(lambda_path)

            if isinstance(raw_lambda, list):
                raise RepoParserError(
                    f"Gitub Path {lambda_path} may have pointed to a directory, multiple files returned for serverless.yml contents query."
                )
            else:
                raw_lambda_files[
                    fn_meta.deployed_lambda_name
                ] = raw_lambda.decoded_content

        return raw_lambda_files

    def _fetch_and_parse_serverless_from_local(
        self, local_dir_path: str
    ) -> SoclessParsedYml:
        with open(os.path.join(local_dir_path, SERVERLESS_YML)) as f:
            raw_yml = f.read()
        return parse_yml(raw_yml)

    def _fetch_raw_lambda_files_from_local(
        self, local_dir_path: str, parsed_yml: SoclessParsedYml
    ) -> Dict[str, ByteString]:
        raw_lambda_files: Dict[str, ByteString] = {}

        for fn_meta in parsed_yml.functions.values():
            full_lambda_path = os.path.join(
                local_dir_path,
                parsed_yml.fn_paths[fn_meta.deployed_lambda_name],
                LAMBDA_FUNCTION_FILE,
            )

            with open(full_lambda_path) as f:
                raw_lambda_as_str = f.read()

            raw_lambda_files[fn_meta.deployed_lambda_name] = bytes(
                raw_lambda_as_str, "UTF-8"
            )
        return raw_lambda_files

    def _fetch_pkg_json_from_local(self, local_dir_path):
        with open(os.path.join(local_dir_path, PACKAGE_JSON)) as f:
            pkg_json = f.read()
        return json.loads(pkg_json)


class SoclessInfoBuilder(SoclessGithubWrapper):
    def build_from_github(
        self, repo_list: Union[str, List[str]], token: str = ""
    ) -> AllIntegrations:
        """For a list of repos, build socless info."""
        all_integrations = AllIntegrations()
        for repo_meta in parse_repo_names(cli_repo_input=repo_list):
            time.sleep(0.5)
            gh_repo = self.get_or_init_github(token).get_repo(repo_meta.get_full_name())
            integration_family = IntegrationFamilyBuilder().build_from_github(gh_repo)
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

        # use private attributes to get the github enterprise domain
        ghe_domain = get_github_domain(self.github_enterprise)  # type: ignore

        all_integrations = AllIntegrations()
        for repo_meta in parse_repo_names(cli_repo_input=repo_list):
            if ghe_domain in repo_meta.url:
                gh = self.get_or_init_github_enterprise()
            else:
                gh = self.get_or_init_github()
            gh_repo = gh.get_repo(repo_meta.get_full_name())
            integration_family = IntegrationFamilyBuilder().build_from_github(gh_repo)

            all_integrations.integrations.append(integration_family)

        return all_integrations

    def build_from_local(self, dir_paths: List[str]):
        all_integrations = AllIntegrations()
        for local_repo_path in dir_paths:
            validate_dir_path(local_repo_path)
            integration_family = IntegrationFamilyBuilder().build_from_local(
                local_repo_path
            )
            all_integrations.integrations.append(integration_family)
        return all_integrations
