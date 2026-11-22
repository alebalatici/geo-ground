import { apiGet, apiPost } from "./client";
import { MOCK_SITES, MOCK_AI_SUMMARY } from "./mockData";

const SIGNAL_TITLES = {
  CONVERSION_ACTIVE: "Active Land Conversion & Structural Buildup",
  STRUCTURAL_EXPANSION: "Structural Expansion Detected (SAR Backscatter Surge)",
  LAND_CLEARING: "Early Ground Clearing & Vegetation Drop",
  BASELINE_STABLE: "Baseline Conditions Stable",
};

function mapBackendSiteToFrontend(site) {
  const ring = site?.geometry?.coordinates?.[0] || [];
  const severity = (site?.latest_alert?.severity || "GREEN").toLowerCase();
  const signalType = site?.latest_alert?.signal_type || "BASELINE_STABLE";
  const sarDelta = site?.latest_alert?.sar_vv_delta_db;

  const alerts =
    site?.latest_alert && signalType !== "BASELINE_STABLE"
      ? [
          {
            id: `${site.id}-alert`,
            title: SIGNAL_TITLES[signalType] || signalType,
            confirmed_by_radar: sarDelta !== null && sarDelta !== undefined && sarDelta > 1.5,
            duration_months: 4,
            winter_uncertain: false,
            detected_at: site.latest_alert.evaluated_at
              ? site.latest_alert.evaluated_at.slice(0, 10)
              : new Date().toISOString().slice(0, 10),
          },
        ]
      : [];

  return {
    id: site.id,
    name: site.name,
    region: site.city,
    sector_type: site.sector_type,
    status: severity === "amber" || severity === "red" ? "amber" : "green",
    area_m2: site.area_hectares ? Math.round(site.area_hectares * 10000) : 0,
    area_hectares: site.area_hectares,
    polygon: ring,
    alerts,
    latest_alert: site.latest_alert,
    timeline: [],
  };
}

export async function fetchSites(city = null) {
  try {
    const query = city ? `/sites?city=${encodeURIComponent(city)}` : "/sites";
    const rawSites = await apiGet(query);
    const data = Array.isArray(rawSites) ? rawSites.map(mapBackendSiteToFrontend) : [];
    return { data, source: "api" };
  } catch (err) {
    console.warn("Using mock sites:", err.message);
    return { data: MOCK_SITES, source: "mock" };
  }
}

export async function fetchSiteTimeline(siteId) {
  try {
    const raw = await apiGet(`/sites/${siteId}/timeline`);
    const data = (raw?.points || []).map((pt) => ({
      year: pt.year,
      month: Number(pt.observation_date?.slice(5, 7) || 6),
      observation_date: pt.observation_date,
      sensor: pt.sensor,
      ndvi: pt.ndvi,
      sar_db: pt.sar_vv_db,
      lst_c: pt.lst_c,
      uncertain: false,
    }));
    return { data, source: "api" };
  } catch (err) {
    console.warn("Using mock timeline:", err.message);
    const site = MOCK_SITES.find((s) => s.id === siteId);
    return { data: site?.timeline ?? [], source: "mock" };
  }
}

export async function fetchAiSummary(siteId) {
  try {
    const data = await apiGet(`/sites/${siteId}/executive-summary`);
    return {
      data: {
        summary: data.executive_summary || data.summary || JSON.stringify(data),
        is_estimate: Boolean(data.is_estimate),
      },
      source: "api",
    };
  } catch (err) {
    console.warn("Using mock AI summary:", err.message);
    return { data: MOCK_AI_SUMMARY, source: "mock" };
  }
}

export async function sendChatMessage(siteId, payload) {
  return apiPost(`/sites/${siteId}/chat`, payload);
}