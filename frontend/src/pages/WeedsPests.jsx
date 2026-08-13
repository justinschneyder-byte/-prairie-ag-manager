import { useState } from "react";
import { WEEDS, PESTS } from "../data/weedsPests.js";
import { TANK_MIX_GROUPS } from "../data/tankMix.js";

const SUB_TABS = [
  { key: "weeds", label: "Weeds" },
  { key: "pests", label: "Pests" },
  { key: "tankmix", label: "Tank Mix Guide" },
];

export default function WeedsPests() {
  const [subTab, setSubTab] = useState("weeds");

  return (
    <div className="card">
      <h2>Weeds &amp; Pests</h2>
      <p className="empty-state" style={{ fontStyle: "normal", marginTop: 0 }}>
        General reference only — always confirm identification and current product labels before treating.
      </p>
      <div className="sub-tab-bar">
        {SUB_TABS.map((t) => (
          <button key={t.key} className={subTab === t.key ? "active" : ""} onClick={() => setSubTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {subTab === "weeds" && (
        <div className="reference-list">
          {WEEDS.map((w) => (
            <div className="reference-item" key={w.name}>
              <h3>{w.name}</h3>
              <p>
                <strong>ID:</strong> {w.id}
              </p>
              <p>
                <strong>Management:</strong> {w.management}
              </p>
            </div>
          ))}
        </div>
      )}

      {subTab === "pests" && (
        <div className="reference-list">
          {PESTS.map((p) => (
            <div className="reference-item" key={p.name}>
              <h3>{p.name}</h3>
              <p>
                <strong>ID:</strong> {p.id}
              </p>
              <p>
                <strong>Management:</strong> {p.management}
              </p>
            </div>
          ))}
        </div>
      )}

      {subTab === "tankmix" && (
        <div className="reference-list">
          {TANK_MIX_GROUPS.map((g) => (
            <div className="reference-item" key={g.category}>
              <h3>{g.category}</h3>
              <ul>
                {g.notes.map((n, i) => (
                  <li key={i}>{n}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
