// Convertește un punct [lon, lat] (GeoJSON) în [lat, lon] (Leaflet)
export function lonLatToLatLng(coord) {
  if (!Array.isArray(coord) || coord.length < 2) return null;
  const [lon, lat] = coord;
  if (typeof lon !== "number" || typeof lat !== "number") return null;
  return [lat, lon];
}

// Convertește un inel de poligon GeoJSON [[lon, lat], ...] în perechi [[lat, lon], ...]
export function ringToLatLngs(ring = []) {
  if (!Array.isArray(ring)) return [];
  return ring.map(lonLatToLatLng).filter(Boolean);
}

// Formatează o suprafață în metri pătrați (ex. 142000 -> "142,000 m²")
export function formatAreaM2(area) {
  if (typeof area !== "number" || Number.isNaN(area)) return "—";
  return `${Math.round(area).toLocaleString("en-US")} m²`;
}

// Verifică dacă o lună (1-12) este în sezonul de iarnă (decembrie, ianuarie, februarie)
export function isWinterMonth(month) {
  return month === 12 || month === 1 || month === 2;
}