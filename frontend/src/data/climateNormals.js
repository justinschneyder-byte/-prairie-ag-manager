// Approximate 30-year climate normals for the Magrath / Lethbridge area of southern Alberta.
// These are representative reference figures for planning purposes only — for precise data,
// check Environment Canada's official station normals for the nearest reporting station.
export const CLIMATE_NORMALS = [
  { month: "January", avgHigh: -2, avgLow: -12, mean: -7, precipMm: 15 },
  { month: "February", avgHigh: 1, avgLow: -9, mean: -4, precipMm: 12 },
  { month: "March", avgHigh: 6, avgLow: -5, mean: 1, precipMm: 18 },
  { month: "April", avgHigh: 12, avgLow: 0, mean: 6, precipMm: 25 },
  { month: "May", avgHigh: 18, avgLow: 5, mean: 11, precipMm: 45 },
  { month: "June", avgHigh: 21, avgLow: 9, mean: 15, precipMm: 65 },
  { month: "July", avgHigh: 25, avgLow: 11, mean: 18, precipMm: 45 },
  { month: "August", avgHigh: 25, avgLow: 10, mean: 17, precipMm: 40 },
  { month: "September", avgHigh: 19, avgLow: 5, mean: 12, precipMm: 30 },
  { month: "October", avgHigh: 13, avgLow: 0, mean: 6, precipMm: 20 },
  { month: "November", avgHigh: 4, avgLow: -6, mean: -1, precipMm: 15 },
  { month: "December", avgHigh: -1, avgLow: -10, mean: -6, precipMm: 15 },
];

export const CLIMATE_NORMALS_NOTE =
  "Figures are approximate reference values for the Magrath area, not an official Environment Canada download. Cross-check against the current 1991–2020 normals for the nearest station (Lethbridge) if you need precise numbers.";
