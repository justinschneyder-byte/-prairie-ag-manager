import { useState } from "react";
import ResourceTable from "../components/ResourceTable.jsx";
import YearSelect from "../components/YearSelect.jsx";
import { useMachineOptions, currentYear } from "../hooks.js";

const machineColumns = [
  { key: "name", label: "Machine", type: "text", required: true },
  { key: "model_year", label: "Model Year", type: "number" },
  { key: "serial_number", label: "Serial #", type: "text" },
  { key: "hours", label: "Hours", type: "number" },
];

export default function Machinery() {
  const [year, setYear] = useState(currentYear());
  const machineOptions = useMachineOptions();

  const maintenanceColumns = [
    { key: "machine_id", label: "Machine", type: "select", options: machineOptions },
    { key: "year", label: "Year", type: "number", required: true, default: year },
    { key: "date", label: "Date", type: "date" },
    { key: "type", label: "Type", type: "text" },
    { key: "description", label: "Description", type: "textarea" },
    { key: "parts", label: "Parts", type: "text" },
    { key: "cost", label: "Cost ($)", type: "number" },
    { key: "done_by", label: "Done By", type: "text" },
  ];

  return (
    <div>
      <div className="card">
        <h2>Machines</h2>
        <ResourceTable resource="machines" columns={machineColumns} addLabel="Add machine" emptyText="No machines added yet." />
      </div>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
          <h2>Maintenance Log</h2>
          <YearSelect value={year} onChange={setYear} />
        </div>
        <ResourceTable
          key={year}
          resource="maintenance"
          columns={maintenanceColumns}
          params={{ year }}
          addLabel="Add maintenance record"
          emptyText={`No maintenance records for ${year}.`}
        />
      </div>
    </div>
  );
}
