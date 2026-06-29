import { Navigate, Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { About } from "./pages/About";
import { LinewidthConverter } from "./pages/LinewidthConverter";
import { UnitConverter } from "./pages/UnitConverter";

export default function App() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6 md:p-8">
        <Routes>
          <Route path="/" element={<About />} />
          <Route path="/unit-converter" element={<UnitConverter />} />
          <Route path="/linewidth-converter" element={<LinewidthConverter />} />
          <Route path="*" element={<Navigate to="/unit-converter" replace />} />
        </Routes>
      </main>
    </div>
  );
}
