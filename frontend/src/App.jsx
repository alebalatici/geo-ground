import { useEffect, useState } from "react";
import { fetchSites } from "./api/endpoints";
import ExecutiveBriefCard from "./components/ai/ExecutiveBriefCard";
import SiteAssistantSidebar from "./components/ai/SiteAssistantSidebar";
import MapPanel from "./components/MapPanel";

function App() {
  const [viewMode, setViewMode] = useState("executive");
  const [sites, setSites] = useState([]);
  const [dataSource, setDataSource] = useState("mock");
  const [selectedSiteId, setSelectedSiteId] = useState(null);
  const [activeYear, setActiveYear] = useState(2026);
  const [loadingSites, setLoadingSites] = useState(true);
  const [recenterSignal, setRecenterSignal] = useState(0);

  useEffect(() => {
    let active = true;

    setLoadingSites(true);
    fetchSites()
      .then(({ data, source }) => {
        if (!active) return;
        setSites(data);
        setDataSource(source);
        if (data.length > 0) {
          setSelectedSiteId((prev) => prev ?? data[0].id);
        }
      })
      .finally(() => {
        if (active) setLoadingSites(false);
      });

    return () => {
      active = false;
    };
  }, []);

  const selectedSite = sites.find((site) => site.id === selectedSiteId) || null;

  const handleRecenter = () => {
    setRecenterSignal((prev) => prev + 1);
  };

  return (
    <div className="flex min-h-screen flex-col bg-surface-base text-text-primary">
      {/* Header */}
      <header className="flex items-center justify-between border-b border-border-subtle bg-surface-elevated px-6 py-3">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-lg font-semibold tracking-tight text-accent-amber">
              GeoGround
            </h1>
            <p className="text-xs text-text-muted">
              Commercial Real Estate &amp; Site Intelligence
            </p>
          </div>

          <span className="rounded-md border border-border-subtle bg-surface-base px-2 py-0.5 text-[11px] text-text-secondary">
            Source: {loadingSites ? "loading..." : dataSource}
          </span>
        </div>

        <div className="flex rounded-lg border border-border-subtle bg-surface-base p-1 text-xs">
          <button
            type="button"
            onClick={() => setViewMode("executive")}
            className={`rounded-md px-3 py-1.5 font-medium transition ${
              viewMode === "executive"
                ? "bg-accent-amber text-slate-950"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Executive
          </button>
          <button
            type="button"
            onClick={() => setViewMode("enterprise")}
            className={`rounded-md px-3 py-1.5 font-medium transition ${
              viewMode === "enterprise"
                ? "bg-accent-amber text-slate-950"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            Enterprise
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="grid flex-1 grid-cols-1 gap-4 p-4 lg:grid-cols-12">
        {/* Coloana stângă: Hartă / Enterprise + Executive Brief + Timeline */}
        <section className="flex flex-col justify-between gap-4 rounded-xl border border-border-subtle bg-surface-card p-4 lg:col-span-8">
          {viewMode === "executive" ? (
            <>
              <MapPanel
                sites={sites}
                selectedSiteId={selectedSiteId}
                onSelectSite={setSelectedSiteId}
                recenterSignal={recenterSignal}
                onRecenter={handleRecenter}
              />

              {/* Rezumatul executiv generat automat pentru parcela selectată */}
              <ExecutiveBriefCard siteId={selectedSite?.id} />
            </>
          ) : (
            <div className="flex min-h-[380px] flex-1 flex-col items-center justify-center rounded-lg border border-dashed border-border-subtle p-4 text-center text-sm text-text-muted">
              Enterprise Analytics: Correlation Charts, Coordinate Table &amp; CSV Export
            </div>
          )}

          {/* Timeline Slider (2000 – Present) */}
          <div className="flex flex-col gap-2 rounded-lg border border-border-subtle bg-surface-elevated px-4 py-3 text-xs text-text-secondary sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <span className="font-medium text-text-primary">
                Timeline Slider (2000 – Present)
              </span>
              <span className="rounded border border-border-subtle bg-surface-base px-2 py-0.5 font-mono text-[11px] text-accent-amber">
                {activeYear}
              </span>
            </div>

            <div className="flex flex-1 items-center gap-3 sm:max-w-md">
              <span className="font-mono text-[11px] text-text-muted">2000</span>
              <input
                type="range"
                min={2000}
                max={2026}
                value={activeYear}
                onChange={(e) => setActiveYear(Number(e.target.value))}
                className="h-1.5 w-full cursor-pointer accent-amber-500"
              />
              <span className="font-mono text-[11px] text-text-muted">2026</span>
            </div>
          </div>
        </section>

        {/* Coloana dreaptă: Detalii Parcelă + Chat AI Contextual */}
        <aside className="flex flex-col gap-4 lg:col-span-4">
          <div className="rounded-xl border border-border-subtle bg-surface-card p-4">
            <h2 className="text-sm font-semibold text-text-primary">
              Site Details &amp; Alerts
            </h2>

            {loadingSites ? (
              <p className="mt-2 text-xs text-text-muted">Loading sites...</p>
            ) : selectedSite ? (
              <div className="mt-2 space-y-2 text-xs">
                <p className="font-medium text-text-primary">{selectedSite.name}</p>
                <p className="text-text-muted">
                  Region: {selectedSite.city || selectedSite.region || "—"} • Status:{" "}
                  {selectedSite.latest_alert?.signal_type || selectedSite.status || "—"}
                </p>
                {Array.isArray(selectedSite.alerts) && selectedSite.alerts.length > 0 && (
                  <div className="space-y-1 pt-1">
                    {selectedSite.alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className="rounded-md border border-border-subtle bg-surface-elevated p-2 text-text-secondary"
                      >
                        <p className="font-medium text-amber-400">{alert.title}</p>
                        <p className="mt-0.5 text-[11px] text-text-muted">
                          {alert.confirmed_by_radar ? "Confirmed by Radar" : "Unconfirmed"} •{" "}
                          {alert.duration_months} months active
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="mt-1 text-xs text-text-muted">
                Select a site polygon on the map to inspect alerts and telemetry.
              </p>
            )}
          </div>

          {/* Asistentul AI interactiv ancorat pe situl activ și anul de pe slider */}
          <div className="flex min-h-[420px] flex-1 overflow-hidden rounded-xl border border-border-subtle">
            <SiteAssistantSidebar
              activeSite={selectedSite}
              activeYear={activeYear}
            />
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;