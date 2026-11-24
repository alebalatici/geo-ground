/**
 * ============================================================================
 * appContent.js — Every piece of text shown in the interface
 * ============================================================================
 *
 * WHAT THIS FILE CONTROLS
 * All human-readable text on screen: headings, labels, button titles, form
 * messages, empty-state messages and the quick prompts of the AI assistant.
 * Edit the text between the quotation marks and the website updates after a
 * refresh. No React knowledge is needed.
 *
 * HOW TO EDIT SAFELY
 * - Change only the text inside the quotes ('...'). Keep the quotes, the
 *   colon after the name, and the comma at the end of every line.
 * - Some texts contain a placeholder written between curly braces, for example
 *   {year} or {minLength}. The website replaces it with the real value.
 *   Keep the placeholder exactly as written, but you may move it inside the
 *   sentence.
 * - Sensor names and descriptions are not here: see satelliteConfig.js.
 * - Colours are not here: see src/styles/themes.css.
 *
 * The file is organised by area of the screen:
 *   COMMON_CONTENT, HEADER_CONTENT, AUTH_CONTENT, SATELLITE_VIEWER_CONTENT,
 *   EXECUTIVE_CONTENT, ENTERPRISE_CONTENT, TIMELINE_CONTENT, ADVISOR_CONTENT.
 */

/**
 * ----------------------------------------------------------------------------
 * COMMON_CONTENT — Texts shared by several areas of the screen
 * ----------------------------------------------------------------------------
 */
export const COMMON_CONTENT = {
  /** Generic message shown while any panel is loading data. */
  loadingLabel: 'Loading…',

  /** Text of the button that repeats a failed action. */
  retryButton: 'Try again',

  /** Text of generic "close" buttons. */
  closeButton: 'Close',

  /** Symbol displayed in place of a value that is missing or not available. */
  emptyValue: '—',

  /** Units written after measured values. */
  units: {
    /** Unit written after a parcel area, e.g. "12,450 m²". */
    areaSquareMeters: 'm²',

    /** Unit written after a radar value, e.g. "-12.4 dB". */
    decibels: 'dB',

    /** Unit written after a temperature, e.g. "31.2 °C". */
    celsius: '°C',
  },

  /**
   * Parcel status levels shown as coloured pill tags (green and amber) in the
   * top bar, the site details card and the executive brief.
   */
  statusLevels: {
    /** Green pill: nothing unusual detected by the satellites. */
    stable: {
      /** Text inside the green pill. */
      label: 'Baseline / Stable',
      /** Tooltip explaining the green pill. */
      description: 'No significant change detected in the satellite signal.',
    },

    /** Amber pill: land clearing or construction detected. */
    alert: {
      /** Text inside the amber pill. */
      label: 'Construction / Land Clearing',
      /** Tooltip explaining the amber pill. */
      description: 'Satellite signals indicate land clearing or construction activity.',
    },
  },
};

/**
 * ----------------------------------------------------------------------------
 * HEADER_CONTENT — Top bar of the website
 * ----------------------------------------------------------------------------
 */

/**
 * ----------------------------------------------------------------------------
 * HEADER_CONTENT — Top navigation bar of the website
 * ----------------------------------------------------------------------------
 */
