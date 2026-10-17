
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";

function ContribMateApp()  {
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
      const parsed = new URL(url.trim());
      const parts = parsed.pathname.split("/").filter(Boolean);

      if (
        !["github.com", "www.github.com"].includes(
          parsed.hostname.toLowerCase()
        ) ||
        parts.length !== 2
      ) {
        throw new Error("Invalid GitHub repository URL");
      }

      [owner, repo] = parts;
      repo = repo.replace(/\.git$/, "");
    } catch {
      setError(
        "Please enter a valid URL like https://github.com/fastapi/fastapi"
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `/api/analyze-repo?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`
      );

      if (!response.ok) {
        throw new Error("Could not connect to the backend.");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setRepository(data.repository);
      setRepoInfo({ owner, repo });
      setAnalysis(data.analysis || "");
    } catch (err) {
      setError(err.message || "Something went wrong.");
      setLoading(false);
      return;
    }

    setLoading(false);
    setIssuesLoading(true);

    try {
      const response = await fetch(
        `/api/beginner-issues?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}`
      );

      if (!response.ok) {
        throw new Error("Could not fetch beginner-friendly issues.");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setIssues(Array.isArray(data.issues) ? data.issues : []);
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

      const response = await fetch(
        `/api/explain-issue?owner=${encodeURIComponent(owner)}&repo=${encodeURIComponent(repo)}&issue_number=${issueNumber}`
      );

      if (!response.ok) {
        throw new Error("Could not connect to the AI explanation service.");
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      if (!data.explanation) {
        throw new Error("No explanation was returned.");
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
        <p>Your AI companion for open-source contributions.</p>
      </header>

      {/* Repository search */}
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
          disabled={loading || issuesLoading || explainingIssue}
        >
          {loading
            ? "Analyzing..."
            : issuesLoading
              ? "Loading Issues..."
              : "✨ Analyze Repository"}
        </button>

        {error && <p className="error">{error}</p>}
      </section>

      {/* Repository details */}
      {repository && (
        <section className="panel">
          <h2>{repository.name}</h2>
          <p>{repository.description}</p>
          <p>Language: {repository.language || "Unknown"}</p>
          <p>⭐ Stars: {repository.stars ?? "Unknown"}</p>

          <a
            href={repository.url}
            target="_blank"
            rel="noreferrer"
          >
            View on GitHub ↗
          </a>
        </section>
      )}

      {/* AI Contribution Guide */}
      {analysis && (
        <section className="panel">
          <h2>🤖 AI Contribution Guide</h2>

          <div className="analysis">
            <ReactMarkdown>{analysis}</ReactMarkdown>
          </div>
        </section>
      )}

      {/* Beginner-friendly issues */}
      {repository && (
        <section className="panel">
          <h2>🌱 Beginner-Friendly Issues</h2>

          <p>
            Explore open GitHub issues labeled "good first issue".
          </p>

          {issuesLoading ? (
            <p>Loading beginner-friendly issues...</p>
          ) : issuesError ? (
            <p className="error">{issuesError}</p>
          ) : issues.length === 0 ? (
            <p>No beginner-friendly issues found right now.</p>
          ) : (
            <div className="issues-list">
              {issues.map((issue) => (
                <div
                  className="issue-card"
                  key={issue.number}
                >
                  <h3>{issue.title}</h3>
                  <p>Issue #{issue.number}</p>

                  <div className="issue-labels">
                    {issue.labels.map((label) => (
                      <span
                        className="issue-label"
                        key={label}
                      >
                        {label}
                      </span>
                    ))}
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
                    onClick={() => explainIssue(issue.number)}
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
                          🤖 Gemma 4 is analyzing this issue.
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
