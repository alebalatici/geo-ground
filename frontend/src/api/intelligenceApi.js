import {apiRequest} from "./client.js";
import { buildMockExecutiveSummary, buildMockChatReply } from "./mockData.js";

/**
 * Site Intelligence API: Fetch executive summary for a specific site
 * @param siteId {string} site ID
 * @returns {Promise<any>} - Promise that resolves to the executive summary data
 */
export function fetchExecutiveSummary(siteId) {
    return apiRequest(`/sites/${siteId}/executive-summary`, {
    method: "GET",
    }).catch((err) => {
      console.warn("Using mock executive summary:", err.message);
      return buildMockExecutiveSummary(siteId);
    });
}

/**
 * Site Intelligence API: Fetch enterprise analytics data for a specific site
 * @param siteId {string} site ID
 * @param message {string} chat message
 * @param activeYear {number} active year
 * @param history {Array<any>} chat history
 * @returns {Promise<any>} - Promise that resolves to the enterprise analytics data
 */
export function sendSiteChatMessage(siteId, { message, activeYear = null, history = [] }) {
    return apiRequest(`/sites/${siteId}/chat`, {
    method: 'POST',
    body: JSON.stringify({
      message,
      active_year: activeYear,
      history: history.slice(-10),
    }),
  }).catch((err) => {
    console.warn("Using mock chat reply:", err.message);
    return buildMockChatReply(siteId, message);
  });
}