export const HEADER_CONTENT = {
  /** Brand name shown at the top-left of every page. */
  brandName: 'GeoGround',

  /** Small line of text describing the brand (used by the page hero and tooltips). */
  brandSubtitle: 'Commercial Real Estate & Satellite Intelligence',

  /** Description read aloud by screen readers for the brand link (it scrolls to the top). */
  brandAriaLabel: 'GeoGround — back to top',

  /** Description read aloud by screen readers for the group of navigation links. */
  navAriaLabel: 'Primary navigation',

  /**
   * Links in the middle of the top bar. Each link scrolls smoothly to the
   * section of the page whose id equals targetId.
   * One block per link: label = visible text, targetId = id of the section.
   * Add, remove or reorder blocks freely; keep the commas.
   */
  navLinks: [
    {
      /** Text of the link. */
      label: 'Platform',
      /** The page section this link scrolls to (the section must have this id). */
      targetId: 'platform',
    },
    {
      /** Text of the link. */
      label: 'Our Mission',
      /** The page section this link scrolls to (the section must have this id). */
      targetId: 'mission',
    },
  ],

  /** Small pill next to the brand showing where the data comes from. */
  dataSourceBadge: {
    /** Pill text when the data comes from the live backend. */
    live: 'Live',

    /** Pill text when the built-in demo dataset is shown. */
    demo: 'Demo',

    /** Pill text while the connection to the backend is being checked. */
    loading: 'Connecting…',

    /** Tooltip shown when hovering the pill while data is live. */
    liveTooltip: 'Data is streamed from the live PostGIS database and Google Earth Engine.',

    /** Tooltip shown when hovering the pill while demo data is shown. */
    demoTooltip: 'The backend is not connected. A built-in demo dataset is shown.',

    /** Tooltip shown when hovering the pill while the connection is being checked. */
    loadingTooltip: 'Checking the connection to the backend…',
  },

  /** Switch between the two dashboard views. */
  viewSwitcher: {
    /** Description read aloud by screen readers for the whole switch. */
    ariaLabel: 'Select dashboard view',

    /** Text of the first view button. */
    executiveLabel: 'Executive',

    /** Text of the second view button. */
    enterpriseLabel: 'Enterprise',
  },

  /** Button that switches between the Dark and the Light theme. */
  themeToggle: {
    /** Description read aloud by screen readers for the button. */
    ariaLabel: 'Switch color theme',

    /** Tooltip shown while the Dark theme is active. */
    switchToLightTooltip: 'Switch to light theme',

    /** Tooltip shown while the Light theme is active. */
    switchToDarkTooltip: 'Switch to dark theme',
  },

  /** Empty area at the top-right reserved for the Log In / Sign Up buttons. */
  authSlot: {
    /** Description read aloud by screen readers for the account buttons area. */
    ariaLabel: 'Account actions',
  },
};

/**
 * ----------------------------------------------------------------------------
 * HERO_CONTENT — Large introduction section under the top bar
 * ----------------------------------------------------------------------------
 */
export const HERO_CONTENT = {
  /** Small pill above the title. */
   eyebrow: 'Satellite intelligence for commercial real estate',

  /** Giant title of the page. */
  title: 'GeoGround',

  /** One clear sentence explaining what the platform does, shown under the title. */
  headline: 'Spot urban expansion and new construction before it reaches the market.',

  /** Longer paragraph under the headline. */
  description:
    'GeoGround combines Sentinel-1, Sentinel-2 and Landsat data to detect land clearing and construction on monitored parcels early, so you can decide based on verified ground truth.',

  /** First (filled) button. */
  primaryButton: {
    /** Text of the button. */
    label: 'Explore Telemetry',
    /** The page section the button scrolls to (the section must have this id). */
    targetId: 'platform',
  },

  /** Second (outlined) button. */
  secondaryButton: {
    /** Text of the button. */
    label: 'Our Mission',
    /** The page section the button scrolls to (the section must have this id). */
    targetId: 'mission',
  },
};

/**
 * ----------------------------------------------------------------------------
 * AUTH_CONTENT — Sign In button, account pill and login window
 * ----------------------------------------------------------------------------
 */
export const AUTH_CONTENT = {
  /** Text of the button at the top-right when nobody is signed in. */
  signInButton: 'Sign In',

  /** Text of the button shown to a signed-in user. */
  signOutButton: 'Sign Out',

  /** Small text written before the user's email in the account menu. */
  signedInAsLabel: 'Signed in as',

  /** Description read aloud by screen readers for the account menu. */
  userMenuAriaLabel: 'Account menu',

  /** Texts inside the login window. */
  modal: {
    /** Large heading of the login window. */
    title: 'Sign in to GeoGround',

    /** Sentence under the heading. */
    subtitle: 'Access institutional site intelligence for your organization.',

    /** Label above the email field. */
    emailLabel: 'Email',

    /** Grey example text inside the empty email field. */
    emailPlaceholder: 'name@company.com',

    /** Label above the password field. */
    passwordLabel: 'Password',

    /** Grey example text inside the empty password field. */
    passwordPlaceholder: 'Enter your password',

    /** Text of the main button of the login window. */
    submitButton: 'Sign In',

    /** Text of the main button while the sign-in request is running. */
    submittingButton: 'Signing in…',

    /** Text of the button that closes the window without signing in. */
    closeButton: 'Cancel',

    /** Description read aloud by screen readers for the "X" close icon. */
    closeAriaLabel: 'Close sign-in window',
  },

  /** Error messages shown under the fields of the login window. */
  validation: {
    /** Shown when the email field is empty. */
    emailRequired: 'Please enter your email address.',

    /** Shown when the email is not written like name@company.com. */
    emailInvalid: 'Please enter a valid email address.',

    /** Shown when the password field is empty. */
    passwordRequired: 'Please enter your password.',

    /** Shown when the password is too short. {minLength} is replaced by the number set in apiConfig.js. */
    passwordTooShort: 'Your password must be at least {minLength} characters long.',

    /** Shown when the server rejects the email or password. */
    invalidCredentials: 'The email or password is incorrect.',

    /** Shown when the sign-in server cannot be reached. */
    serviceUnavailable: 'Sign-in is temporarily unavailable. Please try again.',
  },
};

/**
 * ----------------------------------------------------------------------------
 * SATELLITE_VIEWER_CONTENT — Central satellite imagery and telemetry viewport
 * ----------------------------------------------------------------------------
 */
export const SATELLITE_VIEWER_CONTENT = {
  /** Heading of the satellite viewport card. */
  title: 'Satellite Telemetry Viewport',

  /** Dropdown / strip used to choose which monitored parcel is displayed. */
  parcelSelector: {
    /** Label above the parcel selector. */
    label: 'Monitored parcel',

    /** Label above the group of hubs (Cluj-Napoca, Bucharest, Timișoara). */
    hubLabel: 'Hub',

    /** Grey text shown while no parcel is chosen yet. */
    placeholder: 'Select a parcel',

    /** Description read aloud by screen readers for the selector. */
    ariaLabel: 'Select monitored parcel',
  },

  /** Buttons used to choose the satellite sensor. */
  sensorSelector: {
    /** Label above the sensor buttons. */
    label: 'Sensor',

    /** Description read aloud by screen readers for the sensor buttons. */
    ariaLabel: 'Select satellite sensor',
  },

  /** Information overlay (HUD) drawn on top of the viewport. */
  hud: {
    /** Heading of the list of corner coordinates. */
    cornersTitle: 'Corner coordinates (EPSG:4326)',

    /** Short names of the four corners of the parcel area. */
    cornerLabels: {
      /** North-west corner. */
      northWest: 'NW',
      /** North-east corner. */
      northEast: 'NE',
      /** South-east corner. */
      southEast: 'SE',
      /** South-west corner. */
      southWest: 'SW',
    },

    /** Label in front of the parcel area. */
    areaLabel: 'Parcel area',

    /** Label in front of the selected timeline year. */
    activeYearLabel: 'Acquisition year',

    /** Heading of the block with the latest satellite readings. */
    readingsTitle: 'Latest spectral readings',

    /** Label in front of the vegetation index value. */
    ndviLabel: 'NDVI',

    /** Label in front of the radar VV value. */
    sarVvLabel: 'SAR VV',

    /** Label in front of the radar VH value. */
    sarVhLabel: 'SAR VH',

    /** Label in front of the land surface temperature. */
    lstLabel: 'LST',
  },

  /** Messages shown when the viewport has nothing to display. */
  states: {
    /** Shown while satellite data is loading. */
    loading: 'Loading satellite telemetry…',

    /** Shown when no parcel has been selected. */
    noParcelSelected: 'Select a monitored parcel to view its satellite telemetry.',

    /** Shown when the sensor has no image for the chosen year. {year} is replaced by that year. */
    noReadingForYear: 'No acquisition available for this sensor in {year}.',

    /** Shown when the satellite picture cannot be loaded and only the outline is drawn. */
    rasterUnavailable: 'Raster preview unavailable — showing vector boundary and spectral telemetry.',
  },
};

