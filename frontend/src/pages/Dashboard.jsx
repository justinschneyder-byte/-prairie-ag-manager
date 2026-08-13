import { useMemo } from "react";
import { useResourceList, currentYear } from "../hooks.js";

export default function Dashboard() {
  const year = currentYear();

  const { data: fields } = useResourceList("fields");
  const { data: machines } = useResourceList("machines");
  const { data: crops } = useResourceList("crops", { year });
  const { data: rain } = useResourceList("weather/rain", { year });

  const totalAcres = useMemo(() => fields.reduce((sum, f) => sum + (Number(f.acres) || 0), 0), [fields]);
  const totalRain = useMemo(() => rain.reduce((sum, r) => sum + (Number(r.mm) || 0), 0), [rain]);
  const avgBpa = useMemo(() => {
    const withYield = crops.filter((c) => c.bushels_per_acre);
    if (withYield.length === 0) return null;
    return withYield.reduce((s, c) => s + Number(c.bushels_per_acre), 0) / withYield.length;
  }, [crops]);

  return (
    <div>
      <div className="card">
        <h2>Prairie Ag Manager</h2>
        <p className="empty-state" style={{ fontStyle: "normal", margin: 0 }}>Magrath, Alberta</p>
      </div>

      <div className="stat-grid">
        <div className="stat-tile">
          <div className="value">{fields.length}</div>
          <div className="label">Fields ({totalAcres.toFixed(0)} acres)</div>
        </div>
        <div className="stat-tile">
          <div className="value">{machines.length}</div>
          <div className="label">Machines</div>
        </div>
        <div className="stat-tile">
          <div className="value">{crops.length}</div>
          <div className="label">Crop records ({year})</div>
        </div>
        <div className="stat-tile">
          <div className="value">{avgBpa ? avgBpa.toFixed(1) : "—"}</div>
          <div className="label">Avg bu/acre ({year})</div>
        </div>
        <div className="stat-tile">
          <div className="value">{totalRain.toFixed(0)} mm</div>
          <div className="label">Rainfall ({year})</div>
        </div>
      </div>

      <div className="card">
        <h2>Recent crop activity</h2>
        {crops.length === 0 ? (
          <p className="empty-state">No crop records for {year} yet — add one from Fields &amp; Crops or Add Records.</p>
        ) : (
          <div className="table-scroll">
            <table className="record-table">
              <thead>
                <tr>
                  <th>Crop</th>
                  <th>Variety</th>
                  <th>Seeded</th>
                  <th>Harvested</th>
                  <th>Bu/Acre</th>
                </tr>
              </thead>
              <tbody>
                {crops.slice(0, 8).map((c) => (
                  <tr key={c.id}>
                    <td>{c.crop || "—"}</td>
                    <td>{c.variety || "—"}</td>
                    <td>{c.seeded_date || "—"}</td>
                    <td>{c.harvested_date || "—"}</td>
                    <td>{c.bushels_per_acre ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
