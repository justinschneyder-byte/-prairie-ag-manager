import { useEffect, useMemo, useState } from "react";
import { api } from "../api.js";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import { useResourceList, currentYear } from "../hooks.js";
import { CLIMATE_NORMALS, CLIMATE_NORMALS_NOTE } from "../data/climateNormals.js";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const rainColumns = (year) => [
  { key: "year", label: "Year", type: "number", required: true, default: year },
  { key: "date", label: "Date", type: "date" },
  { key: "month", label: "Month (1-12)", type: "number" },
  { key: "mm", label: "mm", type: "number" },
  { key: "notes", label: "Notes", type: "textarea" },
];

const FROST_TYPES = ["Light Frost", "Hard Frost", "Late Spring Frost", "First Fall Frost"];
const frostColumns = (year) => [
  { key: "year", label: "Year", type: "number", required: true, default: year },
  { key: "date", label: "Date", type: "date" },
  { key: "type", label: "Type", type: "select", options: FROST_TYPES.map((t) => ({ value: t, label: t })) },
  { key: "temp_c", label: "Temp (°C)", type: "number" },
  { key: "notes", label: "Notes", type: "textarea" },
];

const HAIL_SEVERITY = ["Light", "Moderate", "Severe"];
const hailColumns = (year) => [
  { key: "year", label: "Year", type: "number", required: true, default: year },
  { key: "date", label: "Date", type: "date" },
  { key: "severity", label: "Severity", type: "select", options: HAIL_SEVERITY.map((s) => ({ value: s, label: s })) },
  { key: "notes", label: "Notes", type: "textarea" },
];

function MonthlyChart({ year }) {
  const { data, loading } = useResourceList("weather/rain", { year });

  const totals = useMemo(() => {
    const arr = new Array(12).fill(0);
    data.forEach((r) => {
      const m = r.month || (r.date ? Number(r.date.slice(5, 7)) : null);
      if (m >= 1 && m <= 12) arr[m - 1] += Number(r.mm) || 0;
    });
    return arr;
  }, [data]);

  const max = Math.max(1, ...totals);

  if (loading) return <p className="empty-state">Loading…</p>;

  return (
    <div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: "0.5rem", height: "180px", padding: "0.5rem 0" }}>
        {totals.map((mm, i) => (
          <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "0.3rem" }}>
            <div
              title={`${MONTH_NAMES[i]}: ${mm.toFixed(1)} mm`}
              style={{
                width: "100%",
                height: `${Math.max(2, (mm / max) * 150)}px`,
                background: "var(--color-primary)",
                borderRadius: "4px 4px 0 0",
              }}
            />
            <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>{MONTH_NAMES[i]}</span>
          </div>
        ))}
      </div>
      <p className="empty-state" style={{ fontStyle: "normal" }}>
        Total for {year}: {totals.reduce((a, b) => a + b, 0).toFixed(1)} mm
      </p>
    </div>
  );
}

function YearComparison() {
  const { data, loading } = useResourceList("weather/rain");

  const totalsByYear = useMemo(() => {
    const map = {};
    data.forEach((r) => {
      map[r.year] = (map[r.year] || 0) + (Number(r.mm) || 0);
    });
    return Object.entries(map)
      .map(([year, mm]) => ({ year: Number(year), mm }))
      .sort((a, b) => a.year - b.year);
  }, [data]);

  const max = Math.max(1, ...totalsByYear.map((t) => t.mm));

  if (loading) return <p className="empty-state">Loading…</p>;
  if (totalsByYear.length === 0) return <p className="empty-state">No rainfall data logged yet.</p>;

  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: "0.75rem", height: "200px", padding: "0.5rem 0", overflowX: "auto" }}>
      {totalsByYear.map(({ year, mm }) => (
        <div key={year} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.3rem", minWidth: "40px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>{mm.toFixed(0)}</span>
          <div
            style={{
              width: "28px",
              height: `${Math.max(2, (mm / max) * 150)}px`,
              background: "var(--color-primary)",
              borderRadius: "4px 4px 0 0",
            }}
          />
          <span style={{ fontSize: "0.75rem" }}>{year}</span>
        </div>
      ))}
    </div>
  );
}

