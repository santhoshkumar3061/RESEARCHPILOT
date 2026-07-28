import { useState } from "react";
import { api } from "../api/client.js";
import PaperCard from "../components/PaperCard.jsx";

export default function Discover() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [addedIds, setAddedIds] = useState(new Set());

  async function runSearch(e) {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.searchPapers(query, 12);
      setResults(res.results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(paper) {
    await api.addToLibrary(paper);
    setAddedIds((prev) => new Set(prev).add(paper.id));
  }

  return (
    <div className="main">
      <div className="page-header">
        <h1>Discover papers</h1>
        <p>Search arXiv, skim abstracts, and pull the ones worth reading into your library.</p>
      </div>

      <form className="search-bar" onSubmit={runSearch}>
        <input
          placeholder="e.g. retrieval augmented generation for scientific QA"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? <span className="loading-dot">Searching</span> : "Search"}
        </button>
      </form>

      {error && <p style={{ color: "var(--danger)" }}>{error}</p>}

      {!loading && results.length === 0 && !error && (
        <div className="empty-state">
          Try a topic, method name, or a question — e.g. "sparse attention for long context".
        </div>
      )}

      {results.map((paper) => (
        <PaperCard
          key={paper.id}
          paper={paper}
          inLibrary={addedIds.has(paper.id)}
          onAdd={handleAdd}
        />
      ))}
    </div>
  );
}
