import { useState } from "react";
import { api } from "../api/client.js";

export default function LibraryChat() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);

  async function ask(e) {
    e.preventDefault();
    if (!question.trim()) return;
    const userMsg = { role: "user", content: question };
    setMessages((m) => [...m, userMsg]);
    setQuestion("");
    setAsking(true);
    try {
      const res = await api.chat(userMsg.content, null, messages);
      setMessages((m) => [...m, { role: "assistant", content: res.answer, citations: res.citations }]);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="main">
      <div className="page-header">
        <h1>Ask my library</h1>
        <p>Query across every indexed paper you've saved — answers are grounded and cited.</p>
      </div>

      <div className="chat-panel">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div className="empty-state">
              Try: "What approaches has this literature used for long-context retrieval?"
            </div>
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
          {asking && <div className="chat-bubble assistant loading-dot">Thinking</div>}
        </div>
        <form className="chat-input-row" onSubmit={ask}>
          <input
            placeholder="Ask across your whole library…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button type="submit" disabled={asking}>
            Ask
          </button>
        </form>
      </div>
    </div>
  );
}
