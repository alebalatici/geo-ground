/**
 * ============================================================================
 * satelliteConfig.js — Satellite sensors, timeline range and monitored hubs
 * ============================================================================
 *
 * WHAT THIS FILE CONTROLS
 * Everything the satellite viewport and the historical timeline need to know
 * that is NOT a plain screen label: which sensors can be selected (Sentinel-2,
 * Sentinel-1, Landsat), their descriptions and bands, which readings each
 * sensor displays, the first and last year of the timeline, and the default
 * map coordinates of the monitored Romanian hubs.
 *
 * WHO CAN EDIT IT
 * Anyone on the team. No React knowledge is needed. Plain screen labels such
 * as button texts live in appContent.js; this file holds the sensor facts.
 */

/**
 * ----------------------------------------------------------------------------
 * SECTION 1 — Coordinate system
 * ----------------------------------------------------------------------------
 */

/**
 * Name of the coordinate system shown next to every coordinate in the
 * satellite viewport and in the coordinate table (longitude / latitude in
 * degrees, WGS 84).
 */
export const COORDINATE_REFERENCE_SYSTEM = 'EPSG:4326';

/**
 * ----------------------------------------------------------------------------
 * SECTION 2 — Sensor identifiers
 * ----------------------------------------------------------------------------
 * The internal name of each sensor. These names are also sent to the backend
 * to say which satellite layer is wanted, so they must match the backend.
 * Developer setting: do not rename without checking the backend.
 */
