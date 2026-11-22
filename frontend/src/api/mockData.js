// Date mock folosite când backend-ul / mock API-ul lui Elena nu rulează.
// Coordonatele poligoanelor sunt în ordine GeoJSON: [lon, lat].

// Generează o serie de timp anuală (2000-2026) pentru un teren.
// changeYear = anul în care începe construcția (NDVI scade, SAR crește).
// Dacă changeYear este null, terenul rămâne stabil.
function buildTimeline({ ndviStart, ndviEnd, sarStart, sarEnd, lstStart, lstEnd, changeYear }) {
  const points = [];
  for (let year = 2000; year <= 2026; year += 1) {
    const progress =
      changeYear === null ? 0 : Math.min(1, Math.max(0, (year - changeYear) / 4));
    // mic zgomot determinist, ca graficele să nu fie linii perfecte
    const noise = Math.sin(year * 1.7) * 0.02;
    const month = year >= 2026 ? 10 : 6;
    points.push({
      year,
      month,
      observation_date: `${year}-${String(month).padStart(2, "0")}-15`,
      sensor: year < 2015 ? "LANDSAT" : "SENTINEL-2",
      ndvi: Number((ndviStart + (ndviEnd - ndviStart) * progress + noise).toFixed(2)),
      sar_db: Number((sarStart + (sarEnd - sarStart) * progress + noise * 10).toFixed(1)),
      lst_c: Number((lstStart + (lstEnd - lstStart) * progress + noise * 20).toFixed(1)),
      uncertain: false,
    });
  }
  return points;
}

export const MOCK_SITES = [
  {
    id: "bucharest-a0-north",
    name: "Bucharest – Ilfov A0 Corridor",
    region: "Ilfov",
    city: "Bucharest",
    status: "amber", // "green" | "amber"
    area_m2: 142000,
    polygon: [
      [25.92, 44.52],
      [25.96, 44.52],
      [25.96, 44.5],
      [25.92, 44.5],
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
    timeline: buildTimeline({
      ndviStart: 0.68, ndviEnd: 0.19,
      sarStart: -11.4, sarEnd: -4.2,
      lstStart: 29, lstEnd: 37,
      changeYear: 2025,
    }),
  },
  {
    id: "cluj-floresti",
    name: "Cluj-Napoca – Florești Residential Belt",
    region: "Cluj",
    city: "Cluj-Napoca",
    status: "amber",
    area_m2: 98000,
    polygon: [
      [23.47, 46.76],
      [23.5, 46.76],
      [23.5, 46.74],
      [23.47, 46.74],
      [23.47, 46.76],
    ],
    alerts: [
      {
        id: "al-2",
        title: "Structural Expansion Detected (SAR Backscatter Surge)",
        confirmed_by_radar: true,
        duration_months: 6,
        winter_uncertain: false,
        detected_at: "2026-08-03",
      },
    ],
    timeline: buildTimeline({
      ndviStart: 0.71, ndviEnd: 0.22,
      sarStart: -12.1, sarEnd: -5.0,
      lstStart: 27, lstEnd: 35,
      changeYear: 2023,
    }),
  },
  {
    id: "cluj-jucu-logistics",
    name: "Cluj-Napoca – Jucu Logistics Park",
    region: "Cluj",
    city: "Cluj-Napoca",
    status: "green",
    area_m2: 215000,
    polygon: [
      [23.63, 46.85],
      [23.68, 46.85],
      [23.68, 46.82],
      [23.63, 46.82],
      [23.63, 46.85],
    ],
    alerts: [],
    timeline: buildTimeline({
      ndviStart: 0.66, ndviEnd: 0.14,
      sarStart: -11.8, sarEnd: -3.9,
      lstStart: 28, lstEnd: 38,
      changeYear: 2010,
    }),
  },
  {
    id: "timisoara-ghiroda",
    name: "Timișoara – Ghiroda Industrial Zone",
    region: "Timiș",
    city: "Timișoara",
    status: "amber",
    area_m2: 176000,
    polygon: [
      [21.27, 45.8],
      [21.31, 45.8],
      [21.31, 45.78],
      [21.27, 45.78],
      [21.27, 45.8],
    ],
    alerts: [
      {
        id: "al-3",
        title: "Active Land Conversion & Structural Buildup",
        confirmed_by_radar: true,
        duration_months: 5,
        winter_uncertain: false,
        detected_at: "2026-09-21",
      },
    ],
    timeline: buildTimeline({
      ndviStart: 0.64, ndviEnd: 0.2,
      sarStart: -11.0, sarEnd: -4.6,
      lstStart: 28, lstEnd: 36,
      changeYear: 2024,
    }),
  },
  {
    id: "timisoara-agricultural-reserve",
    name: "Timișoara – Western Agricultural Plot",
    region: "Timiș",
    city: "Timișoara",
    status: "green",
    area_m2: 120000,
    polygon: [
      [21.1, 45.76],
      [21.13, 45.76],
      [21.13, 45.74],
      [21.1, 45.74],
      [21.1, 45.76],
    ],
    alerts: [],
    timeline: buildTimeline({
      ndviStart: 0.62, ndviEnd: 0.6,
      sarStart: -11.5, sarEnd: -11.3,
      lstStart: 27, lstEnd: 27.5,
      changeYear: null,
    }),
  },
];

export const MOCK_AI_SUMMARY = {
  summary:
    "Sustained vegetation drop (NDVI) paired with higher SAR backscatter over 4 months indicates ground preparation rather than seasonal field rotation.",
  is_estimate: false,
};

// Răspuns mock în același format ca ExecutiveSummaryResponse din backend.
export function buildMockExecutiveSummary(siteId) {
  const site = MOCK_SITES.find((s) => s.id === siteId);
  const isAmber = site?.status === "amber";
  return {
    site_id: siteId,
    site_name: site?.name ?? siteId,
    signal_type: isAmber ? "CONVERSION_ACTIVE" : "BASELINE_STABLE",
    severity: isAmber ? "AMBER" : "GREEN",
    summary: isAmber
      ? "Sustained vegetation loss paired with a rise in radar backscatter suggests active ground preparation rather than seasonal field rotation. (Mock data – estimate.)"
      : "Vegetation and radar signals are stable against the historical baseline. No construction activity detected. (Mock data – estimate.)",
    key_signals: isAmber
      ? ["NDVI drop", "SAR VV increase", "Radar-confirmed"]
      : ["NDVI stable", "SAR stable"],
    provider_used: "mock",
    generated_at: new Date().toISOString(),
  };
}

// Răspuns mock în formatul SiteChatResponse (reply, referenced_metrics, provider_used).
export function buildMockChatReply(siteId, message) {
  const site = MOCK_SITES.find((s) => s.id === siteId);
  return {
    reply: `Mock answer for "${message}" about ${site?.name ?? siteId}. The real AI assistant answers when the backend is running. Figures here are estimates.`,
    referenced_metrics: [],
    provider_used: "mock",
  };
}