function ClimateNormalsTable() {
  return (
    <div>
      <div className="table-scroll">
        <table className="record-table">
          <thead>
            <tr>
              <th>Month</th>
              <th>Avg High (°C)</th>
              <th>Avg Low (°C)</th>
              <th>Mean (°C)</th>
              <th>Precip (mm)</th>
            </tr>
          </thead>
          <tbody>
            {CLIMATE_NORMALS.map((row) => (
              <tr key={row.month}>
                <td>{row.month}</td>
                <td>{row.avgHigh}</td>
                <td>{row.avgLow}</td>
                <td>{row.mean}</td>
                <td>{row.precipMm}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="empty-state">{CLIMATE_NORMALS_NOTE}</p>
    </div>
  );
}

function RegionalForecast() {
  const [forecast, setForecast] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    api
      .regionalForecast()
      .then((data) => !cancelled && setForecast(data))
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return <p className="error-text">Couldn't load the forecast: {error}</p>;
  if (!forecast) return <p className="empty-state">Loading forecast…</p>;

  return (
    <div className="table-scroll">
      <table className="record-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>High</th>
            <th>Low</th>
            <th>Precip</th>
            <th>Chance</th>
          </tr>
        </thead>
        <tbody>
          {forecast.days.map((d) => (
            <tr key={d.date}>
              <td>{d.date}</td>
              <td>{d.temp_high != null ? `${d.temp_high}°C` : "—"}</td>
              <td>{d.temp_low != null ? `${d.temp_low}°C` : "—"}</td>
              <td>{d.precip_mm != null ? `${d.precip_mm} mm` : "—"}</td>
              <td>{d.precip_probability != null ? `${d.precip_probability}%` : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RegionalHistory({ year }) {
  const [history, setHistory] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    setHistory(null);
    setError("");
    api
      .regionalHistory(year)
      .then((data) => !cancelled && setHistory(data))
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [year]);

  if (error) return <p className="error-text">Couldn't load {year} regional data: {error}</p>;
  if (!history) return <p className="empty-state">Loading {year} regional data…</p>;

  const max = Math.max(1, ...history.months.map((m) => m.precip_mm || 0));

  return (
    <div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: "0.5rem", height: "180px", padding: "0.5rem 0" }}>
        {history.months.map((m) => (
          <div key={m.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "0.3rem" }}>
            <div
              title={`${MONTH_NAMES[m.month - 1]}: ${m.precip_mm ?? 0} mm`}
              style={{
                width: "100%",
                height: `${Math.max(2, ((m.precip_mm || 0) / max) * 150)}px`,
                background: "var(--color-primary)",
                borderRadius: "4px 4px 0 0",
              }}
            />
            <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>{MONTH_NAMES[m.month - 1]}</span>
          </div>
        ))}
      </div>
      <div className="table-scroll">
        <table className="record-table">
          <thead>
            <tr>
              <th>Month</th>
              <th>Precip (mm)</th>
              <th>Avg High (°C)</th>
              <th>Avg Low (°C)</th>
            </tr>
          </thead>
          <tbody>
            {history.months.map((m) => (
              <tr key={m.month}>
                <td>{MONTH_NAMES[m.month - 1]}</td>
                <td>{m.precip_mm ?? "—"}</td>
                <td>{m.temp_high_avg ?? "—"}</td>
                <td>{m.temp_low_avg ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const ANALYSIS_TABS = [
  { key: "chart", label: "Monthly Chart" },
  { key: "compare", label: "Year Comparison" },
  { key: "normals", label: "Climate Normals" },
];

export default function Weather() {
  const [regionalYear, setRegionalYear] = useState(currentYear());
  const [year, setYear] = useState(currentYear());
  const [analysisTab, setAnalysisTab] = useState("chart");

  return (
    <div>
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2>Regional Weather — Magrath, AB</h2>
          <YearSelect value={regionalYear} onChange={setRegionalYear} />
        </div>
        <p className="empty-state" style={{ fontStyle: "normal", marginTop: 0 }}>
          Sourced from Open-Meteo — separate from your own logged rainfall below.
        </p>
        <h3 style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>Forecast (next 10 days)</h3>
        <RegionalForecast />
        <h3 style={{ fontSize: "0.95rem", margin: "1rem 0 0.5rem" }}>{regionalYear} Regional History</h3>
        <RegionalHistory year={regionalYear} />
      </div>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2>Farm Weather Log</h2>
          <YearSelect value={year} onChange={setYear} />
        </div>
        <p className="empty-state" style={{ fontStyle: "normal", marginTop: 0 }}>
          What actually happened on our fields — recorded by you.
        </p>

        <h3 style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>Rainfall</h3>
        <ResourceTable
          key={`rain-${year}`}
          resource="weather/rain"
          columns={rainColumns(year)}
          params={{ year }}
          addLabel="Add rainfall entry"
          emptyText={`No rainfall logged for ${year}.`}
        />

        <h3 style={{ fontSize: "0.95rem", margin: "1.25rem 0 0.5rem" }}>Frost Events</h3>
        <ResourceTable
          key={`frost-${year}`}
          resource="weather/frost"
          columns={frostColumns(year)}
          params={{ year }}
          addLabel="Add frost event"
          emptyText={`No frost events logged for ${year}.`}
        />

        <h3 style={{ fontSize: "0.95rem", margin: "1.25rem 0 0.5rem" }}>Hail Events</h3>
        <ResourceTable
          key={`hail-${year}`}
          resource="weather/hail"
          columns={hailColumns(year)}
          params={{ year }}
          addLabel="Add hail event"
          emptyText={`No hail events logged for ${year}.`}
        />

        <h3 style={{ fontSize: "0.95rem", margin: "1.25rem 0 0.5rem" }}>Analysis</h3>
        <div className="sub-tab-bar">
          {ANALYSIS_TABS.map((t) => (
            <button key={t.key} className={analysisTab === t.key ? "active" : ""} onClick={() => setAnalysisTab(t.key)}>
              {t.label}
            </button>
          ))}
        </div>
        {analysisTab === "chart" && <MonthlyChart year={year} />}
        {analysisTab === "compare" && <YearComparison />}
        {analysisTab === "normals" && <ClimateNormalsTable />}
      </div>
    </div>
  );
}
