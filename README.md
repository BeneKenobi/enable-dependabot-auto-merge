# Enable Dependabot Auto-Merge

This Python script automates several GitHub repository management tasks, including cloning a repository, setting up a workflow for [Dependabot](https://github.com/dependabot) auto-merges.

## Features

- Clones a GitHub repository.
- Creates necessary folder structures for GitHub actions.
- Copies a Dependabot auto-merge workflow into the repository.
- Commits changes and pushes them to a new branch.
- Creates a pull request and assigns user.

## Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/) for dependency management

## Installation

1. Clone this repository:

   ```bash
   git clone <repository-url>
   ```

2. Install the required packages using Poetry:

   ```bash
   poetry install
   ```

## Environment Setup

Before running the script, you need to set up the following environment variables in a .env file in the root directory of the project:

- `GITHUB_TOKEN`: A GitHub access token for authentication with GitHub API and repository operations.
- `GITHUB_USERNAME`: Your GitHub username.
- `COMMIT_USER`: The name to be used for commits.
- `COMMIT_EMAIL`: The email to be used for commits.

Example of `.env` content:

```
GITHUB_TOKEN=your_token_here
GITHUB_USERNAME=your_username_here
COMMIT_USER=your_commit_name_here
COMMIT_EMAIL=your_commit_email_here
```

## Usage

Run the script with the URL of the GitHub repository you want to process:

```bash
poetry run python src/main.py <repo_url>
```
Replace `<repo_url>` with the actual URL of the GitHub repository.

## Contributing

Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT