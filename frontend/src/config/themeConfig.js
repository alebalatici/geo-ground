/**
 * ============================================================================
 * themeConfig.js — Theme settings (Dark / Light)
 * ============================================================================
 *
 * WHAT THIS FILE CONTROLS
 * Which colour theme the website opens with, how the user's choice is
 * remembered in the browser, and a plain-language reference of the brand
 * colour palette.
 *
 * WHO CAN EDIT IT
 * Anyone on the team. No React knowledge is needed.
 *
 * IMPORTANT — WHERE THE REAL COLOURS LIVE
 * Changing a hex value in this file does NOT change any colour on screen.
 * The colours actually used by the interface are defined in:
 *   - src/styles/tokens.css  (the raw palette hex values)
 *   - src/styles/themes.css  (which palette colour each part of the interface
 *                             uses in Dark and in Light mode)
 */

/**
 * ----------------------------------------------------------------------------
 * SECTION 1 — Theme identifiers
 * ----------------------------------------------------------------------------
 * The two internal names of the available themes. They must match the
 * [data-theme="..."] selectors in src/styles/themes.css.
 * Developer setting: do not rename unless themes.css is changed as well.
 */
export const THEME_IDS = {
  /** Dark theme (deep plum background, cream text). */
  DARK: 'dark',

  /** Light theme (warm cream background, near-black text). */
  LIGHT: 'light',
};

/**
 * ----------------------------------------------------------------------------
 * SECTION 2 — Default theme
 * ----------------------------------------------------------------------------
 */

/**
 * The theme shown the first time someone opens the website (before they have
 * ever pressed the theme switch). Use 'dark' or 'light'.
 *
 * @type {'dark' | 'light'}
 */
export const DEFAULT_THEME = THEME_IDS.DARK;

/**
 * ----------------------------------------------------------------------------
 * SECTION 3 — Browser storage (developer settings)
 * ----------------------------------------------------------------------------
 */

/**
 * Name under which the user's theme choice is remembered in the browser, so
 * the same theme is shown on the next visit.
 */
export const THEME_STORAGE_KEY = 'geoground.theme';

/**
 * Name of the attribute set on the page's root element to activate a theme,
 * e.g. <html data-theme="dark">. Must match the selectors in
 * src/styles/themes.css.
 */
export const THEME_ATTRIBUTE_NAME = 'data-theme';

/**
 * ----------------------------------------------------------------------------
 * SECTION 4 — Theme list
 * ----------------------------------------------------------------------------
 * The themes the user can switch between, in display order.
 */
export const THEME_OPTIONS = [
  {
    /** Internal name (see THEME_IDS). */
    id: THEME_IDS.DARK,
    /** Name shown next to the theme switch. */
    label: 'Dark',
  },
  {
    id: THEME_IDS.LIGHT,
    label: 'Light',
  },
];

/**
 * ----------------------------------------------------------------------------
 * SECTION 5 — Brand palette reference (documentation only)
 * ----------------------------------------------------------------------------
 * The six institutional plum-to-cream colours of GeoGround.
 * This list is a REFERENCE for the team. The values that really drive the
 * interface are in src/styles/tokens.css.
 */
export const PALETTE_REFERENCE = [
  {
    /** Short name used for the colour in tokens.css (--palette-cream). */
    token: 'cream',
    /** Human-readable name. */
    name: 'Warm Cream (Alabaster)',
    /** Colour value. */
    hex: '#FAE5D8',
    /** Where this colour is mainly used on screen. */
    usage: 'Light theme background; Dark theme headings and primary text.',
  },
  {
    token: 'rose',
    name: 'Dusty Rose (Soft Blush)',
    hex: '#DFB6B2',
    usage: 'Dark theme body text, borders and primary buttons.',
  },
  {
    token: 'mauve',
    name: 'Muted Plum (Mauve)',
    hex: '#824D69',
    usage: 'Badges, secondary highlights, focus rings and light-theme captions.',
  },
  {
    token: 'aubergine',
    name: 'Deep Aubergine (Royal Plum)',
    hex: '#522959',
    usage: 'Dark theme header and hover surfaces; Light theme primary buttons.',
  },
  {
    token: 'midnight',
    name: 'Midnight Indigo (Deep Violet)',
    hex: '#2A114B',
    usage: 'Dark theme cards, panels and modals; Light theme body text.',
  },
  {
    token: 'obsidian',
    name: 'Obsidian Plum (Deep Dark)',
    hex: '#180018',
    usage: 'Dark theme page background; Light theme headings.',
  },
];