export const SENSOR_IDS = {
  /** Sentinel-2 optical imagery (vegetation index NDVI). */
  SENTINEL_2: 'sentinel2',

  /** Sentinel-1 C-band radar (SAR). */
  SENTINEL_1: 'sentinel1',

  /** Landsat 7 / 8 / 9 historical and thermal imagery (surface temperature). */
  LANDSAT: 'landsat',
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 3 — Sensor definitions
 * ----------------------------------------------------------------------------
 * One entry per sensor, in the order the buttons appear in the sensor
 * selector of the satellite viewport.
 *
 * Fields of each entry:
 *   id                — internal name (see SENSOR_IDS).
 *   name              — main title of the sensor button, e.g. "Sentinel-2".
 *   modeLabel         — small text under the title describing what the sensor shows.
 *   resolutionLabel   — ground detail of the images, shown next to the title.
 *   description       — one or two sentences explaining the sensor, shown in the viewport.
 *   availableFromYear — first year with images; earlier timeline years show "no acquisition".
 *   bands             — the spectral bands used (code, name and wavelength shown in the viewport).
 *   metrics           — the readings displayed in the viewport panel for this sensor:
 *                         key      = field name of the reading in the data returned by the backend,
 *                         label    = text shown in front of the value,
 *                         unit     = unit shown after the value ('' for none),
 *                         decimals = number of digits after the decimal point.
 */
export const SENSOR_DEFINITIONS = [
  {
    id: SENSOR_IDS.SENTINEL_2,
    name: 'Sentinel-2',
    modeLabel: 'Optical / NDVI',
    resolutionLabel: '10 m',
    description:
      'Multispectral optical imagery. The NDVI vegetation index drops when vegetation is cleared, which makes it the earliest signal of land clearing.',
    availableFromYear: 2015,
    bands: [
      { code: 'B2', name: 'Blue', wavelengthLabel: '~490 nm' },
      { code: 'B3', name: 'Green', wavelengthLabel: '~560 nm' },
      { code: 'B4', name: 'Red', wavelengthLabel: '~665 nm' },
      { code: 'B8', name: 'Near infrared', wavelengthLabel: '~840 nm' },
    ],
    metrics: [{ key: 'ndvi', label: 'NDVI', unit: '', decimals: 2 }],
  },
  {
    id: SENSOR_IDS.SENTINEL_1,
    name: 'Sentinel-1',
    modeLabel: 'SAR Radar',
    resolutionLabel: '10 m',
    description:
      'C-band synthetic aperture radar. It sees through clouds and at night, and reveals new buildings, earthworks and surface changes through radar backscatter.',
    availableFromYear: 2014,
    bands: [
      { code: 'VV', name: 'Vertical transmit / vertical receive', wavelengthLabel: 'C-band, ~5.4 GHz' },
      { code: 'VH', name: 'Vertical transmit / horizontal receive', wavelengthLabel: 'C-band, ~5.4 GHz' },
    ],
    metrics: [
      { key: 'vvDb', label: 'SAR VV', unit: 'dB', decimals: 1 },
      { key: 'vhDb', label: 'SAR VH', unit: 'dB', decimals: 1 },
    ],
  },
  {
    id: SENSOR_IDS.LANDSAT,
    name: 'Landsat 7/8/9',
    modeLabel: 'Historical / Thermal LST',
    resolutionLabel: '30 m',
    description:
      'Long-running archive back to 2000 with a thermal band. Land surface temperature rises where vegetation is replaced by bare soil, asphalt or concrete.',
    availableFromYear: 2000,
    bands: [
      { code: 'B4', name: 'Red', wavelengthLabel: '~655 nm' },
      { code: 'B5', name: 'Near infrared', wavelengthLabel: '~865 nm' },
      { code: 'B10', name: 'Thermal infrared', wavelengthLabel: '~10.9 µm' },
    ],
    metrics: [{ key: 'lstCelsius', label: 'LST', unit: '°C', decimals: 1 }],
  },
];

/**
 * The sensor selected when the satellite viewport first opens.
 * Use one of the ids from SENSOR_IDS.
 */
export const DEFAULT_SENSOR_ID = SENSOR_IDS.SENTINEL_2;

/**
 * ----------------------------------------------------------------------------
 * SECTION 4 — Historical timeline range
 * ----------------------------------------------------------------------------
 */

/**
 * The newest year available on the timeline. It follows the current calendar
 * year automatically. To fix it to a specific year, replace the expression
 * with a plain number, e.g. 2026.
 */
const LATEST_TIMELINE_YEAR = new Date().getFullYear();

/**
 * Year range of the historical timeline slider (2000 to the present).
 */
export const TIMELINE_YEAR_BOUNDS = {
  /** First (left-most) year of the slider. */
  minYear: 2000,

  /** Last (right-most) year of the slider. */
  maxYear: LATEST_TIMELINE_YEAR,

  /** Year selected when the website opens. */
  defaultYear: LATEST_TIMELINE_YEAR,
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 5 — Monitored hubs
 * ----------------------------------------------------------------------------
 * The Romanian hubs offered in the parcel selector of the satellite viewport,
 * with their default centre coordinates (latitude and longitude in degrees).
 *
 * Fields of each entry:
 *   id     — internal name; it should match how parcels are tagged in the data
 *            (to be checked when the viewport is connected to the data).
 *   name   — hub name shown on screen.
 *   region — county shown under the hub name.
 *   center — default coordinates used when no parcel geometry is available.
 */
export const MONITORED_HUBS = [
  {
    id: 'cluj-napoca',
    name: 'Cluj-Napoca',
    region: 'Cluj County',
    center: { lat: 46.7712, lng: 23.6236 },
  },
  {
    id: 'bucharest',
    name: 'Bucharest',
    region: 'Bucharest-Ilfov',
    center: { lat: 44.4268, lng: 26.1025 },
  },
  {
    id: 'timisoara',
    name: 'Timișoara',
    region: 'Timiș County',
    center: { lat: 45.7489, lng: 21.2087 },
  },
];

/**
 * The hub selected when the satellite viewport first opens.
 * Use one of the ids from MONITORED_HUBS.
 */
export const DEFAULT_HUB_ID = 'cluj-napoca';

/**
 * ----------------------------------------------------------------------------
 * SECTION 6 — Parcel drawing settings
 * ----------------------------------------------------------------------------
 * Fine-tuning of how the parcel outline is drawn in the satellite viewport.
 */
export const VIEWPORT_DRAWING_SETTINGS = {
  /** Number of grid lines drawn in each direction behind the parcel. More lines = finer grid. */
  gridDivisions: 8,

  /**
   * Empty margin kept around the parcel outline, as a fraction of its size.
   * 0.15 = 15% margin. Increase it to zoom out, decrease it to zoom in.
   */
  polygonPaddingRatio: 0.15,

  /**
   * Digits after the decimal point shown for every coordinate.
   * 5 digits is roughly 1 metre of precision on the ground.
   */
  coordinateDecimals: 5,
};