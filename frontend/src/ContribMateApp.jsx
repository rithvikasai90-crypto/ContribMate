
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

// Use Vercel's /api proxy in production.
// Vite's local development server can use the Render backend.
const API_BASE = import.meta.env.DEV
  ? "https://contribmate3.onrender.com"
  : "/api";

const BACKEND_URL = "https://contribmate3.onrender.com";

async function getApiData(path) {
  let response;

  try {
    response = await fetch(`${API_BASE}${path}`, {
      method: "GET",
      credentials: "include",
      headers: {
        Accept: "application/json",
      },
    });
  } catch {
    throw new Error(
      "Could not reach the backend. Check your connection and try again."
    );
  }

  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    if (response.status === 504 || response.status === 502) {
      throw new Error(
        "The server took too long to respond. Please try again."
      );
    }

    throw new Error(
      `The server returned an unexpected response (HTTP ${response.status}).`
    );
  }

  let data;

  try {
    data = await response.json();
  } catch {
    throw new Error("Could not read the backend response.");
  }

  if (!response.ok || data.error) {
    const detail =
      typeof data.detail === "string"
        ? data.detail
        : typeof data.error === "string"
          ? data.error
          : `Request failed (HTTP ${response.status}).`;

    throw new Error(detail);
  }

  return data;
}

function parseGitHubUrl(input) {
  let parsed;

  try {
    parsed = new URL(input.trim());
  } catch {
    throw new Error(
      "Please enter a valid GitHub URL, such as https://github.com/fastapi/fastapi"
    );
  }

  const hostname = parsed.hostname.toLowerCase();

  if (
    parsed.protocol !== "https:" ||
    !["github.com", "www.github.com"].includes(hostname)
  ) {
    throw new Error(
      "Please enter a GitHub repository URL beginning with https://github.com/"
    );
  }

  const parts = parsed.pathname
    .split("/")
    .filter(Boolean);

  if (parts.length !== 2) {
    throw new Error(
      "Enter a repository URL in the format https://github.com/owner/repository"
    );
  }

  const owner = parts[0];
  const repo = parts[1].replace(/\.git$/i, "");

  if (!owner || !repo) {
    throw new Error("Invalid GitHub repository URL.");
  }

  return { owner, repo };
}