/**
 * ----------------------------------------------------------------------------
 * EXECUTIVE_CONTENT — Executive Intelligence Brief card and Site Details card
 * ----------------------------------------------------------------------------
 */
export const EXECUTIVE_CONTENT = {
  /** AI-written executive summary card. */
  brief: {
    /** Heading of the card. */
    title: 'Executive Intelligence Brief',

    /** Sentence under the heading. */
    subtitle: 'AI-generated summary of satellite signals for the selected parcel',

    /** Shown while the summary is being written. */
    loading: 'Generating executive brief…',

    /** Shown when the summary could not be created. */
    error: 'The executive brief could not be generated. Please try again.',

    /** Shown when no parcel has been selected. */
    noParcelSelected: 'Select a parcel to generate its executive brief.',

    /** Heading of the list of signal badges inside the card. */
    signalsTitle: 'Key signals',

    /** Label in front of the date the summary was created. */
    generatedLabel: 'Generated',
  },

  /** Card with the details of the selected parcel. */
  siteDetails: {
    /** Heading of the card. */
    title: 'Site Details',

    /** Labels of the rows of the card. */
    fields: {
      /** Row with the parcel name. */
      name: 'Parcel',
      /** Row with the hub (city) of the parcel. */
      hub: 'Hub',
      /** Row with the parcel area. */
      area: 'Area',
      /** Row with the satellite status (stable / alert). */
      status: 'Signal status',
      /** Row with the centre coordinates of the parcel. */
      coordinates: 'Centroid',
      /** Row with the date of the latest satellite image. */
      lastAcquisition: 'Last acquisition',
    },

    /** Heading of the list of alerts. */
    alertsTitle: 'Active alerts',

    /** Shown when the parcel has no alerts. */
    noAlerts: 'No active alerts for this parcel.',

    /** Shown when no parcel has been selected. */
    noParcelSelected: 'No parcel selected.',
  },
};

/**
 * ----------------------------------------------------------------------------
 * ENTERPRISE_CONTENT — Enterprise Analytics view
 * ----------------------------------------------------------------------------
 */
export const ENTERPRISE_CONTENT = {
  /** Main heading of the view. */
  title: 'Enterprise Analytics',

  /** Sentence under the main heading. */
  subtitle: 'Multispectral correlation and parcel coordinate data',

  /** Chart comparing vegetation, radar and temperature over the years. */
  correlation: {
    /** Heading of the chart. */
    title: 'Multispectral Correlation',

    /** Sentence under the chart heading. */
    description: 'How vegetation, radar backscatter and surface temperature move together over time.',

    /** Label under the horizontal axis of the chart. */
    xAxisLabel: 'Year',

    /** Names of the lines in the chart legend. */
    series: {
      /** Vegetation index line. */
      ndvi: 'NDVI (Sentinel-2)',
      /** Radar VV line. */
      sarVv: 'SAR VV, dB (Sentinel-1)',
      /** Surface temperature line. */
      lst: 'LST, °C (Landsat)',
    },

    /** Shown when there is no data for the chart. */
    emptyState: 'No correlation data available for this parcel.',
  },

  /** Table listing the corner points of the parcel. */
  coordinateTable: {
    /** Heading of the table. */
    title: 'Parcel Coordinates',

    /** Column titles of the table. */
    columns: {
      /** Column with the point number. */
      vertex: 'Vertex',
      /** Column with the east-west position. */
      longitude: 'Longitude',
      /** Column with the north-south position. */
      latitude: 'Latitude',
    },

    /** Note written under the table. */
    crsNote: 'Coordinates in EPSG:4326 (WGS 84).',

    /** Shown when the parcel has no coordinates. */
    emptyState: 'No coordinates available.',
  },

  /** Button that downloads the data as a spreadsheet file. */
  export: {
    /** Text of the download button. */
    buttonLabel: 'Export CSV',

    /** Text of the button while the file is being prepared. */
    exportingLabel: 'Preparing CSV…',

    /** Shown when the download failed. */
    errorMessage: 'The CSV export failed. Please try again.',

    /** Beginning of the name of the downloaded file, e.g. "geoground-site-cluj-01.csv". */
    fileNamePrefix: 'geoground-site',
  },

  /** Messages shown when the view has nothing to display. */
  states: {
    /** Shown while analytics are loading. */
    loading: 'Loading analytics…',

    /** Shown when analytics could not be loaded. */
    error: 'Analytics could not be loaded.',

    /** Shown when no parcel has been selected. */
    noParcelSelected: 'Select a parcel to see enterprise analytics.',
  },
};

