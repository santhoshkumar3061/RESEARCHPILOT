import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client.js";
import PaperCard from "../components/PaperCard.jsx";

export default function Library() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [collectionFilter, setCollectionFilter] = useState("All");

  async function load() {
    setLoading(true);
    const data = await api.listLibrary();
    setItems(data);
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  const collections = useMemo(
    () => ["All", ...new Set(items.map((i) => i.collection))],
    [items]
  );

  const filtered =
    collectionFilter === "All" ? items : items.filter((i) => i.collection === collectionFilter);

  async function setStatus(paperId, status) {
    await api.updateLibraryItem(paperId, { status });
    load();
  }

  async function remove(paperId) {
    await api.removeFromLibrary(paperId);
    load();
  }

  return (
    <div className="main">
      <div className="page-header">
        <h1>My library</h1>
        <p>Saved papers, organized by collection. Mark progress and index papers for chat.</p>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 18, flexWrap: "wrap" }}>
        {collections.map((c) => (
          <button
            key={c}
            onClick={() => setCollectionFilter(c)}
            className="style-tabs"
            style={{
              padding: "6px 14px",
              borderRadius: 999,
              border: "1px solid var(--rule)",
              background: c === collectionFilter ? "var(--indigo)" : "var(--paper-raised)",
              color: c === collectionFilter ? "#fff" : "var(--ink)",
              fontSize: 12,
            }}
          >
            {c}
          </button>
        ))}
      </div>

      {loading && <p>Loading…</p>}
      {!loading && filtered.length === 0 && (
        <div className="empty-state">
          Nothing here yet. Head to <strong>Discover</strong> to find and save papers.
        </div>
      )}

      {filtered.map((item) => (
        <div key={item.paper.id}>
          <PaperCard paper={item.paper} tags={item.tags} status={item.status} inLibrary />
          <div style={{ display: "flex", gap: 8, margin: "-6px 0 16px 4px" }}>
            {["unread", "reading", "read"].map((s) => (
              <button
                key={s}
                onClick={() => setStatus(item.paper.id, s)}
                style={{
                  fontSize: 11,
                  padding: "4px 9px",
                  borderRadius: 999,
                  border: "1px solid var(--rule)",
                  background: item.status === s ? "var(--sage)" : "var(--paper-raised)",
                  color: item.status === s ? "#fff" : "var(--ink-soft)",
                }}
              >
                {s}
              </button>
            ))}
            <button
              onClick={() => remove(item.paper.id)}
              style={{
                fontSize: 11,
                padding: "4px 9px",
                borderRadius: 999,
                border: "1px solid var(--rule)",
                background: "var(--paper-raised)",
                color: "var(--danger)",
              }}
            >
              remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
