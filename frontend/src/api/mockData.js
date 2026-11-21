export const MOCK_SITES = [
  {
    id: "bucharest-a0-north",
    name: "Bucharest – Ilfov A0 Corridor",
    region: "Ilfov",
    status: "amber", // "green" | "amber"
    area_m2: 142000,
    polygon: [
      [25.92, 44.52],
      [25.96, 44.52],
      [25.96, 44.50],
      [25.92, 44.50],
      [25.92, 44.52],
    ],
    alerts: [
      {
        id: "al-1",
        title: "Early Ground Clearing Detected",
        confirmed_by_radar: true,
        duration_months: 4,
        winter_uncertain: false,
        detected_at: "2026-10-12",
      },
    ],
    timeline: [
      { year: 2022, month: 6, ndvi: 0.68, sar_db: -11.4, uncertain: false },
      { year: 2024, month: 6, ndvi: 0.42, sar_db: -7.8, uncertain: false },
      { year: 2026, month: 10, ndvi: 0.19, sar_db: -4.2, uncertain: false },
    ],
  },
];

export const MOCK_AI_SUMMARY = {
  summary:
    "Sustained vegetation drop (NDVI) paired with higher SAR backscatter over 4 months indicates ground preparation rather than seasonal field rotation.",
  is_estimate: false,
};