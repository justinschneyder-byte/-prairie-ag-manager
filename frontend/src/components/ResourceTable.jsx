import { useEffect, useState } from "react";
import { api } from "../api.js";

function optionLabel(col, value) {
  if (!col.options) return value;
  const match = col.options.find((o) => String(o.value) === String(value));
  return match ? match.label : value;
}

function formatDisplay(col, row) {
  const value = row[col.key];
  if (value === null || value === undefined || value === "") return "—";
  if (col.type === "select") return optionLabel(col, value);
  if (col.type === "number") {
    const num = Number(value);
    return Number.isFinite(num) ? String(Math.round(num * 100) / 100) : String(value);
  }
  return String(value);
}

function FieldInput({ col, value, onChange }) {
  if (col.type === "select") {
    return (
      <select value={value ?? ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">{col.placeholder || "—"}</option>
        {(col.options || []).map((o) => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    );
  }
  if (col.type === "textarea") {
    return <textarea rows={2} value={value ?? ""} onChange={(e) => onChange(e.target.value)} />;
  }
  return (
    <input
      type={col.type === "number" ? "number" : col.type === "date" ? "date" : "text"}
      step={col.type === "number" ? "any" : undefined}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      placeholder={col.placeholder}
    />
  );
}

export default function ResourceTable({ resource, columns, params, addLabel = "Add record", emptyText = "No records yet." }) {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [formValues, setFormValues] = useState({});
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await api.list(resource, params);
      setRows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [resource, JSON.stringify(params)]);

  function startAdd() {
    const defaults = {};
    columns.forEach((c) => {
      defaults[c.key] = c.default !== undefined ? c.default : "";
    });
    setFormValues(defaults);
    setEditingId("new");
    setError("");
  }

  function startEdit(row) {
    const values = {};
    columns.forEach((c) => {
      values[c.key] = row[c.key] ?? "";
    });
    setFormValues(values);
    setEditingId(row.id);
    setError("");
  }

  function cancelEdit() {
    setEditingId(null);
    setFormValues({});
  }

  function updateField(key, value) {
    setFormValues((v) => ({ ...v, [key]: value }));
  }

  function buildPayload() {
    const payload = {};
    columns.forEach((c) => {
      const raw = formValues[c.key];
      if (raw === "" || raw === undefined) {
        payload[c.key] = null;
      } else if (c.type === "number") {
        payload[c.key] = Number(raw);
      } else if (c.type === "select" && (c.valueType === "number" || c.key.endsWith("_id"))) {
        payload[c.key] = Number(raw);
      } else {
        payload[c.key] = raw;
      }
    });
    return payload;
  }

  async function handleSave() {
    const missingRequired = columns.find((c) => c.required && !formValues[c.key]);
    if (missingRequired) {
      setError(`${missingRequired.label} is required.`);
      return;
    }
    setSaving(true);
    setError("");
    try {
      const payload = buildPayload();
      if (editingId === "new") {
        await api.create(resource, payload);
      } else {
        await api.update(resource, editingId, payload);
      }
      cancelEdit();
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this record? This cannot be undone.")) return;
    setError("");
    try {
      await api.remove(resource, id);
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      {error && <p className="error-text">{error}</p>}
      <div className="table-scroll">
        <table className="record-table">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key}>{c.label}</th>
              ))}
              <th></th>
            </tr>
          </thead>
          <tbody>
            {editingId === "new" && (
              <tr>
                {columns.map((c) => (
                  <td key={c.key}>
                    <FieldInput col={c} value={formValues[c.key]} onChange={(v) => updateField(c.key, v)} />
                  </td>
                ))}
                <td>
                  <button className="icon-btn" onClick={handleSave} disabled={saving} title="Save">
                    ✅
                  </button>
                  <button className="icon-btn" onClick={cancelEdit} title="Cancel">
                    ✕
                  </button>
                </td>
              </tr>
            )}
            {rows.map((row) =>
              editingId === row.id ? (
                <tr key={row.id}>
                  {columns.map((c) => (
                    <td key={c.key}>
                      <FieldInput col={c} value={formValues[c.key]} onChange={(v) => updateField(c.key, v)} />
                    </td>
                  ))}
                  <td>
                    <button className="icon-btn" onClick={handleSave} disabled={saving} title="Save">
                      ✅
                    </button>
                    <button className="icon-btn" onClick={cancelEdit} title="Cancel">
                      ✕
                    </button>
                  </td>
                </tr>
              ) : (
                <tr key={row.id}>
                  {columns.map((c) => (
                    <td key={c.key}>{formatDisplay(c, row)}</td>
                  ))}
                  <td>
                    <button className="icon-btn" onClick={() => startEdit(row)} title="Edit">
                      ✏️
                    </button>
                    <button className="icon-btn danger" onClick={() => handleDelete(row.id)} title="Delete">
                      🗑️
                    </button>
                  </td>
                </tr>
              )
            )}
          </tbody>
        </table>
      </div>
      {!loading && rows.length === 0 && editingId !== "new" && <p className="empty-state">{emptyText}</p>}
      {editingId === null && (
        <button className="btn secondary" onClick={startAdd} style={{ marginTop: "0.75rem" }}>
          + {addLabel}
        </button>
      )}
    </div>
  );
}
