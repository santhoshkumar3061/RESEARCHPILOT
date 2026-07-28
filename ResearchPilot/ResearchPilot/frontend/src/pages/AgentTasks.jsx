import { useState } from "react";
import { api } from "../api/client.js";

const EXAMPLES = [
  "Find 3 recent papers on mixture-of-experts routing and summarize the most cited one.",
  "Search my library for anything about evaluation benchmarks.",
  "Find papers on long-context transformers and add the top result to my library.",
];

export default function AgentTasks() {
  const [instruction, setInstruction] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState(null);

  async function runTask(e) {
    e.preventDefault();
    if (!instruction.trim()) return;
    setRunning(true);
    setResult(null);
    try {
      const res = await api.agentTask(instruction);
      setResult(res);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="main">
      <div className="page-header">
        <h1>Agent tasks</h1>
        <p>Give a free-form research instruction — the agent plans steps, runs them, and reports back.</p>
      </div>

      <form className="search-bar" onSubmit={runTask}>
        <input
          placeholder="Find recent papers on X and summarize the top one…"
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
        />
        <button type="submit" disabled={running}>
          {running ? <span className="loading-dot">Working</span> : "Run"}
        </button>
      </form>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 20 }}>
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setInstruction(ex)}
            style={{
              fontSize: 11.5,
              padding: "6px 10px",
              borderRadius: 999,
              border: "1px solid var(--rule)",
              background: "var(--paper-raised)",
              color: "var(--ink-soft)",
            }}
          >
            {ex}
          </button>
        ))}
      </div>

      {result && (
        <div className="summary-card">
          <h3>Plan &amp; execution</h3>
          {result.steps.length === 0 && (
            <p style={{ color: "var(--ink-soft)" }}>
              No discrete tool plan was needed — answered directly from context.
            </p>
          )}
          <ul>
            {result.steps.map((s, i) => (
              <li key={i}>
                <code style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--amber)" }}>
                  {s.tool}
                </code>
                {" — "}
                {s.output_summary}
              </li>
            ))}
          </ul>
          <h3>Answer</h3>
          <p>{result.final_answer}</p>
        </div>
      )}
    </div>
  );
}
