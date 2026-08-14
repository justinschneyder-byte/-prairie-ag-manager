import { useState } from "react";
import Farm from "./pages/Farm.jsx";
import FieldsCrops from "./pages/FieldsCrops.jsx";
import InputsSpray from "./pages/InputsSpray.jsx";
import Machinery from "./pages/Machinery.jsx";
import Weather from "./pages/Weather.jsx";
import WeedsPests from "./pages/WeedsPests.jsx";
import AddRecords from "./pages/AddRecords.jsx";

const TABS = [
  { key: "farm", label: "Farm", component: Farm },
  { key: "fields", label: "Fields & Crops", component: FieldsCrops },
  { key: "inputs", label: "Inputs & Spray", component: InputsSpray },
  { key: "machinery", label: "Machinery", component: Machinery },
  { key: "weather", label: "Weather & Rain", component: Weather },
  { key: "weeds", label: "Weeds & Pests", component: WeedsPests },
  { key: "chat", label: "Add Records", component: AddRecords },
];

export default function App() {
  const [tab, setTab] = useState("farm");

  const ActiveComponent = TABS.find((t) => t.key === tab)?.component || Farm;

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>🌾 Prairie Ag Manager</h1>
      </header>
      <nav className="tab-bar">
        {TABS.map((t) => (
          <button key={t.key} className={tab === t.key ? "active" : ""} onClick={() => setTab(t.key)}>
            {t.label}
          </button>
        ))}
      </nav>
      <main className="tab-content">
        <ActiveComponent />
      </main>
    </div>
  );
}
