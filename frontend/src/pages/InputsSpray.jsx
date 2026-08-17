import { useEffect, useRef, useState } from "react";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import BlueBookViewer from "../components/BlueBookViewer.jsx";
import { api } from "../api.js";
import { useFieldOptions, currentYear } from "../hooks.js";

const INPUT_TYPES = ["Seed", "Fertilizer", "Herbicide", "Fungicide", "Insecticide", "Fuel", "Other"];

function formatSize(bytes) {
  if (!bytes) return "—";
  const mb = bytes / (1024 * 1024);
  if (mb < 1) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${mb.toFixed(1)} MB`;
}

function BlueBookSection() {
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [viewerOpen, setViewerOpen] = useState(false);
  const fileInputRef = useRef(null);

  function loadMeta() {
    setLoading(true);
    api
      .blueBookMeta()
      .then((data) => {
        setMeta(data);
        setError("");
      })
      .catch((err) => {
        if (err.status === 404) setMeta(null);
        else setError(err.message);
      })
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadMeta();
  }, []);

  async function handleFileSelected(e) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      await api.uploadBlueBook(file);
      loadMeta();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm("Remove the uploaded Blue Book PDF? You can upload it again anytime.")) return;
    setError("");
    try {
      await api.deleteBlueBook();
      setMeta(null);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Blue Book Reference</h2>
      <p className="empty-state" style={{ fontStyle: "normal", marginTop: 0 }}>
        Store your own downloaded copy of Alberta's Crop Protection Guide (the "Blue Book") here for quick reference
        on your phone or desktop. We don't extract, copy, or index its contents — it's copyrighted material — this
        just stores and displays your own file, the way it'd sit as a PDF on your phone.
      </p>
      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p className="empty-state">Checking…</p>
      ) : meta ? (
        <div className="blue-book-status">
          <div className="blue-book-status-info">
            <strong>{meta.filename}</strong>
            <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
              {formatSize(meta.size_bytes)} · uploaded {new Date(meta.uploaded_at).toLocaleDateString()}
            </span>
          </div>
          <div className="blue-book-status-actions">
            <button className="btn" onClick={() => setViewerOpen(true)}>
              Open Blue Book
            </button>
            <button className="btn secondary" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
              {uploading ? "Uploading…" : "Replace"}
            </button>
            <button className="btn danger" onClick={handleDelete}>
              Remove
            </button>
          </div>
        </div>
      ) : (
        <div className="blue-book-status">
          <span className="empty-state" style={{ margin: 0 }}>
            No Blue Book uploaded yet.
          </span>
          <button className="btn" onClick={() => fileInputRef.current?.click()} disabled={uploading}>
            {uploading ? "Uploading…" : "Upload Blue Book PDF"}
          </button>
        </div>
      )}

      <input ref={fileInputRef} type="file" accept="application/pdf" style={{ display: "none" }} onChange={handleFileSelected} />

      {viewerOpen && <BlueBookViewer onClose={() => setViewerOpen(false)} />}
    </div>
  );
}

export default function InputsSpray() {
  const [year, setYear] = useState(currentYear());
  const fieldOptions = useFieldOptions();

  const inputColumns = [
    { key: "field_id", label: "Field", type: "select", options: fieldOptions },
    { key: "year", label: "Year", type: "number", required: true, default: year },
    { key: "date", label: "Date", type: "date" },
    { key: "type", label: "Type", type: "select", options: INPUT_TYPES.map((t) => ({ value: t, label: t })), valueType: "string" },
    { key: "product", label: "Product", type: "text" },
    { key: "rate_per_acre", label: "Rate/Acre", type: "text" },
    { key: "total_amount", label: "Total Amount", type: "text" },
    { key: "cost", label: "Cost ($)", type: "number" },
    { key: "notes", label: "Notes", type: "textarea" },
  ];

  const sprayColumns = [
    { key: "field_id", label: "Field", type: "select", options: fieldOptions },
    { key: "year", label: "Year", type: "number", required: true, default: year },
    { key: "date", label: "Date", type: "date" },
    { key: "crop", label: "Crop", type: "text" },
    { key: "products", label: "Products", type: "text" },
    { key: "acres", label: "Acres", type: "number" },
    { key: "wind", label: "Wind", type: "text" },
    { key: "temp", label: "Temp", type: "text" },
    { key: "operator", label: "Operator", type: "text" },
    { key: "notes", label: "Notes", type: "textarea" },
  ];

  return (
    <div>
      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2>Inputs</h2>
          <YearSelect value={year} onChange={setYear} />
        </div>
        <ResourceTable
          key={`inputs-${year}`}
          resource="inputs"
          columns={inputColumns}
          params={{ year }}
          addLabel="Add input"
          emptyText={`No inputs logged for ${year}.`}
        />
      </div>

      <div className="card">
        <h2>Spray Records</h2>
        <ResourceTable
          key={`sprays-${year}`}
          resource="sprays"
          columns={sprayColumns}
          params={{ year }}
          addLabel="Add spray record"
          emptyText={`No spray records for ${year}.`}
        />
      </div>

      <BlueBookSection />
    </div>
  );
}