function ContribMateApp() {
  const [url, setUrl] = useState("");
  const [repository, setRepository] = useState(null);
  const [repoInfo, setRepoInfo] = useState(null);
  const [issues, setIssues] = useState([]);
  const [analysis, setAnalysis] = useState("");

  const [loading, setLoading] = useState(false);
  const [issuesLoading, setIssuesLoading] = useState(false);
  const [error, setError] = useState("");
  const [issuesError, setIssuesError] = useState("");

  const [selectedIssue, setSelectedIssue] = useState(null);
  const [issueExplanation, setIssueExplanation] = useState("");
  const [explainingIssue, setExplainingIssue] = useState(false);
  const [explanationError, setExplanationError] = useState("");

  async function analyzeRepository() {
    if (loading || issuesLoading) return;

    setError("");
    setIssuesError("");
    setAnalysis("");
    setRepository(null);
    setRepoInfo(null);
    setIssues([]);
    setSelectedIssue(null);
    setIssueExplanation("");
    setExplanationError("");

    let owner;
    let repo;

    try {
      ({ owner, repo } = parseGitHubUrl(url));
    } catch (err) {
      setError(err.message);
      return;
    }

    setLoading(true);

    try {
      const endpoint =
        `/analyze-repo?owner=${encodeURIComponent(owner)}` +
        `&repo=${encodeURIComponent(repo)}`;

      const data = await getApiData(endpoint);

      if (!data.repository || !data.analysis) {
        throw new Error(
          "The backend did not return a complete repository analysis."
        );
      }

      setRepository(data.repository);
      setRepoInfo({ owner, repo });
      setAnalysis(data.analysis);
    } catch (err) {
      setError(err.message || "Repository analysis failed.");
      setLoading(false);
      return;
    } finally {
      setLoading(false);
    }

    setIssuesLoading(true);

    try {
      const endpoint =
        `/beginner-issues?owner=${encodeURIComponent(owner)}` +
        `&repo=${encodeURIComponent(repo)}`;

      const data = await getApiData(endpoint);

      setIssues(
        Array.isArray(data.issues) ? data.issues : []
      );
    } catch (err) {
      setIssuesError(
        err.message || "Could not load beginner-friendly issues."
      );
    } finally {
      setIssuesLoading(false);
    }
  }

  async function explainIssue(issueNumber) {
    if (!repoInfo) {
      setExplanationError("Please analyze a repository first.");
      return;
    }

    setSelectedIssue(issueNumber);
    setIssueExplanation("");
    setExplanationError("");
    setExplainingIssue(true);

    try {
      const { owner, repo } = repoInfo;

      const endpoint =
        `/explain-issue?owner=${encodeURIComponent(owner)}` +
        `&repo=${encodeURIComponent(repo)}` +
        `&issue_number=${encodeURIComponent(issueNumber)}`;

      const data = await getApiData(endpoint);

      if (!data.explanation) {
        throw new Error("No issue explanation was returned.");
      }

      setIssueExplanation(data.explanation);
    } catch (err) {
      setExplanationError(
        err.message || "Unable to explain this issue."
      );
    } finally {
      setExplainingIssue(false);
    }
  }

  return (
    <main className="container">
      <header className="hero">
        <h1>🚀 ContribMate</h1>

        <p>
          Your AI companion for open-source contributions.
        </p>

        <p className="backend-address">
          Backend:{" "}
          <a
            href={`${BACKEND_URL}/docs`}
            target="_blank"
            rel="noreferrer"
          >
            {BACKEND_URL}
          </a>
        </p>
      </header>

      <section className="panel">
        <h2>Explore a GitHub Repository</h2>

        <p>
          Paste a GitHub repository URL and discover
          how you can contribute.
        </p>

        <input
          type="url"
          placeholder="https://github.com/fastapi/fastapi"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <button
          type="button"
          onClick={analyzeRepository}
          disabled={
            loading ||
            issuesLoading ||
            explainingIssue
          }
        >
          {loading
            ? "⏳ Analyzing repository..."
            : issuesLoading
              ? "Loading Issues..."
              : "✨ Analyze Repository"}
        </button>

        {loading && (
          <p>
            Groq AI is preparing your contribution guide.
            This may take a little time...
          </p>
        )}

        {error && (
          <p className="error">{error}</p>
        )}
      </section>

      {repository && (
        <section className="panel">
          <h2>{repository.name}</h2>

          <p>
            {repository.description ||
              "No description provided."}
          </p>

          <p>
            Language: {repository.language || "Unknown"}
          </p>

          <p>
            ⭐ Stars: {repository.stars ?? "Unknown"}
          </p>

          <a
            href={repository.url}
            target="_blank"
            rel="noreferrer"
          >
            View on GitHub ↗
          </a>
        </section>
      )}

      {analysis && (
        <section className="panel">
          <h2>🤖 AI Contribution Guide</h2>

          <div className="analysis">
            <ReactMarkdown>
              {analysis}
            </ReactMarkdown>
          </div>
        </section>
      )}

      {repository && (
        <section className="panel">
          <h2>🌱 Beginner-Friendly Issues</h2>

          <p>
            Explore open GitHub issues labeled
            "good first issue".
          </p>

          {issuesLoading ? (
            <p>
              Loading beginner-friendly issues...
            </p>
          ) : issuesError ? (
            <p className="error">
              {issuesError}
            </p>
          ) : issues.length === 0 ? (
            <p>
              No beginner-friendly issues found right now.
            </p>
          ) : (
            <div className="issues-list">
              {issues.map((issue) => (
                <div
                  className="issue-card"
                  key={issue.number}
                >
                  <h3>{issue.title}</h3>

                  <p>
                    Issue #{issue.number}
                  </p>

                  <div className="issue-labels">
                    {(issue.labels || []).map(
                      (label) => (
                        <span
                          className="issue-label"
                          key={label}
                        >
                          {label}
                        </span>
                      )
                    )}
                  </div>

                  <a
                    href={issue.url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View Issue on GitHub ↗
                  </a>

                  <button
                    type="button"
                    onClick={() =>
                      explainIssue(issue.number)
                    }
                    disabled={explainingIssue}
                  >
                    {explainingIssue &&
                    selectedIssue === issue.number
                      ? "⏳ Explaining..."
                      : "✨ Explain This Issue"}
                  </button>

                  {selectedIssue === issue.number && (
                    <div className="issue-explanation">
                      {explainingIssue && (
                        <p>
                          🤖 AI is analyzing this issue.
                          Please wait...
                        </p>
                      )}

                      {explanationError && (
                        <p className="error">
                          {explanationError}
                        </p>
                      )}

                      {issueExplanation && (
                        <div className="analysis">
                          <ReactMarkdown>
                            {issueExplanation}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}
    </main>
  );
}

export default ContribMateApp;
