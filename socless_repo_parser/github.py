from typing import ByteString
import requests, os, time


def github_request_wrapper(url, ghe=False):
    time.sleep(1)  # ratelimit prevention
    if ghe:
        resp = requests.get(
            url, headers={"Authorization": f'token {os.getenv("GHE_TOKEN")}'}
        )
    else:
        resp = requests.get(url)

    resp.raise_for_status()
    return resp


def build_serverless_yml_url(
    repo_name, org_name="twilio-labs", branch="master", ghe=False
):

    if ghe:
        domain = os.getenv("GHE_DOMAIN", "api.github.com")
        base_url = f"https://{domain}/api/v3"

        file_meta_url = f"{base_url}/repos/{org_name}/{repo_name}/contents/serverless.yml?ref=master"

        file_meta_resp = github_request_wrapper(file_meta_url, ghe)

        raw_file_url = file_meta_resp.json()["download_url"]
    else:
        raw_file_url = f"https://raw.githubusercontent.com/{org_name}/{repo_name}/{branch}/serverless.yml"
    return raw_file_url


def fetch_raw_serverless_yml(
    repo_name, org_name="twilio-labs", branch="master", ghe=False
):
    raw_file_url = build_serverless_yml_url(repo_name, org_name, branch, ghe)
    api_response = github_request_wrapper(raw_file_url, ghe)

    raw_file = api_response.content
    return raw_file


def get_lambda_folders_data(repo_name, org_name="twilio-labs", ghe=False):
    if ghe:
        domain = os.getenv("GHE_DOMAIN", "api.github.com")
        base_url = f"https://{domain}/api/v3"
    else:
        base_url = "https://api.github.com"

    functions_folder_url = (
        f"{base_url}/repos/{org_name}/{repo_name}/contents/functions?ref=master"
    )

    api_resp = github_request_wrapper(functions_folder_url, ghe)
    api_resp = api_resp.json()

    return [x for x in api_resp if x["type"] == "dir"]


def fetch_raw_function(
    function_git_meta,
    repo_name,
    org_name="twilio-labs",
    branch="master",
    file_name="lambda_function.py",
    ghe=False,
) -> ByteString:
    # first get the Raw file url
    if ghe:
        # need to get the raw token, can't assume url structure
        lambda_dir_url = function_git_meta["url"]
        lambda_dir_resp = github_request_wrapper(lambda_dir_url, ghe)
        raw_file_url = ""
        for file in lambda_dir_resp.json():
            if file_name in file["download_url"]:
                raw_file_url = file["download_url"]
                break

    else:
        dir_name = function_git_meta["name"]
        raw_file_url = f"https://raw.githubusercontent.com/{org_name}/{repo_name}/{branch}/functions/{dir_name}/{file_name}"

    # get raw file
    api_response = github_request_wrapper(raw_file_url, ghe)

    raw_file = api_response.content
    return raw_file
