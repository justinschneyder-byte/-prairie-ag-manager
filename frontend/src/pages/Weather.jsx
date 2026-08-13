import { useMemo, useState } from "react";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import { useResourceList, currentYear } from "../hooks.js";
import { CLIMATE_NORMALS, CLIMATE_NORMALS_NOTE } from "../data/climateNormals.js";

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

const SUB_TABS = [
  { key: "log", label: "Rainfall Log" },
  { key: "chart", label: "Monthly Chart" },
  { key: "compare", label: "Year Comparison" },
  { key: "normals", label: "Climate Normals" },
  { key: "frost", label: "Frost Events" },
  { key: "hail", label: "Hail Events" },
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

export default function Weather() {
  const [subTab, setSubTab] = useState("log");
  const [year, setYear] = useState(currentYear());

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
        <h2>Weather &amp; Rain</h2>
        {subTab !== "normals" && subTab !== "compare" && <YearSelect value={year} onChange={setYear} />}
      </div>
      <div className="sub-tab-bar">
        {SUB_TABS.map((t) => (
          <button key={t.key} className={subTab === t.key ? "active" : ""} onClick={() => setSubTab(t.key)}>
            {t.label}
          </button>
        ))}
      </div>

      {subTab === "log" && (
        <ResourceTable
          key={year}
          resource="weather/rain"
          columns={rainColumns(year)}
          params={{ year }}
          addLabel="Add rainfall entry"
          emptyText={`No rainfall logged for ${year}.`}
        />
      )}
      {subTab === "chart" && <MonthlyChart year={year} />}
      {subTab === "compare" && <YearComparison />}
      {subTab === "normals" && <ClimateNormalsTable />}
      {subTab === "frost" && (
        <ResourceTable
          key={`frost-${year}`}
          resource="weather/frost"
          columns={frostColumns(year)}
          params={{ year }}
          addLabel="Add frost event"
          emptyText={`No frost events logged for ${year}.`}
        />
      )}
      {subTab === "hail" && (
        <ResourceTable
          key={`hail-${year}`}
          resource="weather/hail"
          columns={hailColumns(year)}
          params={{ year }}
          addLabel="Add hail event"
          emptyText={`No hail events logged for ${year}.`}
        />
      )}
    </div>
  );
}
