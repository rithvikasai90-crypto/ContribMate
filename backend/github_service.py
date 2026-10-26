
import base64
import requests


GITHUB_API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "ContribMate"
}


def github_get(url, params=None):
    """Make a GitHub API request."""
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=15
    )
    response.raise_for_status()
    return response.json()


def get_repository(owner, repo):
    """
    Retrieve repository details.

    Keeps the original fields so existing frontend
    and backend features continue to work.
    """
    data = github_get(
        f"{GITHUB_API}/repos/{owner}/{repo}"
    )

    return {
        "name": data["full_name"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "url": data.get("html_url"),

        # Additional useful repository details
        "default_branch": data.get("default_branch"),
        "topics": data.get("topics", []),
        "homepage": data.get("homepage"),
        "open_issues_count": data.get("open_issues_count"),
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
            ).decode("utf-8", errors="replace")

            # Limit content to keep AI prompts manageable
            return decoded[:12000]

        return "README content is unavailable."

    except requests.RequestException:
        return "README could not be retrieved."


def get_repository_languages(owner, repo):
    """Retrieve languages used in the repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"

    try:
        data = github_get(url)

        # GitHub returns language names and byte counts.
        return list(data.keys())

    except requests.RequestException:
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

    except requests.RequestException:
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
                ).decode("utf-8", errors="replace")

                return decoded[:8000]

        except requests.RequestException:
            continue

    return "No separate CONTRIBUTING.md guide was found."


def get_repository_context(owner, repo):
    """
    Collect detailed repository context for AI analysis.
    """
    repository = get_repository(owner, repo)

    return {
        **repository,
        "readme": get_repository_readme(owner, repo),
        "languages": get_repository_languages(owner, repo),
        "structure": get_repository_structure(owner, repo),
        "contributing_guide": get_contributing_guide(
            owner, repo
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
        # GitHub's issues API also includes pull requests.
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
        "body": data.get("body") or "No description provided.",
        "url": data["html_url"],
        "labels": [
            label["name"]
            for label in data.get("labels", [])
        ],
    }
