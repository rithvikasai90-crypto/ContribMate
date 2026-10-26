
import base64
import logging
import os

import requests


GITHUB_API = "https://api.github.com"

logger = logging.getLogger(__name__)

session = requests.Session()

session.headers.update({
    "Accept": "application/vnd.github+json",
    "User-Agent": "ContribMate",
    "X-GitHub-Api-Version": "2022-11-28",
})

# Optional GitHub token for higher API rate limits.
# Configure this only through environment variables.
github_token = os.getenv("GITHUB_TOKEN", "").strip()

if github_token:
    session.headers.update({
        "Authorization": f"Bearer {github_token}"
    })


def github_get(url, params=None):
    """Make a GitHub API request and report failures."""

    try:
        response = session.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        return response.json()

    except requests.HTTPError as error:
        response = error.response

        status = (
            response.status_code
            if response is not None
            else "unknown"
        )

        message = "Unknown GitHub API error."

        if response is not None:
            try:
                message = response.json().get(
                    "message",
                    message
                )
            except ValueError:
                message = response.text[:300]

        logger.error(
            "GitHub API request failed: "
            "status=%s message=%s",
            status,
            message
        )

        if status == 403 or status == 429:
            raise RuntimeError(
                "GitHub API access was limited. "
                "Please try again later or configure "
                "a GITHUB_TOKEN on Render."
            ) from error

        if status == 404:
            raise RuntimeError(
                "GitHub repository or resource not found."
            ) from error

        raise RuntimeError(
            f"GitHub API returned HTTP {status}: {message}"
        ) from error

    except requests.RequestException as error:
        logger.exception(
            "Unable to connect to GitHub API."
        )

        raise RuntimeError(
            "Unable to connect to GitHub API."
        ) from error


def get_repository(owner, repo):
    """Retrieve repository details."""

    data = github_get(
        f"{GITHUB_API}/repos/{owner}/{repo}"
    )

    return {
        "name": data["full_name"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "url": data.get("html_url"),
        "default_branch": data.get("default_branch"),
        "topics": data.get("topics", []),
        "homepage": data.get("homepage"),
        "open_issues_count": data.get(
            "open_issues_count"
        ),
    }


def get_repository_readme(owner, repo):
    """Retrieve and decode the repository README."""

    url = f"{GITHUB_API}/repos/{owner}/{repo}/readme"

    try:
        data = github_get(url)

        encoded_content = data.get("content", "")

        if data.get("encoding") == "base64":
            decoded = base64.b64decode(
                encoded_content
            ).decode(
                "utf-8",
                errors="replace"
            )

            return decoded[:12000]

        return "README content is unavailable."

    except (RuntimeError, ValueError):
        return "README could not be retrieved."


def get_repository_languages(owner, repo):
    """Retrieve languages used in the repository."""

    url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"

    try:
        data = github_get(url)
        return list(data.keys())

    except (RuntimeError, ValueError):
        return []


def get_repository_structure(owner, repo):
    """Retrieve top-level repository files and folders."""

    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents"

    try:
        data = github_get(url)

        if not isinstance(data, list):
            return []

        return [
            {
                "name": item.get("name"),
                "type": item.get("type")
            }
            for item in data[:40]
        ]

    except (RuntimeError, ValueError):
        return []


def get_contributing_guide(owner, repo):
    """Look for common contribution instruction files."""

    possible_paths = [
        "CONTRIBUTING.md",
        ".github/CONTRIBUTING.md",
        "docs/CONTRIBUTING.md"
    ]

    for path in possible_paths:
        url = (
            f"{GITHUB_API}/repos/"
            f"{owner}/{repo}/contents/{path}"
        )

        try:
            data = github_get(url)

            encoded_content = data.get("content", "")

            if data.get("encoding") == "base64":
                decoded = base64.b64decode(
                    encoded_content
                ).decode(
                    "utf-8",
                    errors="replace"
                )

                return decoded[:8000]

        except (RuntimeError, ValueError):
            continue

    return "No separate CONTRIBUTING.md guide was found."


def get_repository_context(owner, repo):
    """Collect repository context for AI analysis."""

    repository = get_repository(owner, repo)

    return {
        **repository,
        "readme": get_repository_readme(owner, repo),
        "languages": get_repository_languages(owner, repo),
        "structure": get_repository_structure(owner, repo),
        "contributing_guide": get_contributing_guide(
            owner,
            repo
        ),
    }


def get_beginner_issues(owner, repo):
    """Retrieve open issues labeled good first issue."""

    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "labels": "good first issue",
        "per_page": 10
    }

    data = github_get(url, params=params)

    issues = []

    for item in data:
        if "pull_request" in item:
            continue

        issues.append({
            "number": item["number"],
            "title": item["title"],
            "url": item["html_url"],
            "labels": [
                label["name"]
                for label in item.get("labels", [])
            ]
        })

    return issues


def get_issue_details(owner, repo, issue_number):
    """Retrieve the details of one GitHub issue."""

    url = (
        f"{GITHUB_API}/repos/"
        f"{owner}/{repo}/issues/{issue_number}"
    )

    data = github_get(url)

    return {
        "number": data["number"],
        "title": data["title"],
        "body": data.get("body")
        or "No description provided.",
        "url": data["html_url"],
        "labels": [
            label["name"]
            for label in data.get("labels", [])
        ],
    }
