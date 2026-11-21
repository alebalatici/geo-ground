import { apiGet, apiPost } from "./client";
import { MOCK_SITES, MOCK_AI_SUMMARY } from "./mockData";

export async function fetchSites() {
  try {
    const data = await apiGet("/sites");
    return { data, source: "api" };
  } catch (err) {
    console.warn("Using mock sites:", err.message);
    return { data: MOCK_SITES, source: "mock" };
  }
}

export async function fetchAiSummary(siteId) {
  try {
    const data = await apiGet(`/sites/${siteId}/summary`);
    return { data, source: "api" };
  } catch (err) {
    console.warn("Using mock AI summary:", err.message);
    return { data: MOCK_AI_SUMMARY, source: "mock" };
  }
}

export async function sendChatMessage(payload) {
  return apiPost("/chat", payload);
}