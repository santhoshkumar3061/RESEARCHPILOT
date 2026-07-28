import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Discover", end: true },
  { to: "/library", label: "Library" },
  { to: "/chat", label: "Ask my library" },
  { to: "/agent", label: "Agent tasks" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        ResearchPilot
        <small>Research Intelligence Hub</small>
      </div>
      <nav>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.end}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
