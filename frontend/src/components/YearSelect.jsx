import { yearOptions } from "../hooks.js";

export default function YearSelect({ value, onChange, span = 8 }) {
  return (
    <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.85rem" }}>
      Year
      <select value={value} onChange={(e) => onChange(Number(e.target.value))}>
        {yearOptions(span).map((y) => (
          <option key={y} value={y}>
            {y}
          </option>
        ))}
      </select>
    </label>
  );
}
