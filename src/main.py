import os
import git
import yaml
import requests
from typing import Any
import shutil
import dotenv
import argparse
import tempfile
from urllib.parse import urlparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Process a GitHub repository.")
    parser.add_argument("repo_url", type=str, help="The URL of the GitHub repository.")
    return parser.parse_args()


def clone_repo(repo_url: str, local_path: str) -> None:
    git.Repo.clone_from(repo_url, local_path)


def get_api_url(repo_url: str) -> str:
    parsed_url = urlparse(repo_url)
    path_parts = parsed_url.path.strip("/").split("/")
    user, repo = path_parts[0], path_parts[1]
    repo = repo.replace(".git", "")  # Remove .git extension if present
    github_api_url = f"https://api.github.com/repos/{user}/{repo}"
    return github_api_url


def delete_local_repo(local_path: str) -> None:
    shutil.rmtree(local_path)


def create_folder_structure(local_path: str) -> None:
    os.makedirs(os.path.join(local_path, ".github", "workflows"), exist_ok=True)


def read_yaml_file(yaml_path: str) -> Any:
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def add_yaml_file(local_path: str, yaml_content: Any) -> None:
    with open(
        os.path.join(local_path, ".github", "workflows", "dependabot-auto-merge.yml"),
        "w",
    ) as f:
        yaml.dump(yaml_content, f)


def commit_and_push(local_path: str, user: str, email: str) -> None:
    repo = git.Repo(local_path)
    repo.config_writer().set_value("user", "name", user).release()
    repo.config_writer().set_value("user", "email", email).release()
    repo.git.checkout("-b", "enable-dependabot-auto-merge")
    repo.git.add(all=True)
    repo.git.commit("-m", "enable dependabot auto-merge")
    repo.git.push("--set-upstream", "origin", "enable-dependabot-auto-merge")


def create_pull_request(token: str, repo_url: str, user: str) -> None:
    headers = {"Authorization": f"token {token}"}
    data = {
        "title": "enable dependabot auto-merge",
        "head": "enable-dependabot-auto-merge",
        "base": "main",  # or whichever is your default branch
        "assignees": [user],
    }
    response = requests.post(f"{repo_url}/pulls", headers=headers, json=data)
    response_json = response.json()
    if response.status_code != 201:
        print(f"Failed to create pull request: {response_json.get('message')}")
        return -1  # Or some error handling
    else:
        print(f"Pull request created successfully: {response_json['html_url']}")
        return response_json[
            "number"
        ]  # Returning the issue number for the created pull request


def add_assignees_to_pull_request(
    token: str, repo_url: str, issue_number: int, assignees: list
) -> None:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"assignees": assignees}
    response = requests.post(
        f"{repo_url}/issues/{issue_number}/assignees", headers=headers, json=data
    )
    response_json = response.json()
    if response.status_code != 201:
        print(f"Failed to add assignees: {response_json.get('message')}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    github_token = os.getenv("GITHUB_TOKEN")
    user = os.getenv("GITHUB_USERNAME")
    commit_user = os.getenv("COMMIT_USER")
    commit_email = os.getenv("COMMIT_EMAIL")
    args = parse_arguments()
    repo_url = args.repo_url
    github_api_url = get_api_url(repo_url)

    with tempfile.TemporaryDirectory() as temp_dir:
        local_path = temp_dir
        clone_repo(repo_url, local_path)
        create_folder_structure(local_path)
        yaml_file_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)), "dependabot-auto-merge.yml"
        )
        dest_yaml_path = os.path.join(
            local_path, ".github", "workflows", "dependabot-auto-merge.yml"
        )
        shutil.copy(yaml_file_path, dest_yaml_path)
        commit_and_push(local_path, commit_user, commit_email)
        issue_number = create_pull_request(github_token, github_api_url, user)
        if issue_number != -1:
            add_assignees_to_pull_request(
                github_token, github_api_url, issue_number, [user]
            )

        delete_local_repo(local_path)
