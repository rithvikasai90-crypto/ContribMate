
import requests

def get_repository(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

    return {
        "name": data["full_name"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count"),
        "url": data.get("html_url")
    }


def get_beginner_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    params = {
        "state": "open",
        "labels": "good first issue",
        "per_page": 10
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    issues = []

    for item in response.json():
        # GitHub's issues API also returns pull requests.
        if "pull_request" in item:
            continue

        issues.append({
            "number": item["number"],
            "title": item["title"],
            "url": item["html_url"],
            "labels": [
                label["name"]
                for label in item["labels"]
            ]
        })

    return issues

def get_issue_details(owner, repo, issue_number):
    url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repo}/issues/{issue_number}"
    )

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()

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
