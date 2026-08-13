import { useState } from "react";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import { useFieldOptions, currentYear } from "../hooks.js";

const INPUT_TYPES = ["Seed", "Fertilizer", "Herbicide", "Fungicide", "Insecticide", "Fuel", "Other"];

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
    </div>
  );
}
