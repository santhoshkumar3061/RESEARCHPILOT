const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json();
}

export const api = {
  searchPapers: (query, max_results = 10) =>
    request("/papers/search", {
      method: "POST",
      body: JSON.stringify({ query, max_results }),
    }),

  getPaper: (paperId) => request(`/papers/${paperId}`),

  indexPaper: (paperId) => request(`/papers/${paperId}/index`, { method: "POST" }),

  summarizePaper: (paperId, style = "concise") =>
    request("/papers/summarize", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, style }),
    }),

  listLibrary: () => request("/library"),

  addToLibrary: (paper, tags = [], collection = "Uncategorized") =>
    request("/library", {
      method: "POST",
      body: JSON.stringify({ paper, tags, collection }),
    }),

  updateLibraryItem: (paperId, updates) =>
    request(`/library/${paperId}`, {
      method: "PATCH",
      body: JSON.stringify(updates),
    }),

  removeFromLibrary: (paperId) =>
    request(`/library/${paperId}`, { method: "DELETE" }),

  chat: (message, paperId, history = []) =>
    request("/chat", {
      method: "POST",
      body: JSON.stringify({ message, paper_id: paperId, history }),
    }),

  agentTask: (instruction) =>
    request("/agent/task", {
      method: "POST",
      body: JSON.stringify({ instruction }),
    }),
};
