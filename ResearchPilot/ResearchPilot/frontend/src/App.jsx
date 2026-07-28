import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Discover from "./pages/Discover.jsx";
import Library from "./pages/Library.jsx";
import PaperDetail from "./pages/PaperDetail.jsx";
import LibraryChat from "./pages/LibraryChat.jsx";
import AgentTasks from "./pages/AgentTasks.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <Routes>
        <Route path="/" element={<Discover />} />
        <Route path="/library" element={<Library />} />
        <Route path="/paper/:paperId" element={<PaperDetail />} />
        <Route path="/chat" element={<LibraryChat />} />
        <Route path="/agent" element={<AgentTasks />} />
      </Routes>
    </div>
  );
}
