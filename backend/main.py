
from fastapi import FastAPI
from ollama import chat
import requests

from github_service import (
    get_repository,
    get_beginner_issues,
    get_issue_details,
)

# NEW: Import authentication routes
from auth import router as auth_router


# Create the ContribMate application
app = FastAPI()

# NEW: Enable login, signup, logout, and session checking
app.include_router(auth_router)


# Check if our backend is running
@app.get("/")
def home():
    return {
        "message": "ContribMate Backend is Running!"
    }


# Ask a question to Gemma 4
@app.get("/ask")
def ask_ai(question: str):
    response = chat(
        model="gemma4:e2b",
        messages=[
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return {
        "answer": response.message.content
    }


# Get GitHub repository information
@app.get("/repository")
def repository_info(owner: str, repo: str):
    try:
        return get_repository(owner, repo)

    except requests.RequestException:
        return {
            "error": "Could not retrieve repository information"
        }


# Analyze a GitHub repository using Gemma 4
@app.get("/analyze-repo")
def analyze_repo(owner: str, repo: str):
    try:
        repository = get_repository(owner, repo)

        prompt = f"""
        You are ContribMate, an AI assistant that helps
        beginners contribute to open-source projects.

        Analyze this GitHub repository information:

        Repository: {repository['name']}
        Description: {repository['description']}
        Language: {repository['language']}
        GitHub URL: {repository['url']}

        Please explain:
        1. What this project does.
        2. What a beginner should learn before contributing.
        3. General ways someone could contribute.
        4. How to get started with open-source contributions.

        Important:
        Use only the supplied repository information
        for project-specific claims.
        Do not invent issues, source files, or setup commands.
        """

        response = chat(
            model="gemma4:e2b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return {
            "repository": repository,
            "analysis": response.message.content
        }

    except requests.RequestException:
        return {
            "error": "Could not fetch repository information."
        }


# Find beginner-friendly GitHub issues
@app.get("/beginner-issues")
def beginner_issues(owner: str, repo: str):
    try:
        issues = get_beginner_issues(owner, repo)

        return {
            "repository": f"{owner}/{repo}",
            "total": len(issues),
            "issues": issues
        }

    except requests.RequestException:
        return {
            "error": "Could not fetch GitHub issues"
        }


# Explain a GitHub issue using Gemma 4
@app.get("/explain-issue")
def explain_issue(owner: str, repo: str, issue_number: int):
    try:
        issue = get_issue_details(owner, repo, issue_number)

        prompt = f"""
You are ContribMate, an AI mentor helping beginners
contribute to open-source projects.

Repository: {owner}/{repo}

GitHub Issue Title:
{issue["title"]}

GitHub Issue Description:
{issue["body"][:12000]}

Explain this GitHub issue to a beginner.

Use Markdown formatting and include these sections:

1. What does this issue mean?
   Explain it in simple, beginner-friendly language.

2. What skills are needed?
   List the programming languages, tools, or concepts
   someone should understand.

3. How difficult is this issue?
   Estimate Beginner, Intermediate, or Advanced.
   Explain your reasoning. Do not assume that a
   "good first issue" label means the task is easy.

4. How can someone start solving it?
   Provide practical first steps without inventing
   specific file paths or implementation details.

5. What should the contributor do before submitting
   a pull request?

Make it clear when important technical details
are missing from the issue description.
"""

        response = chat(
            model="gemma4:e2b",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        explanation = response["message"]["content"]

        return {
            "issue": issue,
            "explanation": explanation,
        }

    except Exception as e:
        return {"error": str(e)}
