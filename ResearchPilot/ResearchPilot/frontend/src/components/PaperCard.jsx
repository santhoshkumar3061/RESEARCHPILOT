import { Link } from "react-router-dom";

export default function PaperCard({ paper, tags = [], status, onAdd, onOpen, inLibrary }) {
  const year = paper.published ? new Date(paper.published).getFullYear() : "";
  return (
    <div className="paper-card">
      <div className="body">
        <h3 className="title">{paper.title}</h3>
        <div className="meta">
          {paper.id} · {paper.authors.slice(0, 3).join(", ")}
          {paper.authors.length > 3 ? " et al." : ""} · {year}
        </div>
        <p className="abstract">{paper.abstract}</p>
        <div className="actions">
          <Link to={`/paper/${encodeURIComponent(paper.id)}`}>
            <button className="primary" onClick={() => onOpen && onOpen(paper)}>
              Open
            </button>
          </Link>
          {!inLibrary && (
            <button onClick={() => onAdd && onAdd(paper)}>+ Add to library</button>
          )}
          {paper.entry_url && (
            <a href={paper.entry_url} target="_blank" rel="noreferrer">
              <button>arXiv ↗</button>
            </a>
          )}
        </div>
      </div>
      <div className="marginalia">
        {tags.map((t) => (
          <span className="tag" key={t}>
            {t}
          </span>
        ))}
        {status && <span className="status">{status}</span>}
      </div>
    </div>
  );
}
