import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client.js";

const STYLES = ["concise", "detailed", "eli5", "critical"];

export default function PaperDetail() {
  const { paperId } = useParams();
  const [paper, setPaper] = useState(null);
  const [style, setStyle] = useState("concise");
  const [summary, setSummary] = useState(null);
  const [summarizing, setSummarizing] = useState(false);
  const [indexed, setIndexed] = useState(false);
  const [indexing, setIndexing] = useState(false);

  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  useEffect(() => {
    api.getPaper(paperId).then(setPaper).catch(() => setPaper(null));
  }, [paperId]);

  async function runSummary(s) {
    setStyle(s);
    setSummarizing(true);
    try {
      const res = await api.summarizePaper(paperId, s);
      setSummary(res);
    } finally {
      setSummarizing(false);
    }
  }

  async function runIndex() {
    setIndexing(true);
    try {
      await api.indexPaper(paperId);
      setIndexed(true);
    } finally {
      setIndexing(false);
    }
  }

  async function askQuestion(e) {
    e.preventDefault();
    if (!question.trim()) return;
    const userMsg = { role: "user", content: question };
    setMessages((m) => [...m, userMsg]);
    setQuestion("");
    setAsking(true);
    try {
      const res = await api.chat(userMsg.content, paperId, messages);
      setMessages((m) => [...m, { role: "assistant", content: res.answer, citations: res.citations }]);
    } finally {
      setAsking(false);
    }
  }

  if (!paper) return <div className="main">Loading paper…</div>;

  return (
    <div className="main">
      <div className="page-header">
        <h1>{paper.title}</h1>
        <p>
          {paper.authors.join(", ")} · {paper.id}
        </p>
      </div>

      <p style={{ color: "var(--ink-soft)" }}>{paper.abstract}</p>

      <div className="style-tabs" style={{ marginTop: 18 }}>
        {STYLES.map((s) => (
          <button key={s} className={s === style ? "active" : ""} onClick={() => runSummary(s)}>
            {s}
          </button>
        ))}
        {summarizing && <span className="loading-dot">Summarizing</span>}
      </div>

      {summary && (
        <div className="summary-card">
          <p>{summary.summary}</p>
          {summary.key_findings?.length > 0 && (
            <>
              <h3>Key findings</h3>
              <ul>
                {summary.key_findings.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </>
          )}
          {summary.limitations?.length > 0 && (
            <>
              <h3>Limitations</h3>
              <ul>
                {summary.limitations.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      <div style={{ marginTop: 30 }}>
        <h2 style={{ fontSize: 18 }}>Ask this paper</h2>
        {!indexed && (
          <button onClick={runIndex} disabled={indexing} style={{ marginBottom: 12 }}>
            {indexing ? "Indexing…" : "Index paper for Q&A"}
          </button>
        )}
        <div className="chat-panel" style={{ height: 420 }}>
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-state">Ask a question once the paper is indexed.</div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.content}
                {m.citations?.length > 0 && (
                  <div className="chat-citations">
                    {m.citations.map((c, j) => (
                      <div className="cite" key={j}>
                        {c.paper_title}: "{c.chunk_preview}…"
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          <form className="chat-input-row" onSubmit={askQuestion}>
            <input
              placeholder="What method do they use for evaluation?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!indexed}
            />
            <button type="submit" disabled={!indexed || asking}>
              {asking ? "…" : "Ask"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