/**
 * ----------------------------------------------------------------------------
 * TIMELINE_CONTENT — Historical timeline slider
 * ----------------------------------------------------------------------------
 */
export const TIMELINE_CONTENT = {
  /** Heading of the timeline card. */
  title: 'Historical Timeline',

  /** Sentence under the heading. {startYear} is replaced by the first year of the slider (see satelliteConfig.js). */
  description: 'Move the slider to compare satellite snapshots from {startYear} to the present.',

  /** Description read aloud by screen readers for the slider. */
  sliderAriaLabel: 'Select acquisition year',

  /** Small text in front of the currently selected year. */
  activeYearLabel: 'Showing',

  /** Text written next to the last year of the slider. */
  presentLabel: 'Present',

  /** Description read aloud by screen readers for the "previous year" button. */
  previousYearButton: 'Previous year',

  /** Description read aloud by screen readers for the "next year" button. */
  nextYearButton: 'Next year',
};

/**
 * ----------------------------------------------------------------------------
 * ADVISOR_CONTENT — AI site assistant (chat sidebar)
 * ----------------------------------------------------------------------------
 */
export const ADVISOR_CONTENT = {
  /** Heading of the chat sidebar. */
  title: 'Site Assistant',

  /** Sentence under the heading. */
  subtitle: 'Ask about the selected parcel',

  /** Name written above the messages of the user. */
  userLabel: 'You',

  /** Name written above the messages of the assistant. */
  assistantLabel: 'GeoGround Advisor',

  /** First message of the assistant, shown when the chat is empty. */
  welcomeMessage:
    'Hello! I can explain what the satellites see on the selected parcel and how it has changed over time. What would you like to know?',

  /** Heading above the suggested questions. */
  quickPromptsTitle: 'Quick prompts',

  /**
   * Suggested questions shown as clickable chips. Clicking a chip sends that
   * text as a question. Add, remove or reword lines freely: one line per
   * question, each inside quotes and followed by a comma.
   */
  quickPrompts: [
    'What changed on this parcel since 2020?',
    'Is there any land clearing or construction activity?',
    'Summarize the investment risk of this site.',
    'How has vegetation (NDVI) evolved over time?',
  ],

  /** Grey example text inside the empty message box. */
  inputPlaceholder: 'Ask about this parcel…',

  /** Text of the send button. */
  sendButton: 'Send',

  /** Message shown while the assistant is writing an answer. */
  thinkingMessage: 'Analyzing satellite signals…',

  /** Message shown when the assistant could not answer. */
  errorMessage: 'The assistant could not answer right now. Please try again.',

  /** Shown when no parcel has been selected. */
  noParcelSelected: 'Select a parcel to start a conversation about it.',

  /** Small note written under the message box. */
  disclaimer: 'AI-generated analysis. Verify critical findings before making investment decisions.',
};