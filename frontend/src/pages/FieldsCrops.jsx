import { useState } from "react";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import { useFieldOptions, currentYear } from "../hooks.js";

const fieldColumns = [
  { key: "name", label: "Field Name", type: "text", required: true },
  { key: "acres", label: "Acres", type: "number" },
  { key: "soil_type", label: "Soil Type", type: "text" },
  { key: "notes", label: "Notes", type: "textarea" },
];

export default function FieldsCrops() {
  const [year, setYear] = useState(currentYear());
  const fieldOptions = useFieldOptions();

  const cropColumns = [
    { key: "field_id", label: "Field", type: "select", options: fieldOptions },
    { key: "year", label: "Year", type: "number", required: true, default: year },
    { key: "crop", label: "Crop", type: "text" },
    { key: "variety", label: "Variety", type: "text" },
    { key: "seeded_date", label: "Seeded", type: "date" },
    { key: "harvested_date", label: "Harvested", type: "date" },
    { key: "bushels_per_acre", label: "Bu/Acre", type: "number" },
    { key: "total_bushels", label: "Total Bu", type: "number" },
    { key: "notes", label: "Notes", type: "textarea" },
  ];

  return (
    <div>
      <div className="card">
        <h2>Fields</h2>
        <ResourceTable resource="fields" columns={fieldColumns} addLabel="Add field" emptyText="No fields added yet." />
      </div>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2>Crops</h2>
          <YearSelect value={year} onChange={setYear} />
        </div>
        <ResourceTable
          key={year}
          resource="crops"
          columns={cropColumns}
          params={{ year }}
          addLabel="Add crop record"
          emptyText={`No crop records for ${year}.`}
        />
      </div>
    </div>
  );
}
