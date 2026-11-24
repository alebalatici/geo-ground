/**
 * ============================================================================
 * apiConfig.js — Backend connection settings
 * ============================================================================
 *
 * WHAT THIS FILE CONTROLS
 * Where the GeoGround website looks for its data (the backend server), which
 * address each kind of request is sent to, and what the website does when the
 * backend cannot be reached (it switches to the built-in demo dataset).
 *
 * WHO CAN EDIT IT
 * Anyone on the team. No React knowledge is needed: change a value, save the
 * file and refresh the browser.
 *
 * NOTES FOR DEVELOPERS
 * - This file contains plain data only: no React, no fetch calls.
 * - The requests themselves are made by the files in src/services/ (and, until
 *   the migration is finished, by the legacy files in src/api/).
 * - Endpoint paths use placeholders written like :siteId. The HTTP layer
 *   replaces each placeholder with the real value when a request is sent.
 */

/**
 * ----------------------------------------------------------------------------
 * SECTION 1 — Backend address
 * ----------------------------------------------------------------------------
 */

/**
 * Base address of the GeoGround backend. Every path listed in API_ENDPOINTS is
 * added to the end of this address.
 *
 * Example: 'http://localhost:8000' means the list of parcels is requested from
 * http://localhost:8000/sites
 *
 * Do not add a "/" at the end.
 *
 * To use a different server for a staging or production build WITHOUT editing
 * this file, create a file named .env in the project root containing:
 *   VITE_API_BASE_URL=https://api.your-domain.com
 *
 * @type {string}
 */
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

/**
 * ----------------------------------------------------------------------------
 * SECTION 2 — Endpoint paths
 * ----------------------------------------------------------------------------
 * Each value is the path of one backend route, added after API_BASE_URL.
 * Anything written like :siteId is replaced automatically with the identifier
 * of the parcel currently selected on screen.
 *
 * Keep these paths identical to the routes exposed by the backend.
 */
export const API_ENDPOINTS = {
  /** List of all monitored parcels ("sites") with their polygon geometry. Feeds the parcel selector and the satellite viewport. */
  sites: '/sites',

  /** Executive intelligence brief for one parcel. Feeds the "Executive Intelligence Brief" card. */
  executiveSummary: '/sites/:siteId/executive-summary',

  /** Contextual AI advisor chat for one parcel (messages are sent here). Feeds the chat sidebar. */
  siteChat: '/sites/:siteId/chat',

  /** Yearly satellite readings (NDVI, SAR, surface temperature) for one parcel. Feeds the historical timeline and the viewport readings. */
  siteTimeline: '/sites/:siteId/timeline',

  /** Multispectral correlation series for one parcel. Feeds the charts in the Enterprise Analytics view. */
  siteCorrelations: '/sites/:siteId/correlations',

  /** Satellite raster preview or tile address for one parcel, sensor and year. Feeds the image drawn behind the parcel polygon. */
  siteRaster: '/sites/:siteId/raster',

  /** CSV file with the parcel coordinates and readings. Used by the "Export CSV" button. */
  siteCsvExport: '/sites/:siteId/export.csv',

  /** Sign-in request (email and password are sent here). Used by the login window. */
  authLogin: '/auth/login',

  /** Sign-out request. Used by the "Sign Out" button. */
  authLogout: '/auth/logout',
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 3 — Demo (fallback) mode
 * ----------------------------------------------------------------------------
 * Controls when the website uses the built-in demo dataset instead of the
 * live backend. The "Live" / "Demo Dataset" badge in the top bar reflects
 * whichever source is active.
 */
export const API_FALLBACK_FLAGS = {
  /**
   * true  = never contact the backend; always show the demo dataset.
   * false = try the backend first (normal behaviour).
   * Useful for presentations or when the backend is down for maintenance.
   */
  forceDemoMode: false,

  /**
   * true  = if the backend cannot be reached, silently switch to the demo
   *         dataset and show the "Demo Dataset" badge.
   * false = show an error message instead of demo data.
   */
  allowDemoFallback: true,
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 4 — Request behaviour
 * ----------------------------------------------------------------------------
 */
export const API_REQUEST_SETTINGS = {
  /**
   * How long (in milliseconds) the website waits for the backend before it
   * gives up on a request. 8000 = 8 seconds.
   */
  timeoutMs: 8000,

  /**
   * Name of the HTTP header that carries the sign-in token on every request
   * made by a signed-in user. Developer setting: change only if the backend
   * expects a different header name.
   */
  authHeaderName: 'Authorization',

  /**
   * Word placed before the token inside that header, e.g. "Bearer <token>".
   * Developer setting: change only if the backend expects a different scheme.
   */
  authHeaderScheme: 'Bearer',
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 5 — Data source identifiers
 * ----------------------------------------------------------------------------
 * The two possible values of "where the data on screen came from". They match
 * the `source` value already returned by the existing fetchSites() function.
 * Developer setting: do not change unless the data layer changes too.
 */
export const DATA_SOURCE = {
  /** Data came from the live backend (PostGIS / Google Earth Engine). */
  LIVE: 'api',

  /** Data came from the built-in demo dataset. */
  DEMO: 'mock',
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 6 — Sign-in behaviour
 * ----------------------------------------------------------------------------
 */
export const AUTH_SETTINGS = {
  /**
   * true  = the login window works immediately WITHOUT a backend: any valid
   *         email with a long enough password is accepted (demo / development).
   * false = the login window sends the email and password to the
   *         `authLogin` endpoint above.
   */
  useMockAuth: true,

  /**
   * Name under which the signed-in session is remembered in the browser, so
   * the user stays signed in after a page refresh. Developer setting.
   */
  sessionStorageKey: 'geoground.session',

  /**
   * Minimum number of characters accepted for a password. The matching
   * on-screen message is AUTH_CONTENT.validation.passwordTooShort in
   * appContent.js.
   */
  minPasswordLength: 6,
};