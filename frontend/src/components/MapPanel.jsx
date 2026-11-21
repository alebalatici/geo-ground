import { useEffect, useMemo, useRef } from "react";
import { MapContainer, TileLayer, Polygon, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { ringToLatLngs } from "../utils/geo";

const DEFAULT_CENTER = [45.9432, 24.9668];
const DEFAULT_ZOOM = 7;

export function MapController({
  containerRef,
  selectedPositions,
  allPositions,
  recenterSignal,
}) {
  const map = useMap();

  useEffect(() => {
    const el = containerRef?.current;
    if (!el) return;

    const syncSize = () => map.invalidateSize();
    syncSize();
    const t1 = setTimeout(syncSize, 150);
    const t2 = setTimeout(syncSize, 400);

    const observer = new ResizeObserver(syncSize);
    observer.observe(el);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      observer.disconnect();
    };
  }, [containerRef, map]);

  useEffect(() => {
    map.invalidateSize();
    if (selectedPositions && selectedPositions.length >= 3) {
      map.fitBounds(selectedPositions, { padding: [40, 40], maxZoom: 13 });
    } else if (allPositions && allPositions.length >= 3) {
      map.fitBounds(allPositions, { padding: [40, 40], maxZoom: 12 });
    } else {
      map.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
    }
  }, [selectedPositions, allPositions, recenterSignal, map]);

  return null;
}

export default function MapPanel({
  sites = [],
  selectedSiteId,
  onSelectSite,
  recenterSignal = 0,
  onRecenter,
}) {
  const containerRef = useRef(null);

  const parsedSites = useMemo(() => {
    if (!Array.isArray(sites)) return [];
    return sites
      .map((site) => ({
        ...site,
        latLngs: site?.polygon ? ringToLatLngs(site.polygon) : [],
      }))
      .filter((site) => site.latLngs && site.latLngs.length >= 3);
  }, [sites]);

  const selectedSite =
    parsedSites.find((site) => site.id === selectedSiteId) || parsedSites[0] || null;

  const allPoints = useMemo(() => {
    return parsedSites.flatMap((site) => site.latLngs);
  }, [parsedSites]);

  return (
    <div className="flex flex-col gap-3">
      <div
        ref={containerRef}
        className="relative h-[400px] w-full overflow-hidden rounded-lg border border-border-subtle bg-slate-900"
      >
        <MapContainer
          center={DEFAULT_CENTER}
          zoom={DEFAULT_ZOOM}
          style={{ height: "100%", width: "100%" }}
          scrollWheelZoom
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <MapController
            containerRef={containerRef}
            selectedPositions={selectedSite?.latLngs}
            allPositions={allPoints}
            recenterSignal={recenterSignal}
          />

          {parsedSites.map((site) => {
            const isAmber = site.status === "amber";
            const isSelected = site.id === selectedSite?.id;

            return (
              <Polygon
                key={site.id}
                positions={site.latLngs}
                pathOptions={{
                  color: isAmber ? "#eab308" : "#16a34a",
                  fillColor: isAmber ? "#eab308" : "#16a34a",
                  fillOpacity: isSelected ? 0.35 : 0.18,
                  weight: isSelected ? 3 : 2,
                }}
                eventHandlers={{
                  click: () => onSelectSite?.(site.id),
                }}
              >
                <Popup>
                  <div className="text-slate-900">
                    <p className="font-semibold">{site.name}</p>
                    <p className="text-xs">Status: {site.status || "green"}</p>
                  </div>
                </Popup>
              </Polygon>
            );
          })}
        </MapContainer>
      </div>

      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={() => onRecenter?.()}
          title="Recenter map on selected site"
          className="rounded-lg border-2 border-accent-amber bg-surface-elevated px-5 py-2.5 text-sm font-bold text-accent-amber shadow-md transition hover:bg-accent-amber hover:text-slate-950 active:scale-95"
        >
          Recenter Map
        </button>
      </div>
    </div>
  );
}