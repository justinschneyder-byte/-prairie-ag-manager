import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useResourceList } from "../hooks.js";

function formatMoney(value) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "—";
  return num.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function formatNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? String(Math.round(num * 100) / 100) : "—";
}

function buildTimeline(yearData) {
  const events = [];

  yearData.crops.forEach((c) => {
    if (c.seeded_date) {
      events.push({
        date: c.seeded_date,
        type: "seeded",
        label: `Seeded ${c.crop || "crop"}${c.variety ? ` (${c.variety})` : ""}`,
      });
    }
    if (c.harvested_date) {
      const parts = [];
      if (c.bushels_per_acre) parts.push(`${formatNumber(c.bushels_per_acre)} bu/ac`);
      if (c.total_bushels) parts.push(`${formatNumber(c.total_bushels)} total bu`);
      events.push({
        date: c.harvested_date,
        type: "harvested",
        label: `Harvested${parts.length ? ` — ${parts.join(", ")}` : ""}`,
      });
    }
  });

  yearData.inputs.forEach((i) => {
    if (!i.date) return;
    const parts = [i.product].filter(Boolean);
    if (i.rate_per_acre) parts.push(`@ ${i.rate_per_acre}`);
    events.push({
      date: i.date,
      type: "input",
      label: `${i.type || "Input"}${parts.length ? `: ${parts.join(" ")}` : ""}`,
      cost: i.cost,
    });
  });

  yearData.sprays.forEach((s) => {
    if (!s.date) return;
    const parts = [];
    if (s.wind) parts.push(`wind ${s.wind}`);
    if (s.temp) parts.push(s.temp);
    events.push({
      date: s.date,
      type: "spray",
      label: `Sprayed ${s.products || ""}${parts.length ? ` — ${parts.join(", ")}` : ""}`,
    });
  });

  return events.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
}

function FieldDetail({ field, onBack }) {
  const [history, setHistory] = useState(null);
  const [error, setError] = useState("");
  const [selectedYear, setSelectedYear] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api
      .fieldHistory(field.id)
      .then((data) => {
        if (cancelled) return;
        setHistory(data);
        if (data.years.length > 0) setSelectedYear(data.years[0].year);
      })
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [field.id]);

  const yearData = history?.years.find((y) => y.year === selectedYear);

  return (
    <div>
      <button className="btn secondary" onClick={onBack} style={{ marginBottom: "0.75rem" }}>
        ← All fields
      </button>

      <div className="card">
        <h2>{field.name}</h2>
        <p className="empty-state" style={{ fontStyle: "normal", margin: 0 }}>
          {field.acres ? `${formatNumber(field.acres)} acres` : "Acres not set"}
          {field.soil_type ? ` · ${field.soil_type}` : ""}
        </p>
      </div>

      {error && <p className="error-text">{error}</p>}

      {history && history.years.length === 0 && (
        <p className="empty-state">No crop, input, or spray records for this field yet.</p>
      )}

      {history && history.years.length > 0 && (
        <div className="card">
          <div className="sub-tab-bar">
            {history.years.map((y) => (
              <button
                key={y.year}
                className={selectedYear === y.year ? "active" : ""}
                onClick={() => setSelectedYear(y.year)}
              >
                {y.year}
              </button>
            ))}
          </div>

          {yearData && (
            <>
              <div className="stat-grid" style={{ marginBottom: "1rem" }}>
                <div className="stat-tile">
                  <div className="value">{formatMoney(yearData.total_cost)}</div>
                  <div className="label">Total input cost ({selectedYear})</div>
                </div>
              </div>

              {yearData.crops.length > 0 && (
                <div style={{ marginBottom: "1rem" }}>
                  <h3 style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>Crop</h3>
                  {yearData.crops.map((c) => (
                    <div key={c.id} className="reference-item">
                      <p>
                        <strong>{c.crop || "—"}</strong>
                        {c.variety ? ` (${c.variety})` : ""}
                      </p>
                      <p>
                        Seeded {c.seeded_date || "—"} · Harvested {c.harvested_date || "—"}
                      </p>
                      <p>
                        {c.bushels_per_acre ? `${formatNumber(c.bushels_per_acre)} bu/ac` : "—"}
                        {c.total_bushels ? ` · ${formatNumber(c.total_bushels)} total bu` : ""}
                      </p>
                    </div>
                  ))}
                </div>
              )}

              <h3 style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>Timeline</h3>
              {buildTimeline(yearData).length === 0 ? (
                <p className="empty-state">No dated events for {selectedYear}.</p>
              ) : (
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {buildTimeline(yearData).map((e, i) => (
                    <li
                      key={i}
                      style={{
                        display: "flex",
                        gap: "0.75rem",
                        padding: "0.5rem 0",
                        borderBottom: "1px solid var(--color-border)",
                      }}
                    >
                      <span className="badge" style={{ flexShrink: 0 }}>
                        {e.date}
                      </span>
                      <span>
                        {e.label}
                        {e.cost ? ` — ${formatMoney(e.cost)}` : ""}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default function Farm() {
  const { data: fields, loading } = useResourceList("fields");
  const [selectedField, setSelectedField] = useState(null);

  if (selectedField) {
    return <FieldDetail field={selectedField} onBack={() => setSelectedField(null)} />;
  }

  return (
    <div>
      {!loading && fields.length === 0 && (
        <p className="empty-state">No fields yet — add one from Fields & Crops.</p>
      )}
      <div className="field-picker-grid">
        {fields.map((f) => (
          <button key={f.id} className="field-card" onClick={() => setSelectedField(f)}>
            <div className="field-card-name">{f.name}</div>
            <div className="field-card-acres">{f.acres ? `${formatNumber(f.acres)} acres` : "—"}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
