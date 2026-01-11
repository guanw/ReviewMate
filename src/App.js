import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [diff, setDiff] = useState("");
  const [prUrl, setPrUrl] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const savedHistory = localStorage.getItem("reviewmate_history");
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  const saveToHistory = (newResult) => {
    const newEntry = {
      diff: diff.slice(0, 100) + "...",
      result: newResult,
      timestamp: new Date().toISOString(),
    };
    const updatedHistory = [newEntry, ...history.slice(0, 9)]; // Keep last 10
    setHistory(updatedHistory);
    localStorage.setItem("reviewmate_history", JSON.stringify(updatedHistory));
  };

  const handleAnalyze = async () => {
    if (!diff.trim()) {
      alert("Please enter a code diff");
      return;
    }

    setLoading(true);
    setResult("");

    try {
      const response = await fetch("http://localhost:8000/analyze-diff", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          diff: diff,
          pr_url: prUrl || undefined,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data.message);
        saveToHistory(data.message);
      } else {
        setResult(`Error: ${data.detail}`);
        saveToHistory(`Error: ${data.detail}`);
      }
    } catch (error) {
      setResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 ReviewMate - AI Code Review</h1>
        <p>Analyze your code diffs with AI-powered insights</p>
      </header>
      <main>
        <div className="input-section">
          <label>
            Code Diff:
            <textarea
              value={diff}
              onChange={(e) => setDiff(e.target.value)}
              placeholder="Paste your Git diff here..."
              rows={10}
            />
          </label>
          <label>
            PR URL (optional):
            <input
              type="text"
              value={prUrl}
              onChange={(e) => setPrUrl(e.target.value)}
              placeholder="https://github.com/repo/pr/123"
            />
          </label>
          <button onClick={handleAnalyze} disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Diff"}
          </button>
        </div>
        {result && (
          <div className="result-section">
            <h2>AI Analysis Result:</h2>
            <pre>{result}</pre>
          </div>
        )}
        {history.length > 0 && (
          <div className="history-section">
            <h2>Review History</h2>
            {history.map((entry, index) => (
              <div key={index} className="history-item">
                <p>
                  <strong>Diff:</strong> {entry.diff}
                </p>
                <p>
                  <strong>Result:</strong> {entry.result}
                </p>
                <p>
                  <em>{entry.timestamp}</em>
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
