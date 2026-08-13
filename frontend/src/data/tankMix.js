// General tank-mix compatibility reference. This is NOT a substitute for the current product
// label — always follow label directions, do a jar test before mixing anything new, and check
// with your ag retailer/agronomist for specific product combinations.
export const TANK_MIX_GROUPS = [
  {
    category: "General mixing order (jar test first)",
    notes: [
      "Fill tank 1/2 to 3/4 with clean water before adding anything.",
      "Mixing order: compatibility agents/water conditioners → dry products (WDG/WP) → liquid flowables (SC/SE) → emulsifiable concentrates (EC) → surfactants/adjuvants → liquid fertilizer last.",
      "Keep agitation running the whole time products are being added and while spraying.",
      "Always jar-test an unfamiliar combination in small scale before filling the sprayer.",
    ],
  },
  {
    category: "Herbicide + herbicide",
    notes: [
      "Group 4 (e.g. 2,4-D, MCPA, clopyralid) generally mixes fine with Group 1/2 grassy or broadleaf products, but tank-mixing a Group 1 (fop/dim) with a Group 4 can antagonize wild oat control — check the specific label.",
      "Glyphosate mixed with a residual soil-applied product can be reduced in efficacy by hard water or high pH — use a water conditioner (AMS) when tank mixing.",
    ],
  },
  {
    category: "Herbicide + liquid fertilizer (28-0-0 / UAN)",
    notes: [
      "Many broadleaf herbicides tolerate a fertilizer carrier at reduced rates, but crop injury risk goes up — check label rate limits for fertilizer as carrier.",
      "Never exceed the label's maximum fertilizer percentage in the mix.",
    ],
  },
  {
    category: "Insecticide / fungicide additions",
    notes: [
      "Adding an insecticide or fungicide to a herbicide pass is common but increases the chance of antagonism or crop stress — jar test and check both labels for tank-mix guidance.",
      "Avoid mixing products with conflicting pH requirements without a buffering/compatibility agent.",
    ],
  },
];
